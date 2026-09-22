"""Task 3 - analyze a supplier invoice with the prebuilt-invoice model.

Completed reference implementation.
"""

from dotenv import load_dotenv
import os

# Add references
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest


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

        # Create the client
        document_analysis_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        # Analyze the invoice
        poller = document_analysis_client.begin_analyze_document(
            fileModelId,
            AnalyzeDocumentRequest(url_source=fileUri),
            locale=fileLocale
        )

        # Display invoice information to the user
        result = poller.result()

        for document in result.documents:

            vendor_name = document.fields.get("VendorName")
            if vendor_name:
                print(f"\nVendor Name: {vendor_name.get('valueString')}, with confidence {vendor_name.get('confidence')}.")

            customer_name = document.fields.get("CustomerName")
            if customer_name:
                print(f"Customer Name: {customer_name.get('valueString')}, with confidence {customer_name.get('confidence')}.")

            invoice_total = document.fields.get("InvoiceTotal")
            if invoice_total:
                amount = invoice_total.get("valueCurrency", {})
                print(f"Invoice Total: {amount.get('currencySymbol', '$')}{amount.get('amount')}, with confidence {invoice_total.get('confidence')}.")

    except Exception as ex:
        print(ex)

    print("\nAnalysis complete.\n")


if __name__ == "__main__":
    main()
