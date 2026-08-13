---
lab:
    title: 'Task 1 – Build a knowledge mining index'
    description: 'Use the Azure AI Search Import data wizard to crawl a document library, enrich it with AI skills that extract key phrases, people, and locations, then query the index from Search explorer and a Python client app.'
    level: 200
    concepts: 'Azure AI Search, indexers, AI enrichment skills, Search explorer, search SDK'
    islab: true
    status: 'draft'
---

# Task 1 — Build a knowledge mining index

*Part of the **Make extracted information searchable** lab. New here? Start with [Getting started](B0-getting-started.md).*

> **Set up (start here):** This task needs an **Azure AI Search** resource, a **storage account**,
> the sample documents, and the starter code. It does **not** need a Foundry resource. If you
> haven't already, complete [Getting started](B0-getting-started.md) to create the search and
> storage resources, download **documents.zip**, clone the code, and set `SEARCH_ENDPOINT`,
> `SEARCH_QUERY_KEY`, and `SEARCH_INDEX_NAME` in `Python/.env`. Then, from the
> `Python` folder, verify you're ready:

```
python ../setup/check_env.py --task 1
```

---

Fabrikam Logistics has a library of reference documents that everyone knows contains the answers
and nobody can find anything in. In this task you'll fix that without writing a line of indexing
code: Azure AI Search will crawl the library, run AI skills over every document to pull out the
key phrases, people, and places mentioned in it, and build a queryable index.

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
<summary>What's an indexer, a skill, and an index?</summary>
<div class="concept-body" markdown="1">

Three pieces, and it's worth keeping them straight:

- A **data source** is where your documents live — here, a blob container.
- An **indexer** is the crawler. It connects to the data source on a schedule, pulls each
  document, and pushes the results into an index.
- A **skillset** is the AI that runs *while* the indexer works. Each **skill** adds something the
  raw document didn't have: key phrases, recognized people and locations, text read out of
  images. This is what "AI enrichment" means.
- An **index** is the searchable result: a set of fields, each marked as searchable, filterable,
  sortable, or facetable.

The field attributes you set in the wizard aren't cosmetic — a field you don't mark
**filterable** can't be used in a `$filter`, no matter how much you want it to be later.

