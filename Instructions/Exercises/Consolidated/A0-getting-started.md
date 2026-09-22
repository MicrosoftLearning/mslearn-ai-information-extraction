---
lab:
    title: 'Getting started: set up your environment'
    description: 'Shared setup for the Extract information from business content lab: create a Microsoft Foundry resource and project, connect Content Understanding, get the sample content and starter code, and configure your environment. Complete this once before any task.'
    level: 300
    concepts: 'environment setup, Microsoft Foundry resource, Content Understanding'
    status: 'draft'
---

# Getting started

This page sets up everything the **Extract information from business content** lab needs.
**Every task begins here** — complete this page first. Each task is written so you can then do
it on its own; if you're working through the whole lab in one sitting, you only need to do this
setup once.

**Your scenario:** you work at **Fabrikam Logistics**, a freight-forwarding company. Across the
lab you'll build the extraction layer that turns the company's incoming documents, images,
audio, and video into structured fields.

> **Note**: Some of the technologies used in this lab are in preview or in active development.
> You may experience some unexpected behavior, warnings, or errors.

## Prerequisites

Before starting, ensure you have:

- An [Azure subscription](https://azure.microsoft.com/free/) with sufficient permissions and quota to provision Azure AI resources
- [Visual Studio Code](https://code.visualstudio.com/) installed on your local machine
- [Python 3.11](https://www.python.org/downloads/) or later installed\*
- [Git](https://git-scm.com/downloads) installed on your local machine
- Basic familiarity with Python (needed for Tasks 2, 3, and 4 only)

> \* The Azure SDK for Python supports Python 3.9 or later. This lab was tested with Python 3.13.

## Create a Microsoft Foundry resource and project

Tasks 1 and 2 use **Azure Content Understanding**, which runs on a Microsoft Foundry resource.

1. In a web browser, open the [Microsoft Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in.

    > **Important**: For this lab, you're using the **New** Foundry experience. Make sure the **New Foundry** toggle is on.

1. If you aren't prompted to create a project automatically, select the project name in the upper-left corner, and then select **Create new project**.

1. Give your project a name (for example, `fabrikam-extraction`) and expand **Advanced options** to specify the following settings:
    - **Foundry resource**: *A valid name for your Foundry resource*
    - **Region**: Choose one of the following supported regions:\*
        - Australia East
        - East US
        - East US 2
        - Japan East
        - North Europe
        - South Central US
        - Southeast Asia
        - Sweden Central
        - UK South
        - West Europe
        - West US
        - West US 3
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *Create or select a resource group*

    > \*Azure Content Understanding is available in selected regions. See the [region support documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support) for the latest availability.

1. Select **Create** and wait for your project to be created. This creates a project and its parent Foundry resource.

1. Once created, select the project name at the top of the page, and select **Project details**. On that page, follow the link to the parent resource. **Leave this browser tab open** — you'll copy the endpoint and key from it for Task 2.

## Connect Content Understanding to your Foundry resource

Content Understanding analyzers use models that are deployed in your Foundry resource. Connecting
the resource in Content Understanding Studio deploys them for you.

1. In a new tab, navigate to [Content Understanding Studio](https://contentunderstanding.ai.azure.com/home) at `https://contentunderstanding.ai.azure.com/home` and sign in with your credentials.
1. Select the settings gear icon on the top navigation bar, and select **+ Add resource**.
1. Select your subscription and the resource group where you created your Foundry resource, then select your Foundry resource name from the dropdown. This is the parent resource of the project you created above.
1. Make sure the **Enable auto-deployment** box is checked, then select **Next** and **Save**.

    > **Tip**: Auto-deployment deploys the chat and embedding models that custom analyzers need — currently a `gpt-5.2`-family completion model and `text-embedding-3-large`. Without it, building an analyzer fails with a missing-model error.

1. Wait while the required models deploy.

> **Note**: Content Understanding has two authoring experiences. The **Foundry portal**
> (`https://ai.azure.com`) is the primary one for agentic workflows. **Content Understanding
> Studio** (`https://contentunderstanding.ai.azure.com`) is the complementary experience
> optimized for building and labeling custom analyzers — that's what this lab uses.

## Create a Document Intelligence resource (Tasks 3 and 4 only)

Skip this section if you're only doing Tasks 1 and 2.

1. In a web browser, navigate to **Document Intelligence Studio** at `https://documentintelligence.ai.azure.com/studio` and sign in with your Azure credentials.
1. In the Studio, select the **Settings** icon (⚙) in the upper-right corner, and then select the **Resource** tab.
1. Select **Create a new resource** and configure it with the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *The same resource group you used above*
    - **Name**: *A valid name for your Document Intelligence resource*
    - **Region**: *Any available region*
    - **Pricing tier**: Free F0 (*if you don't have a Free tier available, select Standard S0*)
1. Select **Create** and wait for the resource to be deployed. The Studio connects to the new resource automatically.

## Download the sample content

Task 1 analyzes a set of Fabrikam Logistics sample files: an invoice, a slide image, a voicemail
recording, and a recorded operations call.

1. In a new browser tab, download [content.zip](https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/content/content.zip) from `https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/content/content.zip` and save it in a local folder.
1. Extract the downloaded *content.zip* file and view the files it contains. You'll upload these into Content Understanding in Task 1.

## Get the starter code

Tasks 2, 3, and 4 write and run Python. Task 1 doesn't need any of this, so you can skip ahead
if you're only doing the Core task.

1. In VS Code, open the Command Palette (**Ctrl+Shift+P**), run **Git: Clone**, and enter:

    ```
    https://github.com/microsoftlearning/mslearn-ai-information-extraction
    ```

1. Open the cloned repo, then **File > Open Folder** and select `mslearn-ai-information-extraction/Labfiles/A-extract-information-from-business-content/Python`. This single folder holds the starter code for **every** code task in this lab — you use one virtual environment and one `.env` throughout.

1. Right-click **requirements.txt** and choose **Open in Integrated Terminal**. Then create a virtual environment and install packages:

    ```
    python -m venv labenv
    .\labenv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

    > **Note**: This installs the [azure-ai-contentunderstanding](https://pypi.org/project/azure-ai-contentunderstanding/) and [azure-ai-documentintelligence](https://learn.microsoft.com/python/api/overview/azure/ai-documentintelligence-readme) Python SDK packages and their dependencies.

1. Copy **.env.example** to a new file named **.env** in the same folder, then fill in the values for the tasks you plan to do:

    | Key | Where to get it | Needed by |
    | --- | --- | --- |
    | `FOUNDRY_ENDPOINT` | Foundry resource > **Overview**, or **Resource Management > Keys and Endpoint** | Task 2 |
    | `FOUNDRY_KEY` | Foundry resource > **Resource Management > Keys and Endpoint** | Task 2 |
    | `ANALYZER_NAME` | Already filled in as `fabrikam-contact-analyzer` | Task 2 |
    | `DOC_INTELLIGENCE_ENDPOINT` | Document Intelligence resource > **Keys and Endpoint** | Tasks 3, 4 |
    | `DOC_INTELLIGENCE_KEY` | Document Intelligence resource > **Keys and Endpoint** | Tasks 3, 4 |
    | `CUSTOM_MODEL_ID` | The Model ID you choose when you train in Task 4 | Task 4 |

1. Save the file (**Ctrl+S**).

    > **Note**: These tasks authenticate with resource keys because that's the quickest path in a lab. For production, Microsoft recommends [Microsoft Entra ID authentication](https://learn.microsoft.com/azure/ai-services/authentication) with `DefaultAzureCredential` instead of keys.

## Check you're ready for a task

Each task needs specific values in your `.env`. Before starting a task, run the preflight check
from the `Python` folder you opened above — it reads your `.env` and tells you what (if anything)
is missing:

```
python ../setup/check_env.py --task 2
```

Swap `2` for the task number you're about to start. That's it — head to any task:

| Task | Page |
| --- | --- |
| Task 1 – Extract fields from multimodal content | [A1](A1-extract-fields-from-multimodal-content.md) |
| Task 2 – Build an analyzer with the Python SDK | [A2](A2-build-an-analyzer-with-the-python-sdk.md) |
| Task 3 – Extract invoice data with a prebuilt model | [A3](A3-extract-invoice-data-with-a-prebuilt-model.md) |
| Task 4 – Train a custom extraction model | [A4](A4-train-a-custom-extraction-model.md) |
