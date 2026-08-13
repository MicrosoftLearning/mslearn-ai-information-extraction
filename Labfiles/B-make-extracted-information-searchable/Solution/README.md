# Lab B solution - Make extracted information searchable

Reference notes for the **Make extracted information searchable** lab.

> **This lab has no fill-in-the-blanks.** Its source exercises were
> review-and-run: you read each script, understand what it does, and run it.
> So `../Python/` ships the complete, working implementation and there is no
> separate `Solution/Python/` tree to compare against. (Lab A is the
> write-the-code lab in this family - it has starter TODOs and a matching
> `Solution/Python/`.)

## File tree

```
Labfiles/B-make-extracted-information-searchable/
  Python/                  complete, runnable code for every task
    .env.example           copy to .env and fill in
    requirements.txt
    search-app.py          Task 1 - query the knowledge mining index
    create-analyzer.py     Task 2 - register the ingestion analyzer
    ingest-pipeline.py     Tasks 2 and 4 - extract, embed, index (+ --watch)
    rag-agent.py           Tasks 3 and 4 - answer questions over the index
    data/                  put the sample documents here
  Solution/
    README.md              this file
  setup/
    check_env.py           preflight check: python ../setup/check_env.py --task N
```

## How to run each task

All commands run from `Labfiles/B-make-extracted-information-searchable/Python`
with the virtual environment activated:

```
python -m venv labenv
.\labenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

| Task | Command | Needs in `.env` |
| --- | --- | --- |
| Task 1 | `python search-app.py` | `SEARCH_ENDPOINT`, `SEARCH_QUERY_KEY`, `SEARCH_INDEX_NAME` |
| Task 2 | `python create-analyzer.py` then `python ingest-pipeline.py` | `FOUNDRY_*`, `EMBEDDING_DEPLOYMENT_NAME`, `SEARCH_ENDPOINT`, `SEARCH_ADMIN_KEY` |
| Task 3 | `python rag-agent.py` | adds `CHAT_DEPLOYMENT_NAME` |
| Task 4 | `python ingest-pipeline.py --watch` in one terminal, `python rag-agent.py` in another | same as Task 3 |

Before starting a task, check you have what it needs. Run this from the lab's
`Python/` folder (this lab has only one — there is no `Solution/Python/`):

```
python ../setup/check_env.py --task 2
```

## How the pieces fit together

- **Task 1** uses an index built by the Azure AI Search **Import data** wizard.
  The wizard's AI skills enrich each document with `locations`, `persons`, and
  `keyPhrases`, and `search-app.py` reads those fields back.
- **Tasks 2-4** build a *second*, different index (`fabrikam-rag-index`) in
  code. This one holds chunked content plus a 3072-dimension embedding vector,
  which is what makes hybrid (keyword + vector) retrieval possible.
- The two indexes live side by side in the same search resource. Task 1 needs
  only a query key; Tasks 2-4 create and write an index, so they need an admin
  key.

## Notes

- **Two keys, one resource.** `SEARCH_QUERY_KEY` is read-only and is all Task 1
  needs. `SEARCH_ADMIN_KEY` is required to create and populate an index.
- **Embedding dimensions must match.** `ingest-pipeline.py` sets
  `EMBEDDING_DIMENSIONS = 3072` for `text-embedding-3-large`. If you deploy a
  different embedding model, change that constant and delete the index so it
  gets recreated with the right vector width.
- **Azure OpenAI v1 API.** The scripts use the `OpenAI` client pointed at
  `<your-foundry-endpoint>/openai/v1/`, which is the current GA pattern and
  needs no dated `api-version`. See
  [Azure OpenAI v1 API](https://learn.microsoft.com/azure/foundry/openai/api-version-lifecycle).
- **API keys.** These tasks authenticate with resource keys because that's the
  quickest path in a lab. For production, Microsoft recommends Microsoft Entra
  ID with `DefaultAzureCredential` - see
  [Azure AI Search RBAC](https://learn.microsoft.com/azure/search/search-security-rbac).
- **`processed_files.json`** is created by the pipeline to track which files it
  has already ingested. Delete it (or run `--reset`) to reprocess everything.
