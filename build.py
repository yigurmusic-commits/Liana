import json
import re

with open('page_source.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">([\s\S]*?)</script>', html)
if not match:
    print("No JSON found")
    exit(1)

json_data = json.loads(match.group(1))
page_data = json_data['props']['pageProps']['pageData']['builderPageData']
container = page_data['blocks'][0]
components = container['components']

# Container dimensions — original uses 430px wide mobile frame
CONTAINER_WIDTH = 430
CONTAINER_HEIGHT_PX = int(container['style']['height'].replace('px', '').strip())

html_output = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{page_data.get('title', 'Приглашаем на свадьбу')}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="page-container">
"""

css_output = """/* Base styles */
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Montserrat:wght@400;600&display=swap');

@font-face {
    font-family: 'Kz_DessertScript_kz';
    src: local('Caveat');
}
@font-face {
    font-family: 'KZOptima';
    src: local('Cormorant Garamond');
}
@font-face {
    font-family: 'KZPFMonumentaPro-Regular';
    src: local('Cinzel');
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    margin: 0;
    padding: 0;
    background-color: #141524;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    overflow-x: hidden;
}

.page-container {
    position: relative;
    width: 430px;
    height: """ + str(CONTAINER_HEIGHT_PX) + """px;
    background-color: #ffffff;
    overflow: hidden;
    margin: 0 auto;
    flex-shrink: 0;
}

@media (max-width: 430px) {
    .page-container {
        width: 100vw;
        height: """ + str(CONTAINER_HEIGHT_PX) + """px;
        transform-origin: top left;
    }
}

.component {
    position: absolute;
    box-sizing: border-box;
}

img.component {
    display: block;
}

@keyframes wobble {
    0% { transform: rotate(0deg); }
    15% { transform: rotate(-5deg); }
    30% { transform: rotate(5deg); }
    45% { transform: rotate(-3deg); }
    60% { transform: rotate(3deg); }
    75% { transform: rotate(-1deg); }
    100% { transform: rotate(0deg); }
}
"""

def map_font(f_family):
    if not f_family: return "'Cormorant Garamond', serif"
    if 'Kz_DessertScript_kz' in f_family: return "'Caveat', cursive"
    if 'KZOptima' in f_family: return "'Cormorant Garamond', serif"
    if 'KZPFMonumentaPro' in f_family: return "'Cinzel', serif"
    return f_family

for comp in components:
    s = comp['size']
    p = comp['position']
    st = comp['style']
    d = comp['data']

    w = s['width']   # px
    h = s['height']  # px

    # x is percentage of CONTAINER_WIDTH, represents center of component
    # y is percentage of CONTAINER_HEIGHT_PX, represents top of component
    left_px = (p['x'] / 100.0 * CONTAINER_WIDTH) - (w / 2.0)
    top_px  = (p['y'] / 100.0 * CONTAINER_HEIGHT_PX) - (h / 2.0)
    z       = p['z']

    comp_css = f"""
    width: {w}px;
    height: {h}px;
    top: {top_px:.2f}px;
    left: {left_px:.2f}px;
    z-index: {z};
