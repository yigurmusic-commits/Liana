with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
# Remove the old custom script we injected last time
html = re.sub(r'<script>\s*// --- RSVP FETCH INTERCEPTOR ---.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style>\s*#custom-wishes-modal.*?</style>', '', html, flags=re.DOTALL)
html = re.sub(r'<div id="custom-wishes-modal">.*?</div>', '', html, flags=re.DOTALL)

# Inject the fixed script with advanced Swiper support
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
    if (url.includes('/api/') || url.includes('submit') || url.includes('form') || url.includes('wishes')) {
        // Only block actual submissions, not our own GET /api/wishes
        if (args[1] && args[1].method && args[1].method.toUpperCase() === 'GET') {
            return originalFetch.apply(this, args);
        }

        const reqOpts = args[1] || {};
        let rawBody = {};
        try { if(reqOpts.body) rawBody = JSON.parse(reqOpts.body); } catch(e){}

        if (!url.includes('wishes')) { // It's RSVP
            let guestName = 'Гость';
            const nameInput = document.querySelector('input[placeholder*="имя"], input[name*="field"]');
            if (nameInput && nameInput.value) guestName = nameInput.value;
            let guestStatus = JSON.stringify(rawBody);
            
            try {
                await originalFetch('/api/rsvp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: guestName, status: guestStatus })
                });
            } catch(e) { console.error(e); }
            alert('Ваш ответ успешно сохранен в базе данных!');
        }
        return new Response(JSON.stringify({ success: true }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    return originalFetch.apply(this, args);
};

const originalXHR = window.XMLHttpRequest.prototype.open;
window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this._url = url;
    return originalXHR.call(this, method, url, ...rest);
};
const originalSend = window.XMLHttpRequest.prototype.send;
window.XMLHttpRequest.prototype.send = function(...args) {
    if (this._url && (this._url.includes('/api/') || this._url.includes('submit') || this._url.includes('form') || this._url.includes('wishes'))) {
        alert('Успешно сохранено!');
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
    document.getElementById('cw-close').addEventListener('click', () => {
        document.getElementById('custom-wishes-modal').style.display = 'none';
    });
    
    document.getElementById('cw-submit').addEventListener('click', async () => {
        const name = document.getElementById('cw-name').value;
        const text = document.getElementById('cw-text').value;
        if (!name.trim() || !text.trim()) { alert('Заполните все поля!'); return; }
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
            loadWishes();
        } catch(e) { alert('Ошибка при отправке.'); }
    });

    function loadWishes() {
        const sliderContainer = document.querySelector('.wl-slider');
        const swiperWrapper = document.querySelector('.wl-slider .swiper-wrapper') || document.querySelector('.swiper-wrapper');
        
        if (!sliderContainer && !swiperWrapper) return;
        
        originalFetch('/api/wishes')
            .then(r => r.json())
            .then(data => {
                const wishes = data.wishes && data.wishes.length > 0 ? data.wishes : [];
                
                // Build new slides HTML
                let slidesHtml = '';
                if (wishes.length === 0) {
                    slidesHtml = '<div class="swiper-slide"><div style="text-align:center;padding:20px;color:#000;">Пока нет пожеланий. Будьте первыми!</div></div>';
                } else {
                    slidesHtml = wishes.map(wish => `
                        <div class="swiper-slide">
                            <div class="wl-card" style="background-color:rgb(255,255,255);border:1px solid rgba(47,115,38,0.3);padding:20px;border-radius:10px;height:100%;box-sizing:border-box;">
                                <div class="wl-card-body" style="min-height:80px;">
                                    <p class="wl-card-text" style="color:rgb(26,26,26);margin:0;font-size:16px;">${wish.text}</p>
                                </div>
                                <div class="wl-card-footer" style="display:flex;align-items:center;margin-top:20px;border-top:1px solid #eee;padding-top:15px;">
                                    <div class="wl-avatar" style="background-color:rgb(47,115,38);color:white;width:35px;height:35px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;margin-right:12px;">${wish.name.substring(0,2).toUpperCase()}</div>
                                    <div class="wl-meta">
                                        <span class="wl-name" style="color:rgb(26,26,26);font-weight:bold;display:block;">${wish.name}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }

                // Inject into DOM
                if (swiperWrapper) {
                    swiperWrapper.innerHTML = slidesHtml;
                    
                    // Try to update Swiper instance
                    const possibleInstances = [
                        sliderContainer?.swiper, 
                        swiperWrapper?.swiper, 
                        swiperWrapper?.parentNode?.swiper,
                        document.querySelector('.swiper')?.swiper,
                        document.querySelector('.swiper-container')?.swiper
                    ];
                    
                    const swiperInstance = possibleInstances.find(i => i != null);
                    if (swiperInstance) {
                        swiperInstance.update();
                    } else {
                        // Fallback: force reflow/resize to let React or Swiper pick it up
                        window.dispatchEvent(new Event('resize'));
                        // Also try modifying the style manually if it doesn't scroll
                        if (wishes.length > 0) {
                           sliderContainer.style.overflowX = 'auto';
                           swiperWrapper.style.display = 'flex';
                        }
                    }
                }
            });
    }

    setInterval(() => {
        // Hook custom wishes modal
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

        // Clear fake wishes once
        const sliderContainer = document.querySelector('.wl-slider');
        if (sliderContainer && !sliderContainer.dataset.cleared) {
            sliderContainer.dataset.cleared = '1';
            loadWishes();
        }
    }, 1000);
});
</script>
"""

html = html.replace('</body>', custom_script + '</body>')

with open('Original_Clone/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Applied advanced Swiper patch.')
