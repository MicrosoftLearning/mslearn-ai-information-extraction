from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from dotenv import load_dotenv
import os


def main():

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    try:
        # Get configuration settings 
        load_dotenv()
        endpoint = os.getenv("DOC_INTELLIGENCE_ENDPOINT")
        key = os.getenv("DOC_INTELLIGENCE_KEY")
        model_id = os.getenv("MODEL_ID")

        formUrl = "https://github.com/MicrosoftLearning/mslearn-ai-information-extraction/blob/main/Labfiles/custom-doc-intelligence/test1.jpg?raw=true"

        document_analysis_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        # Make sure your document's type is included in the list of document types the custom model can analyze
        poller = document_analysis_client.begin_analyze_document(
            model_id,
            AnalyzeDocumentRequest(url_source=formUrl)
        )
        result = poller.result()

        for idx, document in enumerate(result.documents):
            print("--------Analyzing document #{}--------".format(idx + 1))
            print("Document has type {}".format(document.doc_type))
            print("Document has confidence {}".format(document.confidence))
            print("Document was analyzed by model with ID {}".format(result.model_id))
            for name, field in document.fields.items():
                field_value = field.get("valueString") or field.get("content", "N/A")
                print("Found field '{}' with value '{}' and with confidence {}".format(name, field_value, field.get("confidence")))

        print("-----------------------------------")
    except Exception as ex:
        print(ex)

    print("\nAnalysis complete.\n")

if __name__ == "__main__":
    main()     