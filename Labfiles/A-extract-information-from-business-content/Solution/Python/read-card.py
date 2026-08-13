"""Task 2 - analyze a Fabrikam Logistics contact card with a Content Understanding analyzer.

Completed reference implementation.

Usage:
    python read-card.py                 Analyze the default card (biz-card-1.png)
    python read-card.py biz-card-2.png  Analyze another sample card
"""

from dotenv import load_dotenv
import os
import sys
import json
from pathlib import Path
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

# Sample cards live with the shared lab media, five levels up from this file:
# Labfiles/A-extract-information-from-business-content/Solution/Python/read-card.py
MEDIA_DIR = Path(__file__).resolve().parents[4] / "Instructions" / "Exercises" / "media"


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

    # Use Content Understanding to analyze the image
    print(f"Analyzing {image_file}")

    # Create the Content Understanding client
    client = ContentUnderstandingClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Read the image data
    with open(image_file, "rb") as file:
        image_data = file.read()

    # Submit the image for analysis
    print("Submitting request...")
    poller = client.begin_analyze_binary(
        analyzer_id=analyzer,
        binary_input=image_data
    )

    # Wait for the analysis to complete
    result = poller.result()
    print("Analysis succeeded:\n")

    # Save JSON results to a file
    output_file = "results.json"
    with open(output_file, "w") as json_file:
        json.dump(dict(result), json_file, indent=4, default=str)
        print(f"Response saved in {output_file}\n")

    # Iterate through the contents and extract fields
    for content in result.contents:
        if hasattr(content, 'fields') and content.fields:
            for field_name, field_data in content.fields.items():
                value = field_data.value if hasattr(field_data, 'value') else None
                print(f"{field_name}: {value}")


if __name__ == "__main__":
    main()