"""

    # Apply style properties from component style
    skip_keys = {'width', 'height', 'fontFamily', 'fontSize', 'color', 'textAlign', 'fontWeight', 'lineHeight'}
    for k, v in st.items():
        if k in skip_keys or v is None:
            continue
        if k == 'transform':
            # We'll handle transform specially — combine with translateX(0)
            comp_css += f"    transform: {v};\n"
            continue
        kebab = re.sub(r'[A-Z]', lambda m: '-' + m.group(0).lower(), k)
        # Handle WebkitMaskImage → -webkit-mask-image
        kebab = re.sub(r'^webkit-', '-webkit-', kebab)
        comp_css += f"    {kebab}: {v};\n"

    css_output += f"\n#comp-{comp['id']} {{{comp_css}}}"

    inner = ''
    tag = 'div'
    extra_attrs = ''

    ctype = comp['type']
    if ctype == 'image':
        tag = 'img'
        extra_attrs = f' src="{d.get("src", "")}" alt="{d.get("alt", "")}"'
        obj_fit = st.get('objectFit', 'cover')
        css_output += f"\n#comp-{comp['id']} {{ object-fit: {obj_fit}; }}"

    elif ctype == 'text':
        content = d.get('content', '').replace('\\n', '<br>').replace('\n', '<br>')
        if 'Игорь' in content and 'Анна' in content:
            content = content.replace('Игорь & Анна', 'Мейрлен & Лиана')
            content = content.replace('Игорь', 'Мейрлен').replace('Анна', 'Лиана')
        if '13' in content and 'сентября' in content and '2026' in content:
            content = content.replace('13 сентября 2026', '15 августа 17:00')
        inner = content
        font_family = map_font(st.get('fontFamily', ''))
        font_size   = st.get('fontSize', '16px')
        color       = st.get('color', '#000')
        text_align  = st.get('textAlign', 'left')
        font_weight = st.get('fontWeight', 'normal')
        line_height = st.get('lineHeight', '1.4')
        animation   = st.get('animation', '')
        anim_css = f"animation: {animation};" if animation and animation != 'none' else ''
        css_output += f"""
#comp-{comp['id']} {{
    display: flex;
    align-items: center;
    justify-content: { 'center' if text_align == 'center' else 'flex-start' };
    font-size: {font_size};
    font-family: {font_family};
    color: {color};
    text-align: {text_align};
    font-weight: {font_weight};
    line-height: {line_height};
    white-space: pre-wrap;
    overflow: visible;
    {anim_css}
}}"""

    elif ctype == 'button':
        tag = 'a'
        extra_attrs = f' href="{d.get("url", "")}" target="_blank"'
        inner = d.get('text', '')
        bg_color    = d.get('backgroundColor', '#4d792e')
        text_color  = d.get('textColor', '#ffffff')
        border_r    = d.get('borderRadius', 90)
        font_size   = d.get('fontSize', 16)
        font_family = map_font(d.get('fontFamily', ''))
        font_weight = d.get('fontWeight', 600)
        border_w    = d.get('borderWidth', 0)
        border_col  = d.get('borderColor', bg_color)
        css_output += f"""
#comp-{comp['id']} {{
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    background-color: {bg_color};
    color: {text_color};
    border-radius: {border_r}px;
    font-size: {font_size}px;
    font-family: {font_family};
    font-weight: {font_weight};
    border: {border_w}px solid {border_col};
    letter-spacing: 0.05em;
}}"""

    elif ctype == 'timer':
        inner = f"""
            <div class="timer-inner" data-date="{d.get('event_date')}">
                <div class="timer-title">{d.get('event_title')}</div>
                <div class="timer-display">
                    <div class="time-block"><span class="t-num" id="t-days">00</span><span class="t-label">Дней</span></div>
                    <div class="time-block"><span class="t-num" id="t-hours">00</span><span class="t-label">Часов</span></div>
                    <div class="time-block"><span class="t-num" id="t-mins">00</span><span class="t-label">Минут</span></div>
                    <div class="time-block"><span class="t-num" id="t-secs">00</span><span class="t-label">Секунд</span></div>
                </div>
            </div>
        """
        css_output += f"""
