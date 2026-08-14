---
lab:
    title: 'Task 2 – Build an analyzer with the Python SDK'
    description: 'Use the Azure Content Understanding Python SDK to create an analyzer from a JSON schema and call it from a client application to extract contact details from scanned cards.'
    level: 300
    concepts: 'Content Understanding SDK, analyzer schemas, long-running operations'
    islab: true
    status: 'draft'
---

# Task 2 — Build an analyzer with the Python SDK

*Part of the **Extract information from business content** lab. New here? Start with [Getting started](A0-getting-started.md).*

> **Set up (start here):** This task needs a Microsoft Foundry resource with Content Understanding
> connected, and the starter code. If you haven't already, complete
> [Getting started](A0-getting-started.md) to create your project, connect Content Understanding
> Studio with auto-deployment enabled, clone the code, and set `FOUNDRY_ENDPOINT`, `FOUNDRY_KEY`,
> and `ANALYZER_NAME` in `Python/.env`. Then, from the
> `Python` folder, verify you're ready:

```
python ../setup/check_env.py --task 2
```

> **Continuing from a previous task?** If you just finished Task 1, your Foundry resource and
> Content Understanding connection are already set up — you only need the starter code and
> `.env` steps from [Getting started](A0-getting-started.md). You do **not** need any analyzer
> you built in the portal: this task creates its own analyzer from code.

---

Building analyzers in a portal is great for designing them. It's no good for running them a
thousand times a day. Fabrikam Logistics reps come back from trade shows with a stack of scanned
contact cards, and somebody has to get those into the CRM. In this task you'll create a Content
Understanding analyzer **from code** and then call it **from code**, so the whole thing can run
unattended.

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
<summary>Why does everything return a "poller"?</summary>
<div class="concept-body" markdown="1">

Creating an analyzer and analyzing a file are both **long-running operations** — they take longer
than a single HTTP request should wait for. So the service accepts the request, returns
immediately, and gives you a handle to check on it.

In the Python SDK that handle is an `LROPoller`. You call `.result()` on it, and the SDK does the
polling loop for you and hands back the finished result. That's why you'll see this shape twice
in this task:

```python
poller = client.begin_something(...)
result = poller.result()
```

You never write a retry loop yourself.

</div>
</details>

Open the `Python` folder and activate the virtual environment from
[Getting started](A0-getting-started.md) (`.\labenv\Scripts\Activate.ps1`), then continue below.

### Review the analyzer schema

1. In the VS Code Explorer pane, open the **contact-card.json** file and review its contents.

    This is the same kind of schema you built by clicking in Task 1 — just written directly as
    JSON. It specifies the fields to extract (`Company`, `Name`, `Title`, `Email`, `Phone`), the
    base analyzer to build on, and the models to use.

    > **Note**: The `models` block pins `gpt-5.2` for completion and `text-embedding-3-large` for embedding. If your Foundry resource doesn't have those deployments, change them to models you do have. You can see your deployments in the Foundry portal under **Build > Deployments**.

### Create the analyzer

1. Open the **create-analyzer.py** file in VS Code.

