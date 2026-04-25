import re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the wishes container
# The section has a header, probably "ПОЖЕЛАНИЯ"
match = re.search(r'ВАШИ ПОЖЕЛАНИЯ(.*?)(СМОТРЕТЬ ВСЕ|ПОЖЕЛАНИЕ)', html, re.DOTALL | re.IGNORECASE)
if match:
    print('Found section:', match.group(1)[:500])
    # extract swiper slide template
    slide_match = re.search(r'(<div[^>]*swiper-slide.*?)</div></div></div></div>', match.group(1), re.DOTALL)
    if slide_match:
        print('\nSlide HTML:')
        print(slide_match.group(1))
