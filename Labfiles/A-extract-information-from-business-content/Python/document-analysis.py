"""Task 3 - analyze a supplier invoice with the prebuilt-invoice model.

Fabrikam Logistics receives invoices from dozens of suppliers in different
layouts. The prebuilt invoice model reads them all without any training.
"""

from dotenv import load_dotenv
import os

# TODO: Add references
# Import AzureKeyCredential, DocumentIntelligenceClient, and AnalyzeDocumentRequest.


def main():

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get config settings
        load_dotenv()
        endpoint = os.getenv('DOC_INTELLIGENCE_ENDPOINT')
        key = os.getenv('DOC_INTELLIGENCE_KEY')

        # Set analysis settings
        fileUri = "https://raw.githubusercontent.com/MicrosoftLearning/mslearn-ai-information-extraction/main/Labfiles/03-document-intelligence/prebuilt/sample-invoice/sample-invoice.pdf"
        fileLocale = "en-US"
        fileModelId = "prebuilt-invoice"

        print(f"\nConnecting to Azure Document Intelligence at: {endpoint}")
        print(f"Analyzing invoice at: {fileUri}")

        # TODO: Create the client

        # TODO: Analyze the invoice

        # TODO: Display invoice information to the user

    except Exception as ex:
        print(ex)

    print("\nAnalysis complete.\n")


if __name__ == "__main__":
    main()
