---
lab:
  title: Create a knowledge mining solution
  description: Use Azure AI Search to extract key information from documents and make it easier to search and analyze.
  duration: 40 minutes
  level: 200
  islab: true
  primarytopics:
    - Azure
---

# Create a knowledge mining solution

In this exercise, you use Azure AI Search to create a knowledge mining solution that indexes a set of travel brochure documents. The indexing process uses AI skills to extract key information from the documents, and you'll build a knowledge store containing enriched data for further analysis. Finally, you'll create a Python client application to search the index.

This exercise takes approximately **40** minutes.

## Create Azure resources

The solution requires multiple resources in your Azure subscription, all created in the same region.

### Create an Azure AI Search resource

1. In a web browser, open the [Azure portal](https://portal.azure.com) at `https://portal.azure.com` and sign in with your Azure credentials.
1. Select the **&#65291;Create a resource** button, search for `Azure AI Search`, and create an **Azure AI Search** resource with the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *Create or select a resource group*
    - **Service name**: *A valid name for your search resource*
    - **Location**: *Any available location*
    - **Pricing tier**: Free
1. Wait for deployment to complete, and then go to the deployed resource.
1. Review the **Overview** page. Here you can use a visual interface to create, test, manage, and monitor the various components of a search solution.

### Create a storage account

1. Return to the Azure portal home page and create a **Storage account** resource with the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *The same resource group as your Azure AI Search resource*
    - **Storage account name**: *A valid name for your storage resource*
    - **Region**: *The same region as your Azure AI Search resource*
    - **Primary service**: Azure Blob Storage or Azure Data Lake Storage Gen 2
    - **Performance**: Standard
    - **Redundancy**: Locally-redundant storage (LRS)
1. Wait for deployment to complete, and then go to the deployed resource.

## Upload documents to Azure Storage

Your knowledge mining solution will extract information from travel brochure documents stored in Azure Blob Storage.

1. In a new browser tab, download [documents.zip](https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/knowledge/documents.zip) from `https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/knowledge/documents.zip` and save it to a local folder.
1. Extract the downloaded *documents.zip* file and view the travel brochure files it contains.
1. In the Azure portal, navigate to your storage account and select **Storage browser** in the navigation pane.
1. In the storage browser, select **Blob containers**.
1. In the toolbar, select **+ Container** and create a new container with the following settings:
    - **Name**: `documents`
    - **Anonymous access level**: Private (no anonymous access)
1. Select the **documents** container, and use the **Upload** toolbar button to upload the .pdf files you extracted from **documents.zip**.

    ![TODO: New screenshot of the Azure storage browser with the documents container and its file contents.](./media/blob-containers.png)

## Create and run an indexer

Now that you have the documents in place, you can create an indexer to use AI skills to extract information from them.

1. In the Azure portal, browse to your Azure AI Search resource. On its **Overview** page, select **Import data**.
1. On the **Connect to your data** page, in the **Data Source** list, select **Azure Blob Storage**. Then complete the data store details with the following values:
    - **Data Source**: Azure Blob Storage
    - **Data source name**: `margies-documents`
    - **Data to extract**: Content and metadata
    - **Parsing mode**: Default
    - **Subscription**: *Your Azure subscription*
    - **Connection string**:
        - Select **Choose an existing connection**
        - Select your storage account
        - Select the **documents** container
    - **Managed identity authentication**: None
    - **Container name**: documents
    - **Blob folder**: *Leave this blank*
    - **Description**: `Travel brochures`
1. Proceed to the next step (**Add cognitive skills**), which has three expandable sections.
1. In the **Attach Azure AI Services** section, select **Free (limited enrichments)**\*.

    > **Note**: \*The free Azure AI Services enrichment for Azure AI Search can be used to index a maximum of 20 documents. In a production solution, you should create and attach an Azure AI Services resource.

1. In the **Add enrichments** section:
    - Change the **Skillset name** to `margies-skillset`.
    - Select the option **Enable OCR and merge all text into merged_content field**.
    - Ensure that the **Source data field** is set to **merged_content**.
    - Leave the **Enrichment granularity level** as **Source field**.
    - Select the following enriched fields:

        | Cognitive Skill | Parameter | Field name |
        | --------------- | ---------- | ---------- |
        | **Text Cognitive Skills** | |  |
        | Extract people names | | people |
        | Extract location names | | locations |
        | Extract key phrases | | keyphrases |
        | **Image Cognitive Skills** | |  |
        | Generate tags from images | | imageTags |
        | Generate captions from images | | imageCaption |

        Double-check your selections (it can be difficult to change them later).

1. In the **Save enrichments to a knowledge store** section:
    - Select only the following checkboxes (an <font color="red">error</font> will appear — you'll resolve that shortly):
        - **Azure file projections**:
            - Image projections
        - **Azure table projections**:
            - Documents
                - Key phrases
        - **Azure blob projections**:
            - Document
    - Under **Storage account connection string** (beneath the <font color="red">error messages</font>):
        - Select **Choose an existing connection**
        - Select your storage account
        - Select the **documents** container (*this is only required to set the storage account — you'll change the container name below!*)
    - Change the **Container name** to `knowledge-store`.
1. Proceed to the next step (**Customize target index**).
1. Change the **Index name** to `margies-index`.
1. Ensure that the **Key** is set to **metadata_storage_path**, leave the **Suggester name** blank, and ensure **Search mode** is **analyzingInfixMatching**.
1. Make the following changes to the index fields, leaving all other fields with their default settings (**IMPORTANT**: you may need to scroll to the right to see the entire table):

    | Field name | Retrievable | Filterable | Sortable | Facetable | Searchable |
    | ---------- | ----------- | ---------- | -------- | --------- | ---------- |
    | metadata_storage_size | &#10004; | &#10004; | &#10004; | | |
    | metadata_storage_last_modified | &#10004; | &#10004; | &#10004; | | |
    | metadata_storage_name | &#10004; | &#10004; | &#10004; | | &#10004; |
    | locations | &#10004; | &#10004; | | | &#10004; |
    | people | &#10004; | &#10004; | | | &#10004; |
    | keyphrases | &#10004; | &#10004; | | | &#10004; |

    Double-check your selections carefully.

1. Proceed to the next step (**Create an indexer**).
1. Change the **Indexer name** to `margies-indexer`.
1. Leave the **Schedule** set to **Once**.
1. Select **Submit** to create the data source, skillset, index, and indexer. The indexer runs automatically and:
    - Extracts the document metadata fields and content from the data source
    - Runs the skillset of cognitive skills to generate additional enriched fields
    - Maps the extracted fields to the index
    - Saves the extracted data assets to the knowledge store
1. In the navigation pane on the left, under **Search management**, view the **Indexers** page. The **margies-indexer** should appear. Wait a few minutes, and click **&orarr; Refresh** until the **Status** indicates **Success**.

## Search the index

Now that you have an index, you can search it.

1. Return to the **Overview** page for your Azure AI Search resource, and on the toolbar, select **Search explorer**.
1. In Search explorer, in the **Query string** box, enter `*` (a single asterisk) and then select **Search**.

    This query retrieves all documents in the index in JSON format. Examine the results and note the fields for each document, which include document content, metadata, and enriched data extracted by the cognitive skills.

1. In the **View** menu, select **JSON view** and note that the JSON request for the search is shown:

    ```json
    {
      "search": "*",
      "count": true
    }
    ```

1. Modify the JSON request to include a **select** parameter:

    ```json
    {
      "search": "*",
      "count": true,
      "select": "metadata_storage_name,locations"
    }
    ```

    This time the results include only the file name and any locations mentioned in the document content.

1. Try the following query string:

    ```json
    {
      "search": "New York",
      "count": true,
      "select": "metadata_storage_name,keyphrases"
    }
    ```

    This search finds documents that mention "New York" in any searchable field, and returns the file name and key phrases.

1. Try one more query:

    ```json
    {
        "search": "New York",
        "count": true,
        "select": "metadata_storage_name,keyphrases",
        "filter": "metadata_storage_size lt 380000"
    }
    ```

    This returns documents mentioning "New York" that are smaller than 380,000 bytes.

## Create a search client application

Now that you have a useful index, you can query it from a Python client application using the Azure AI Search SDK.

### Get the endpoint and keys for your search resource

1. In the Azure portal, return to the **Overview** page for your Azure AI Search resource. Note the **Url** value (e.g., `https://your_resource_name.search.windows.net`). This is the endpoint for your search resource.
1. In the navigation pane on the left, expand **Settings** and view the **Keys** page. Note the **query** key — you'll need this for your client application.

### Prepare to use the Azure AI Search SDK

1. Start **Visual Studio Code**.
1. Open the Command Palette (press **Ctrl+Shift+P**), type **Git: Clone**, and select it.
1. In the URL bar, paste the following repository URL and press **Enter**:

    ```
    https://github.com/microsoftlearning/mslearn-ai-information-extraction
    ```

1. Choose a local folder to clone into, and then when prompted, select **Open** to open the cloned repository in VS Code.
1. Open a new terminal and navigate to the Python code folder:

    ```
    cd Labfiles/04-knowledge-mining
    ```

1. Install the required packages:

    ```
    python -m venv labenv
    labenv\Scripts\activate
    pip install -r requirements.txt
    ```

    > **Note**: The requirements.txt installs the [azure-search-documents](https://learn.microsoft.com/python/api/overview/azure/search-documents-readme?view=azure-python) Python SDK package and its dependencies.

1. In the VS Code Explorer pane, open the **.env** file in **Labfiles/04-knowledge-mining**.

1. Replace the following placeholder values:
    - **your_search_endpoint**: *The endpoint for your Azure AI Search resource*
    - **your_query_key**: *The query key for your Azure AI Search resource*
    - **your_index_name**: *The name of your index (should be `margies-index`)*
1. Save the file (**CTRL+S**).

1. In VS Code, open the **search-app.py** file.

1. Review the code, which:
    - Retrieves the configuration settings from the .env file.
    - Creates a `SearchClient` with the endpoint, key, and index name.
    - Prompts the user for a search query in a loop (until they type "quit").
    - Searches the index and displays the file name, locations, people, and key phrases for each result.
1. In the VS Code terminal, run the application:

    ```
    python search-app.py
    ```

1. When prompted, enter a query such as `London` and view the results.
1. Try another query, such as `flights`.
1. When you're finished testing, enter `quit` to close the app.

## View the knowledge store

After running the indexer, the enriched data extracted by the indexing process is stored in the knowledge store projections.

### View object projections

The *object* projections consist of a JSON file for each indexed document, stored in a blob container.

1. In the Azure portal, view the storage account you created previously.
1. Select **Storage browser** in the navigation pane.
1. Expand **Blob containers** to view the containers. In addition to the **documents** container, there should be two new containers: **knowledge-store** and **margies-skillset-image-projection**.
1. Select the **knowledge-store** container. It should contain a folder for each indexed document.
1. Open any folder, then select the **objectprojection.json** file and download it. Each JSON file contains a representation of an indexed document with the enriched data extracted by the skillset.

### View file projections

The *file* projections create JPEG files for each image extracted from the documents during indexing.

1. In the storage browser, select the **margies-skillset-image-projection** blob container. It contains a folder for each document that contained images.
1. Open any folder and view its \*.jpg files. Download and open an image file to see the extracted image.

### View table projections

The *table* projections form a relational schema of enriched data.

1. In the storage browser, expand **Tables**.
1. Select the **margiesSkillsetDocument** table to view a row for each indexed document.
1. View the **margiesSkillsetKeyPhrases** table, which contains a row for each key phrase extracted from the documents.

The table projections enable you to build analytical and reporting solutions that query a relational schema. Key columns can be used to join tables — for example, to retrieve all key phrases from a specific document.

## Clean up

If you've finished working with Azure AI Search, you should delete the resources you created in this exercise to avoid incurring unnecessary Azure costs.

1. In the [Azure portal](https://portal.azure.com), delete the resource group you created for this exercise.

## More information

To learn more about Azure AI Search, see the [Azure AI Search documentation](https://docs.microsoft.com/azure/search/search-what-is-azure-search).
