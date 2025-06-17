from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_vector(query_text, k=3):
    vector = model.encode(query_text).tolist()

    response = client.query_points(
        collection_name="docs",
        query=vector,
        limit=k,
        with_payload=True
    )

    # Access actual list of results from .points
    
    return [point.payload for point in response.points] 

if __name__ == "__main__":
    for file_path in search_vector("Tell me about the latest AI research", k=3):
        print(file_path)
