import json
from strands import tool

@tool
def search_rool(target_id:str):
    with open ('../data/data.json','r') as file:
        data = json.load(file)
        return data.get(target_id, "ID not found")