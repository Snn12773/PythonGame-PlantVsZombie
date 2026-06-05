import json
from pathlib import Path

ROOT = Path(__file__).parent

def loadJson(path:str) -> dict:
    json_path = Path(ROOT / path)
    with open(json_path) as file:
        data = json.load(file)
        return data