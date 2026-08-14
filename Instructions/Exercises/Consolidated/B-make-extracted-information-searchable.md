---
lab:
    title: 'Make extracted information searchable'
    description: 'Turn the Fabrikam Logistics document library into something people can actually query: build an AI-enriched search index in the portal, then a code-driven RAG pipeline that extracts, embeds, indexes, and answers questions - and keeps itself up to date. A modular lab you can complete end to end or one task at a time.'
    level: 300
    concepts: 'Azure AI Search, AI enrichment, indexers, vector search, RAG, continuous ingestion'
    duration: 40
    islab: true
    status: 'draft'
---

# Make extracted information searchable

**Difficulty** ▰▰▰▱▱ **L300**  (filled bars out of 5; **L100** beginner → **L500** expert)

Extracting information is only half the job. A folder full of perfectly extracted fields that
nobody can query is still a folder nobody uses. In this lab you'll build the retrieval layer for
**Fabrikam Logistics** — first with a no-code indexer, then with a pipeline you write yourself
that keeps answering questions as new documents arrive.

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
<summary>What is RAG, and why does it need a search index?</summary>
<div class="concept-body" markdown="1">

**Retrieval-augmented generation (RAG)** means: before you ask a language model a question, go
and fetch the most relevant bits of your own content, and paste them into the prompt as context.
The model then answers from *your* data instead of from whatever it happened to memorize.

That "go and fetch" step is a search problem, which is why RAG solutions are built on a search
index. And it's why the quality of your index sets the ceiling on the quality of your answers —
if retrieval returns the wrong three chunks, no model can rescue the answer.

[Learn more →](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)

</div>
</details>

**Your scenario:** you work at **Fabrikam Logistics**, a freight-forwarding company. The company
has years of reference documents — destination and route guides, operating notes, service
information — sitting in a document library. Staff know the answers are in there somewhere, and
that's exactly the problem. Your job is to make that library searchable, then answerable, then
self-maintaining.

You'll start with the **Core** task, which gets you a working AI-enriched search index and a
client app that queries it. From there, a set of **Optional** tasks builds a full RAG pipeline on
top.

> **Note**: Some of the technologies used in this exercise are in preview or in active
> development. You may experience some unexpected behavior, warnings, or errors.

## What you'll learn

By completing the **Core** task of this exercise, you'll be able to:

- **Build an AI-enriched search index** with Azure AI Search — attach skills that pull key
  phrases, people, and locations out of your documents during indexing, then query the result
  from Search explorer and from a Python client app.

The **Optional** tasks let you additionally:

- **Build an ingestion pipeline in code** that extracts content with Content Understanding,
  chunks it, embeds it with Azure OpenAI, and indexes it for vector search.
- **Answer questions with a RAG agent** that combines keyword and vector retrieval and grounds a
  chat model in what it finds.
- **Keep the index fresh automatically**, running the pipeline in watch mode so new documents
  become answerable without anyone reprocessing anything.

## How this lab is organized

This lab is **modular**. Each task is written to be completed **on its own, starting fresh** —
so you can pick a single task and do just that one. Every task also shares one starter folder,
one virtual environment, and one `.env`, so if you'd rather work straight through, you can.

1. **Start with [Getting started](B0-getting-started.md)** — create your Azure AI Search resource
   (and, for the optional tasks, a Microsoft Foundry resource and storage account), get the
   starter code and sample documents, and set up your `.env`. Every task begins here; if you're
   doing the whole lab in one sitting, you only need to do this once.
2. **Do any task.** Each task lists the setup it needs so you can start it independently. If
   you're moving straight from the previous task, a short *"Continuing from a previous task?"*
   note at the top lets you skip the repeated setup and keep going.

## Lab at a glance

Complete the **Core** task first (about **40 minutes**) — it ends with a queryable, AI-enriched
index. Then expand any **Optional** tasks that interest you. The full lab, including all optional
tasks, takes about **2 hours 10 minutes**.

| Section | Task | Difficulty | Time |
| --- | --- | --- | --- |
| **Core** | [Task 1 – Build a knowledge mining index](B1-build-a-knowledge-mining-index.md) | ▰▰▱▱▱ L200 | ~40 min |
| *Optional* | [Task 2 – Build a RAG ingestion pipeline](B2-build-a-rag-ingestion-pipeline.md) | ▰▰▰▱▱ L300 | ~30 min |
| *Optional* | [Task 3 – Answer questions with a RAG agent](B3-answer-questions-with-a-rag-agent.md) | ▰▰▰▱▱ L300 | ~20 min |
| *Optional* | [Task 4 – Keep the index fresh with watch mode](B4-keep-the-index-fresh-with-watch-mode.md) | ▰▰▰▰▱ L400 | ~40 min |

**Choosing your path** — pick the tasks that fit the time you have:

- **Core only (~40 min):** do Task 1. You'll have a working AI-enriched index and a client app.
- **A working RAG solution (~1h 30m):** add **Task 2** and **Task 3** — index your own content in
  code, then ask questions of it.
- **Everything (~2h 10m):** add **Task 4**, which turns the pipeline into something that keeps
  running.

> **Note**: Tasks 2, 3, and 4 build on each other and are best done in order. Each one still
> states exactly what it needs, so you can start at Task 3 or 4 if you've already got an index
> populated.

## Two ways to build an index

The lab deliberately shows both, because real solutions choose between them:

- In **Task 1**, Azure AI Search does everything. You point the **Import data** wizard at a blob
  container, tick some AI skills, and it crawls, enriches, and indexes on a schedule. No code.
  You get an index full of extracted key phrases, people, and locations.
- In **Tasks 2–4**, *you* do everything. Your code extracts with Content Understanding, chunks
  the content, generates embeddings, and pushes documents into an index you defined. It's more
  work — and it's the only way to control chunking, add vector search, and decide exactly when
  and what gets reprocessed.

The first is how you get value in an afternoon. The second is how you build a RAG system you can
tune.

## Summary

Across this lab you:

- Built an **AI-enriched Azure AI Search index** with an indexer and skills, and queried it from
  Search explorer and a Python client.
- (Optionally) built an **ingestion pipeline** that extracts, chunks, embeds, and indexes
  documents in code.
- (Optionally) answered questions with a **RAG agent** using hybrid keyword + vector retrieval.
- (Optionally) ran the pipeline in **watch mode** so new documents become answerable
  automatically.

Together these take you from "the answer is in a PDF somewhere" to "ask a question, get a
grounded answer, including from the document that arrived five minutes ago."

If you haven't already extracted structured fields from your content, see
[Extract information from business content](A-extract-information-from-business-content.md).

## Clean up

If you're finished, delete the resources you created to avoid unnecessary Azure costs.

1. In the [Azure portal](https://portal.azure.com), navigate to the resource group that contains your Azure AI Search, storage, and Foundry resources.
1. On the toolbar, select **Delete resource group**, enter the resource group name, and confirm.
