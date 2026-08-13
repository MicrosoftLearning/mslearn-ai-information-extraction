"""Task 2 - create a Content Understanding analyzer for Fabrikam Logistics contact cards.

Run this once to register the analyzer with your Foundry resource, then use
read-card.py to analyze scanned contact cards with it.
"""

from dotenv import load_dotenv
import os
import json
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential


def main():

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:

        # Get the contact card schema
        with open("contact-card.json", "r") as file:
            schema_json = json.load(file)

        card_schema = json.dumps(schema_json)

        # Get config settings
        load_dotenv()
        ai_svc_endpoint = os.getenv('FOUNDRY_ENDPOINT')
        ai_svc_key = os.getenv('FOUNDRY_KEY')
        analyzer = os.getenv('ANALYZER_NAME')

        # Create the analyzer
        create_analyzer(card_schema, analyzer, ai_svc_endpoint, ai_svc_key)

        print("\n")

    except Exception as ex:
        print(ex)


def create_analyzer(schema, analyzer, endpoint, key):

    # TODO: Create a Content Understanding analyzer
    # Create a ContentUnderstandingClient, parse the schema JSON, and call
    # begin_create_analyzer to register the analyzer with your Foundry resource.
    pass


if __name__ == "__main__":
    main()
