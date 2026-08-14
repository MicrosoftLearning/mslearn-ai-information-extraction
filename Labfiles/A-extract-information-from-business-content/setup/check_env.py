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

# Escape sequences a quoted value decodes. Double quotes decode the full
# C-style set; single quotes decode only the delimiter and the backslash
# itself - everything else stays literal. Measured against python-dotenv, not
# assumed: 'raw \n stays' keeps the backslash, but 'a\'b' yields a'b.
_ESCAPES_DOUBLE = {
    "n": "\n", "r": "\r", "t": "\t",
    "a": "\a", "b": "\b", "f": "\f", "v": "\v",
    "\\": "\\", '"': '"', "'": "'",
}
_ESCAPES_SINGLE = {"\\": "\\", "'": "'"}

# Kept for callers/tests that reference the original name.
_ESCAPES = _ESCAPES_DOUBLE


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


def _keys_written_in_file(path):
    """Return the key names that physically appear as assignments in the file.

    Used to tell a key that was never written from one that IS written but got
    eaten by a malformation, so the check can report the difference honestly.
    """
    written = set()
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            for raw_line in handle:
                line = raw_line.strip().lstrip("\ufeff")
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].lstrip()
                if "=" not in line:
                    continue
                written.add(line.partition("=")[0].strip())
    except OSError:
        return written
    return written


def _unterminated_hint(line_number, eaten):
    keys = ", ".join(eaten)
    return (
        f"Line {line_number} of your .env opens a quote that is never closed. "
        "python-dotenv keeps looking for the closing quote on the lines that "
        f"follow, so {keys} is in your file but never reaches the app. Close "
        f"the quote on line {line_number} (or remove both quotes; these "
        "settings don't need them)."
    )


def _find_closing_line(lines, start, quote, honor_escapes):
    """Index of the first line at/after `start` containing an unescaped quote.

    Returns None if there isn't one. Note that while recovering from an
    unterminated value python-dotenv honours backslash escapes for BOTH quote
    characters, even though single-quoted values are otherwise literal.
    """
    index = start
    while index < len(lines):
        line = lines[index]
        position = 0
        while position < len(line):
            char = line[position]
            if honor_escapes and char == "\\" and position + 1 < len(line):
                position += 2
                continue
            if char == quote:
                return index
            position += 1
        index += 1
    return None


def _parse_env_file(path):
    """Minimal .env reader used when python-dotenv isn't installed.

    Defined at module level (rather than inside the ImportError branch below)
    so it can be imported and tested directly even when python-dotenv is
    available. Its output matches dotenv.dotenv_values, including the awkward
    cases, because this check has to agree with what the app will actually
    see at runtime - the app reads the same file with python-dotenv.

    INTENTIONAL DIVERGENCE - do not "fix" this to match dotenv:
        This reads with utf-8-sig, so a UTF-8 BOM is stripped and the first
        key parses under its real name. python-dotenv does NOT do that - it
        returns the first key as "\\ufeffNAME". The difference is deliberate:
        it lets the per-key report stay readable, and the BOM is caught
        separately by _has_utf8_bom(), which forces the check to fail with an
        explanation. Removing the strip to gain byte-parity with dotenv would
        make the per-key output confusing without adding any safety, because
        the safety lives in the detector, not in the parser. A parser-level
        differential test cannot see this - assert it at check level instead.
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
            escapes = _ESCAPES_DOUBLE if quote == '"' else _ESCAPES_SINGLE
            chars = []
            index = 1
            closed = False
            while index < len(value):
                char = value[index]
                # Both quote styles honour a backslash escape, but they decode
                # different sets: a \" does not end a double-quoted value and
                # \n becomes a newline, while a single-quoted value decodes
                # only \' and \\ and leaves every other escape literal.
                # Decoding happens in this single pass so an escaped backslash
                # isn't re-processed.
                if char == "\\" and index + 1 < len(value):
                    nxt = value[index + 1]
                    chars.append(escapes.get(nxt, "\\" + nxt))
                    index += 2
                    continue
                if char == quote:
                    closed = True
                    break
                chars.append(char)
                index += 1

            if not closed:
                # python-dotenv treats this as the start of a multi-line
                # value and scans ahead for the matching quote. It is
                # escape-aware while doing so, but if no escaped-quote-aware
                # close exists anywhere it retries treating every quote
                # character literally - so an escaped quote can still end the
                # recovery when it's the only candidate. Neither pass alone
                # reproduces both behaviours.
                lookahead = _find_closing_line(lines, position, quote, True)
                if lookahead is None:
                    lookahead = _find_closing_line(lines, position, quote, False)
                if lookahead is not None:
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


def _placeholder_values():
    """PLACEHOLDERS plus any placeholder-looking value in the shipped
    .env.example, so the list can't silently rot when the example is edited.

    Only values that *look* like placeholders are absorbed. .env.example also
    ships real pre-filled values - an analyzer id, an index name, model names -
    that a learner is meant to keep. Absorbing those would report a correctly
    configured .env as MISSING, so the behavioural assertion to test is
    "an unedited copy of .env.example is not ready", never "every value in
    .env.example is a placeholder".
    """
    values = set(PLACEHOLDERS)
    example = Path(__file__).resolve().parent.parent / "Python" / ".env.example"
    try:
        with open(example, "r", encoding="utf-8-sig") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                value = line.partition("=")[2].strip()
                lowered = value.lower()
                if lowered.startswith("your_") or lowered.startswith("your-"):
                    values.add(value)
    except OSError:
        pass
    return values


_PLACEHOLDER_CACHE = None


def _all_placeholders():
    """Cached placeholder set (PLACEHOLDERS unioned with the example file)."""
    global _PLACEHOLDER_CACHE
    if _PLACEHOLDER_CACHE is None:
        _PLACEHOLDER_CACHE = _placeholder_values()
    return _PLACEHOLDER_CACHE


def is_set(values, key):
    """A key counts as set if it's present and not a leftover placeholder."""
    value = (values.get(key) or "").strip()
    return bool(value) and value not in _all_placeholders()


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
    # A key that's written in the file but absent from the parsed result was
    # eaten by the malformation - that's the difference between "you never set
    # this" and "you set this and it isn't reaching the app".
    written = _keys_written_in_file(env_path) if env_path.exists() else set()
    eaten = [key for key in required if key in written and key not in values]

    for key in required:
        mark = "OK " if is_set(values, key) else "MISSING"
        print(f"  [{mark}] {key}")

    # A BOM always corrupts the first setting, so it's always fatal. An
    # unterminated quote is only fatal when it actually ate something this
    # task needs - a stray quote below the keys in use changes nothing, and
    # failing the check for it would be its own false alarm.
    if has_bom:
        print("  [PROBLEM] .env starts with a UTF-8 BOM")
    if bad_quote_line and eaten:
        print(f"  [PROBLEM] .env line {bad_quote_line}: unterminated quote")
    elif bad_quote_line:
        print(f"  [NOTE] .env line {bad_quote_line}: unterminated quote "
              f"(nothing this task needs is affected)")

    if not missing and not has_bom:
        print()
        print(f"You're ready to start Task {args.task}.")
        return 0

    print()
    print("Fix the following before starting this task:")
    if has_bom:
        print(f"\n  .env encoding\n    {BOM_HINT}")
    if bad_quote_line and eaten:
        print(f"\n  .env line {bad_quote_line}\n"
              f"    {_unterminated_hint(bad_quote_line, eaten)}")
    for key in missing:
        if key in eaten:
            continue  # already explained by the unterminated-quote note above
        print(f"\n  {key}\n    {FIX_HINTS.get(key, 'Add this key to your .env file.')}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