[Learn more →](https://learn.microsoft.com/azure/search/search-what-is-azure-search)

</div>
</details>

## Upload documents to Azure Storage

1. If you haven't already, extract *documents.zip* (downloaded in [Getting started](B0-getting-started.md)) and view the reference documents it contains.
1. In the Azure portal, navigate to your storage account and select **Storage browser** in the navigation pane.
1. In the storage browser, select **Blob containers**.
1. In the toolbar, select **+ Container** and create a new container with the following settings:
    - **Name**: `documents`
    - **Anonymous access level**: Private (no anonymous access)
1. Select the **documents** container, and use the **Upload** toolbar button to upload the .pdf files you extracted from **documents.zip**.

## Create and run an indexer

Now that the documents are in place, create an indexer that uses AI skills to extract information
from them.

1. In the Azure portal, browse to your Azure AI Search resource. On its **Overview** page, select **Import data**.
1. On the **Connect to your data** page, in the **Data Source** list, select **Azure Blob Storage**.
1. Select **keyword search**. Then complete the data store details with the following values:
    - **Storage account**: *Your storage account*
    - **Blob container**: Select the **documents** container.
    - Leave the remaining options as their default values, and then select **Next**.

1. On **Apply AI enrichments**, set the following:
    - Select **Extract phrases**.
    - Select **Extract entities**, select the settings icon, ensure only **Persons** and **Locations** are selected, and then select **Save**.
    - Select **Extract text from images**, select the settings icon, ensure **Generate tags** and **Categorize content** are selected, and then select **Save**.
    - If it isn't already selected, choose the free Foundry Tools resource option, and then select **Next**.

    > **Note**: The free Foundry Tools enrichment for Azure AI Search can be used to index a maximum of 20 documents. In a production solution, you'd create and attach a dedicated Foundry Tools resource.

1. On **Preview mappings**, set the following configuration:
    - The fields are already mapped based on the options you selected in the previous step.
    - Review the following fields and ensure that they're configured as shown in the table. To update a field, select it and then select **Configure field**. Leave all other fields with their default settings.

    | Target index field name | Retrievable | Filterable | Sortable | Facetable | Searchable |
    | ---------- | ----------- | ---------- | -------- | --------- | ---------- |
    | metadata_storage_size | &#10004; | &#10004; | &#10004; | | |
    | metadata_storage_last_modified | &#10004; | &#10004; | &#10004; | | |
    | title | &#10004; | &#10004; | &#10004; | | &#10004; |
    | locations | &#10004; | &#10004; | | | &#10004; |
    | persons | &#10004; | &#10004; | | | &#10004; |
    | keyPhrases | &#10004; | &#10004; | | | &#10004; |

    - Double-check your selections carefully — the client app later in this task selects and orders by exactly these fields.
    - Select **Next**.

1. On **Advanced settings**, set the following:
    - Ensure **Enable semantic ranker** is selected.
    - If it isn't already selected, set **Schedule** to **Once**.
    - Select **Next**.

1. On **Review and create**, set **Objects name prefix** to `fabrikam-index` and then select **Create**.
1. You may close the success notification.
1. In the navigation pane on the left, under **Search management**, view the **Indexers** page. The **fabrikam-index-indexer** should appear. Wait a few minutes, and select **&orarr; Refresh** until the **Status** indicates **Success**.

## Search the index

Now that you have an index, search it.

1. Return to the **Overview** page for your Azure AI Search resource, and on the toolbar, select **Search explorer**.
1. In Search explorer, in the **Query string** box, enter `*` (a single asterisk) and then select **Search**.

    This query retrieves all documents in the index in JSON format. Examine the results and note
    the fields for each document, which include document content, metadata, and the enriched data
    extracted by the AI skills.

1. In the **View** menu, select **JSON view** and note that the JSON request for the search is shown:

    ```json
    {
      "search": "*",
      "count": true
    }
    ```

1. The results include an **@odata.count** field at the top that indicates the number of documents returned by the search.

1. Modify the JSON request to include a **select** parameter:

    ```json
    {
      "search": "*",
      "count": true,
      "select": "title,locations"
    }
    ```

    This time the results include only the file name and any locations mentioned in the document
    content. The file name is in the **title** field. The **locations** field was generated by an
    AI skill — it wasn't in the PDF as a field, the skillset inferred it.

1. Try the following query string:

    ```json
    {
      "search": "New York",
      "count": true,
      "select": "title,keyPhrases"
    }
    ```

    This search finds documents that mention "New York" in any searchable field, and returns the
    file name and key phrases.

1. Try one more query:

    ```json
    {
        "search": "New York",
        "count": true,
        "select": "title,keyPhrases",
        "filter": "metadata_storage_size lt 380000"
    }
    ```

    This returns documents mentioning "New York" that are smaller than 380,000 bytes. This only
    works because you marked `metadata_storage_size` as **filterable** in the wizard.

## Query the index from a client application

Search explorer is for you. Your colleagues need an app.

1. In VS Code, open the **.env** file in **Labfiles/B-make-extracted-information-searchable/Python** and confirm:
    - `SEARCH_ENDPOINT` — the **Url** from your search resource's Overview page
    - `SEARCH_QUERY_KEY` — the **query** key from **Settings** > **Keys**
    - `SEARCH_INDEX_NAME` — `fabrikam-index`
1. Save the file (**Ctrl+S**).

1. Open the `Python` folder and activate the virtual environment from [Getting started](B0-getting-started.md):

    ```
    .\labenv\Scripts\Activate.ps1
    ```

1. In VS Code, open the **search-app.py** file.

1. Review the code, which:
    - Retrieves the configuration settings from the `.env` file.
    - Creates a `SearchClient` with the endpoint, query key, and index name.
    - Prompts the user for a search query in a loop (until they type `quit`).
    - Searches the index using the query, returning the following fields ordered by title:
        - title
        - locations
        - persons
        - keyPhrases
    - Parses the search results and displays the fields returned for each document.

    > **Note**: A **query** key is enough here because this app only reads. Tasks 2 and 4 create and write to an index, so they need an **admin** key instead.

1. In the VS Code terminal, run the application:

    ```
    python search-app.py
    ```

1. When prompted, enter a query such as `London` and view the results.
1. Try another query, such as `flights`.
1. When you're finished testing, enter `quit` to close the app.

> ✅ **Checkpoint**: You've built an AI-enriched search index without writing any indexing code,
> and queried it both interactively and from an application. That's the Core of this lab. The
> optional tasks below build a very different kind of index — one you define yourself, with
> vectors — so you can ask questions in natural language instead of searching for keywords.

When you're finished, enter `deactivate` to exit the virtual environment.

---

**Next (optional):** [Task 2 — Build a RAG ingestion pipeline](B2-build-a-rag-ingestion-pipeline.md)
