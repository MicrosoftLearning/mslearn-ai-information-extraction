---
lab:
    title: 'Task 2 – Build a RAG ingestion pipeline'
    description: 'Create a Content Understanding analyzer in code, then run an ingestion pipeline that extracts document content, chunks it, embeds it with Azure OpenAI, and indexes it into Azure AI Search for vector search.'
    level: 300
    concepts: 'Content Understanding SDK, chunking, embeddings, vector search, Azure AI Search index definition'
    islab: true
    status: 'draft'
---

# Task 2 — Build a RAG ingestion pipeline

*Part of the **Make extracted information searchable** lab. New here? Start with [Getting started](B0-getting-started.md).*

> **Set up (start here):** This task needs an **Azure AI Search** resource, a **Microsoft Foundry**
> resource with an embedding model deployed, the sample documents in the `data` folder, and the
> starter code. It does **not** need anything you built in Task 1 — this task creates its own
> index from scratch. If you haven't already, complete [Getting started](B0-getting-started.md)
> and set `SEARCH_ENDPOINT`, `SEARCH_ADMIN_KEY`, `FOUNDRY_ENDPOINT`, `FOUNDRY_KEY`, and
> `EMBEDDING_DEPLOYMENT_NAME` in `Python/.env`. Then, from the
> `Python` folder, verify you're ready:

```
python ../setup/check_env.py --task 2
```

> **Continuing from a previous task?** If you just finished Task 1, your search resource,
> virtual environment, and `.env` are already set up. You need to add three things: the
> `FOUNDRY_*` values, `EMBEDDING_DEPLOYMENT_NAME`, and `SEARCH_ADMIN_KEY` (Task 1's query key
> can't create an index). You also need the sample PDFs copied into the `Python/data` folder —
> see [Getting started](B0-getting-started.md). The index you built in Task 1 is untouched;
> this task creates a separate one.

---

Task 1's index was built *for* you. It's excellent at "find me documents mentioning New York."
It's useless at "what's our policy on oversized freight?" — because keyword search matches words,
not meaning, and because the wizard chose the chunking and the fields.

In this task you take control. You'll write the pipeline that extracts, chunks, embeds, and
indexes Fabrikam Logistics documents, producing an index that supports **vector search**.

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
<summary>Why chunk documents at all?</summary>
<div class="concept-body" markdown="1">

Two reasons, and both matter.

**Precision.** If you embed a whole 20-page document as one vector, that vector is an average of
everything in it — and matches nothing well. Chunks are small enough that each one is *about*
something.

**Context limits.** At query time you paste retrieved content into the prompt. You can fit three
useful paragraphs; you can't fit three whole documents.

The trade-off is that chunks that are too small lose the context that made them meaningful. The
pipeline here splits at **paragraph boundaries** with a 2000-character ceiling, which keeps each
chunk self-contained. There's no universally right answer — chunking strategy is one of the main
things you tune in a real RAG system.

</div>
</details>

Open the `Python` folder and activate the virtual environment from
[Getting started](B0-getting-started.md) (`.\labenv\Scripts\Activate.ps1`), then continue below.

## Step 1: Create a Content Understanding analyzer

The first stage of the pipeline extracts structured content from each document. You'll create the
analyzer that does it programmatically.

1. In VS Code, open the **create-analyzer.py** file.

1. Review the code, which:
    - Loads environment variables from the `.env` file.
    - Creates a `ContentUnderstandingClient` using the Foundry endpoint and API key.
    - Defines a document analyzer whose field schema captures a generated `Summary` and a list of `KeyTopics`.
    - Creates the analyzer by calling `begin_create_analyzer`.

    Notice that the schema asks for `markdown` content *plus* generated fields. The pipeline uses
    the markdown as the text to chunk and embed, and stores the summary and key topics alongside
    each chunk as extra searchable metadata.

    > **Note**: The `models` block pins `gpt-5.2` for completion and `text-embedding-3-large` for embedding. If your Foundry resource has different deployments, change them to match — check **Build > Deployments** in the Foundry portal.

1. In the VS Code terminal (with the virtual environment activated), run the script:

    ```
    python create-analyzer.py
    ```

1. Wait for the analyzer to be created. The output should confirm that it was created successfully.

## Step 2: Run the ingestion pipeline

Now run the pipeline itself. This single script handles the entire flow — extracting content with
Content Understanding, generating vector embeddings with Azure OpenAI, and indexing into Azure AI
Search. It also tracks which files it has already processed, which is what makes Task 4 possible.

1. In VS Code, open the **ingest-pipeline.py** file.

1. Review the code and notice how it:
    - **Tracks processed files** using a manifest (`processed_files.json`) that records the SHA-256 hash of each file. On each run, the pipeline compares the current hash of every file in the `data/` folder against the manifest, so only new or modified files are processed.
    - **Ensures the search index exists** by calling `ensure_index()`, which creates or updates the Azure AI Search index with the required schema — text fields, a vector field, and HNSW vector search configuration.
    - **Extracts content** from each new file by submitting it to the Content Understanding analyzer via `begin_analyze_binary`, which returns markdown content and the extracted fields.
    - **Chunks the content** by splitting at paragraph boundaries with a 2000-character limit, keeping each chunk self-contained.
    - **Generates embeddings** for each chunk using the Azure OpenAI embedding model, producing a 3072-dimension vector for semantic search.
    - **Indexes the chunks** into Azure AI Search using deterministic document IDs (based on the file name and chunk index), so re-ingesting an updated file replaces its old chunks instead of duplicating them.
    - Supports a `--watch` flag for continuous monitoring (Task 4) and a `--reset` flag to reprocess all files.

    > **Important**: The `EMBEDDING_DIMENSIONS` constant is set to `3072`, which matches `text-embedding-3-large`. If you deployed a different embedding model, change this constant *and* delete the index so it's recreated with the correct vector width — a mismatch here fails at upload time with a confusing error.

1. In the VS Code terminal, run the pipeline:

    ```
    python ingest-pipeline.py
    ```

1. Watch the output as the pipeline processes each document. You'll see timestamped log messages showing each file being extracted, chunks being embedded, and results being indexed. For example:

    ```
    [14:23:01] Verifying search index...
    [14:23:02] Search index 'fabrikam-rag-index' is ready.
    [14:23:02] Detected 5 new/updated file(s).
    [14:23:02]   Processing: route-guide-dubai.pdf
    [14:23:08]     Embedding chunk 1/3...
    [14:23:09]     Embedding chunk 2/3...
    [14:23:09]     Embedding chunk 3/3...
    [14:23:10]     Indexed 3 chunk(s) from route-guide-dubai.pdf.
    ...
    ```

1. After the pipeline finishes, check that it created a **processed_files.json** file in the `Python` folder. This manifest records the hash of each processed file. Run the pipeline again:

    ```
    python ingest-pipeline.py
    ```

    This time the output should say `No new files to ingest - all documents are up to date.`
    Nothing was re-extracted and nothing was re-embedded — which, when embedding calls cost money,
    is the difference between a pipeline and a script.

1. Optionally, confirm the index exists in the Azure portal: open your Azure AI Search resource, and under **Search management** select **Indexes**. You should see **fabrikam-rag-index** alongside the index from Task 1, with a document count matching the number of chunks the pipeline reported.

> ✅ **Checkpoint**: You've built an index you defined yourself, containing chunked content and
> embedding vectors. Nothing can query it meaningfully yet — that's Task 3.

When you're finished, enter `deactivate` to exit the virtual environment.

---

**Next (optional):** [Task 3 — Answer questions with a RAG agent](B3-answer-questions-with-a-rag-agent.md)
