# Lab A solution - Extract information from business content

Completed reference implementations for the **Extract information from business content**
lab. Use these if you get stuck, or to compare against your own code. The starter
files you edit during the lab are in `../Python/`.

## File tree

```
Labfiles/A-extract-information-from-business-content/
  Python/                    STARTER - the files you edit during the lab
    .env.example             copy to .env and fill in
    requirements.txt
    contact-card.json        analyzer schema used by Task 2
    create-analyzer.py       Task 2 - has a TODO
    read-card.py             Task 2 - has a TODO
    document-analysis.py     Task 3 - has TODOs
    test-model.py            Task 4 - complete, no TODOs
  Solution/
    README.md                this file
    Python/                  COMPLETE reference implementation
  setup/
    check_env.py             preflight check: python ../setup/check_env.py --task N
    upload-training-forms.sh Task 4 - uploads labeled training forms to storage
```

Task 1 is completed entirely in the browser, so it has no code.

## How to run each task

All commands run from the **starter** folder,
`Labfiles/A-extract-information-from-business-content/Python`,
with the virtual environment activated:

```
python -m venv labenv
.\labenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

| Task | Command | Needs in `.env` |
| --- | --- | --- |
| Task 1 | *(portal only)* | nothing |
| Task 2 | `python create-analyzer.py` then `python read-card.py biz-card-1.png` | `FOUNDRY_ENDPOINT`, `FOUNDRY_KEY`, `ANALYZER_NAME` |
| Task 3 | `python document-analysis.py` | `DOC_INTELLIGENCE_ENDPOINT`, `DOC_INTELLIGENCE_KEY` |
| Task 4 | `bash ../setup/upload-training-forms.sh`, train in Studio, then `python test-model.py` | `DOC_INTELLIGENCE_ENDPOINT`, `DOC_INTELLIGENCE_KEY`, `CUSTOM_MODEL_ID` |

Before starting a task, check you have what it needs. Run this from the
**starter** `Python/` folder — *not* from `Solution/Python/`, where `../setup/`
would resolve to a `Solution/setup/` folder that doesn't exist:

```
python ../setup/check_env.py --task 2
```

## Notes

- **Sample images aren't duplicated.** `read-card.py` resolves a bare file name
  such as `biz-card-1.png` from `Instructions/Exercises/media/`, so the sample
  contact cards that ship with the repo are used in place. You can also pass a
  full path to any image of your own.
- **Two services, one lab.** Tasks 1 and 2 use Azure Content Understanding
  (LLM-powered analyzers you define with a schema). Tasks 3 and 4 use Azure
  Document Intelligence (deterministic extraction, prebuilt and custom models).
  Both are part of Foundry Tools, and the lab uses one `.env` for both.
- **API keys.** These tasks authenticate with resource keys because that's the
  quickest path in a lab. For production, Microsoft recommends Microsoft Entra
  ID with `DefaultAzureCredential` instead - see
  [Authenticate requests to Foundry Tools](https://learn.microsoft.com/azure/ai-services/authentication).
- **Models.** The Task 2 analyzer schema in `contact-card.json` pins
  `gpt-5.2` for completion and `text-embedding-3-large` for embedding. If your
  Foundry resource doesn't have those deployments, change them to models you do
  have deployed.
