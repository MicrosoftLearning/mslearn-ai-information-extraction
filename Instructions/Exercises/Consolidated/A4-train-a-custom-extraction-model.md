---
lab:
    title: 'Task 4 – Train a custom extraction model'
    description: 'Train a custom Azure Document Intelligence extraction model on labeled Fabrikam Logistics forms, then call it from Python to extract fields no prebuilt model knows about.'
    level: 300
    concepts: 'Document Intelligence, custom extraction models, training data, SAS URIs'
    islab: true
    status: 'draft'
---

# Task 4 — Train a custom extraction model

*Part of the **Extract information from business content** lab. New here? Start with [Getting started](A0-getting-started.md).*

> **What you need:** a **Document Intelligence** resource, the starter code, and a Bash shell
> with the Azure CLI signed in (for the training-data upload script). This task does **not** need
> a Foundry resource or anything you built in Tasks 1, 2, or 3. If you haven't already, complete
> [Getting started](A0-getting-started.md) to create your Document Intelligence resource, clone
> the code, and set `DOC_INTELLIGENCE_ENDPOINT` and `DOC_INTELLIGENCE_KEY` in `Python/.env`.
> You'll fill in `CUSTOM_MODEL_ID` partway through this task, once you've trained the model. Then, from the `Python` folder, verify you're ready:

```
python ../setup/check_env.py --task 4
```

> `CUSTOM_MODEL_ID` will show as MISSING until you train the model below — that's expected.

> **Continuing from a previous task?** If you just finished Task 3, you already have everything
> except the trained model itself: same resource, same `.env`, same virtual environment. Skip
> straight to **Prepare training data** below.

---

Prebuilt models are unbeatable for standard documents. But Fabrikam Logistics also runs on forms
that only Fabrikam Logistics uses — internal transfer dockets whose layout no prebuilt model has
ever seen. For those, you train your own model on a handful of labeled examples.

