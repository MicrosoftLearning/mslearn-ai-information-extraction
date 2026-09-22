"""Task 3 - answer questions about the Fabrikam Logistics document set.

Retrieves the most relevant indexed content with hybrid search (keyword +
vector), then asks a chat model to answer using only that content.
"""

from dotenv import load_dotenv
import os
from openai import OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

INDEX_NAME = "fabrikam-rag-index"


def openai_base_url(foundry_endpoint):
    """Build the Azure OpenAI v1 base URL from a Foundry resource endpoint."""
    endpoint = (foundry_endpoint or "").rstrip("/")
    if endpoint.endswith("/openai/v1"):
        return endpoint + "/"
    return f"{endpoint}/openai/v1/"


def main():
    """RAG agent that answers questions using retrieved content from Azure AI Search."""

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get config settings
        load_dotenv()
        foundry_endpoint = os.getenv('FOUNDRY_ENDPOINT')
        foundry_key = os.getenv('FOUNDRY_KEY')
        chat_deployment = os.getenv('CHAT_DEPLOYMENT_NAME')
        embedding_deployment = os.getenv('EMBEDDING_DEPLOYMENT_NAME')
        search_endpoint = os.getenv('SEARCH_ENDPOINT')
        search_key = os.getenv('SEARCH_ADMIN_KEY')

        # Create clients
        openai_client = OpenAI(
            api_key=foundry_key,
            base_url=openai_base_url(foundry_endpoint),
        )

        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(search_key)
        )

        print("RAG agent ready. Ask questions about your indexed documents.")
        print("Type 'quit' to exit.\n")

        # Conversation loop
        while True:
            question = input("You: ").strip()
            if question.lower() == "quit":
                print("Goodbye!")
                break
            if not question:
                continue

            # Retrieve relevant content using hybrid search
            context = retrieve_context(
                question, search_client, openai_client, embedding_deployment
            )

            # Generate a response using the chat model
            answer = generate_answer(
                question, context, openai_client, chat_deployment
            )

            print(f"\nAssistant: {answer}\n")

    except Exception as ex:
        print(f"Error: {ex}")


def retrieve_context(question, search_client, openai_client, embedding_deployment, top_k=3):
    """Perform hybrid search (keyword + vector) to retrieve relevant content chunks."""

    # Generate embedding for the question
    embedding_response = openai_client.embeddings.create(
        input=question,
        model=embedding_deployment
    )
    query_vector = embedding_response.data[0].embedding

    # Perform hybrid search
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="content_vector"
    )

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        select=["content", "file_name", "summary"],
        top=top_k
    )

    # Build context from results
    context_parts = []
    for result in results:
        source = result.get("file_name", "Unknown")
        content = result.get("content", "")
        if content:
            context_parts.append(f"[Source: {source}]\n{content}")

    return "\n\n---\n\n".join(context_parts) if context_parts else ""


def generate_answer(question, context, openai_client, chat_deployment):
    """Generate an answer using the chat model with retrieved context."""

    if not context:
        system_message = (
            "You are a helpful assistant. The user asked a question but no "
            "relevant documents were found in the knowledge base. Let the user know."
        )
    else:
        system_message = (
            "You are a helpful assistant that answers questions based on the provided context. "
            "Use only the information from the context to answer. If the context doesn't contain "
            "enough information to fully answer the question, say so. "
            "Cite the source document names when possible.\n\n"
            f"Context:\n{context}"
        )

    response = openai_client.chat.completions.create(
        model=chat_deployment,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    main()
