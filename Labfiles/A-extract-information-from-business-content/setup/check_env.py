"""
Preflight check for the Fabrikam Logistics "Extract information from business
content" lab (Lab A).

Each task in this lab can be completed on its own. Before you start a task,
run this script from the starter `Python` folder (the one you edit during the
lab - NOT `Solution/Python`) to confirm your .env has everything that task needs:

    python ../setup/check_env.py --task 2

It never changes anything - it only reads your .env and tells you what (if
anything) is missing, so you can fix it before running the task.

Tasks and what they need:

    Task 1  (portal) nothing - Task 1 is done entirely in the browser
    Task 2  (code)   FOUNDRY_ENDPOINT, FOUNDRY_KEY, ANALYZER_NAME
    Task 3  (code)   DOC_INTELLIGENCE_ENDPOINT, DOC_INTELLIGENCE_KEY
    Task 4  (code)   DOC_INTELLIGENCE_ENDPOINT, DOC_INTELLIGENCE_KEY,
                     CUSTOM_MODEL_ID
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

# Which .env keys each task needs to run on its own.
TASK_REQUIREMENTS = {
    1: [],
    2: ["FOUNDRY_ENDPOINT", "FOUNDRY_KEY", "ANALYZER_NAME"],
    3: ["DOC_INTELLIGENCE_ENDPOINT", "DOC_INTELLIGENCE_KEY"],
    4: ["DOC_INTELLIGENCE_ENDPOINT", "DOC_INTELLIGENCE_KEY", "CUSTOM_MODEL_ID"],
}

# Every key this lab might read, used when merging real environment variables.
ALL_KEYS = [
    "FOUNDRY_ENDPOINT",
    "FOUNDRY_KEY",
    "ANALYZER_NAME",
    "DOC_INTELLIGENCE_ENDPOINT",
    "DOC_INTELLIGENCE_KEY",
    "CUSTOM_MODEL_ID",
]

# Placeholder text shipped in .env.example - present but not yet filled in.
PLACEHOLDERS = {
    "",
    "your_foundry_endpoint",
    "your_foundry_key",
    "your_document_intelligence_endpoint",
    "your_document_intelligence_key",
    "your_custom_model_id",
    "YOUR_ENDPOINT",
    "YOUR_KEY",
    "your_endpoint",
    "your_key",
    "your_model_id",
}

# How to fix each key, shown only when it's missing.
FIX_HINTS = {
    "FOUNDRY_ENDPOINT": (
        "Copy the Endpoint from the Overview page of your Microsoft Foundry "
        "resource in the Azure portal (or from Resource Management > Keys and "
        "Endpoint), then set FOUNDRY_ENDPOINT in .env."
    ),
    "FOUNDRY_KEY": (
        "Copy one of the keys from Resource Management > Keys and Endpoint on "
        "your Microsoft Foundry resource, then set FOUNDRY_KEY in .env."
    ),
    "ANALYZER_NAME": (
        "Set ANALYZER_NAME to the analyzer id you want to create, for example "
        "fabrikam-contact-analyzer (this ships pre-filled in .env.example)."
    ),
    "DOC_INTELLIGENCE_ENDPOINT": (
        "Copy the Endpoint from Resource Management > Keys and Endpoint on your "
        "Document Intelligence resource, then set DOC_INTELLIGENCE_ENDPOINT."
    ),
    "DOC_INTELLIGENCE_KEY": (
        "Copy one of the keys from Resource Management > Keys and Endpoint on "
        "your Document Intelligence resource, then set DOC_INTELLIGENCE_KEY."
    ),
    "CUSTOM_MODEL_ID": (
        "Task 4 needs the Model ID you entered when you trained your custom "
        "model in Document Intelligence Studio. Set CUSTOM_MODEL_ID in .env."
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

    if not required:
        print("  Task 1 runs entirely in the browser - no .env values needed.")
        print()
        print("You're ready to start Task 1.")
        return 0

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
