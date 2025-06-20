import pandas as pd
import json
from datetime import datetime

def load_logs(path="../feedback/feedback_log.jsonl"):
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    # Ensure required fields exist
                    if 'timestamp' in item:
                        records.append(item)
                except json.JSONDecodeError:
                    continue  # skip malformed lines
    except FileNotFoundError:
        return pd.DataFrame()

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    
    # Defensive conversion
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['date'] = df['timestamp'].dt.date
    else:
        df['timestamp'] = pd.NaT
        df['date'] = None

    return df

