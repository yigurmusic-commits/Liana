import json

def search_text(obj, query):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if search_text(v, query):
                return True
    elif isinstance(obj, list):
        for v in obj:
            if search_text(v, query):
                return True
    elif isinstance(obj, str):
        if query in obj:
            return True
    return False

with open('next_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Жастар in json:", search_text(data, "Жастар"))
print("Тынышгул in json:", search_text(data, "Тынышгул"))

# Let's search for "wishes" arrays
def find_wishes(obj):
    if isinstance(obj, dict):
        if 'wishes' in obj:
            print("Found wishes array:", obj['wishes'])
        for k, v in obj.items():
            find_wishes(v)
    elif isinstance(obj, list):
        for item in obj:
            find_wishes(item)

find_wishes(data)
