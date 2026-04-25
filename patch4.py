import json
import re

with open('Original_Clone/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's remove the previous custom script that might have broken React interactions
html = re.sub(r'<script>.*?document\.addEventListener\(\'DOMContentLoaded\'.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<div id="custom-wishes-modal">.*?</div>', '', html, flags=re.DOTALL)
html = re.sub(r'<style>.*?#custom-wishes-modal.*?</style>', '', html, flags=re.DOTALL)
html = re.sub(r'<script>.*?cw-close.*?cw-submit.*?</script>', '', html, flags=re.DOTALL)

# Now inject a cleaner script that intercepts fetch and XHR globally!
custom_script = """
<script>
// Intercept fetch requests to the form submission endpoints
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const url = args[0] && typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url ? args[0].url : '');
    
    // Check if it's a form submission or wish submission (adjust the URL keyword as needed)
    if (url.includes('/api/') || url.includes('submit') || url.includes('wishes') || url.includes('form')) {
        console.log('Intercepted fetch:', url);
        alert('Ваш ответ успешно отправлен!');
        return new Response(JSON.stringify({ success: true }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    
    return originalFetch.apply(this, args);
};

// Intercept XMLHttpRequest
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
        // Mock successful response
        Object.defineProperty(this, 'readyState', { value: 4 });
        Object.defineProperty(this, 'status', { value: 200 });
        Object.defineProperty(this, 'responseText', { value: '{"success":true}' });
        if (this.onreadystatechange) { this.onreadystatechange(); }
        if (this.onload) { this.onload(); }
        return;
    }
    return originalSend.apply(this, args);
};

// Also let's handle the "ПОЖЕЛАНИЕ" button if it opens a modal, we let it.
// If it submits, our fetch interceptor catches it.
// We just need to clear the fake wishes visually. We can do that by finding them and removing them.
document.addEventListener('DOMContentLoaded', () => {
    setInterval(() => {
        const fakeNames = ['Жансая', 'Айнур', 'Динара', 'Айдос', 'Гульмира'];
        document.querySelectorAll('div').forEach(node => {
            if (node.children.length > 3 && node.innerText.includes('Счастья вам')) {
                if (!node.dataset.cleared) {
                    node.dataset.cleared = '1';
                    node.innerHTML = '<div style="text-align:center;padding:20px;color:#000;">Пока нет пожеланий. Будьте первыми!</div>';
                }
            }
        });
        
        // Also if the map button was an anchor, make sure it points to the new link.
        document.querySelectorAll('a').forEach(a => {
            if (a.href && a.href.includes('2gis.com/i147J')) {
                a.href = 'https://go.2gis.com/xlBab';
            }
        });
    }, 1000);
});
</script>
"""

# Append the new script at the end of the body
if 'originalFetch = window.fetch' not in html:
    html = html.replace('</body>', custom_script + '</body>')

with open('Original_Clone/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Applied new fetch interceptor patch.')
