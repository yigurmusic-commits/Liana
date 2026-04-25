import json, re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">([\s\S]*?)</script>', html)
d = json.loads(match.group(1))

def find_wishes(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'wishes' or k == 'comments':
                print(f"Found {k} at {path}.{k}: {str(v)[:200]}")
            find_wishes(v, path + "." + k)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_wishes(item, f"{path}[{i}]")

find_wishes(d)
