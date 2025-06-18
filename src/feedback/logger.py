import json
from datetime import datetime
import os

LOG_FILE = "feedback_log.jsonl"

def log_feedback(query, answer, rating):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "answer": answer,
        "rating": rating  # 1 = 👍, 0 = 👎
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        json.dump(entry, f)
        f.write("\n")
