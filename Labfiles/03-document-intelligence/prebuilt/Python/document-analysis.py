from dotenv import load_dotenv
import os

# Add references



def main():

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    try:
        # Get config settings
        load_dotenv()
        endpoint = os.getenv('ENDPOINT')
        key = os.getenv('KEY')


        # Set analysis settings
        fileUri = "https://github.com/MicrosoftLearning/mslearn-ai-information-extraction/blob/main/Labfiles/prebuilt-doc-intelligence/sample-invoice/sample-invoice.pdf?raw=true"
        fileLocale = "en-US"
        fileModelId = "prebuilt-invoice"

        print(f"\nConnecting to Forms Recognizer at: {endpoint}")
        print(f"Analyzing invoice at: {fileUri}")


        # Create the client



        # Analyse the invoice



        # Display invoice information to the user


            


    except Exception as ex:
        print(ex)

    print("\nAnalysis complete.\n")

if __name__ == "__main__":
    main()        
