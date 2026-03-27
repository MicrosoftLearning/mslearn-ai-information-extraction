---
lab:
  title: Build an automated RAG ingestion pipeline with Content Understanding
  description: Use Azure Content Understanding, Azure AI Search, and Azure OpenAI to build a continuous multimodal RAG ingestion pipeline.
  duration: 45 minutes
  level: 300
  islab: true
  primarytopics:
    - Azure
    - Azure Content Understanding
---

# Build an automated RAG ingestion pipeline with Content Understanding

Retrieval-augmented generation (RAG) is a method that enhances Large Language Models (LLMs) by integrating data from external knowledge sources. In production scenarios, new documents arrive continuously and must be extracted, embedded, and indexed so they're available for search in near real-time.

In this exercise, you'll build an automated RAG ingestion pipeline that uses Azure Content Understanding to extract content from multimodal documents, embeds the content using Azure OpenAI, and indexes it in Azure AI Search. The pipeline tracks which files have already been processed and can run in **watch mode** to automatically detect and ingest new documents as they arrive. You'll finish by creating a conversational agent that answers questions grounded in your indexed data.

This exercise takes approximately **45** minutes.

## Create Azure resources

You need several Azure resources for this pipeline: a Microsoft Foundry resource (for Content Understanding and Azure OpenAI), and an Azure AI Search resource.

### Create a Microsoft Foundry resource and project

