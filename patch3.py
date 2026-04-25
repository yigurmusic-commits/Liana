import json
import re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'(<script id="__NEXT_DATA__" type="application/json">)(.*?)(</script>)', html)
if match:
    prefix = match.group(1)
    data_str = match.group(2)
    suffix = match.group(3)
    
    try:
        data = json.loads(data_str)
        json_str = json.dumps(data, ensure_ascii=False)
        
        # Replace the time
        json_str = json_str.replace('15 августа 17:00', '15 августа 18:00')
        json_str = json_str.replace('15 августа в 17:00', '15 августа в 18:00')
        
        # Replace the map link
        json_str = json_str.replace('https://2gis.com/i147J', 'https://go.2gis.com/xlBab')
        
        data = json.loads(json_str)
        final_json_str = json.dumps(data, ensure_ascii=False)
        
        new_script_block = prefix + final_json_str + suffix
        html = html.replace(prefix + data_str + suffix, new_script_block)
        
        with open('Original_Clone/index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('Successfully updated time and map link.')
    except Exception as e:
        print('Error:', e)
