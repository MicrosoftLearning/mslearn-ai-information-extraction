---
lab:
    title: 'Task 3 – Answer questions with a RAG agent'
    description: 'Query your vector index with hybrid keyword and vector search, and ground a chat model in the retrieved content so it answers from your documents and cites its sources.'
    level: 300
    concepts: 'RAG, hybrid search, vector queries, grounding, prompt construction'
    islab: true
    status: 'draft'
---

# Task 3 — Answer questions with a RAG agent

*Part of the **Make extracted information searchable** lab. New here? Start with [Getting started](B0-getting-started.md).*

> **What you need:** a populated **`fabrikam-rag-index`** in Azure AI Search, a **Microsoft
> Foundry** resource with both a **chat** and an **embedding** model deployed, and the starter
> code. This task queries an index — it doesn't create one, so
> **[Task 2](B2-build-a-rag-ingestion-pipeline.md) must have run successfully first**. If you
> haven't done Task 2, do it now: it takes about 30 minutes and there's no other way to populate
> the index. Then set `SEARCH_ENDPOINT`, `SEARCH_ADMIN_KEY`, `FOUNDRY_ENDPOINT`, `FOUNDRY_KEY`,
> `CHAT_DEPLOYMENT_NAME`, and `EMBEDDING_DEPLOYMENT_NAME` in `Python/.env` and verify from the
> `Python` folder:

```
python ../setup/check_env.py --task 3
```

> **Continuing from a previous task?** If you just finished Task 2, everything is in place except
> `CHAT_DEPLOYMENT_NAME` — Task 2 only needed the *embedding* model, and this task also needs a
> chat model to generate answers. Add it to your `.env` and go straight to
> **Ask questions of your documents** below.

---

You have an index full of chunked content and vectors. On its own, that's a very expensive
filing cabinet. In this task you'll add the two things that turn it into an assistant: **hybrid
retrieval** to find the right chunks, and a **grounded prompt** so the model answers from those
chunks instead of from its own memory.

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
<summary>Why hybrid search instead of just vectors?</summary>
<div class="concept-body" markdown="1">

**Keyword search** is exact. Ask for a part number, a person's name, or an unusual acronym and it
finds it — but it can't match "oversized freight" to a document that says "out-of-gauge cargo."

**Vector search** matches meaning. It handles the paraphrase beautifully — and it can miss the
literal string you actually needed, because "close in meaning" isn't "identical."

**Hybrid search** runs both and fuses the rankings, so you get exact matches *and* semantic ones.
For RAG this matters more than almost any other tuning decision, because whatever retrieval
misses, the model can never mention.

In the code, hybrid is what you get by passing **both** `search_text=` and `vector_queries=` to
the same `search()` call.

[Learn more →](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)

</div>
</details>

Open the `Python` folder and activate the virtual environment from
[Getting started](B0-getting-started.md) (`.\labenv\Scripts\Activate.ps1`), then continue below.

## Review the agent

1. In VS Code, open the **rag-agent.py** file.

1. Review the code, which:
    - Creates an Azure AI Search client to retrieve documents from `fabrikam-rag-index`.
    - Creates an Azure OpenAI client pointed at your Foundry resource's `/openai/v1/` endpoint.
    - Implements `retrieve_context()`, which embeds the user's question with the *same* embedding model the pipeline used, then performs hybrid search (keyword + vector) to find the most relevant content chunks.
    - Constructs a system prompt that includes the retrieved context and instructs the model to answer only from it, and to cite source document names.
    - Runs a conversational loop so you can ask multiple questions.

1. Look closely at `retrieve_context()`. Two details are worth noticing:

    ```python
    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        select=["content", "file_name", "summary"],
        top=top_k
    )
    ```

    Passing `search_text` **and** `vector_queries` together is what makes this hybrid rather than
    either one alone. And `select` limits what comes back to the three fields the prompt actually
    uses — retrieving the whole document would waste context budget.

1. Now look at `generate_answer()`. The system message tells the model to use *only* the provided
   context, to say so when the context is insufficient, and to cite sources. Those three
   instructions are what stop a RAG app from confidently inventing an answer.

## Ask questions of your documents

1. In the VS Code terminal, run the agent:

    ```
    python rag-agent.py
    ```

1. When prompted, enter a question about the content you indexed. For example:
    - `What destinations are covered in the reference documents?`
    - `What activities are recommended in Dubai?`
    - `What can you tell me about travel to London?`

1. Review the agent's responses. They should be grounded in the actual content extracted from the documents, and cite the source document names.

1. Now test the guardrail. Ask something the documents definitely don't cover:

    ```
    What is Fabrikam Logistics' parental leave policy?
    ```

    The agent should tell you it can't find relevant information rather than inventing a policy.
    That behavior comes entirely from the system prompt — remove those instructions and the same
    model will happily make something up.

1. When you're satisfied, type `quit` to exit the agent.

> ✅ **Checkpoint**: You've built a working RAG solution: hybrid retrieval over your own vector
> index, feeding a grounded, source-citing chat model. There's one thing still missing — right
> now it only knows about the documents that were in the folder when you ran the pipeline. Task 4
> fixes that.

When you're finished, enter `deactivate` to exit the virtual environment.

---

**Next (optional):** [Task 4 — Keep the index fresh with watch mode](B4-keep-the-index-fresh-with-watch-mode.md)
