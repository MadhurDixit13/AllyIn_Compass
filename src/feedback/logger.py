import json
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "feedback_log.jsonl")

print("Writing to:", LOG_FILE)

def log_feedback(query, answer, rating, tool="RAG", response_time=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "answer": answer,
        "rating": rating,
        "tool": tool,
        "response_time": response_time
    }
    print("[LOGGING FEEDBACK]", entry)  # ✅ Debug print
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        json.dump(entry, f)
        f.write("\n")
