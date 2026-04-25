import json
import re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Safely replace text in Next.js JSON without re.sub
match = re.search(r'(<script id="__NEXT_DATA__" type="application/json">)(.*?)(</script>)', html)
if match:
    prefix = match.group(1)
    data_str = match.group(2)
    suffix = match.group(3)
    
    try:
        data = json.loads(data_str)
        # Update JSON safely
        # We'll just convert to string, replace text, and parse back to make sure it's valid
        json_str = json.dumps(data, ensure_ascii=False)
        json_str = json_str.replace('Игорь & Анна', 'Мейрлен & Лиана')
        json_str = json_str.replace('ИГОРЬ & АННА', 'МЕЙРЛЕН & ЛИАНА')
        json_str = json_str.replace('13 сентября 2026', '15 августа 17:00')
        json_str = json_str.replace('13 сентября в 12:00', '15 августа в 17:00')
        
        # Verify it's still valid JSON
        data = json.loads(json_str)
        # Dump back using default Next.js-like format if possible, or just standard dumps
        final_json_str = json.dumps(data, ensure_ascii=False)
        
        # Build new script block
        old_script_block = prefix + data_str + suffix
        new_script_block = prefix + final_json_str + suffix
        
        # Use simple string replacement!
        html = html.replace(old_script_block, new_script_block)
        print("Replaced names and dates in NEXT_DATA.")
    except Exception as e:
        print("Error parsing/modifying JSON:", e)

# 2. Add custom wishes and button logic
custom_script = """
<style>
#custom-wishes-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 10000; align-items: center; justify-content: center; }
.custom-modal-content { background: white; padding: 20px; border-radius: 10px; width: 80%; max-width: 350px; display: flex; flex-direction: column; gap: 10px; font-family: sans-serif; color: black; }
.custom-btn { padding: 10px; border: none; border-radius: 5px; cursor: pointer; }
.custom-input { padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: black; }
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {
    setInterval(() => {
        // Intercept form buttons
        document.querySelectorAll('button').forEach(btn => {
            const text = btn.innerText || '';
            if ((text.includes('Ответить') || text.includes('ОТПРАВИТЬ') || text.includes('Да, я приду') || text.includes('К сожалению')) && !btn.dataset.patched) {
                if (text.includes('Ответить') || text.includes('ОТПРАВИТЬ')) {
                    const newBtn = btn.cloneNode(true);
                    newBtn.dataset.patched = '1';
                    btn.parentNode.replaceChild(newBtn, btn);
                    newBtn.addEventListener('click', (e) => {
                        e.preventDefault(); e.stopPropagation();
                        alert('Ваш ответ успешно отправлен!');
                    });
                }
            }
        });

        // Intercept forms
        document.querySelectorAll('form').forEach(f => {
            if (!f.dataset.patched) {
                f.dataset.patched = '1';
                f.addEventListener('submit', e => { e.preventDefault(); alert('Ваш ответ успешно отправлен!'); });
            }
        });

        // Intercept wishes button
        document.querySelectorAll('button, div').forEach(b => {
            if (b.innerText === 'ПОЖЕЛАНИЕ' && !b.dataset.patched && window.getComputedStyle(b).position === 'fixed') {
                const nb = b.cloneNode(true);
                nb.dataset.patched = '1';
                b.parentNode.replaceChild(nb, b);
                nb.addEventListener('click', (e) => {
                    e.preventDefault(); e.stopPropagation();
                    document.getElementById('custom-wishes-modal').style.display = 'flex';
                });
            }
        });

        // Find wishes container by looking for specific fake wishes or just the container before "ПОЖЕЛАНИЕ"
        let wishesContainer = null;
        document.querySelectorAll('div').forEach(node => {
            if (node.children.length > 3 && node.innerText.includes('Счастья вам')) {
                wishesContainer = node;
            }
        });

        if (wishesContainer && !wishesContainer.dataset.patched) {
            wishesContainer.dataset.patched = '1';
            let w = JSON.parse(localStorage.getItem('wedding_wishes_clone') || '[]');
            if (w.length === 0) {
                wishesContainer.innerHTML = '<div style="text-align:center;padding:20px;color:#000;">Пока нет пожеланий. Будьте первыми!</div>';
            } else {
                wishesContainer.innerHTML = w.map(wish => `<div style="background:rgba(255,255,255,0.8);border-radius:8px;padding:10px;margin:5px;color:#000;"><strong>${wish.name}</strong><p style="margin:5px 0 0;">${wish.text}</p></div>`).join('');
            }
        }
    }, 1000);
});
</script>
<div id="custom-wishes-modal">
    <div class="custom-modal-content">
        <h3 style="margin:0;text-align:center;">Написать пожелание</h3>
        <input type="text" id="cw-name" class="custom-input" placeholder="Ваше имя">
        <textarea id="cw-text" class="custom-input" placeholder="Ваше пожелание" rows="4"></textarea>
        <div style="display:flex;gap:10px;">
            <button id="cw-close" class="custom-btn" style="flex:1;background:#ccc;">Отмена</button>
            <button id="cw-submit" class="custom-btn" style="flex:1;background:#4d792e;color:white;">Отправить</button>
        </div>
    </div>
</div>
<script>
document.getElementById('cw-close').addEventListener('click', () => { document.getElementById('custom-wishes-modal').style.display = 'none'; });
document.getElementById('cw-submit').addEventListener('click', () => {
    const name = document.getElementById('cw-name').value;
    const text = document.getElementById('cw-text').value;
    if (!name.trim() || !text.trim()) { alert('Заполните все поля!'); return; }
    let w = JSON.parse(localStorage.getItem('wedding_wishes_clone') || '[]');
    w.push({name, text});
    localStorage.setItem('wedding_wishes_clone', JSON.stringify(w));
    document.getElementById('custom-wishes-modal').style.display = 'none';
    document.getElementById('cw-name').value = ''; document.getElementById('cw-text').value = '';
    alert('Спасибо за пожелание!');
    // Trigger re-render by clearing patch flag
    document.querySelectorAll('div').forEach(n => { if(n.dataset.patched==='1' && n.innerText.includes('Пока нет пожеланий')) n.dataset.patched = ''; });
});
</script>
"""

if 'custom-wishes-modal' not in html:
    html = html.replace('</body>', custom_script + '</body>')

with open('Original_Clone/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Safely patched index.html.")
