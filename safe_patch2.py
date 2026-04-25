with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Safe string replacement for JSON payload
html = html.replace('Игорь \\u0026 Анна', 'Мейрлен \\u0026 Лиана')
html = html.replace('Игорь & Анна', 'Мейрлен & Лиана')
html = html.replace('ИГОРЬ \\u0026 АННА', 'МЕЙРЛЕН \\u0026 ЛИАНА')
html = html.replace('ИГОРЬ & АННА', 'МЕЙРЛЕН & ЛИАНА')
html = html.replace('13 сентября 2026', '15 августа 18:00')
html = html.replace('13 сентября в 12:00', '15 августа в 18:00')
html = html.replace('https://2gis.com/i147J', 'https://go.2gis.com/xlBab')

# Inject fetch interceptor and custom wishes clearer
custom_script = """
<script>
// Intercept fetch requests to the form submission endpoints
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const url = args[0] && typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url ? args[0].url : '');
    
    if (url.includes('/api/') || url.includes('submit') || url.includes('wishes') || url.includes('form')) {
        console.log('Intercepted fetch:', url);
        alert('Ваш ответ успешно отправлен!');
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
    if (this._url && (this._url.includes('/api/') || this._url.includes('submit') || this._url.includes('wishes') || this._url.includes('form'))) {
        console.log('Intercepted XHR:', this._url);
        alert('Ваш ответ успешно отправлен!');
        Object.defineProperty(this, 'readyState', { value: 4 });
        Object.defineProperty(this, 'status', { value: 200 });
        Object.defineProperty(this, 'responseText', { value: '{"success":true}' });
        if (this.onreadystatechange) { this.onreadystatechange(); }
        if (this.onload) { this.onload(); }
        return;
    }
    return originalSend.apply(this, args);
};

document.addEventListener('DOMContentLoaded', () => {
    setInterval(() => {
        // Clear fake wishes
        document.querySelectorAll('div').forEach(node => {
            if (node.children.length > 3 && node.innerText.includes('Счастья вам')) {
                if (!node.dataset.cleared) {
                    node.dataset.cleared = '1';
                    node.innerHTML = '<div style="text-align:center;padding:20px;color:#000;">Пока нет пожеланий. Будьте первыми!</div>';
                }
            }
        });
        
        // Ensure map button gets updated if it's rendered late
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
print('Patch applied successfully using safe string replacements!')