#comp-{comp['id']} .timer-inner {{
    background-color: transparent;
    border-radius: {d.get('borderRadius', 8)}px;
    padding: 20px;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: {d.get('spacing', 12)}px;
    height: 100%;
    box-sizing: border-box;
}}
#comp-{comp['id']} .timer-title {{
    font-size: {d.get('titleFontSize', 14)}px;
    font-family: {map_font(d.get('titleFontFamily', ''))};
    color: {d.get('titleColor', '#4d792e')};
}}
#comp-{comp['id']} .timer-display {{ display: flex; justify-content: space-around; }}
#comp-{comp['id']} .time-block {{ display: flex; flex-direction: column; align-items: center; gap: 4px; }}
#comp-{comp['id']} .t-num {{ font-size: {d.get('numbersFontSize', 24)}px; font-family: {map_font(d.get('numbersFontFamily', ''))}; color: {d.get('numbersColor', '#4d792e')}; font-weight: 600; }}
#comp-{comp['id']} .t-label {{ font-size: {d.get('labelsFontSize', 10)}px; font-family: {map_font(d.get('labelsFontFamily', ''))}; color: {d.get('labelsColor', '#4d792e')}; text-transform: uppercase; letter-spacing: 0.05em; }}
"""

    elif ctype == 'form2':
        fields = d.get('form_fields', [{}])
        buttons = d.get('form_buttons', [])
        buttons_html = ''.join([
            f'<button class="{"btn-yes" if b.get("button_value") == "yes" else "btn-no"}">{b.get("button_text")}</button>'
            for b in buttons
        ])
        inner = f"""
            <div class="form-container">
                <input type="text" placeholder="{fields[0].get('placeholder', '')}" required>
                <div class="form-buttons">{buttons_html}</div>
                <button class="btn-submit">{d.get('submit_button_text', 'Отправить')}</button>
            </div>
        """
        field_ff = map_font(d.get('field_fontFamily', ''))
        opt_ff   = map_font(d.get('option_fontFamily', ''))
        sub_ff   = map_font(d.get('submit_button_fontFamily', ''))
        css_output += f"""
#comp-{comp['id']} .form-container {{ display: flex; flex-direction: column; gap: 12px; height: 100%; }}
#comp-{comp['id']} input {{
    font-size: {d.get('field_fontSize', 15)}px;
    font-family: {field_ff};
    color: {d.get('field_color', '#347632')};
    background-color: {d.get('field_backgroundColor', '#ffffff')};
    border: {d.get('field_borderWidth', 2)}px solid {d.get('field_borderColor', '#347632')};
    border-radius: {d.get('field_borderRadius', 24)}px;
    height: {d.get('field_height', 48)}px;
    padding: 0 15px;
    box-sizing: border-box;
    outline: none;
    width: 100%;
}}
#comp-{comp['id']} .form-buttons {{ display: flex; flex-direction: column; gap: 10px; }}
#comp-{comp['id']} .form-buttons button {{
    font-size: {d.get('option_fontSize', 15)}px;
    font-family: {opt_ff};
    color: {d.get('option_color', '#161413')};
    border: 2px solid {d.get('field_borderColor', '#347632')};
    border-radius: {d.get('option_borderRadius', 24)}px;
    height: {d.get('option_height', 56)}px;
    background: white;
    cursor: pointer;
    width: 100%;
    transition: background 0.2s, color 0.2s;
}}
#comp-{comp['id']} .btn-submit {{
    background-color: {d.get('submit_button_backgroundColor', '#347632')};
    color: {d.get('submit_button_textColor', '#ffffff')};
    border-radius: {d.get('submit_button_borderRadius', 24)}px;
    font-size: {d.get('submit_button_fontSize', 17)}px;
    font-family: {sub_ff};
    height: {d.get('submit_button_height', 56)}px;
    border: none;
    cursor: pointer;
    width: 100%;
}}
"""

    elif ctype == 'audio-fixed':
        inner = f"""
            <button class="audio-btn" id="audio-btn">
                <span>🎵 {d.get('button_text', 'Музыка')}</span>
                <audio id="bg-audio" loop><source src="{d.get('audio_url')}" type="audio/mpeg"></audio>
            </button>
        """
        ff = map_font(d.get('font_family', ''))
        css_output += f"""
