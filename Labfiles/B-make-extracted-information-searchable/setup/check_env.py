"""
Preflight check for the Fabrikam Logistics "Make extracted information
searchable" lab (Lab B).

Each task in this lab can be completed on its own. Before you start a task,
run this script from the lab's `Python` folder to confirm your .env file has
everything that task needs:

    python ../setup/check_env.py --task 1

It never changes anything - it only reads your .env and tells you what (if
anything) is missing, so you can fix it before running the task.

Tasks and what they need:

    Task 1  (code)   SEARCH_ENDPOINT, SEARCH_QUERY_KEY, SEARCH_INDEX_NAME
    Task 2  (code)   FOUNDRY_ENDPOINT, FOUNDRY_KEY, EMBEDDING_DEPLOYMENT_NAME,
                     SEARCH_ENDPOINT, SEARCH_ADMIN_KEY
    Task 3  (code)   FOUNDRY_ENDPOINT, FOUNDRY_KEY, CHAT_DEPLOYMENT_NAME,
                     EMBEDDING_DEPLOYMENT_NAME, SEARCH_ENDPOINT, SEARCH_ADMIN_KEY
    Task 4  (code)   Same as Task 3 (watch mode ingests, then you re-query)
"""

import argparse
import os
from pathlib import Path

def _parse_env_file(path):
    """Minimal .env reader used when python-dotenv isn't installed.

    Defined at module level (rather than inside the ImportError branch below)
    so it can be imported and tested directly even when python-dotenv is
    available. Its output matches dotenv.dotenv_values for the .env syntax
    these labs use.
    """
    values = {}
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                # Strip 'export ' before splitting, so the key is the real
                # name and not 'export KEY'.
                if line.startswith("export "):
                    line = line[len("export "):].lstrip()
                if "=" not in line:
                    # python-dotenv records a bare key with no '=' as None.
                    values[line] = None
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if value[:1] in ("'", '"'):
                    # Quoted: take what's inside the quotes, so a '#' inside
                    # is kept and a trailing comment outside is dropped.
                    quote = value[0]
                    end = value.find(quote, 1)
                    if end == -1:
                        # Unterminated quote; python-dotenv drops the key.
                        continue
                    value = value[1:end]
                else:
                    value = value.split(" #", 1)[0].strip()
                if key:
                    values[key] = value
    except OSError:
        return {}
    return values


try:
    # python-dotenv is installed into the lab's virtual environment, but this
    # preflight check is meant to run BEFORE 'pip install -r requirements.txt'
    # (and Task 1 is portal-only, so that install may never happen), so fall
    # back to the stdlib parser above when it isn't importable.
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = _parse_env_file

RAG_KEYS = [
    "FOUNDRY_ENDPOINT",
    "FOUNDRY_KEY",
    "CHAT_DEPLOYMENT_NAME",
    "EMBEDDING_DEPLOYMENT_NAME",
    "SEARCH_ENDPOINT",
    "SEARCH_ADMIN_KEY",
]

# Which .env keys each task needs to run on its own.
TASK_REQUIREMENTS = {
    1: ["SEARCH_ENDPOINT", "SEARCH_QUERY_KEY", "SEARCH_INDEX_NAME"],
    2: [
        "FOUNDRY_ENDPOINT",
        "FOUNDRY_KEY",
        "EMBEDDING_DEPLOYMENT_NAME",
        "SEARCH_ENDPOINT",
        "SEARCH_ADMIN_KEY",
    ],
    3: RAG_KEYS,
    4: RAG_KEYS,
}

# Every key this lab might read, used when merging real environment variables.
ALL_KEYS = [
    "SEARCH_ENDPOINT",
    "SEARCH_QUERY_KEY",
    "SEARCH_ADMIN_KEY",
    "SEARCH_INDEX_NAME",
    "FOUNDRY_ENDPOINT",
    "FOUNDRY_KEY",
    "CHAT_DEPLOYMENT_NAME",
    "EMBEDDING_DEPLOYMENT_NAME",
]

