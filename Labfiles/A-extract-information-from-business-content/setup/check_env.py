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

_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", '"': '"', "'": "'"}


def _has_utf8_bom(path):
    """True if the file starts with a UTF-8 BOM.

    Checked on the raw bytes, so the result is the same whether python-dotenv
    or the fallback parser below did the reading.
    """
    try:
        with open(path, "rb") as handle:
            return handle.read(3) == b"\xef\xbb\xbf"
    except OSError:
        return False


BOM_HINT = (
    "Your .env was saved as 'UTF-8 with BOM' (Notepad does this by default). "
    "The BOM becomes part of the first setting's name, so the app reads that "
    "setting as empty even though the file looks correct. Re-save as plain "
    "UTF-8: in VS Code, click the encoding in the status bar, choose 'Save "
    "with Encoding', then 'UTF-8' (not 'UTF-8 with BOM')."
)


def _find_unterminated_quote(path):
    """Return the 1-based line number of the first unterminated quoted value.

    Read from the raw file, so the answer is the same whether python-dotenv or
    the fallback parser did the reading. An unterminated quote is why a set of
    otherwise-correct settings can vanish: python-dotenv keeps scanning for the
    closing quote and swallows the lines it crosses, so the app never sees them.
    """
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            for number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].lstrip()
                if "=" not in line:
                    continue
                _, _, value = line.partition("=")
                value = value.strip()
                if value[:1] not in ("'", '"'):
                    continue
                quote = value[0]
                index = 1
                closed = False
                while index < len(value):
                    char = value[index]
                    if quote == '"' and char == "\\" and index + 1 < len(value):
                        index += 2
                        continue
                    if char == quote:
                        closed = True
                        break
                    index += 1
                if not closed:
                    return number
    except OSError:
        return None
    return None


def _unterminated_hint(line_number):
    return (
        f"Line {line_number} of your .env opens a quote that is never closed. "
        "python-dotenv keeps looking for the closing quote on the lines that "
        "follow, so that setting - and potentially every setting after it - is "
        f"read as one long value and never reaches the app. Close the quote on "
        f"line {line_number} (or remove both quotes; these settings don't need "
        "them)."
    )


def _parse_env_file(path):
    """Minimal .env reader used when python-dotenv isn't installed.

    Defined at module level (rather than inside the ImportError branch below)
    so it can be imported and tested directly even when python-dotenv is
    available. Its output matches dotenv.dotenv_values, including the awkward
    cases, because this check has to agree with what the app will actually
    see at runtime - the app reads the same file with python-dotenv.
    """
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            lines = handle.readlines()
    except OSError:
        return {}

    values = {}
    position = 0
    while position < len(lines):
        line = lines[position].strip()
        position += 1

        if not line or line.startswith("#"):
            continue
        # Strip 'export ' before splitting, so the key is the real name and
        # not 'export KEY'.
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
            quote = value[0]
            chars = []
            index = 1
            closed = False
            while index < len(value):
                char = value[index]
                # Only double quotes process backslash escapes, so a \" does
                # not end the value and \n becomes a real newline. Decoding
                # happens in this single pass so an escaped backslash isn't
                # re-processed.
                if quote == '"' and char == "\\" and index + 1 < len(value):
                    chars.append(_ESCAPES.get(value[index + 1], "\\" + value[index + 1]))
                    index += 2
                    continue
                if char == quote:
                    closed = True
                    break
                chars.append(char)
                index += 1

            if not closed:
                # python-dotenv treats this as the start of a multi-line
                # value and scans ahead for the matching quote. If it finds
                # one, every line up to it is swallowed and the keys on those
                # lines never reach the app; if it doesn't, only this line is
                # dropped. Either way the malformed entry itself is discarded.
                lookahead = position
                while lookahead < len(lines) and quote not in lines[lookahead]:
                    lookahead += 1
                if lookahead < len(lines):
                    position = lookahead + 1
                continue

            value = "".join(chars)
        else:
            value = value.split(" #", 1)[0].strip()

        if key:
            values[key] = value

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
        for key, value in dotenv_values(env_path).items():
            if value is None:
                continue
            # A UTF-8 BOM ends up glued to the first key's name. Strip it here
            # so the per-key report is still readable; the BOM itself is
            # reported separately as a problem, never silently accepted.
            values[key.lstrip("\ufeff")] = value
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
    has_bom = env_path.exists() and _has_utf8_bom(env_path)
    bad_quote_line = _find_unterminated_quote(env_path) if env_path.exists() else None

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

    # These two break the app even when the keys look right, so neither is
    # ever treated as "ready" - the app would fail after this said OK. They're
    # also usually the root cause of the MISSING keys listed above.
    if has_bom:
        print("  [PROBLEM] .env starts with a UTF-8 BOM")
    if bad_quote_line:
        print(f"  [PROBLEM] .env line {bad_quote_line}: unterminated quote")

    if not missing and not has_bom and not bad_quote_line:
        print()
        print(f"You're ready to start Task {args.task}.")
        return 0

    print()
    print("Fix the following before starting this task:")
    if has_bom:
        print(f"\n  .env encoding\n    {BOM_HINT}")
    if bad_quote_line:
        print(f"\n  .env line {bad_quote_line}\n    {_unterminated_hint(bad_quote_line)}")
    for key in missing:
        print(f"\n  {key}\n    {FIX_HINTS.get(key, 'Add this key to your .env file.')}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