#comp-{comp['id']} {{
    position: fixed !important;
    bottom: 20px;
    right: 20px;
    left: auto !important;
    top: auto !important;
    width: auto !important;
    height: auto !important;
    z-index: 9999;
    transform: none !important;
}}
#comp-{comp['id']} .audio-btn {{
    background-color: {d.get('button_color', '#4d792e')};
    color: {d.get('text_color', '#ffffff')};
    font-family: {ff};
    font-size: {d.get('font_size', 17)}px;
    height: {d.get('button_height', 54)}px;
    padding: 0 20px;
    border-radius: 30px;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 8px;
}}
"""

    elif ctype in ['wishes-list', 'fixed-wishes']:
        bg_col = d.get('card_bg_color', d.get('button_color', '#fff'))
        tc     = d.get('text_color', '#ffffff')
        ff     = map_font(d.get('font_family', ''))
        btn_h  = d.get('button_height', 54)
        
        if ctype == 'fixed-wishes':
            inner = f'<div class="wishes-btn" id="open-wishes-modal">{d.get("button_text", "Оставить пожелание")}</div>'
            css_output += f"""
#comp-{comp['id']} {{
    position: fixed !important;
    bottom: 20px;
    left: 20px;
    top: auto !important;
    width: auto !important;
    height: auto !important;
    z-index: 9999;
    transform: none !important;
}}
#comp-{comp['id']} .wishes-btn {{
    background-color: {d.get('button_color', '#4d792e')};
    color: {tc};
    font-family: {ff};
    font-size: {d.get('font_size', 17)}px;
    height: {btn_h}px;
    padding: 0 20px;
    border-radius: 30px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}}
"""
        else:
            inner = f'''
            <div class="wishes-container" style="width: 100%; height: 100%; display: flex; flex-direction: column; overflow: hidden;">
                <div id="wishes-items" style="flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 10px;">
                    <!-- Wishes will be loaded here by JS -->
                </div>
            </div>
            '''
            css_output += f"""
#comp-{comp['id']} {{
    background: {bg_col};
    border-radius: 10px;
    overflow: hidden;
}}
"""

    elif ctype == 'shape':
        shape_type = d.get('shapeType', 'square')
        if shape_type == 'circle':
            css_output += f"\n#comp-{comp['id']} {{ border-radius: 50%; }}"

    html_output += f'        <{tag} id="comp-{comp["id"]}" class="component"{extra_attrs}>{inner}</{tag}>\n'

html_output += """
        <div id="wishes-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; align-items: center; justify-content: center;">
            <div style="background: white; padding: 20px; border-radius: 10px; width: 80%; max-width: 350px; display: flex; flex-direction: column; gap: 10px; font-family: sans-serif;">
                <h3 style="margin: 0; text-align: center; color: black;">Написать пожелание</h3>
                <input type="text" id="wish-name" placeholder="Ваше имя" style="padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <textarea id="wish-text" placeholder="Ваше пожелание" rows="4" style="padding: 10px; border: 1px solid #ccc; border-radius: 5px;"></textarea>
                <div style="display: flex; gap: 10px;">
                    <button id="close-wishes-modal" style="flex: 1; padding: 10px; border: none; background: #ccc; border-radius: 5px; cursor: pointer;">Отмена</button>
                    <button id="submit-wish" style="flex: 1; padding: 10px; border: none; background: #4d792e; color: white; border-radius: 5px; cursor: pointer;">Отправить</button>
                </div>
            </div>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_output)
with open('style.css', 'w', encoding='utf-8') as f:
    f.write(css_output)