# Placeholder text shipped in .env.example - present but not yet filled in.
PLACEHOLDERS = {
    "",
    "your_search_endpoint",
    "your_query_key",
    "your_search_admin_key",
    "your_index_name",
    "your_foundry_endpoint",
    "your_foundry_key",
    "YOUR_ENDPOINT",
    "YOUR_KEY",
}

# How to fix each key, shown only when it's missing.
FIX_HINTS = {
    "SEARCH_ENDPOINT": (
        "Copy the Url from the Overview page of your Azure AI Search resource "
        "in the Azure portal (for example https://your-search.search.windows.net), "
        "then set SEARCH_ENDPOINT in .env."
    ),
    "SEARCH_QUERY_KEY": (
        "In the Azure portal, open your Azure AI Search resource and go to "
        "Settings > Keys. Copy the query key and set SEARCH_QUERY_KEY in .env. "
        "The default query key can appear with a blank name - that's expected."
    ),
    "SEARCH_ADMIN_KEY": (
        "Tasks 2-4 create and write to an index, so they need an admin key. "
        "In the Azure portal, open your Azure AI Search resource, go to "
        "Settings > Keys, and copy a primary or secondary admin key."
    ),
    "SEARCH_INDEX_NAME": (
        "Set SEARCH_INDEX_NAME to the index the Import data wizard created, "
        "for example fabrikam-index."
    ),
    "FOUNDRY_ENDPOINT": (
        "Copy the Endpoint from the Overview page of your Microsoft Foundry "
        "resource in the Azure portal, then set FOUNDRY_ENDPOINT in .env."
    ),
    "FOUNDRY_KEY": (
        "Copy one of the keys from Resource Management > Keys and Endpoint on "
        "your Microsoft Foundry resource, then set FOUNDRY_KEY in .env."
    ),
    "CHAT_DEPLOYMENT_NAME": (
        "Set CHAT_DEPLOYMENT_NAME to the name of your deployed chat model. In "
        "the Foundry portal, select Build > Deployments to see it. Deployment "
        "names often have a numeric suffix, so copy it exactly."
    ),
    "EMBEDDING_DEPLOYMENT_NAME": (
        "Set EMBEDDING_DEPLOYMENT_NAME to the name of your deployed embedding "
        "model (text-embedding-3-large). Check Build > Deployments in the "
        "Foundry portal and copy the name exactly, including any suffix."
    ),
}


def find_env_file():
    """Return the .env next to the lab's Python folder, wherever this is run from."""
    here = Path(__file__).resolve().parent
    candidates = [
        Path.cwd() / ".env",
        here.parent / "Python" / ".env",
        here.parent / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Default to the Python-folder location even if it doesn't exist yet.
    return here.parent / "Python" / ".env"


def load_values(env_path):
    """Merge real environment variables over .env file values (env wins)."""
    values = {}
    if env_path.exists():
        values.update({k: v for k, v in dotenv_values(env_path).items() if v is not None})
    for key in ALL_KEYS:
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values


def is_set(values, key):
    """A key counts as set if it's present and not a leftover placeholder."""
    value = (values.get(key) or "").strip()
    return bool(value) and value not in PLACEHOLDERS


def main():
    parser = argparse.ArgumentParser(
        description="Check that your .env has what a given lab task needs."
    )
    parser.add_argument(
        "--task",
        type=int,
        choices=sorted(TASK_REQUIREMENTS),
        required=True,
        help="Which task you're about to start (1-4).",
    )
    args = parser.parse_args()

    env_path = find_env_file()
    values = load_values(env_path)
    required = TASK_REQUIREMENTS[args.task]

    print(f"Checking readiness for Task {args.task}")
    print(f"Reading: {env_path}{'' if env_path.exists() else '  (not found yet)'}")
    print()

    missing = [key for key in required if not is_set(values, key)]

    for key in required:
        mark = "OK " if is_set(values, key) else "MISSING"
        print(f"  [{mark}] {key}")

    if not missing:
        print()
        print(f"You're ready to start Task {args.task}.")
        return 0

    print()
    print("Set the following before starting this task:")
    for key in missing:
        print(f"\n  {key}\n    {FIX_HINTS.get(key, 'Add this key to your .env file.')}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
