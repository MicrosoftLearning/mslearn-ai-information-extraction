---
lab:
    title: 'Task 4 – Keep the index fresh with watch mode'
    description: 'Run the ingestion pipeline in watch mode so it detects and ingests new documents automatically, then confirm the RAG agent can answer from content that arrived after you started asking questions.'
    level: 400
    concepts: 'continuous ingestion, change detection, manifests, near real-time RAG'
    islab: true
    status: 'draft'
---

# Task 4 — Keep the index fresh with watch mode

*Part of the **Make extracted information searchable** lab. New here? Start with [Getting started](B0-getting-started.md).*

> **What you need:** everything Task 3 needed — a populated **`fabrikam-rag-index`**, a
> **Microsoft Foundry** resource with **chat** and **embedding** models deployed, and the starter
> code — plus the ability to run **two terminals side by side**. This task extends the pipeline
> from [Task 2](B2-build-a-rag-ingestion-pipeline.md) and re-uses the agent from
> [Task 3](B3-answer-questions-with-a-rag-agent.md), so both should have run successfully first.
> Verify from the `Python` folder:

```
python ../setup/check_env.py --task 4
```

> **Continuing from a previous task?** If you just finished Task 3, you need nothing new — same
> resources, same `.env`, same virtual environment. Go straight to **Start the pipeline in watch
> mode** below.

---

Everything you've built so far runs once. Real document libraries don't hold still: an updated
route guide lands on Monday, and if the index doesn't know about it, your agent confidently
answers from last month's version.

In this task you'll run the pipeline in **watch mode**, add a document while it's running, and
watch it become answerable without anyone reprocessing anything.

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
<summary>Why hash the files instead of checking the timestamp?</summary>
<div class="concept-body" markdown="1">

The manifest stores a **SHA-256 hash** of every file's contents, not its modified date.

Timestamps lie constantly. Copying a file, syncing a folder, or opening and saving it without
edits all bump the modified date — and each false positive means re-extracting and re-embedding a
document you already have, which costs real money at volume. Meanwhile some sync tools *preserve*
timestamps, so a genuinely changed file can slip through.

A content hash asks the only question that matters: are these bytes different from the bytes I
processed last time?

It pairs with **deterministic document IDs** (`hash(file_name::chunk_index)`). Because chunk 2 of
a given file always gets the same ID, re-ingesting an updated document *overwrites* its old
chunks rather than leaving stale duplicates in the index next to the new ones.

</div>
</details>

## Start the pipeline in watch mode

1. In VS Code, open a terminal in the `Python` folder (the folder you opened in [Getting started](B0-getting-started.md)) and activate the virtual environment:

    ```
    .\labenv\Scripts\Activate.ps1
    ```

1. Start the pipeline in watch mode:

    ```
    python ingest-pipeline.py --watch
    ```

    The pipeline begins polling the `data/` folder every 30 seconds. You should see output like:

    ```
    [14:30:00] Watching 'data/' for new documents (press Ctrl+C to stop)...

    [14:30:01] No new files. Waiting...
    ```

    **Leave this terminal running.**

## Add a new document

1. In VS Code, open a **second terminal** (select **Terminal** > **New Terminal**) so you can work while the pipeline keeps watching.

1. Switch to the VS Code Explorer pane and right-click the **data** folder under **Labfiles/B-make-extracted-information-searchable/Python**. Select **New File** and name it **tokyo-route-guide.txt**.

1. Add the following content to the new file and save it:

    ```text
    Tokyo Route Guide

    Tokyo, the capital of Japan, is one of the most dynamic cities in the world,
    blending centuries-old tradition with cutting-edge technology and innovation.
    It is also one of the busiest freight and passenger hubs in Asia.

    Key Locations:
    - Senso-ji Temple: Tokyo's oldest temple, located in Asakusa. The approach
      through Nakamise-dori shopping street is iconic.
    - Shibuya Crossing: The world's busiest pedestrian crossing is a symbol of
      Tokyo's energy and pace.
    - Meiji Shrine: A serene Shinto shrine set in a lush forest in the heart of
      the city, dedicated to Emperor Meiji.
    - Tokyo Skytree: At 634 meters, this broadcasting tower offers panoramic views
      of the entire metropolitan area.
    - Tsukiji Outer Market: While the inner wholesale market has moved to Toyosu,
      the outer market still offers incredible fresh seafood and street food.

    Districts to Know:
    - Shinjuku: A vibrant district known for its nightlife, shopping, and the
      Shinjuku Gyoen National Garden.
    - Akihabara: The hub of anime, manga, and electronics retail.
    - Harajuku: Known for youth fashion, Takeshita Street, and trendy cafes.
    - Ginza: Tokyo's upscale shopping and dining district.

    Getting Around:
    Tokyo has one of the world's most efficient public transportation systems.
    The Tokyo Metro and JR lines connect every corner of the city. A Suica or
    Pasmo card makes travel seamless. For longer journeys, the Japan Rail Pass
    offers unlimited travel on JR lines.

    Best Time to Travel:
    Spring (March-May) for cherry blossoms and autumn (October-November) for
    fall foliage are the most popular seasons. Summers can be hot and humid,
    while winters are mild compared to northern Japan.
    ```

1. Switch back to the terminal running the pipeline in watch mode. Within 30 seconds, you should see the pipeline detect and process the new file:

    ```
    [14:31:00] Detected 1 new/updated file(s).
    [14:31:00]   Processing: tokyo-route-guide.txt
    [14:31:05]     Embedding chunk 1/1...
    [14:31:06]     Indexed 1 chunk(s) from tokyo-route-guide.txt.
    [14:31:06] Ingestion complete - 1 file(s), 1 chunk(s) indexed.
    ```

    Nobody told it the file existed. It compared hashes, found one it hadn't seen, and ran the
    full extract-chunk-embed-index flow on just that file.

## Query the newly ingested content

1. Switch to your **second terminal**, activate the virtual environment if you haven't, and run the RAG agent:

    ```
    .\labenv\Scripts\Activate.ps1
    python rag-agent.py
    ```

1. Ask a question about the newly added document:
    - `What can you tell me about Tokyo?`
    - `What are the key locations in Tokyo?`
    - `How do I get around in Tokyo?`

1. The agent should now return answers grounded in the Tokyo route guide — content that didn't exist during your first query session in Task 3. This is the whole point of the pipeline: new knowledge becomes answerable without any manual reprocessing.

1. Optionally, test change detection too. Switch to VS Code, add a line to **tokyo-route-guide.txt**, and save it. Within 30 seconds the watch terminal should re-process the file — and because the chunk IDs are deterministic, it replaces the old chunks rather than adding duplicates.

1. Type `quit` to exit the agent, then switch to the watch-mode terminal and press **Ctrl+C** to stop the pipeline.

> ✅ **Checkpoint**: You've built a continuous ingestion pipeline that keeps a RAG index current
> as documents arrive, and confirmed end to end that a document added minutes ago is answerable
> now. That's the difference between a RAG demo and a RAG system.

When you're finished, enter `deactivate` in both terminals to exit the virtual environment.

## More information

- [Tutorial: Build a RAG solution with Content Understanding](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/build-rag-solution)
- [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
- [Azure Content Understanding Python SDK](https://pypi.org/project/azure-ai-contentunderstanding/)

---

**Next:** You've completed the optional tasks. Head back to the [lab overview](B-make-extracted-information-searchable.md) for a summary and clean-up steps.
