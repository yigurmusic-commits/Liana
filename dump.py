import json, re
with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
match = re.search(r'(<script id="__NEXT_DATA__" type="application/json">)(.*?)(</script>)', html)
if match:
    with open('next_data.json', 'w', encoding='utf-8') as out:
        out.write(match.group(2))
    print('Saved next_data.json')
