---
lab:
    title: 'Task 1 – Extract fields from multimodal content'
    description: 'Use Azure Content Understanding to define custom schemas and build analyzers that extract named fields from an invoice, a slide image, a voicemail recording, and a recorded call.'
    level: 200
    concepts: 'Content Understanding, prebuilt analyzers, custom schemas, multimodal extraction'
    islab: true
    status: 'draft'
---

# Task 1 — Extract fields from multimodal content

*Part of the **Extract information from business content** lab. New here? Start with [Getting started](A0-getting-started.md).*

> **Set up (start here):** This task needs a Microsoft Foundry resource with Content Understanding
> connected, plus the sample content files. If you haven't already, complete
> [Getting started](A0-getting-started.md) to create your Foundry project, connect Content
> Understanding Studio with auto-deployment enabled, and download and extract **content.zip**.
> This task is done entirely in the browser — no code, no `.env`. If you want to confirm that,
> run the following from the `Python` folder:

```
python ../setup/check_env.py --task 1
```

---

Fabrikam Logistics receives four very different kinds of content, and all four hide information
somebody currently retypes by hand. In this task you'll build a Content Understanding analyzer
for each one: a **supplier invoice** (document), a **quarterly review slide** (image), a
**customer voicemail** (audio), and a **recorded operations call** (video).

The pattern is identical every time, which is the point: **describe the fields you want, test,
build an analyzer, then run it against content it has never seen.**

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
<summary>What's the difference between a schema and an analyzer?</summary>
<div class="concept-body" markdown="1">

A **schema** is the list of fields you want, each with a name, a description, a value type, and a
method. It's the *what*.

An **analyzer** is a schema that's been built into a reusable, callable service asset. Once built,
you can point it at new content — in the portal, or from code, as you'll do in Task 2 — and get
those fields back. It's the *how you use it again*.

The **method** on each field matters:

- **Extract** pulls a value that's literally present in the content (an invoice total).
- **Generate** produces a value the model infers from the content (a summary, a count of charts).

</div>
</details>

> **Note**: If you're only interested in one modality, you can do just that section. Each of the
> four sections below is self-contained. For the full picture, do all four.

## Try prebuilt analyzers first

Before building anything custom, see what you get for free. Content Understanding includes
prebuilt **Read** and **Layout** analyzers that extract text and structure from documents with no
configuration at all.

