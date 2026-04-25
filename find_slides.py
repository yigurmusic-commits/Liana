import re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

slides = re.findall(r'<div[^>]*swiper-slide[^>]*>.*?</div></div>', html, re.DOTALL)
print('Found swiper slides:', len(slides))
for i, slide in enumerate(slides[:3]):
    print(f'Slide {i}:', slide[:100], '...', slide[-50:])
