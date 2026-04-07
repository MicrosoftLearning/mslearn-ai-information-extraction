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

In this exercise, you use Azure AI Search to create a knowledge mining solution that indexes a set of travel brochure documents. The indexing process uses AI skills to extract key information from the documents, and you'll create a Python client application to search the index.

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
1. On the **Connect to your data** page, in the **Data Source** list, select **Azure Blob Storage**.
1. Select **keyword search**. Then complete the data store details with the following values:

1. On **Connect to your data** form set the following:
    - **Storage account**: *Your recently created storage account*
    - **Blob container**: Select the **documents** container.
    - Leave the remaining options as their default values, and then select **Next**.

1. On **Apply AI enrichments** set the following:
    - Select **Extract phrases**.
    - Select **Extract entities**, select the settings icon, ensure only **Persons** and **Locations** are selected, and then select **Save**.
    - Select **Extract text from images**, select the settings icon, ensure **Generate tags** and **Categorize content** are selected, and then select **Save**.
    - If it isn't already selected, choose the free Foundry Tools resource option, and then select **Next**.

    > **Note**: The free Azure AI Services enrichment for Azure AI Search can be used to index a maximum of 20 documents. In a production solution, you should create and attach an Azure AI Services resource.

1. On **Preview mappings** set the following configuration:
    - The fields are already mapped based on the options you selected in the previous step.
    - Review the following fields and ensure that they're configured as shown in the following table. To update a field, select it and then select **Configure field**. Leave all other fields with their default settings.

    | Target index field name | Retrievable | Filterable | Sortable | Facetable | Searchable |
    | ---------- | ----------- | ---------- | -------- | --------- | ---------- |
    | metadata_storage_size | &#10004; | &#10004; | &#10004; | | |
    | metadata_storage_last_modified | &#10004; | &#10004; | &#10004; | | |
    | title | &#10004; | &#10004; | &#10004; | | &#10004; |
    | locations | &#10004; | &#10004; | | | &#10004; |
    | persons | &#10004; | &#10004; | | | &#10004; |
    | keyPhrases | &#10004; | &#10004; | | | &#10004; |

    - Double-check your selections carefully.
    - Select **Next**.

1. On **Advanced settings** set the following:
    - Ensure **Enable semantic ranker** is selected.
    - If it isn't already selected, set **Schedule** to **Once**.
    - Select **Next**.

1. On **Review and create** set **Objects name prefix** to `margies-index` and then select **Create**.
1. You may close the success notification.
1. In the navigation pane on the left, under **Search management**, view the **Indexers** page. The **margies-index-indexer** should appear. Wait a few minutes, and click **&orarr; Refresh** until the **Status** indicates **Success**.

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

1. The results include a **@odata.count** field at the top of the results that indicates the number of documents returned by the search.

1. Modify the JSON request to include a **select** parameter:

    ```json
    {
      "search": "*",
      "count": true,
      "select": "title,locations"
    }
    ```

        This time the results include only the file name and any locations mentioned in the document content. The file name is in the **title** field. The **locations** field was generated by an AI skill.

1. Try the following query string:

    ```json
    {
      "search": "New York",
      "count": true,
      "select": "title,keyPhrases"
    }
    ```

    This search finds documents that mention "New York" in any searchable field, and returns the file name and key phrases.

1. Try one more query:

    ```json
    {
        "search": "New York",
        "count": true,
        "select": "title,keyPhrases",
        "filter": "metadata_storage_size lt 380000"
    }
    ```

    This returns documents mentioning "New York" that are smaller than 380,000 bytes.

## Create a search client application

Now that you have a useful index, you can query it from a Python client application using the Azure AI Search SDK.

### Get the endpoint and keys for your search resource

1. In the Azure portal, return to the **Overview** page for your Azure AI Search resource. Note the **Url** value (e.g., `https://your_resource_name.search.windows.net`). This is the endpoint for your search resource.
1. In the navigation pane on the left, expand **Settings** and view the **Keys** page. Note the **query** key — you'll need this for your client application.

    > **Note**: Azure AI Search creates one default query key for the service. In the Azure portal, this default query key can appear with a blank name. This is expected behavior.

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
    - Searches the index using the query, returning the following fields ordered by title:
        - title
        - locations
        - persons
        - keyPhrases
    - Parses the search results that are returned to display the fields returned for each document in the result set.
1. In the VS Code terminal, run the application:

    ```
    python search-app.py
    ```

1. When prompted, enter a query such as `London` and view the results.
1. Try another query, such as `flights`.
1. When you're finished testing, enter `quit` to close the app.

## Note about knowledge store

Knowledge store steps are excluded from this version of the exercise.

The current **Import data** keyword search flow in the Azure portal doesn't create a knowledge store for this scenario, and the multimodal alternative hasn't been adopted for this exercise.

## Clean up

If you've finished working with Azure AI Search, you should delete the resources you created in this exercise to avoid incurring unnecessary Azure costs.

1. In the [Azure portal](https://portal.azure.com), delete the resource group you created for this exercise.

## More information

To learn more about Azure AI Search, see the [Azure AI Search documentation](https://docs.microsoft.com/azure/search/search-what-is-azure-search).
