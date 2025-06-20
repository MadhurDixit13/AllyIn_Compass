import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.security.pii_filter import contains_pii
from src.security.compliance_tagger import tag_compliance_flags
from src.agents.multi_tool_agent import run_agent
from src.feedback.logger import log_feedback
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import time

import dotenv
# Load environment variables from .env file
dotenv.load_dotenv()
# llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-8b-8192", temperature=0)

def generate_rag_answer(user_query):
    start = time.time()
    docs = run_agent(user_query)

    # If the agent returned a dict with output text (ideal case)
    if isinstance(docs, dict) and "output" in docs:
        output = docs["output"]
    # If it's a plain string (LLM-only response)
    elif isinstance(docs, str):
        output = docs
    # If it's a list of documents, extract from metadata or fallback
    elif isinstance(docs, list):
        output = "\n".join(doc.get("meta", {}).get("text", "")[:300] if isinstance(doc, dict) else str(doc) for doc in docs)
    else:
        output = str(docs)  # Fallback

    duration = round(time.time() - start, 2)
    log_feedback(user_query, output, 1, tool="RAG", response_time=duration)

    if contains_pii(output):
        return "[Warning] Answer may contain PII. Please review carefully."

    flags = tag_compliance_flags(output)
    if flags:
        return f"[Compliance Warning] Keywords flagged: {', '.join(flags)}\n\n{output}"

    return {
        "answer": output,
        "sources": [doc.get("meta", {}).get("file") for doc in docs if isinstance(doc, dict) and "meta" in doc]
    }


# def generate_rag_answer(user_query):
#     start = time.time()
#     # docs = search_vector(user_query)
#     docs = run_agent(user_query)  # Use the multi-tool agent to get relevant documents
#     output_text = docs.get("output", "").strip()
#     print("DEBUG DOCS:", docs)
#     print("TYPE of first doc:", type(docs[0]) if docs else "None")
#     if not docs:
#         return "No relevant documents found."

#     # Limit context to ~4000 characters (approx. 1500–2000 tokens)
#     # Truncate long outputs
#     max_context_length = 4000
#     # context = "\n---\n".join(
#     #     doc.get("meta", {}).get("text") or doc.get("meta", {}).get("body", "") for doc in docs
#     # )
#     context = output_text[:max_context_length]
#     prompt = f"""
#     You are a helpful assistant. Use the context below if helpful, but feel free to answer using your own knowledge if needed.



#     Context:
#     {context}

#     Question: {user_query}
#     Answer:"""

#     response = llm.invoke([HumanMessage(content=prompt)])
#     duration = round(time.time() - start, 2)
#     log_feedback(user_query, "RAG", 1, tool="RAG", response_time=duration)
#     if contains_pii(response.content):
#         return "[Warning] Answer may contain PII. Please review carefully."

#     flags = tag_compliance_flags(response.content)
#     if flags:
#         return f"[Compliance Warning] Keywords flagged: {', '.join(flags)}\n\n{response.content}"

#     return response.content

if __name__ == "__main__":
    query = "Tell me when the meeting is."
    print(generate_rag_answer(query))
