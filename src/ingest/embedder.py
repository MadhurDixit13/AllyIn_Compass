import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "unstructured", "parsed.jsonl")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " "]
)

def is_garbage(text):
    return len(set(text.lower().split())) < 30 or "threat think finally figure" in text.lower()
# This function checks if the text is garbage by looking for a low number of unique words or specific phrases.
# It returns True if the text is considered garbage, otherwise False.

# Load pre-parsed documents
def load_documents(file_path=DB_PATH):
    # Check if the file exists
    try:
        # utf-8 encoding is used to handle special characters in the text
        # Each line in the file is a JSON object representing a document
        # Using json.loads to parse each line as a JSON object
        # This allows for efficient loading of large files where each line is a separate JSON object
        # The file is expected to be in JSON Lines format (JSONL), where each line is a separate JSON object
        # This format is efficient for large datasets and allows for easy streaming of data
        with open(file_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return []

# Generate unique ID using hash of text
def generate_id(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16) % (10**12) # Uses md5 hash to create a unique ID (12 digits)
# MD5 converts the text to a hash, which is then converted to an integer.
# The integer is then reduced to a 12-digit number to fit within Qdrant's ID constraints.
# MD5 is not cryptographically secure, but it's sufficient for generating unique IDs in this context.
# Other hashing algorithms like SHA-256 could be used, but they would produce larger numbers. (MD5 produces a 128-bit hash value.)(SHA-256 produces a 256-bit hash value.)
# If you need more security, consider using SHA-256 and adjusting the modulus accordingly.

# Create or upload to Qdrant
def upload_to_qdrant(docs, model_name="all-MiniLM-L6-v2", collection_name="docs"):
    """
    we use qdrant because it is a vector database that allows us to store and search high-dimensional vectors efficiently.
    Args:
        docs (list): List of documents to upload, each document should be a dictionary with a 'text' or 'body' key.
        model_name (str): Name of the SentenceTransformer model to use for embedding.
        collection_name (str): Name of the Qdrant collection to upload the documents to.
    Returns:
        None
    Other options:
        - Use a different model for embedding, such as 'all-mpnet-base-v2' or 'paraphrase-MiniLM-L3-v2'.
        - Change the collection name to something more descriptive based on the context of the documents.
        - Implement chunking for long documents to ensure they fit within the model's input limits.
    Other vector databases:
        - Pinecone: A managed vector database service that provides high performance and scalability.
        - Weaviate: An open-source vector search engine that supports various data types and has a GraphQL interface.
        - Milvus: An open-source vector database designed for similarity search and AI applications.
    Why Qdrant?
    Qdrant is chosen for its ease of use, efficient handling of high-dimensional vectors, and support for various distance metrics. It integrates well with SentenceTransformers for embedding documents and allows for fast similarity search.
    Why all-MiniLM-L6-v2?
    The 'all-MiniLM-L6-v2' model is a lightweight, efficient model that provides good performance for semantic textual similarity tasks. It balances speed and accuracy, making it suitable for embedding documents in a vector database.
    """
    client = QdrantClient("localhost", port=6333) # 6333 is the default port for Qdrant
    
    # Create collection if it doesn't exist
    if collection_name not in [col.name for col in client.get_collections().collections]:
        # Create a new collection with specified vector parameters
        # VectorParams defines the size of the vectors and the distance metric to use.
        # Distance.COSINE is used for cosine similarity, which is common for text embeddings.
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    model = SentenceTransformer(model_name)
    texts = [] # List to hold document texts
    payloads = [] # List to hold document metadata (vector search with inverted index)

    for doc in docs:
        # Extract text content from the document
        # The document can have either 'text' or 'body' key, depending on the parsing method used.
        # If both keys are present, 'text' is preferred.
        # If neither key is present, the document is skipped.
        # This allows for flexibility in the document structure, accommodating different parsing methods.
        content = doc.get("text") or doc.get("body", "")
        
        if len(content.strip()) == 0:
            continue
        if is_garbage(content):
            continue
        chunks = text_splitter.split_text(content)
        # Chunking the text into smaller parts to fit within the model's input limits
        # This is important for long documents to ensure they can be processed by the model.
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            
            payloads.append({"meta": doc, "chunk": i})# Metadata for the document, which can include file name, type, etc.
        
    try:
        vectors = model.encode(texts, show_progress_bar=True).tolist()
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}")
        return
    # Encode the texts into vectors using the SentenceTransformer model
    # The model.encode method converts the list of texts into a list of vectors.
    # Convert vectors to list of lists for Qdrant
    # Qdrant expects vectors to be in a list of lists format, where each inner list is a vector.
    points = [
        # Create PointStruct for each document with a unique ID, vector, and payload
        # PointStruct is a data structure used by Qdrant to represent a point in the vector space.
        PointStruct(id=generate_id(payload['meta'].get('file', '') + str(i)), vector=vec, payload=payload)
        for i, (vec, payload) in enumerate(zip(vectors, payloads))
    ]

    client.upsert(collection_name=collection_name, points=points)
    print(f"Uploaded {len(points)} documents to Qdrant.")

if __name__ == "__main__":
    docs = load_documents()
    upload_to_qdrant(docs)
