import json, time
from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()
LOG_DIR = Path(os.getenv('LOG_DIR', './logs'))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / 'llm_interactions.jsonl'




def log_interaction(record):
    record['ts'] = time.time()
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')