1. In the [Microsoft Foundry portal](https://ai.azure.com), make sure the **New Foundry** toggle is on.
1. Select **Build** in the upper-right menu, then select **Deployments** in the left pane.
1. Select the **AI Services** tab to view the prebuilt models provided by Foundry Tools.
1. Find and select **Azure Content Understanding - Layout**.

    This opens the Layout analyzer playground, where you can test the layout model on sample data
    or your own files.

1. In the playground, use the option to upload your own data and upload the **invoice-1234.pdf** file from the folder where you extracted the content files. This is the supplier invoice:

    ![Image of an invoice number 1234.](../media/invoice-1234.png)

1. Run the analyzer and wait for analysis to complete.
1. Review the results. You can view the extracted content either as formatted output or as raw JSON. Notice that Layout extracts text, tables, and structural elements such as paragraphs and sections.

    > **Note**: The prebuilt **Read** and **Layout** analyzers extract content from documents without using a generative AI model. **Read** extracts text elements (words, paragraphs, formulas, and barcodes); **Layout** additionally extracts tables, figures, document structure, hyperlinks, and annotations. They're great for general-purpose extraction — but neither one gives you *specific* fields like an invoice total or a vendor name. That's what you'll build next.

1. Optionally, go back to the **AI Services** tab and try **Azure Content Understanding - Read** with the same file to compare. Notice that Read extracts text without layout analysis.

## Set up Content Understanding Studio for custom analyzers

To extract specific fields, you build **custom analyzers** in Content Understanding Studio.

1. In a new browser tab, open [Content Understanding Studio](https://contentunderstanding.ai.azure.com) at `https://contentunderstanding.ai.azure.com`.
1. If prompted, sign in with the same Azure credentials you used for the Foundry portal.
1. If you didn't already connect your resource in [Getting started](A0-getting-started.md), go to the **Settings** page, select **+ Add resource**, select your Foundry resource, and select **Next** > **Save**.

    > **Tip**: Make sure the **Enable autodeployment for required models if no defaults are available** checkbox is selected, so your resource gets the models custom analyzers depend on.

1. Once your resource is connected, select **Content Understanding** in the top navigation to go to the home page.

### Create a storage account

Content Understanding Studio stores the data you use to build custom analyzers in Azure Blob
Storage. Create one in the same resource group as your Foundry resource.

1. In a new browser tab, open the [Azure portal](https://portal.azure.com) at `https://portal.azure.com` and sign in with your Azure credentials.
1. Select **+ Create a resource**, search for `Storage account`, and create a new **Storage account** resource with the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *The same resource group as your Foundry resource*
    - **Storage account name**: *Enter a globally unique name*
    - **Region**: *The same region as your Foundry resource*
    - **Preferred storage type**: Azure Blob Storage or Azure Data Lake Storage Gen 2
    - **Performance**: Standard
    - **Redundancy**: Locally-redundant storage (LRS)
1. Select **Review + create**, and then **Create**. Wait for deployment to complete.

## Extract fields from an invoice document

Fabrikam Logistics receives supplier invoices constantly, in layouts that vary by supplier. Build
an analyzer that pulls the same fields out of all of them.

### Define a schema for invoice analysis

1. In Content Understanding Studio, select the **Get started** button in the custom projects section, and select **Create**.
1. Select **Extract content and fields with a custom schema**, then create a project with the following settings:
    - **Project name**: `Invoice analysis`
    - **Description**: `Extract data from a supplier invoice`
    - **Advanced settings**
        - **Connected resource**: *Confirm your Foundry resource is selected*
        - **Connect storage account**: *Select the storage account you just created*
        - **Blob container**: *Create a new container named* `content-understanding`
1. Wait for the project to be created.

    > **Tip**: If an error accessing storage occurs, wait a minute and try again. Permissions for a new resource can take a few minutes to propagate.

1. Upload the **invoice-1234.pdf** file from the folder where you extracted the content files.

    Content Understanding classifies your data and recommends analyzer templates based on the
    uploaded content.

1. In the **Choose a template** window, select the **Invoice** template and select **Save**.

    The *Invoice* template includes common invoice fields. Use the schema editor to delete
    suggested fields you don't need, and add custom fields you do.

1. In the list of suggested fields, select **BillingAddress**. Fabrikam Logistics doesn't need it for this invoice format, so use the **Delete field** (**&#128465;**) icon at the end of the selected field row to delete it.
1. In the top bar of the schema tab, select **Suggest**. This looks at the sample invoice and suggests which fields should be part of your schema. Expand the **Items** field to see the suggested subfields. Adding those fields replaces your existing schema, so be careful in your own projects if you've already edited one. Select **Save**.
1. Use the **+ Add new field** button to add the following field, selecting **Save** (**&#10003;**) for it:

    | Field name | Field description | Value type | Method |
    |--|--|--|--|
    | `TotalQuantity` | `Total number of items on the invoice` | String | Auto |

1. Verify that your completed schema looks like this, and select **Save**.

    ![Screenshot of the invoice analyzer schema in Content Understanding Studio showing fields such as VendorName, InvoiceDate, SubTotal, Items, and TotalQuantity.](../media/invoice-schema.png)

1. Select the **Test** tab, then select **Run analysis** to test your schema. Wait for analysis to complete.

1. Review the analysis results, which should look similar to this:

    ![Screenshot of invoice analysis test results in Content Understanding Studio showing extracted field values from the sample invoice.](../media/invoice-analysis.png)

1. View the details of the fields that were identified in the **Fields** pane.

### Build and test an analyzer for invoices

Now that the schema works, build it into a reusable analyzer.

1. Select the **Build analyzer** button at the top, and build a new analyzer with the following properties (typed exactly as shown here):
    - **Name**: `invoiceanalyzer`
    - **Description**: `Invoice analyzer`
1. When the analyzer has been built, select **Jump to analyzer list** to view all built analyzers, then select the **invoiceanalyzer** link. The fields defined in the analyzer's schema are displayed.
1. On the **invoiceanalyzer** page, select the **Test** tab.
1. Upload **invoice-1235.pdf** from the folder where you extracted the content files, and run the analysis.

    This is a *different* invoice the analyzer has never seen:

    ![Image of an invoice number 1235.](../media/invoice-1235.png)

1. Review the **Fields** pane, and verify that the analyzer extracted the correct fields from the test invoice.
1. Review the **Results** pane to see the JSON response that the analyzer would return to a client application.
1. Close the **invoiceanalyzer** page to return to the analyzer list.

## Extract information from a slide image

Fabrikam Logistics' quarterly review decks contain charts that nobody has time to transcribe.

### Define a schema for image analysis

1. On the **Project list** tab, select **Create**, select **Extract content and fields with a custom schema**, then create a project with the following settings:
    - **Project name**: `Slide analysis`
    - **Description**: `Extract data from an image of a slide`
    - **Advanced settings**: *Verify the settings are the same as the last project*
1. Wait for the project to be created.

1. Upload the **slide-1.jpg** file from the folder where you extracted the content files. Then select the **Image analysis** template and select **Save**.

    The *Image analysis* template doesn't include any predefined fields — you define everything
    you want to extract.

1. Use the **+ Add new field** button to add the following fields, selecting **Save changes** (**&#10003;**) for each new field:

    | Field name | Field description | Value type | Method |
    |--|--|--|--|
    | `Title` | `Slide title` | String | Generate |
    | `Summary` | `Summary of the slide` | String | Generate |
    | `Charts` | `Number of charts on the slide` | Integer | Generate |

1. Use the **+ Add new field** button to add a new field named `QuarterlyRevenue` with the description `Revenue per quarter` and the value type **List of objects**. Then select the table icon next to the value type dropdown. On the page for the table subfields that opens, add the following subfields:

    | Field name | Field description | Value type | Method |
    |--|--|--|--|
    | `Quarter` | `Which quarter?` | String | Generate |
    | `Revenue` | `Revenue for the quarter` | Number | Generate |

1. Select **Back** to return to the top level of your schema, and use the **+ Add new field** button to add a new field named `ProductCategories` with the description `Product categories` and the value type **List of objects**. Select the table icon next to the value type to open the subfields page, and add the following subfields:

    | Field name | Field description | Value type | Method |
    |--|--|--|--|
    | `ProductCategory` | `Product category name` | String | Generate |
    | `RevenuePercentage` | `Percentage of revenue` | Number | Generate |

1. Select **Back** to return to the top level of your schema, and verify that it looks like this. Then select **Save**.

    ![Screenshot of the image analyzer schema in Content Understanding Studio showing fields for Title, Summary, Charts, QuarterlyRevenue, and ProductCategories.](../media/slide-schema.png)

1. Select the **Test** tab, then **Run analysis** and wait for analysis to complete.
1. Review the analysis results, which should look similar to this:

    ![Screenshot of image analysis test results in Content Understanding Studio showing extracted fields from the slide including revenue data and product categories.](../media/slide-analysis.png)

1. View the details of the fields that were identified in the **Fields** pane, expanding the **QuarterlyRevenue** and **ProductCategories** fields to see the subfield values.

### Build and test a slide analyzer

1. Select the **Build analyzer** button at the top, and build a new analyzer with the following properties (typed exactly as shown here):
    - **Name**: `slideanalyzer`
    - **Description**: `Slide image analyzer`
1. When the analyzer has been built, select **Jump to analyzer list**, then select the **slideanalyzer** link. The fields defined in the analyzer's schema are displayed.
1. On the **slideanalyzer** page, select the **Test** tab.
1. Use the **+ Upload test files** button to upload **slide-2.jpg** from the folder where you extracted the content files, and run the analysis.

1. Review the **Fields** pane, and verify that the analyzer extracted the correct fields from the slide image.

    > **Note**: Slide 2 doesn't include a breakdown by product category, so the product category revenue data isn't found. An analyzer returning nothing for a field that genuinely isn't there is correct behavior — worth remembering when you consume these results in code.

1. Review the **Results** pane to see the JSON response that the analyzer would return to a client application.
1. Close the **slideanalyzer** page.

## Extract information from a voicemail recording

Customers leave voicemails for the Fabrikam Logistics service desk. Each one contains a callback
number and a request that somebody has to action.

### Define a schema for audio analysis

1. On the **Project list** tab, select **Create**, select **Extract content and fields with a custom schema**, then create a project with the following settings:
    - **Project name**: `Voicemail analysis`
    - **Description**: `Extract data from a voicemail recording`
    - **Advanced settings**: *Verify the settings are the same as the last project*
1. Wait for the project to be created.

1. Upload the **call-1.mp3** file from the folder where you extracted the content files. Then select the **Audio analysis** template and select **Save**.
1. In the **Content** pane on the right, select **Get transcription preview** to see a transcription of the recorded message.

    The *Audio analysis* template doesn't include any predefined fields — you define what you want
    to extract.

1. Use the **+ Add new field** button to add the following fields, selecting **Save** (**&#10003;**) for each new field:

    | Field name | Field description | Value type | Method |
    |--|--|--|--|
    | `Caller` | `Person who left the message` | String | Generate |
    | `Summary` | `Summary of the message` | String | Generate |
    | `Actions` | `Requested actions` | String | Generate |
    | `CallbackNumber` | `Telephone number to return the call` | String | Generate |
    | `AlternativeContacts` | `Alternative contact details` | List of Strings | Generate |

1. Select **Run analysis** and wait for analysis to complete.

    Audio analysis can take some time. While you're waiting, you can play the audio file below:

    <video controls src="../media/call-1.mp4" title="Call 1" width="300">
        <track src="../media/call-1.vtt" kind="captions" srclang="en" label="English">
    </video>

    **Note**: This audio was generated using AI.

1. Review the analysis results and view the details of the fields that were identified in the **Fields** pane, expanding the **AlternativeContacts** field to see the listed values.

### Build and test a voicemail analyzer

1. Select the **Build analyzer** button at the top, and build a new analyzer with the following properties (typed exactly as shown here):
    - **Name**: `voicemailanalyzer`
    - **Description**: `Voicemail audio analyzer`
1. When the analyzer has been built, select **Jump to analyzer list**, then select the **voicemailanalyzer** link. The fields defined in the analyzer's schema are displayed.
1. On the **voicemailanalyzer** page, select the **Test** tab.
1. Use the **+ Upload test files** button to upload **call-2.mp3** from the folder where you extracted the content files, and run the analysis.

    Audio analysis can take some time. While you're waiting, you can play the audio file below:

    <video controls src="../media/call-2.mp4" title="Call 2" width="300">
        <track src="../media/call-2.vtt" kind="captions" srclang="en" label="English">
    </video>

    **Note**: This audio was generated using AI.

1. Review the **Fields** pane, and verify that the analyzer extracted the correct fields from the voice message.
1. Review the **Results** pane to see the JSON response that the analyzer would return to a client application.
1. Close the **voicemailanalyzer** page.

## Extract information from a recorded call

Finally, the hardest modality: a recorded operations call, where the useful information is spread
across what people said *and* what they showed on screen.

### Define a schema for video analysis

1. In Content Understanding Studio, select **Create project** on the home page (or use the navigation to return to the home page first).
1. Select **Extract content and fields with a custom schema**, then create a project with the following settings:
    - **Project name**: `Operations call analysis`
    - **Description**: `Extract data from a recorded operations call`
1. Wait for the project to be created.

1. Upload the **meeting-1.mp4** file from the folder where you extracted the content files. Then select the **Video analysis** template and select **Create**.
1. In the **Content** pane on the right, select **Get transcription preview** to see a transcription of the recorded call.

    The *Video analysis* template extracts data for each segment. It doesn't include any
    predefined fields — you define what you want to extract.

1. Use the **+ Add new field** button to add the following fields, selecting **Save** (**&#10003;**) for each new field:

    | Field name | Field description | Value type | Method |
    |--|--|--|--|
    | `Summary` | `Summary of the discussion` | String | Generate |
    | `Participants` | `Count of call participants` | Integer | Generate |
    | `ParticipantNames` | `Names of call participants` | List of Strings | Generate |
    | `SharedSlides` | `Descriptions of any slides presented` | List of Strings | Generate |
    | `AssignedActions` | `Tasks assigned to participants` | List of Objects | Generate |

1. When you enter the **AssignedActions** field, in the table of subfields, create the following subfields:

    | Field name | Field description | Value type | Method |
    |--|--|--|--|
    | `Task` | `Description of the task` | String | Generate |
    | `AssignedTo` | `Who the task is assigned to` | String | Generate |

1. Select **Back** to return to the top level of your schema, verify that it looks correct, and select **Save**.

1. Select **Run analysis** and wait for analysis to complete.

    Video analysis can take some time. While you're waiting, you can view the video below:

    <video controls src="../media/meeting-1.mp4" title="Meeting 1" width="480">
        <track src="../media/meeting-1.vtt" kind="captions" srclang="en" label="English">
    </video>

    **Note**: This video was generated using AI.

1. When analysis is complete, review the results.
1. In the **Fields** pane, view the extracted data.

### Build and test a call analyzer

1. Select the **Build analyzer** button at the top, and build a new analyzer with the following properties (typed exactly as shown here):
    - **Name**: `meetinganalyzer`
    - **Description**: `Operations call video analyzer`
1. Wait for the new analyzer to be ready (use the **Refresh** button to check).
1. When the analyzer has been built, select **Jump to analyzer list**, then select the **meetinganalyzer** link. The fields defined in the analyzer's schema are displayed.
1. On the **meetinganalyzer** page, select the **Test** tab.
1. Use the **+ Upload test files** button to upload **meeting-2.mp4** from the folder where you extracted the content files, and run the analysis.

    Video analysis can take some time. While you're waiting, you can view the video below:

    <video controls src="../media/meeting-2.mp4" title="Meeting 2" width="480">
        <track src="../media/meeting-2.vtt" kind="captions" srclang="en" label="English">
    </video>

    **Note**: This video was generated using AI.

1. Review the **Fields** pane, and view the fields that the analyzer extracted for each shot in the recorded call.
1. Review the **Results** pane to see the JSON response that the analyzer would return to a client application.
1. Close the **meetinganalyzer** page.

> ✅ **Checkpoint**: You've built four custom analyzers with Content Understanding — one each for
> documents, images, audio, and video — and tested each against content it hadn't seen. The
> workflow was identical every time: describe the fields, test, build, reuse. That's the Core of
> this lab. The optional tasks below take the same idea into code, and then compare it against a
> different service.

---

**Next (optional):** [Task 2 — Build an analyzer with the Python SDK](A2-build-an-analyzer-with-the-python-sdk.md) · [Task 3 — Extract invoice data with a prebuilt model](A3-extract-invoice-data-with-a-prebuilt-model.md)