1. Review the code, which:
    - Imports the `ContentUnderstandingClient` and `AzureKeyCredential` from the [Azure Content Understanding SDK](https://learn.microsoft.com/python/api/overview/azure/ai-contentunderstanding-readme).
    - Loads the analyzer schema from the **contact-card.json** file.
    - Retrieves the endpoint, key, and analyzer name from the environment configuration file.
    - Calls a function named **create_analyzer**, which is currently not implemented.

1. In the **create_analyzer** function, find the comment **TODO: Create a Content Understanding analyzer** and replace the comment block and the `pass` statement with the following code (being careful to maintain the correct indentation):

    ```python
    # Create a Content Understanding analyzer
    print(f"Creating {analyzer}")

    # Create the Content Understanding client
    client = ContentUnderstandingClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Parse the schema JSON into a ContentAnalyzer object
    analyzer_definition = json.loads(schema)

    # Create the analyzer using the SDK (long-running operation)
    poller = client.begin_create_analyzer(
        analyzer_id=analyzer,
        resource=analyzer_definition,
        allow_replace=True
    )

    # Wait for the operation to complete
    result = poller.result()
    print(f"Analyzer '{analyzer}' created successfully.")
    print(f"Status: {result['status'] if isinstance(result, dict) else 'Succeeded'}")
    ```

1. Review the code you added, which:
    - Creates a `ContentUnderstandingClient` instance with the endpoint and API key.
    - Parses the analyzer schema JSON.
    - Uses `begin_create_analyzer` to start the long-running operation that creates the analyzer.
    - Calls `.result()` to wait for the operation to complete.

    > **Note**: `allow_replace=True` means re-running the script overwrites an existing analyzer with the same name instead of failing — handy while you're iterating on a schema.

1. Save the file (**Ctrl+S**).
1. In the VS Code terminal (with the virtual environment activated and the **Python** folder as your working directory), run the code:

    ```
    python create-analyzer.py
    ```

1. Review the output, which should indicate that the analyzer has been created.

### Analyze content with the analyzer

Now consume the analyzer you just created from a client application.

1. In VS Code, open the **read-card.py** file.

1. Review the code, which:
    - Imports the `ContentUnderstandingClient` and `AzureKeyCredential` from the SDK.
    - Identifies the image file to be analyzed, defaulting to **biz-card-1.png**.
    - Resolves a bare file name against the shared `Instructions/Exercises/media` folder, so the sample cards that ship with the repo are used in place.
    - Retrieves the endpoint, key, and analyzer name from the environment configuration file.
    - Calls a function named **analyze_card**, which is currently not implemented.

1. In the **analyze_card** function, find the comment **TODO: Use Content Understanding to analyze the image** and replace the comment block and the `pass` statement with the following code (being careful to maintain the correct indentation):

    ```python
    # Use Content Understanding to analyze the image
    print(f"Analyzing {image_file}")

    # Create the Content Understanding client
    client = ContentUnderstandingClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Read the image data
    with open(image_file, "rb") as file:
        image_data = file.read()

    # Submit the image for analysis
    print("Submitting request...")
    poller = client.begin_analyze_binary(
        analyzer_id=analyzer,
        binary_input=image_data
    )

    # Wait for the analysis to complete
    result = poller.result()
    print("Analysis succeeded:\n")

    # Save JSON results to a file
    output_file = "results.json"
    with open(output_file, "w") as json_file:
        json.dump(dict(result), json_file, indent=4, default=str)
        print(f"Response saved in {output_file}\n")

    # Iterate through the contents and extract fields
    for content in result.contents:
        if hasattr(content, 'fields') and content.fields:
            for field_name, field_data in content.fields.items():
                value = field_data.value if hasattr(field_data, 'value') else None
                print(f"{field_name}: {value}")
    ```

1. Review the code you added, which:
    - Creates a `ContentUnderstandingClient` instance.
    - Reads the content of the image file as bytes.
    - Calls `begin_analyze_binary` to submit the image to the analyzer.
    - Calls `.result()` to wait for and retrieve the analysis results.
    - Saves the JSON response and parses the extracted fields.

1. Save the file (**Ctrl+S**).
1. In the VS Code terminal, run the code:

    ```
    python read-card.py biz-card-1.png
    ```

1. Review the output, which should show the values for the fields on the following card:

    ![A scanned contact card showing a name, job title, company, email address, and phone number.](../media/biz-card-1.png)

1. Run the program again with a different card:

    ```
    python read-card.py biz-card-2.png
    ```

1. Review the results, which should reflect the values on this card:

    ![A second scanned contact card in a different layout, showing a name, job title, company, email address, and phone number.](../media/biz-card-2.png)

    Notice that the two cards have completely different layouts, and the same analyzer handled
    both. You never told it where on the card to look — only what you wanted.

1. To view the full JSON response that was returned, open the **results.json** file in VS Code, or run the following command in the terminal:

    ```
    type results.json
    ```

> ✅ **Checkpoint**: You've created a Content Understanding analyzer from a JSON schema and called
> it from a client application. Same service as Task 1, no portal involved — which is what makes
> it automatable.

When you're finished, enter `deactivate` to exit the virtual environment.

---

**Next (optional):** [Task 3 — Extract invoice data with a prebuilt model](A3-extract-invoice-data-with-a-prebuilt-model.md) · [Task 4 — Train a custom extraction model](A4-train-a-custom-extraction-model.md)