1. In a web browser, open the [Microsoft Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in.
1. Make sure the **New Foundry** toggle is on so that you're using **Foundry (new)**.
1. Select the project name in the upper-left corner, and then select **Create new project**.
1. Give your project a name and expand **Advanced options** to specify the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *Create or select a resource group*
    - **Location**: Choose one of the following supported regions:\*
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

    > \*Azure Content Understanding is available in selected regions. See the [region support documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support) for the latest availability.

1. Select **Create** and wait for your project to be created. This will create a project and the parent resource.
1. Once created, select the project name at the top of the page, and select **Project details**. On that page, follow the link to the parent resource. Leave this browser tab open.

### Configure Content Understanding models and connection

Content Understanding uses OpenAI models for analysis that are deployed in your project. You need to deploy these models before using analyzers, and set up the connection between Content Understanding and your Foundry resource. The easiest way is through the Content Understanding Studio.

1. In a new tab, navigate to [Content Understanding Studio](https://contentunderstanding.ai.azure.com/home) at `https://contentunderstanding.ai.azure.com/home` and sign in with your credentials.
1. Select the settings gear icon on the top navigation bar, and select **+ Add resource**.
1. Select your subscription and resource group where you created your Foundry resource, then select your Foundry resource name from the dropdown. This resource is the parent resource to the project you previously created.
1. Ensure the **Enable auto-deployment** box is checked, then select **Next** and **Save** to create the configuration.
1. Wait while it deploys the required models for Content Understanding.

### Create an Azure AI Search resource

1. In a new browser tab, open the [Azure portal](https://portal.azure.com) at `https://portal.azure.com` and sign in with your Azure credentials.
1. Select **&#65291;Create a resource**, search for `Azure AI Search`, and create an **Azure AI Search** resource with the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *The same resource group as your Microsoft Foundry resource*
    - **Service name**: *A valid unique name*
    - **Location**: *The same location as your Microsoft Foundry resource*
    - **Pricing tier**: Free or Basic
1. Wait for deployment to complete.

### Gather credentials

You'll need the following values to configure the pipeline. Note them from the Azure portal:

- **Foundry endpoint**: From the parent resource tab you left open, copy the **Endpoint** from the **Overview** page (e.g., `https://<name>.services.ai.azure.com/`).
- **Foundry API key**: From the same page, select **Resource Management** > **Keys and Endpoint** and copy one of the **Keys**.
- **Azure AI Search endpoint**: From your AI Search resource's **Overview** page in the Azure portal (e.g., `https://<name>.search.windows.net`).
- **Model deployments**: From the Foundry Home page, select **Build** > **Models** to view your deployed models. Note that there is a number at the end of your embedding model name, which you'll need to update in your `.env` file.
- **Azure AI Search admin key**: From your AI Search resource's **Settings** > **Keys** page.

    > **Note**: The Foundry endpoint and key are used for both Content Understanding and Azure OpenAI, since both services are included in the same Foundry resource.

## Prepare the development environment

You'll use Visual Studio Code as your development environment.

1. Start **Visual Studio Code**.
1. Open the Command Palette (press **Ctrl+Shift+P**), type **Git: Clone**, and select it.
1. In the URL bar, paste the following repository URL and press **Enter**:

    ```
    https://github.com/microsoftlearning/mslearn-ai-information-extraction
    ```

1. Choose a local folder to clone into, and then when prompted, select **Open** to open the cloned repository in VS Code.
1. Open a new terminal and navigate to the RAG pipeline folder:

    ```
    cd Labfiles/05-rag-pipeline
    ```

1. Install the required Python packages:

    ```
    python -m venv labenv
    labenv\Scripts\activate
    pip install -r requirements.txt
    ```

    > **Note**: The requirements.txt installs the [azure-ai-contentunderstanding](https://learn.microsoft.com/python/api/overview/azure/ai-contentunderstanding-readme?view=azure-python-preview) SDK, the [azure-search-documents](https://learn.microsoft.com/python/api/overview/azure/search-documents-readme?view=azure-python) SDK, and the [openai](https://pypi.org/project/openai/) package.

1. In the VS Code Explorer pane, open the **.env** file in **Labfiles/05-rag-pipeline**.
1. Replace the placeholder values in the `.env` file with the credentials you gathered earlier:
    - `FOUNDRY_ENDPOINT` — Your Microsoft Foundry resource endpoint
    - `FOUNDRY_KEY` — Your Microsoft Foundry resource API key
    - `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` — Your chat model deployment name (e.g., `gpt-4.1-######`)
    - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` — Your embedding model deployment name (e.g., `text-embedding-3-large-######`)
    - `AZURE_SEARCH_ENDPOINT` — Your Azure AI Search endpoint
    - `AZURE_SEARCH_KEY` — Your Azure AI Search admin key
1. Save the file (**CTRL+S**).

### Download sample documents

The RAG pipeline needs documents to process. You'll use the same travel brochure documents from the knowledge mining exercise.

1. Download [documents.zip](https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/knowledge/documents.zip) from `https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/knowledge/documents.zip`.
1. Extract the PDF files from the zip and copy them into the **Labfiles/05-rag-pipeline/data** folder.
1. Verify the files are in place by checking the data folder in VS Code Explorer or running in your terminal:

    ```
    dir data
    ```

## Step 1: Create a Content Understanding analyzer

The first step in the pipeline is to create an analyzer that will extract structured content from documents. You'll use the Content Understanding Python SDK to create an analyzer programmatically.

1. In VS Code, open the **create-analyzer.py** file.

1. Review the code, which:
    - Loads environment variables from the `.env` file.
    - Creates a `ContentUnderstandingClient` using the endpoint and API key.
    - Defines a document analyzer with a field extraction schema to capture summaries and key topics.
    - Creates the analyzer by calling `begin_create_analyzer`.

1. In the VS Code terminal (make sure the virtual environment is activated), run the script:

    ```
    python create-analyzer.py
    ```

1. Wait for the analyzer to be created. The output should confirm that the analyzer was created successfully.

## Step 2: Run the automated ingestion pipeline

Now you'll run the automated ingestion pipeline. This single script handles the entire flow — extracting content with Content Understanding, generating vector embeddings with Azure OpenAI, and indexing into Azure AI Search. It also tracks which files have been processed so it can detect new or updated documents on subsequent runs.

1. In VS Code, open the **ingest-pipeline.py** file.

1. Review the code and notice how it:
    - **Tracks processed files** using a manifest (`processed_files.json`) that records the SHA-256 hash of each file. On each run, the pipeline compares the current hash of every file in the `data/` folder against the manifest, so only new or modified files are processed.
    - **Ensures the search index exists** by calling `ensure_index()`, which creates or updates the Azure AI Search index with the required schema (text fields, a vector field, and HNSW vector search configuration).
    - **Extracts content** from each new file by submitting it to the Content Understanding analyzer via `begin_analyze_binary`, which returns markdown content and extracted fields (summary, key topics).
    - **Chunks the content** by splitting at paragraph boundaries with a 2000-character limit, keeping each chunk self-contained.
    - **Generates embeddings** for each chunk using the Azure OpenAI embedding model, producing a 3072-dimension vector for semantic search.
    - **Indexes the chunks** into Azure AI Search using deterministic document IDs (based on the file name and chunk index), so re-ingesting an updated file replaces its old chunks.
    - Supports a `--watch` flag for continuous monitoring and a `--reset` flag to reprocess all files.

1. In the VS Code terminal, run the pipeline:

    ```
    python ingest-pipeline.py
    ```

1. Watch the output as the pipeline processes each document. You'll see timestamped log messages showing each file being extracted, chunks being embedded, and results being indexed. For example:

    ```
    [14:23:01] Verifying search index...
    [14:23:02] Search index 'rag-content-index' is ready.
    [14:23:02] Detected 5 new/updated file(s).
    [14:23:02]   Processing: Margies-Travel-Company-Info.pdf
    [14:23:08]     Embedding chunk 1/3...
    [14:23:09]     Embedding chunk 2/3...
    [14:23:09]     Embedding chunk 3/3...
    [14:23:10]     Indexed 3 chunk(s) from Margies-Travel-Company-Info.pdf.
    ...
    ```

1. After the pipeline finishes, check that it created a **processed_files.json** file in the rag-pipeline folder. This manifest records the hash of each processed file — if you run the pipeline again, it will detect that there are no new files:

    ```
    python ingest-pipeline.py
    ```

    The output should say "No new files to ingest — all documents are up to date."

## Step 3: Query the index with a RAG agent

With the content indexed, you can use a conversational agent that retrieves relevant content and uses an OpenAI chat model to answer questions.

1. In VS Code, open the **rag-agent.py** file.

1. Review the code, which:
    - Creates an Azure AI Search client to retrieve documents.
    - Creates an Azure OpenAI chat client.
    - Implements a retrieval function that performs hybrid search (combining keyword and vector search) to find the most relevant content chunks.
    - Constructs a prompt that includes the retrieved context and the user's question.
    - Sends the prompt to the chat model for answer generation.
    - Runs a conversational loop so you can ask multiple questions.

1. In the VS Code terminal, run the agent:

    ```
    python rag-agent.py
    ```

1. When prompted, enter a question about the content you indexed. For example:
    - `What destinations are featured in the travel brochures?`
    - `What activities are recommended in Dubai?`
    - `Tell me about the Margie's Travel company`

1. Review the agent's responses. They should be grounded in the actual content extracted from the documents, with answers that cite the source document names. When you're satisfied, type `quit` to exit the agent.

## Step 4: Ingest new documents automatically

The real power of this pipeline is continuous ingestion. You'll now start the pipeline in watch mode so it monitors the `data/` folder, then add a new document and watch it get automatically extracted, embedded, and indexed.

### Start the pipeline in watch mode

1. In VS Code, open a **second terminal** (select **Terminal** > **New Terminal**). Make sure you activate the virtual environment and navigate to the pipeline folder:

    ```
    cd Labfiles\05-rag-pipeline
    labenv\Scripts\activate
    ```

1. Start the pipeline in watch mode:

    ```
    python ingest-pipeline.py --watch
    ```

    The pipeline will begin polling the `data/` folder every 30 seconds. You should see output like:

    ```
    [14:30:00] Watching 'data/' for new documents (press Ctrl+C to stop)...

    [14:30:01] No new files. Waiting...
    ```

    Leave this terminal running.

### Add a new document

1. Switch to the VS Code Explorer pane and right-click the **data** folder under **Labfiles/05-rag-pipeline**. Select **New File** and name it **tokyo-guide.txt**.

1. Add the following content to the new file and save it:

    ```text
    Tokyo Travel Guide

    Tokyo, the capital of Japan, is one of the most dynamic cities in the world,
    blending centuries-old tradition with cutting-edge technology and innovation.

    Top Attractions:
    - Senso-ji Temple: Tokyo's oldest temple, located in Asakusa, is a must-visit.
      The approach through Nakamise-dori shopping street is iconic.
    - Shibuya Crossing: The world's busiest pedestrian crossing is a symbol of
      Tokyo's energy and pace.
    - Meiji Shrine: A serene Shinto shrine set in a lush forest in the heart of
      the city, dedicated to Emperor Meiji.
    - Tokyo Skytree: At 634 meters, this broadcasting tower offers panoramic views
      of the entire metropolitan area.
    - Tsukiji Outer Market: While the inner wholesale market has moved to Toyosu,
      the outer market still offers incredible fresh seafood and street food.

    Neighborhoods to Explore:
    - Shinjuku: A vibrant district known for its nightlife, shopping, and the
      beautiful Shinjuku Gyoen National Garden.
    - Akihabara: The hub of anime, manga, and electronics culture.
    - Harajuku: Famous for its youth fashion, Takeshita Street, and trendy cafes.
    - Ginza: Tokyo's upscale shopping and dining district.

    Getting Around:
    Tokyo has one of the world's most efficient public transportation systems.
    The Tokyo Metro and JR lines connect every corner of the city. A Suica or
    Pasmo card makes travel seamless. For visitors, the Japan Rail Pass offers
    unlimited travel on JR lines.

    Best Time to Visit:
    Spring (March-May) for cherry blossoms and autumn (October-November) for
    fall foliage are the most popular seasons. Summers can be hot and humid,
    while winters are mild compared to northern Japan.
    ```

1. Switch back to the terminal running the pipeline in watch mode. Within 30 seconds, you should see the pipeline detect and process the new file:

    ```
    [14:31:00] Detected 1 new/updated file(s).
    [14:31:00]   Processing: tokyo-guide.txt
    [14:31:05]     Embedding chunk 1/1...
    [14:31:06]     Indexed 1 chunk(s) from tokyo-guide.txt.
    [14:31:06] Ingestion complete — 1 file(s), 1 chunk(s) indexed.
    ```

### Query the newly ingested content

1. Switch to your **first terminal** (or open a new one with the virtual environment activated) and run the RAG agent again:

    ```
    python rag-agent.py
    ```

1. Ask a question about the newly added document:
    - `What can you tell me about Tokyo?`
    - `What are the top attractions in Tokyo?`
    - `How do I get around in Tokyo?`

1. The agent should now return answers grounded in the Tokyo travel guide — content that wasn't available during your first query session. This demonstrates how the continuous pipeline makes new knowledge available without any manual reprocessing.

1. Type `quit` to exit the agent, then switch to the watch-mode terminal and press **Ctrl+C** to stop the pipeline.

## Clean up

If you've finished working with the RAG pipeline, you should delete the resources you created in this exercise to avoid incurring unnecessary Azure costs.

1. In the [Azure portal](https://portal.azure.com), delete the resource group you created for this exercise.

## More information

- [Tutorial: Build a RAG solution with Content Understanding](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/build-rag-solution)
- [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
- [Azure Content Understanding Python SDK](https://pypi.org/project/azure-ai-contentunderstanding/)
