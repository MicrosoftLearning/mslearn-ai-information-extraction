---
lab:
    title: 'Getting started: set up your environment'
    description: 'Shared setup for the Make extracted information searchable lab: create an Azure AI Search resource, storage, and a Microsoft Foundry resource, get the starter code and sample documents, and configure your environment. Complete this once before any task.'
    level: 300
    concepts: 'environment setup, Azure AI Search, Microsoft Foundry resource'
    status: 'draft'
---

# Getting started

This page sets up everything the **Make extracted information searchable** lab needs. **Every
task begins here** — complete this page first. Each task is written so you can then do it on its
own; if you're working through the whole lab in one sitting, you only need to do this setup once.

**Your scenario:** you work at **Fabrikam Logistics**, a freight-forwarding company. Across the
lab you'll turn the company's reference document library into a searchable, answerable, and
self-updating knowledge base.

> **Note**: Some of the technologies used in this lab are in preview or in active development.
> You may experience some unexpected behavior, warnings, or errors.

## Prerequisites

Before starting, ensure you have:

- An [Azure subscription](https://azure.microsoft.com/free/) with sufficient permissions and quota to provision Azure AI resources
- [Visual Studio Code](https://code.visualstudio.com/) installed on your local machine
- [Python 3.11](https://www.python.org/downloads/) or later installed\*
- [Git](https://git-scm.com/downloads) installed on your local machine
- Basic familiarity with Python

> \* The Azure SDK for Python supports Python 3.9 or later. This lab was tested with Python 3.13.

## What each task needs

Create only what you need. Everything goes in **one resource group**, in **one region**.

| Resource | Needed by |
| --- | --- |
| Azure AI Search | All tasks |
| Azure Storage account | Task 1 (holds the documents the indexer crawls) |
| Microsoft Foundry resource with model deployments | Tasks 2, 3, 4 |

## Create an Azure AI Search resource

1. In a web browser, open the [Azure portal](https://portal.azure.com) at `https://portal.azure.com` and sign in with your Azure credentials.
1. Select **&#65291;Create a resource**, search for `Azure AI Search`, and create an **Azure AI Search** resource with the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *Create or select a resource group*
    - **Service name**: *A valid unique name for your search resource*
    - **Location**: *Any available location — note it, and use the same one for everything else*
    - **Pricing tier**: Free (*or Basic if Free isn't available*)
1. Wait for deployment to complete, and then go to the deployed resource.
1. Review the **Overview** page. Here you can create, test, manage, and monitor the components of a search solution.

    > **Note**: The Free tier is enough for this lab, but it limits you to a small number of indexes and documents. If you plan to run Task 1 *and* Tasks 2-4 on a Free-tier service, you'll be creating two indexes — that's within the Free limit.

## Create a storage account (Task 1 only)

Skip this if you're only doing Tasks 2, 3, and 4.

1. Return to the Azure portal home page and create a **Storage account** resource with the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *The same resource group as your Azure AI Search resource*
    - **Storage account name**: *A valid globally unique name*
    - **Region**: *The same region as your Azure AI Search resource*
    - **Primary service**: Azure Blob Storage or Azure Data Lake Storage Gen 2
    - **Performance**: Standard
    - **Redundancy**: Locally-redundant storage (LRS)
1. Wait for deployment to complete, and then go to the deployed resource.

## Create a Microsoft Foundry resource and project (Tasks 2, 3, 4 only)

Skip this if you're only doing Task 1.

1. In a web browser, open the [Microsoft Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes.

    > **Important**: For this lab, you're using the **New** Foundry experience. Make sure the **New Foundry** toggle is on.

1. Select the project name in the upper-left corner, and then select **Create new project**.
1. Give your project a name and expand **Advanced options** to specify the following settings:
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *The same resource group you've been using*
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

1. Select **Create** and wait for your project to be created. This creates a project and its parent Foundry resource.
1. Once created, select the project name at the top of the page, and select **Project details**. On that page, follow the link to the parent resource. **Leave this browser tab open.**

### Connect Content Understanding and deploy models

1. In a new tab, navigate to [Content Understanding Studio](https://contentunderstanding.ai.azure.com/home) at `https://contentunderstanding.ai.azure.com/home` and sign in with your credentials.
1. Select the settings gear icon on the top navigation bar, and select **+ Add resource**.
1. Select your subscription and resource group, then select your Foundry resource from the dropdown.
1. Make sure the **Enable auto-deployment** box is checked, then select **Next** and **Save**.
1. Wait while the required models deploy.
1. Back in the Foundry portal, select **Build** > **Deployments** and note the exact names of your **chat** and **embedding** model deployments.

    > **Important**: Deployment names often have a numeric suffix (for example, `gpt-5.2-######`). Copy them exactly — a wrong deployment name is the single most common cause of failures in Tasks 2-4.

## Gather your credentials

You'll need these values for your `.env`:

| Value | Where to find it |
| --- | --- |
| **Search endpoint** | Azure AI Search resource > **Overview** > **Url** (for example, `https://your-search.search.windows.net`) |
| **Search query key** | Azure AI Search resource > **Settings** > **Keys** > query key |
| **Search admin key** | Azure AI Search resource > **Settings** > **Keys** > primary or secondary admin key |
| **Foundry endpoint** | Foundry parent resource > **Overview** > **Endpoint** |
| **Foundry key** | Foundry parent resource > **Resource Management** > **Keys and Endpoint** |
| **Model deployment names** | Foundry portal > **Build** > **Deployments** |

> **Note**: Azure AI Search creates one default query key for the service. In the Azure portal,
> this default query key can appear with a blank name. That's expected behavior.

## Get the starter code

1. In VS Code, open the Command Palette (**Ctrl+Shift+P**), run **Git: Clone**, and enter:

    ```
    https://github.com/microsoftlearning/mslearn-ai-information-extraction
    ```

1. Open the cloned repo, then **File > Open Folder** and select `mslearn-ai-information-extraction/Labfiles/B-make-extracted-information-searchable/Python`. This single folder holds the code for **every** task in this lab — you use one virtual environment and one `.env` throughout.

1. Right-click **requirements.txt** and choose **Open in Integrated Terminal**. Then create a virtual environment and install packages:

    ```
    python -m venv labenv
    .\labenv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

    > **Note**: This installs the [azure-search-documents](https://learn.microsoft.com/python/api/overview/azure/search-documents-readme), [azure-ai-contentunderstanding](https://pypi.org/project/azure-ai-contentunderstanding/), and [openai](https://pypi.org/project/openai/) packages and their dependencies.

1. Copy **.env.example** to a new file named **.env** in the same folder, then fill in the values for the tasks you plan to do:

    | Key | Needed by |
    | --- | --- |
    | `SEARCH_ENDPOINT` | All tasks |
    | `SEARCH_QUERY_KEY` | Task 1 |
    | `SEARCH_INDEX_NAME` | Task 1 (set it to `fabrikam-index`) |
    | `SEARCH_ADMIN_KEY` | Tasks 2, 3, 4 |
    | `FOUNDRY_ENDPOINT`, `FOUNDRY_KEY` | Tasks 2, 3, 4 |
    | `CHAT_DEPLOYMENT_NAME` | Tasks 3, 4 |
    | `EMBEDDING_DEPLOYMENT_NAME` | Tasks 2, 3, 4 |

1. Save the file (**Ctrl+S**).

    > **Note**: These tasks authenticate with resource keys because that's the quickest path in a lab. For production, Microsoft recommends [role-based access with Microsoft Entra ID](https://learn.microsoft.com/azure/search/search-security-rbac) instead of keys.

## Download the sample documents

Every task uses the same Fabrikam Logistics reference document set.

1. Download [documents.zip](https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/knowledge/documents.zip) from `https://github.com/microsoftlearning/mslearn-ai-information-extraction/raw/main/Labfiles/knowledge/documents.zip` and save it to a local folder.
1. Extract the downloaded *documents.zip* file and view the PDF files it contains.
1. **For Task 1**, you'll upload these to blob storage (the task walks you through it).
1. **For Tasks 2, 3, and 4**, copy the PDF files into the **Labfiles/B-make-extracted-information-searchable/Python/data** folder. Verify they're in place:

    ```
    dir data
    ```

## Check you're ready for a task

Each task needs specific values in your `.env`. Before starting a task, run the preflight check
from the `Python` folder you opened above — it reads your `.env` and tells you what (if anything)
is missing:

```
python ../setup/check_env.py --task 1
```

Swap `1` for the task number you're about to start. That's it — head to any task:

| Task | Page |
| --- | --- |
| Task 1 – Build a knowledge mining index | [B1](B1-build-a-knowledge-mining-index.md) |
| Task 2 – Build a RAG ingestion pipeline | [B2](B2-build-a-rag-ingestion-pipeline.md) |
| Task 3 – Answer questions with a RAG agent | [B3](B3-answer-questions-with-a-rag-agent.md) |
| Task 4 – Keep the index fresh with watch mode | [B4](B4-keep-the-index-fresh-with-watch-mode.md) |
