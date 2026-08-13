"""Task 2 - analyze a Fabrikam Logistics contact card with a Content Understanding analyzer.

Usage:
    python read-card.py                 Analyze the default card (biz-card-1.png)
    python read-card.py biz-card-2.png  Analyze another sample card
    python read-card.py C:\\path\\card.png  Analyze a card by full path

Sample cards ship with the repo in Instructions/Exercises/media, so a bare file
name is resolved from there. No sample images are duplicated into this folder.
"""

from dotenv import load_dotenv
import os
import sys
import json
from pathlib import Path
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

# Sample cards live with the shared lab media, four levels up from this file:
# Labfiles/A-extract-information-from-business-content/Python/read-card.py
MEDIA_DIR = Path(__file__).resolve().parents[3] / "Instructions" / "Exercises" / "media"


def resolve_card(name):
    """Return a path to the card image, looking in the shared media folder."""
    candidate = Path(name)
    if candidate.exists():
        return candidate
    return MEDIA_DIR / name


def main():

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:

        # Get the contact card
        image_file = 'biz-card-1.png'
        if len(sys.argv) > 1:
            image_file = sys.argv[1]
        image_path = resolve_card(image_file)

        if not image_path.exists():
            print(f"[error] Could not find {image_file}. Looked in {MEDIA_DIR}")
            return

        # Get config settings
        load_dotenv()
        ai_svc_endpoint = os.getenv('FOUNDRY_ENDPOINT')
        ai_svc_key = os.getenv('FOUNDRY_KEY')
        analyzer = os.getenv('ANALYZER_NAME')

        # Analyze the contact card
        analyze_card(str(image_path), analyzer, ai_svc_endpoint, ai_svc_key)

        print("\n")

    except Exception as ex:
        print(ex)


def analyze_card(image_file, analyzer, endpoint, key):

    # TODO: Use Content Understanding to analyze the image
    # Create a ContentUnderstandingClient, read the image bytes, submit them
    # with begin_analyze_binary, save the JSON response, and print each field.
    pass


if __name__ == "__main__":
    main()
