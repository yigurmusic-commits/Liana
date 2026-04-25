import json, re
html=open('page_source.html', encoding='utf-8').read()
m = re.search(r'__NEXT_DATA__.*?>(.*?)</script>', html)
data = json.loads(m.group(1))
page_data = data['props']['pageProps']['pageData']['builderPageData']
for b in page_data['blocks']:
    if b['type'] == 'text':
        print(b.get('style', {}))
