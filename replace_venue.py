with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"Villa Borghese"', '"Абдукахар"')
text = text.replace('Villa Borghese', 'Абдукахар')

# The original has "Ресторанный комплекс" somewhere. Let's find it.
text = text.replace('Ресторанный комплекс', 'ресторан, с. Ават')

with open('Original_Clone/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Replaced venue details.')
