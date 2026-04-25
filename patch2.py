import json
import re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
if match:
    data_str = match.group(1)
    # decode JSON
    data = json.loads(data_str)
    
    # We can just convert data to a json string and replace the text in it, then put it back
    # but json.dumps might escape cyrillic. Let's do it with ensure_ascii=False
    data_str_decoded = json.dumps(data, ensure_ascii=False)
    
    # Replace
    data_str_decoded = data_str_decoded.replace('Игорь & Анна', 'Мейрлен & Лиана')
    data_str_decoded = data_str_decoded.replace('ИГОРЬ & АННА', 'МЕЙРЛЕН & ЛИАНА')
    data_str_decoded = data_str_decoded.replace('13 сентября 2026', '15 августа 17:00')
    data_str_decoded = data_str_decoded.replace('13 сентября в 12:00', '15 августа в 17:00')

    # Replace the script content
    new_script = f'<script id="__NEXT_DATA__" type="application/json">{data_str_decoded}</script>'
    
    # Let's replace the whole script block
    html = re.sub(r'<script id="__NEXT_DATA__" type="application/json">.*?</script>', new_script, html)
    
    with open('Original_Clone/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Names and dates replaced in Next.js JSON.')
else:
    print('Could not find NEXT_DATA script.')
