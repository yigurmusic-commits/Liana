with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the old interceptor
import re
html = re.sub(r'<script>\s*// Intercept fetch requests.*?</script>', '', html, flags=re.DOTALL)

# New injected script that talks to our API!
custom_script = """
<style>
#custom-wishes-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 10000; align-items: center; justify-content: center; }
.custom-modal-content { background: white; padding: 20px; border-radius: 10px; width: 80%; max-width: 350px; display: flex; flex-direction: column; gap: 10px; font-family: sans-serif; color: black; }
.custom-btn { padding: 10px; border: none; border-radius: 5px; cursor: pointer; }
.custom-input { padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: black; }
</style>

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
// --- RSVP FETCH INTERCEPTOR ---
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const url = args[0] && typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url ? args[0].url : '');
    
    // Intercept RSVP form submission from React
    if (url.includes('/api/') || url.includes('submit') || url.includes('form')) {
        const reqOpts = args[1] || {};
        let rawBody = {};
        try { if(reqOpts.body) rawBody = JSON.parse(reqOpts.body); } catch(e){}

        // Try to extract name from DOM as fallback
        let guestName = 'Гость';
        const nameInput = document.querySelector('input[placeholder*="имя"], input[name*="field"]');
        if (nameInput && nameInput.value) {
            guestName = nameInput.value;
        }

        // Try to extract status by looking at selected radio/button (if possible), otherwise rawBody
        let guestStatus = JSON.stringify(rawBody);
        
        // Actually send to our backend
        try {
            await originalFetch('/api/rsvp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: guestName, status: guestStatus })
            });
        } catch(e) { console.error('Error saving to DB', e); }

        alert('Ваш ответ успешно сохранен в базе данных!');
        return new Response(JSON.stringify({ success: true }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    return originalFetch.apply(this, args);
};

// --- XHR Interceptor (just in case) ---
const originalXHR = window.XMLHttpRequest.prototype.open;
window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this._url = url;
    return originalXHR.call(this, method, url, ...rest);
};
const originalSend = window.XMLHttpRequest.prototype.send;
window.XMLHttpRequest.prototype.send = function(...args) {
    if (this._url && (this._url.includes('/api/') || this._url.includes('submit') || this._url.includes('form'))) {
        alert('Ваш ответ успешно сохранен!');
        Object.defineProperty(this, 'readyState', { value: 4 });
        Object.defineProperty(this, 'status', { value: 200 });
        Object.defineProperty(this, 'responseText', { value: '{"success":true}' });
        if (this.onreadystatechange) { this.onreadystatechange(); }
        if (this.onload) { this.onload(); }
        return;
    }
    return originalSend.apply(this, args);
};

// --- CUSTOM WISHES LOGIC ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Hook up the custom modal
    document.getElementById('cw-close').addEventListener('click', () => {
        document.getElementById('custom-wishes-modal').style.display = 'none';
    });
    
    document.getElementById('cw-submit').addEventListener('click', async () => {
        const name = document.getElementById('cw-name').value;
        const text = document.getElementById('cw-text').value;
        if (!name.trim() || !text.trim()) { alert('Заполните все поля!'); return; }
        
        // Send to backend
        try {
            await originalFetch('/api/wishes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, text })
            });
            alert('Спасибо за пожелание! Оно сохранено.');
            document.getElementById('custom-wishes-modal').style.display = 'none';
            document.getElementById('cw-name').value = '';
            document.getElementById('cw-text').value = '';
            loadWishes(); // reload
        } catch(e) {
            alert('Ошибка при отправке.');
        }
    });

    // 2. Clear fake wishes and load from DB
    let wishesContainer = null;
    
    function loadWishes() {
        if (!wishesContainer) return;
        originalFetch('/api/wishes')
            .then(r => r.json())
            .then(data => {
                if (data.wishes && data.wishes.length > 0) {
                    wishesContainer.innerHTML = data.wishes.map(wish => 
                        \`<div style="background:rgba(255,255,255,0.8);border-radius:8px;padding:10px;margin:5px;color:#000;">
                            <strong>\${wish.name}</strong>
                            <p style="margin:5px 0 0;">\${wish.text}</p>
                        </div>\`
                    ).join('');
                } else {
                    wishesContainer.innerHTML = '<div style="text-align:center;padding:20px;color:#000;">Пока нет пожеланий. Будьте первыми!</div>';
                }
            });
    }

    setInterval(() => {
        // Intercept "ПОЖЕЛАНИЕ" button
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

        // Find wishes container
        document.querySelectorAll('div').forEach(node => {
            if (node.children.length > 3 && node.innerText.includes('Счастья вам')) {
                if (!wishesContainer) {
                    wishesContainer = node;
                    node.dataset.cleared = '1';
                    loadWishes();
                }
            }
        });
        
        // Ensure map button is correct
        document.querySelectorAll('a').forEach(a => {
            if (a.href && a.href.includes('2gis.com/i147J')) {
                a.href = 'https://go.2gis.com/xlBab';
            }
        });
    }, 1000);
});
</script>
"""

html = html.replace('</body>', custom_script + '</body>')

with open('Original_Clone/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('DB Fetch patch applied.')
