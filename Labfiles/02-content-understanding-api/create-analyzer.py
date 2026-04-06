from dotenv import load_dotenv
import os
import json
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential


def main():

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    try:

        # Get the business card schema
        with open("biz-card.json", "r") as file:
            schema_json = json.load(file)
        
        card_schema = json.dumps(schema_json)

        # Get config settings
        load_dotenv()
        ai_svc_endpoint = os.getenv('ENDPOINT')
        analyzer = os.getenv('ANALYZER_NAME')

        # Create the analyzer
        create_analyzer (card_schema, analyzer, ai_svc_endpoint)

        print("\n")

    except Exception as ex:
        print(ex)



def create_analyzer (schema, analyzer, endpoint):
    
    # Create a Content Understanding analyzer
 




if __name__ == "__main__":
    main()        
