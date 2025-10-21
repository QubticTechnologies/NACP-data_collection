import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_json(filename, default=None):
    """
    Load JSON from data/ folder. Returns default if file not found or invalid.
    """
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def save_json(filename, data):
    """
    Save dictionary/list as JSON in data/ folder.
    """
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
