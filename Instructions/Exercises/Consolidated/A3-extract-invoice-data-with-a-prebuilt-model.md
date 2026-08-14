---
lab:
    title: 'Task 3 – Extract invoice data with a prebuilt model'
    description: 'Use Azure Document Intelligence prebuilt models to extract text and structured invoice fields with no schema and no training: try Read in the Studio, then call prebuilt-invoice from Python.'
    level: 300
    concepts: 'Document Intelligence, prebuilt models, OCR, confidence scores'
    islab: true
    status: 'draft'
---

# Task 3 — Extract invoice data with a prebuilt model

*Part of the **Extract information from business content** lab. New here? Start with [Getting started](A0-getting-started.md).*

> **Set up (start here):** This task needs a **Document Intelligence** resource and the starter
> code — it does **not** need a Foundry resource or anything you built in Tasks 1 or 2. If you
> haven't already, complete [Getting started](A0-getting-started.md) to create your Document
> Intelligence resource, clone the code, and set `DOC_INTELLIGENCE_ENDPOINT` and
> `DOC_INTELLIGENCE_KEY` in `Python/.env`. Then, from the
> `Python` folder, verify you're ready:

```
python ../setup/check_env.py --task 3
```

> **Continuing from a previous task?** If you just finished an earlier task in the same `Python`
> folder, your virtual environment and `.env` are already in place — you only need to add the
> two `DOC_INTELLIGENCE_*` values, which come from a **different** resource than the
> `FOUNDRY_*` ones. Create the Document Intelligence resource per
> [Getting started](A0-getting-started.md) if you skipped that section.

---

In Tasks 1 and 2, you told Content Understanding what fields you wanted. Now try the opposite
approach. Fabrikam Logistics processes thousands of invoices, and "invoice" is a document type
the world already agrees on — so Azure Document Intelligence ships a model that already knows
what a vendor name and an invoice total are. No schema. No training. Just call it.

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
<summary>What is a confidence score, and what should I do with it?</summary>
<div class="concept-body" markdown="1">

Every field a Document Intelligence model returns comes with a **confidence** value between 0
and 1 — how sure the model is that it read that field correctly.

This is the practical difference between a demo and a production pipeline. Real invoice
processing sets a threshold: above it, post the value automatically; below it, route the document
to a human to check. You get that for free with Document Intelligence, which is a big part of why
it's used for high-volume, money-touching documents.

Watch the confidence values in the output of this task — they aren't all the same.

[Learn more →](https://learn.microsoft.com/azure/ai-services/document-intelligence/overview)

</div>
</details>

## Use the Read model in the Studio

First, see what pure OCR gives you — including a detail that matters for a freight forwarder
handling paperwork in several languages.

1. In a web browser, navigate to **Document Intelligence Studio** at `https://documentintelligence.ai.azure.com/studio` and sign in with your Azure credentials.
1. On the Studio home page, under **Document analysis**, select the **Read** tile.
1. In the list of documents on the left, select **read-german.pdf**.
1. On the top toolbar, select **Analyze options**, then enable the **Language** check-box (under **Optional detection**) in the **Analyze options** pane and select **Save**.
1. At the top-left, select **Run Analysis**.
1. When the analysis is complete, the text extracted from the image is shown on the right in the **Content** tab. Review this text and compare it to the text in the original image for accuracy.
1. Select the **Result** tab. This tab displays the extracted JSON.
1. Scroll to the bottom of the JSON in the **Result** tab. Notice that the read model has detected the language of each span, indicated by `locale`. Most spans are in German (language code `de`), but you can find other language codes in the spans (for example, English — language code `en` — in one of the first spans).

    Read gives you *text*. What it doesn't give you is meaning: nothing here says "this number is
    the total". That's the job of the prebuilt invoice model, next.

## Analyze an invoice with a prebuilt model using the Python SDK

1. In the [Azure portal](https://portal.azure.com), find the Document Intelligence resource you created. Under **Resource Management**, select **Keys and Endpoint**, and confirm the **Endpoint** and **Key** match what you put in your `.env`.

1. Open the `Python` folder and activate the virtual environment from [Getting started](A0-getting-started.md):

    ```
    .\labenv\Scripts\Activate.ps1
    ```

This is the sample invoice that your code will analyze:

![Screenshot showing a sample invoice document.](../media/sample-invoice.png)

1. In VS Code, open the **document-analysis.py** file.

1. Review the code. Notice that it already sets `fileModelId = "prebuilt-invoice"` — that string is the entire "schema" for this task.

1. In the code file, find the comment **TODO: Add references** and replace it with the following code:

    ```python
    # Add references
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
    ```

1. Find the comment **TODO: Create the client** and replace it with the following code (being careful to maintain the correct indentation):

    ```python
    # Create the client
    document_analysis_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    ```

1. Find the comment **TODO: Analyze the invoice** and replace it with the following code:

    ```python
    # Analyze the invoice
    poller = document_analysis_client.begin_analyze_document(
        fileModelId,
        AnalyzeDocumentRequest(url_source=fileUri),
        locale=fileLocale
    )
    ```

1. Find the comment **TODO: Display invoice information to the user** and replace it with the following code:

    ```python
    # Display invoice information to the user
    result = poller.result()

    for document in result.documents:

        vendor_name = document.fields.get("VendorName")
        if vendor_name:
            print(f"\nVendor Name: {vendor_name.get('valueString')}, with confidence {vendor_name.get('confidence')}.")

        customer_name = document.fields.get("CustomerName")
        if customer_name:
            print(f"Customer Name: {customer_name.get('valueString')}, with confidence {customer_name.get('confidence')}.")

        invoice_total = document.fields.get("InvoiceTotal")
        if invoice_total:
            amount = invoice_total.get("valueCurrency", {})
            print(f"Invoice Total: {amount.get('currencySymbol', '$')}{amount.get('amount')}, with confidence {invoice_total.get('confidence')}.")
    ```

1. Review the code you added, which:
    - Creates a `DocumentIntelligenceClient` with your endpoint and credentials.
    - Uses the `prebuilt-invoice` model to analyze the document from a URL.
    - Iterates through the results and prints the vendor name, customer name, and invoice total — each with its confidence score.

1. Save the file (**Ctrl+S**).
1. In the VS Code terminal, run the application:

    ```
    python document-analysis.py
    ```

1. Review the output. The program should display the vendor name, customer name, and invoice total with confidence levels. Compare the values with the sample invoice shown above.

    Note how much you *didn't* have to do: no schema, no field descriptions, no training data. For
    a document type that's standard across the industry, the prebuilt model is simply the fastest
    correct answer.

> ✅ **Checkpoint**: You've extracted structured invoice fields with a prebuilt Document
> Intelligence model and seen the confidence score attached to each one. Prebuilt models cover
> common document types — but Fabrikam Logistics also has forms that no prebuilt model has ever
> seen. That's Task 4.

When you're finished, enter `deactivate` to exit the virtual environment.

---

**Next (optional):** [Task 4 — Train a custom extraction model](A4-train-a-custom-extraction-model.md)
