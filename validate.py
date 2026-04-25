import json, re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
if match:
    try:
        data = json.loads(match.group(1))
        print('JSON is valid.')
    except Exception as e:
        print('JSON is invalid:', e)
else:
    print('No NEXT_DATA found.')
