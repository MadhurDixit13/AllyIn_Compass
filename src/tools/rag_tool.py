import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.retrievers.vector_retriever import search_vector
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

import dotenv
# Load environment variables from .env file
dotenv.load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-8b-8192", temperature=0)

def generate_rag_answer(user_query):
    docs = search_vector(user_query)
    print("DEBUG DOCS:", docs)
    print("TYPE of first doc:", type(docs[0]) if docs else "None")
    if not docs:
        return "No relevant documents found."

    # Limit context to ~4000 characters (approx. 1500–2000 tokens)
    max_context_length = 4000

    context = "\n---\n".join(
        doc.get("meta", {}).get("text") or doc.get("meta", {}).get("body", "") for doc in docs
    )
    context = context[:max_context_length] 
    prompt = f"""
    You are a helpful assistant. Use the following context to answer the question.

    Context:
    {context}

    Question: {user_query}
    Answer:"""
    

    response = llm.invoke([HumanMessage(content=prompt)]) 

    return response.content

if __name__ == "__main__":
    query = "Find reports about carbon emissions in South region"
    print(generate_rag_answer(query))
