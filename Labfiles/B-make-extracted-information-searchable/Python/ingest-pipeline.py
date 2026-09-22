"""Automated RAG ingestion pipeline for Fabrikam Logistics.

Monitors a data folder for new or updated documents, extracts content using
Azure Content Understanding, generates embeddings with Azure OpenAI, and
indexes the results into Azure AI Search.

Usage:
    python ingest-pipeline.py            Process new files once and exit
    python ingest-pipeline.py --watch    Continuously watch for new files
    python ingest-pipeline.py --reset    Clear tracking data and reprocess all files
"""

import argparse
import glob
import hashlib
import json
import os
import time
from datetime import datetime

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchableField,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from dotenv import load_dotenv
from openai import OpenAI

# ----- Configuration -------------------------------------------------------
MANIFEST_FILE = "processed_files.json"
INDEX_NAME = "fabrikam-rag-index"
ANALYZER_ID = "fabrikam_document_analyzer"
DATA_FOLDER = "data"
POLL_INTERVAL = 30  # seconds between polls in watch mode
EMBEDDING_DIMENSIONS = 3072  # text-embedding-3-large
# ---------------------------------------------------------------------------


def log(message):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def openai_base_url(foundry_endpoint):
    """Build the Azure OpenAI v1 base URL from a Foundry resource endpoint."""
    endpoint = (foundry_endpoint or "").rstrip("/")
    if endpoint.endswith("/openai/v1"):
        return endpoint + "/"
    return f"{endpoint}/openai/v1/"


# -- Manifest helpers -------------------------------------------------------

def load_manifest():
    """Load the manifest that tracks which files have been processed."""
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r") as f:
            return json.load(f)
    return {}


def save_manifest(manifest):
    """Save the processed-files manifest to disk."""
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)


