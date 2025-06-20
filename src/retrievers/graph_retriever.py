from neo4j import GraphDatabase
import os
import dotenv
# Load environment variables from .env file
dotenv.load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def run_query(cypher_query, parameters=None):
    with driver.session() as session:
        result = session.run(cypher_query, parameters or {})
        return [record.data() for record in result]
def run_query_safe(cypher_query, parameters=None):
    raw_results = run_query(cypher_query, parameters)
    # Optional: truncate long field values (e.g. plot, poster)
    for r in raw_results:
        for key in r:
            if isinstance(r[key], str) and len(r[key]) > 200:
                r[key] = r[key][:200] + "..."
    return raw_results[:5]  # limit number of results returned to the agent


if __name__ == "__main__":
    cypher = """
            MATCH (a:Person {name: $actor})-[:ACTED_IN]->(m:Movie)
            RETURN m.title AS title
            LIMIT 5
            """

    actor = "Tom Cruise"  # Example actor name
    results = run_query(cypher, {"actor": actor})


    if results:
        for row in results:
            print(row)
    else:
        print("No recommendations found.")