<style>
/* "Ask Rani" just-in-time concept blocks */
details.concept { margin:.6rem 0 1rem; }
details.concept > summary { display:inline-block; cursor:pointer; list-style:none;
  font-size:.85em; font-weight:600; color:#0b6a8f; background:#0b6a8f12;
  border:1px solid #0b6a8f33; border-radius:999px; padding:.2em .7em; }
details.concept > summary::-webkit-details-marker { display:none; }
details.concept > summary::before { content:"Ask Rani: "; font-weight:700; }
details.concept > summary:hover { background:#0b6a8f; color:#fff; border-color:#0b6a8f; }
details.concept[open] > summary { border-bottom-left-radius:0; border-bottom-right-radius:0; }
details.concept .concept-body { border:1px solid #0b6a8f33; border-top:none;
  border-radius:0 8px 8px 8px; padding:.6rem .9rem; background:#0b6a8f08; font-size:.95em; }
</style>

<details markdown="1" class="concept">
<summary>Why only five training forms?</summary>
<div class="concept-body" markdown="1">

A **custom template** model learns from *position*: it expects each field to appear in roughly
the same place on every document. Because it's learning a fixed layout rather than a general
concept, it needs very little data — five labeled examples is the documented minimum, and for a
consistent form it's often enough.

That's also its limitation. If your documents vary a lot in structure, a template model struggles,
and you'd reach for a custom **neural** model (more tolerant of variation, needs more data) or
back to Content Understanding.

The labeling itself is what those `.labels.json` and `.ocr.json` files next to each image are —
they've been prepared for you here so you can skip straight to training.

[Learn more →](https://learn.microsoft.com/azure/ai-services/document-intelligence/overview)

</div>
</details>

### Prepare training data

A setup script creates a storage account and uploads the labeled sample forms for training.

1. In the VS Code terminal, navigate to the lab's setup folder. It's a sibling of the `Python` folder your terminal opens in:

    ```
    cd ../setup
    ```

1. In VS Code, open the **upload-training-forms.sh** file.

1. Review the commands in the script. It will:
    - Create a storage account in your Azure resource group
    - Upload the labeled training forms to a container named `sampleforms`
    - Print a Shared Access Signature (SAS) URI

    > **Note**: The script uses the labeled training forms that already ship with this repo, so nothing is duplicated. If you moved them, set the `SAMPLE_FORMS_DIR` environment variable to their folder before running the script.

1. Modify the **subscription_id**, **resource_group**, and **location** variable declarations with the appropriate values for the subscription, resource group, and location where you deployed the Document Intelligence resource.

    > **Important**: For your **location** string, use the code format (for example, `eastus` for "East US"). You can find this in the **JSON View** of your resource group in the Azure portal.

    If the **expiry_date** variable is in the past, update it to a future date.

1. Save the file (**Ctrl+S**).
1. To run the setup script, you need a Bash shell, and you must be signed in to your Azure account. Use one of the following:
    - **Azure Cloud Shell**: In the [Azure portal](https://portal.azure.com), open a Cloud Shell (Bash), navigate to the folder, and run `./upload-training-forms.sh`.
    - **VS Code terminal (with WSL or Git Bash on Windows)**: Run `bash upload-training-forms.sh`.

1. When the script completes, review the displayed output and **note the storage account name** — you'll select it when you create the training project.
1. In the Azure portal, refresh your resource group and verify that the storage account was created. Open the storage account and, in **Storage browser**, expand **Blob containers** and select the **sampleforms** container to confirm the files were uploaded.

### Train the model in Document Intelligence Studio

Now use the training forms to build a custom extraction model.

1. Open a new browser tab and navigate to **Document Intelligence Studio** at `https://documentintelligence.ai.azure.com/studio`.
1. Scroll down to the **Custom models** section and select the **Custom extraction model** tile.
1. If prompted, sign in with your Azure credentials.
1. If asked which Azure Document Intelligence resource to use, select the subscription and resource name you used when you created the resource.
1. Under **My Projects**, create a new project with the following configuration:

    - **Enter project details**:
        - **Project name**: *A valid name for your project*
    - **Configure service resource**:
        - **Subscription**: *Your Azure subscription*
        - **Resource group**: *The resource group of your Document Intelligence resource*
        - **Document Intelligence resource**: *Your Document Intelligence resource* (select the *Set as default* option and use the default API version)
    - **Connect training data source**:
        - **Subscription**: *Your Azure subscription*
        - **Resource group**: *Your resource group*
        - **Storage account**: *The storage account created by the setup script* (select the *Set as default* option, select the `sampleforms` blob container, and leave the folder path blank)

1. When your project is created, at the top right of the page select **Train** to train your model. Use the following configuration:
    - **Model ID**: *A valid name for your model — note it down, you'll need it in a moment*
    - **Build Mode**: Template
1. Select **Go to Models**.
1. Training may take some time. Wait until the model status shows **succeeded**.

### Test the custom model with the Python SDK

1. In VS Code, open the **.env** file in **Labfiles/A-extract-information-from-business-content/Python** and set `CUSTOM_MODEL_ID` to the **Model ID** you specified when training your model. Save the file (**Ctrl+S**).

1. In the VS Code terminal, return to the `Python` folder and activate the virtual environment if it isn't already active:

    ```
    cd ../Python
    .\labenv\Scripts\Activate.ps1
    ```

1. Confirm you're now ready:

    ```
    python ../setup/check_env.py --task 4
    ```

    All four keys should show `OK`.

1. In VS Code, open the **test-model.py** file.

1. Review the code, which uses the [azure-ai-documentintelligence](https://learn.microsoft.com/python/api/overview/azure/ai-documentintelligence-readme) SDK. Notice that it:
    - Reads your endpoint, key, and `CUSTOM_MODEL_ID` from `.env`, so it needs no changes to work with *your* model.
    - References a test form hosted in the GitHub repo — a form the model was **not** trained on.
    - Creates a `DocumentIntelligenceClient`, submits the form for analysis with your custom model, and prints each extracted field with its confidence.

1. In the VS Code terminal, run the program:

    ```
    python test-model.py
    ```

1. Review the output. The program should display the field names and values extracted from the test form, such as `Merchant`, `CompanyPhoneNumber`, and the other fields defined in the training labels.

    ![An image of the form used to test the custom model.](../media/Form_1.jpg)

    Compare this to Task 3: there, the field names came from Microsoft's invoice model. Here, they
    came from *your* labels. That's the whole difference between prebuilt and custom.

> ✅ **Checkpoint**: You've trained a custom Document Intelligence extraction model on labeled
> forms and called it from Python. Between this and the previous tasks you've now covered all
> three extraction strategies: generative (Content Understanding), prebuilt, and trained.

When you're finished, enter `deactivate` to exit the virtual environment.

---

**Next:** You've completed the optional tasks. Head back to the [lab overview](A-extract-information-from-business-content.md) for a summary and clean-up steps — or carry on to [Make extracted information searchable](B-make-extracted-information-searchable.md), where you make everything you've extracted findable and answerable.
