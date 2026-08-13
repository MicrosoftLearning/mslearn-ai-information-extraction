"""Task 2 - create the Content Understanding analyzer used by the ingestion pipeline.

Run this once. It registers an analyzer that returns markdown content plus a
generated summary and key topics for every document Fabrikam Logistics ingests.
"""

from dotenv import load_dotenv
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

ANALYZER_ID = "fabrikam_document_analyzer"


def main():
    """Create a Content Understanding analyzer for extracting content from documents."""

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get config settings
        load_dotenv()
        endpoint = os.getenv('FOUNDRY_ENDPOINT')
        key = os.getenv('FOUNDRY_KEY')

        print(f"Creating analyzer '{ANALYZER_ID}'...")

        # Create the Content Understanding client
        client = ContentUnderstandingClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

        # Define the analyzer schema for document extraction
        analyzer_definition = {
            "description": "Analyzer for extracting structured content from Fabrikam Logistics documents",
            "baseAnalyzerId": "prebuilt-document",
            "models": {
                "completion": "gpt-5.2",
                "embedding": "text-embedding-3-large"
            },
            "config": {
                "returnDetails": True
            },
            "fieldSchema": {
                "fields": {
                    "Summary": {
                        "type": "string",
                        "method": "generate",
                        "description": "A brief summary of the document content"
                    },
                    "KeyTopics": {
                        "type": "array",
                        "method": "generate",
                        "description": "Key topics or themes covered in the document",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        }

        # Create the analyzer (long-running operation)
        poller = client.begin_create_analyzer(
            analyzer_id=ANALYZER_ID,
            resource=analyzer_definition,
            allow_replace=True
        )

        # Wait for the operation to complete
        poller.result()
        print(f"Analyzer '{ANALYZER_ID}' created successfully.")

    except Exception as ex:
        print(f"Error: {ex}")


if __name__ == "__main__":
    main()
