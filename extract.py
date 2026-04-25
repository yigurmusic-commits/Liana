import json, re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'(<script id="__NEXT_DATA__" type="application/json">)(.*?)(</script>)', html)
if match:
    data = json.loads(match.group(2))
    blocks = data.get('props', {}).get('pageProps', {}).get('pageData', {}).get('blocks', [])
    for b in blocks:
        for c in b.get('components', []):
            if c.get('type') == 'wishes-list':
                print("Found wishes-list component!")
                print(json.dumps(c.get('data', {}), ensure_ascii=False, indent=2))
