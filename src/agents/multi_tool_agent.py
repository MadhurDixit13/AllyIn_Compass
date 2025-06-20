import time
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq
import os
import sys

import dotenv
# Import tool functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.retrievers.sql_retriever import query_sql
from src.retrievers.vector_retriever import search_vector
from src.retrievers.graph_retriever import run_query_safe as run_graph_query
dotenv.load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),  # Ensure you have set this in your .env file
    model_name="llama3-70b-8192",  # or use llama3-8b-8192, gemma-7b-it
    temperature=0
)
def vector_tool_response(query):
    docs = search_vector(query)
    texts = [doc.get("meta", {}).get("text", "")[:300] for doc in docs]
    return "\n\n---\n\n".join(texts)



# Define LangChain tool wrappers
tools = [
    Tool(
        name="SQLSearch",
        func=query_sql,
        description="Use this to answer questions about structured tabular data like customers or orders."
    ),
    Tool(
        name="VectorSearch",
        # func=lambda q: str(search_vector(q)),
        func=vector_tool_response,
        description="Use this to retrieve relevant documents or paragraphs from parsed files."
    ),
    Tool(
        name="GraphSearch",
        func=lambda actor: run_graph_query(
            """
            MATCH (a:Person {name: $actor})-[:ACTED_IN]->(m:Movie)
            RETURN m.title AS title
            LIMIT 5
            """,
            {"actor": actor}
        ),
        description=(
            "Use this to find movies acted in by a person. "
            "Input should be the actor's full name, like 'Tom Hanks'. Persons full name will be the actor"
        )
    )
]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True

)

def run_agent(user_query):
    start = time.time()
    response = agent.invoke({"input": user_query})

    duration = round(time.time() - start, 2)
    print(f"[LOG] Time: {duration}s | Query: {user_query}")
    return response

if __name__ == "__main__":
    # user_query = "What is the name of the customer with id 1?"
    # user_query = "Which customers have placed an order?"
    # user_query = "Tell me about the latest AI research"
    user_query = "Recommend movies to Angela Thompson based on what similar users liked."
    answer = run_agent(user_query)
    print(answer)
    