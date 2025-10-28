import json
from typing import List, Dict, Any

def load_program(path: str) -> (List, Dict[str,int]):
    data = json.load(open(path, 'r'))
    tags = data.get("tags", {})
    rungs = data.get("rungs", [])
    return rungs, tags