def file_hash(file_path):
    """Compute a SHA-256 hash of a file for change detection."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha.update(block)
    return sha.hexdigest()


# -- File discovery ---------------------------------------------------------

def get_pending_files(manifest):
    """Return a list of files that are new or have changed since last run."""
    supported = ["*.pdf", "*.png", "*.jpg", "*.docx", "*.txt"]
    all_files = []
    for pattern in supported:
        all_files.extend(glob.glob(os.path.join(DATA_FOLDER, pattern)))

    pending = []
    for fp in all_files:
        current_hash = file_hash(fp)
        if manifest.get(fp) != current_hash:
            pending.append(fp)
    return pending


# -- Search index -----------------------------------------------------------

def ensure_index(search_endpoint, search_key):
    """Create or update the Azure AI Search index."""
    index_client = SearchIndexClient(
        endpoint=search_endpoint,
        credential=AzureKeyCredential(search_key),
    )

    fields = [
        SimpleField(
            name="id", type=SearchFieldDataType.String,
            key=True, filterable=True
        ),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(
            name="file_name", type=SearchFieldDataType.String, filterable=True
        ),
        SearchableField(name="summary", type=SearchFieldDataType.String),
        SearchableField(name="key_topics", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algorithm")],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-algorithm",
            )
        ],
    )

    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    index_client.create_or_update_index(index)


# -- Content chunking -------------------------------------------------------

def chunk_content(text, max_chars=2000):
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks, current = [], ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 > max_chars and current:
            chunks.append(current.strip())
            current = para
        else:
            current += ("\n\n" + para) if current else para

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text[:max_chars]]


def make_doc_id(file_name, chunk_index):
    """Generate a deterministic document ID from the file name and chunk."""
    raw = f"{file_name}::{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


# -- Ingestion logic --------------------------------------------------------

def ingest_file(file_path, cu_client, openai_client, search_client,
                embedding_deployment):
    """Extract, embed, and index a single file.

    Returns the number of chunks successfully indexed.
    """
    file_name = os.path.basename(file_path)

    # --- Extract with Content Understanding ---------------------------------
    with open(file_path, "rb") as f:
        file_data = f.read()

    poller = cu_client.begin_analyze_binary(
        analyzer_id=ANALYZER_ID,
        binary_input=file_data,
    )
    result = poller.result()

    doc_content = ""
    fields = {}
    for item in result.contents:
        if hasattr(item, "markdown") and item.markdown:
            doc_content += item.markdown + "\n"
        if hasattr(item, "fields") and item.fields:
            for name, data in item.fields.items():
                if hasattr(data, "value_array") and data.value_array is not None:
                    fields[name] = [v.get("value", str(v)) for v in data.value_array]
                elif hasattr(data, "value"):
                    fields[name] = data.value

    if not doc_content.strip():
        log("    Skipped (no extractable content).")
        return 0

    # --- Chunk, embed, and index -------------------------------------------
    chunks = chunk_content(doc_content)
    summary = fields.get("Summary", "")
    key_topics = (
        ", ".join(fields.get("KeyTopics", []))
        if isinstance(fields.get("KeyTopics"), list)
        else str(fields.get("KeyTopics", ""))
    )

    docs_to_upload = []
    for j, chunk in enumerate(chunks):
        log(f"    Embedding chunk {j + 1}/{len(chunks)}...")
        resp = openai_client.embeddings.create(
            input=chunk, model=embedding_deployment
        )
        embedding = resp.data[0].embedding

        docs_to_upload.append({
            "id": make_doc_id(file_name, j),
            "content": chunk,
            "file_name": file_name,
            "summary": str(summary) if not isinstance(summary, str) else summary,
            "key_topics": key_topics,
            "content_vector": embedding,
        })

    if docs_to_upload:
        upload_result = search_client.upload_documents(documents=docs_to_upload)
        succeeded = sum(1 for r in upload_result if r.succeeded)
        log(f"    Indexed {succeeded} chunk(s) from {file_name}.")
        return succeeded

    return 0


def run_ingestion(cu_client, openai_client, search_client,
                  embedding_deployment, manifest):
    """Process any new or updated files. Returns True if files were ingested."""
    pending = get_pending_files(manifest)
    if not pending:
        return False

    log(f"Detected {len(pending)} new/updated file(s).")
    total_chunks = 0

    for file_path in pending:
        log(f"  Processing: {os.path.basename(file_path)}")
        chunks = ingest_file(
            file_path, cu_client, openai_client, search_client,
            embedding_deployment,
        )
        total_chunks += chunks

        # Mark the file as processed immediately after successful ingestion
        manifest[file_path] = file_hash(file_path)
        save_manifest(manifest)

    log(f"Ingestion complete - {len(pending)} file(s), "
        f"{total_chunks} chunk(s) indexed.\n")
    return True


# -- Entry point ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Automated RAG ingestion pipeline"
    )
    parser.add_argument(
        "--watch", action="store_true",
        help="Continuously watch for new files "
             f"(polls every {POLL_INTERVAL} seconds)",
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Clear processed-file tracking and reprocess everything",
    )
    args = parser.parse_args()

    os.system("cls" if os.name == "nt" else "clear")

    # Load environment configuration
    load_dotenv()
    foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")
    foundry_key = os.getenv("FOUNDRY_KEY")
    embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_key = os.getenv("SEARCH_ADMIN_KEY")

    # Create SDK clients
    cu_client = ContentUnderstandingClient(
        endpoint=foundry_endpoint, credential=AzureKeyCredential(foundry_key),
    )
    openai_client = OpenAI(
        api_key=foundry_key,
        base_url=openai_base_url(foundry_endpoint),
    )
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(search_key),
    )

    # Ensure the search index exists
    log("Verifying search index...")
    ensure_index(search_endpoint, search_key)
    log(f"Search index '{INDEX_NAME}' is ready.")

    # Handle --reset flag
    if args.reset and os.path.exists(MANIFEST_FILE):
        os.remove(MANIFEST_FILE)
        log("Cleared processed-file tracking - all files will be reprocessed.")

    manifest = load_manifest()

    if args.watch:
        log(f"Watching '{DATA_FOLDER}/' for new documents "
            f"(press Ctrl+C to stop)...\n")
        try:
            while True:
                found = run_ingestion(
                    cu_client, openai_client, search_client,
                    embedding_deployment, manifest,
                )
                if not found:
                    log("No new files. Waiting...")
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopped watching.")
    else:
        found = run_ingestion(
            cu_client, openai_client, search_client,
            embedding_deployment, manifest,
        )
        if not found:
            log("No new files to ingest - all documents are up to date.")


if __name__ == "__main__":
    main()