script_output = """
document.addEventListener('DOMContentLoaded', () => {
    const audioBtn = document.getElementById('audio-btn');
    const audio = document.getElementById('bg-audio');
    let isPlaying = false;

    if (audioBtn && audio) {
        audioBtn.addEventListener('click', () => {
            if (isPlaying) {
                audio.pause();
                audioBtn.querySelector('span').innerText = '🎵 Музыка';
            } else {
                audio.play();
                audioBtn.querySelector('span').innerText = '🎵 Музыка ♪';
            }
            isPlaying = !isPlaying;
        });
    }

    const timerInner = document.querySelector('.timer-inner');
    if (timerInner) {
        const targetDate = new Date(timerInner.getAttribute('data-date')).getTime();
        
        function updateTimer() {
            const now = new Date().getTime();
            const distance = targetDate - now;

            if (distance < 0) return;

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            document.getElementById('t-days').innerText = days.toString().padStart(2, '0');
            document.getElementById('t-hours').innerText = hours.toString().padStart(2, '0');
            document.getElementById('t-mins').innerText = minutes.toString().padStart(2, '0');
            document.getElementById('t-secs').innerText = seconds.toString().padStart(2, '0');
        }
        updateTimer();
        setInterval(updateTimer, 1000);
    }
    
    const formButtons = document.querySelectorAll('.form-buttons button');
    formButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            formButtons.forEach(b => {
                b.style.backgroundColor = 'white';
                b.style.color = '#161413';
            });
            this.style.backgroundColor = '#347632';
            this.style.color = 'white';
        });
    });
    
    const submitBtn = document.querySelector('.btn-submit');
    if(submitBtn) {
        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Ваш ответ успешно отправлен!');
        });
    }

    // Wishes logic
    const wishesItems = document.getElementById('wishes-items');
    const openWishesModal = document.getElementById('open-wishes-modal');
    const wishesModal = document.getElementById('wishes-modal');
    const closeWishesModal = document.getElementById('close-wishes-modal');
    const submitWish = document.getElementById('submit-wish');
    const wishName = document.getElementById('wish-name');
    const wishText = document.getElementById('wish-text');

    function loadWishes() {
        if (!wishesItems) return;
        const wishes = JSON.parse(localStorage.getItem('wedding_wishes') || '[]');
        if (wishes.length === 0) {
            wishesItems.innerHTML = '<div style="text-align: center; color: #666; margin-top: 20px;">Пока нет пожеланий. Будьте первыми!</div>';
            return;
        }
        wishesItems.innerHTML = wishes.map(w => `
            <div style="background: rgba(255,255,255,0.8); border-radius: 8px; padding: 10px; color: #000;">
                <strong>${w.name}</strong>
                <p style="margin: 5px 0 0 0; font-size: 14px;">${w.text}</p>
            </div>
        `).join('');
    }

    if (openWishesModal && wishesModal) {
        openWishesModal.addEventListener('click', () => {
            wishesModal.style.display = 'flex';
        });
        closeWishesModal.addEventListener('click', () => {
            wishesModal.style.display = 'none';
        });
        submitWish.addEventListener('click', () => {
            const name = wishName.value.trim();
            const text = wishText.value.trim();
            if (!name || !text) {
                alert('Пожалуйста, заполните все поля!');
                return;
            }
            const wishes = JSON.parse(localStorage.getItem('wedding_wishes') || '[]');
            wishes.push({name, text});
            localStorage.setItem('wedding_wishes', JSON.stringify(wishes));
            wishName.value = '';
            wishText.value = '';
            wishesModal.style.display = 'none';
            loadWishes();
            alert('Спасибо за ваше пожелание!');
        });
    }
    
    loadWishes();

    // Scale page to fit viewport on mobile
    function scaleContainer() {
        const container = document.querySelector('.page-container');
        if (!container) return;
        const vw = window.innerWidth;
        if (vw < 430) {
            const scale = vw / 430;
            container.style.transform = 'scale(' + scale + ')';
            container.style.transformOrigin = 'top left';
            container.style.width = '430px';
            document.body.style.height = (3600 * scale) + 'px';
        } else {
            container.style.transform = '';
            container.style.width = '430px';
            document.body.style.height = '';
        }
    }
    scaleContainer();
    window.addEventListener('resize', scaleContainer);
});
"""

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(script_output)

print("Success! Container:", CONTAINER_WIDTH, "x", CONTAINER_HEIGHT_PX)
