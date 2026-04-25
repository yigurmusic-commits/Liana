const fs = require('fs');

const html = fs.readFileSync('page_source.html', 'utf8');

// Extract JSON
const jsonMatch = html.match(/<script id="__NEXT_DATA__" type="application\/json">([\s\S]*?)<\/script>/);
if (!jsonMatch) {
    console.error('No JSON found');
    process.exit(1);
}

const jsonData = JSON.parse(jsonMatch[1]);
const pageData = jsonData.props.pageProps.pageData.builderPageData;
const container = pageData.blocks[0];
const components = container.components;

let htmlOutput = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>${pageData.title || 'Приглашаем на свадьбу'}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="page-container" style="height: ${container.style.height}; min-height: ${container.style.minHeight}; background-color: ${container.style.backgroundColor};">
`;

let cssOutput = `/* Base styles */
@font-face {
    font-family: 'Kz_DessertScript_kz';
    src: url('fonts/Kz_DessertScript_kz.ttf') format('truetype');
}
@font-face {
    font-family: 'KZOptima';
    src: url('fonts/KZOptima.ttf') format('truetype');
}
@font-face {
    font-family: 'KZPFMonumentaPro-Regular';
    src: url('fonts/KZPFMonumentaPro-Regular.ttf') format('truetype');
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
    width: 100%;
    max-width: 430px; /* Mobile width */
    overflow: hidden;
    margin: 0 auto;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}

.component {
    position: absolute;
    box-sizing: border-box;
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

`;

function toCSS(obj) {
    if (!obj) return '';
    return Object.entries(obj).map(([k, v]) => {
        const kebab = k.replace(/[A-Z]/g, m => "-" + m.toLowerCase());
        return \`\${kebab}: \${v};\`;
    }).join(' ');
}

components.forEach(comp => {
    const s = comp.size;
    const p = comp.position;
    const st = comp.style;
    const d = comp.data;

    let compCss = \`
        width: \${s.width}px;
        height: \${s.height}px;
        top: \${p.y}%;
        left: \${p.x}%;
        z-index: \${p.z};
    \`;
    if (p.x === 50) {
        compCss += \`transform: translateX(-50%);\`;
        if (st.transform) {
             // If there's an additional transform, handle it
             compCss = compCss.replace('transform: translateX(-50%);', \`transform: translateX(-50%) \${st.transform};\`);
        }
    } else {
        if (st.transform) {
            compCss += \`transform: \${st.transform};\`;
        }
    }

    // specific styles
    for (const [k, v] of Object.entries(st)) {
        if (k === 'transform') continue; // handled
        const kebab = k.replace(/[A-Z]/g, m => "-" + m.toLowerCase());
        compCss += \`\n        \${kebab}: \${v};\`;
    }

    cssOutput += \`\n#comp-\${comp.id} { \${compCss} }\`;

    let inner = '';
    let tag = 'div';
    let extraAttrs = '';

    if (comp.type === 'image') {
        tag = 'img';
        extraAttrs = \` src="\${d.src}" alt="\${d.alt || ''}"\`;
    } else if (comp.type === 'text') {
        inner = d.content ? d.content.replace(/\\n/g, '<br>') : '';
        cssOutput += \`\n#comp-\${comp.id} { \${toCSS({
            fontSize: st.fontSize,
            fontFamily: st.fontFamily,
            color: st.color,
            textAlign: st.textAlign,
            fontWeight: st.fontWeight,
            lineHeight: st.lineHeight
        })} }\`;
    } else if (comp.type === 'button') {
        tag = 'a';
        extraAttrs = \` href="\${d.url}" target="_blank"\`;
        inner = d.text;
        cssOutput += \`\n#comp-\${comp.id} {
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            background-color: \${d.backgroundColor};
            color: \${d.textColor};
            border-radius: \${d.borderRadius}px;
            font-size: \${d.fontSize}px;
            font-family: \${d.fontFamily};
            font-weight: \${d.fontWeight};
            border: \${d.borderWidth}px solid \${d.borderColor};
        }\`;
    } else if (comp.type === 'timer') {
        inner = \`
            <div class="timer-inner" data-date="\${d.event_date}">
                <div class="timer-title">\${d.event_title}</div>
                <div class="timer-display">
                    <div class="time-block">
                        <span class="t-num" id="t-days">00</span>
                        <span class="t-label">Дней</span>
                    </div>
                    <div class="time-block">
                        <span class="t-num" id="t-hours">00</span>
                        <span class="t-label">Часов</span>
                    </div>
                    <div class="time-block">
                        <span class="t-num" id="t-mins">00</span>
                        <span class="t-label">Минут</span>
                    </div>
                    <div class="time-block">
                        <span class="t-num" id="t-secs">00</span>
                        <span class="t-label">Секунд</span>
                    </div>
                </div>
            </div>
        \`;
        cssOutput += \`\n#comp-\${comp.id} .timer-inner {
            background-color: \${d.backgroundColor === 'transparent' ? 'transparent' : d.backgroundColor};
            border-radius: \${d.borderRadius}px;
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: \${d.spacing}px;
            height: 100%;
            box-sizing: border-box;
        }
        #comp-\${comp.id} .timer-title {
            font-size: \${d.titleFontSize}px;
            font-family: \${d.titleFontFamily};
            color: \${d.titleColor};
        }
        #comp-\${comp.id} .timer-display {
            display: flex;
            justify-content: space-around;
        }
        #comp-\${comp.id} .time-block {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        #comp-\${comp.id} .t-num {
            font-size: \${d.numbersFontSize}px;
            font-family: \${d.numbersFontFamily};
            color: \${d.numbersColor};
        }
        #comp-\${comp.id} .t-label {
            font-size: \${d.labelsFontSize}px;
            font-family: \${d.labelsFontFamily};
            color: \${d.labelsColor};
        }\`;
    } else if (comp.type === 'form2') {
        inner = \`
            <div class="form-container">
                <input type="text" placeholder="\${d.form_fields[0].placeholder}" required>
                <div class="form-buttons">
                    \${d.form_buttons.map(b => \`<button class="\${b.button_value === 'yes' ? 'btn-yes' : 'btn-no'}">\${b.button_text}</button>\`).join('')}
                </div>
                <button class="btn-submit">\${d.submit_button_text}</button>
            </div>
        \`;
        cssOutput += \`\n#comp-\${comp.id} .form-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            height: 100%;
        }
        #comp-\${comp.id} input {
            font-size: \${d.field_fontSize}px;
            font-family: \${d.field_fontFamily};
            color: \${d.field_color};
            background-color: \${d.field_backgroundColor};
            border: \${d.field_borderWidth}px solid \${d.field_borderColor};
            border-radius: \${d.field_borderRadius}px;
            height: \${d.field_height}px;
            padding: 0 15px;
            box-sizing: border-box;
            outline: none;
        }
        #comp-\${comp.id} .form-buttons {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        #comp-\${comp.id} .form-buttons button {
            font-size: \${d.option_fontSize}px;
            font-family: \${d.option_fontFamily};
            color: \${d.option_color};
            border: 1px solid #ccc;
            border-radius: \${d.option_borderRadius}px;
            height: \${d.option_height}px;
            background: white;
            cursor: pointer;
        }
        #comp-\${comp.id} .btn-submit {
            background-color: \${d.submit_button_backgroundColor};
            color: \${d.submit_button_textColor};
            border-radius: \${d.submit_button_borderRadius}px;
            font-size: \${d.submit_button_fontSize}px;
            font-family: \${d.submit_button_fontFamily};
            height: \${d.submit_button_height}px;
            border: none;
            cursor: pointer;
        }
        \`;
    } else if (comp.type === 'audio-fixed') {
        inner = \`
            <button class="audio-btn" id="audio-btn">
                <span>🎵 \${d.button_text}</span>
                <audio id="bg-audio" loop>
                    <source src="\${d.audio_url}" type="audio/mpeg">
                </audio>
            </button>
        \`;
        cssOutput += \`\n#comp-\${comp.id} {
            position: fixed !important;
            bottom: 20px;
            right: 20px;
            left: auto !important;
            top: auto !important;
            width: auto !important;
            height: auto !important;
            z-index: 9999;
            transform: none !important;
        }
        #comp-\${comp.id} .audio-btn {
            background-color: \${d.button_color};
            color: \${d.text_color};
            font-family: \${d.font_family};
            font-size: \${d.font_size}px;
            height: \${d.button_height}px;
            padding: 0 20px;
            border-radius: 30px;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        @media (max-width: 430px) {
            #comp-\${comp.id} {
                bottom: 20px;
                right: 20px;
            }
        }\`;
    } else if (comp.type === 'wishes-list' || comp.type === 'fixed-wishes') {
        // basic placeholder
        inner = \`<div style="display:flex; justify-content:center; align-items:center; height:100%; width:100%; background: \${d.card_bg_color||d.button_color}; color: \${d.text_color||'#000'}; border-radius: 10px; padding: 10px; box-sizing: border-box; text-align:center;">\${d.button_text}</div>\`;
        if (comp.type === 'fixed-wishes') {
            cssOutput += \`\n#comp-\${comp.id} {
                position: fixed !important;
                bottom: 20px;
                left: 20px;
                top: auto !important;
                width: auto !important;
                height: auto !important;
                z-index: 9999;
                transform: none !important;
            }
            #comp-\${comp.id} div {
                height: \${d.button_height}px !important;
                border-radius: 30px !important;
                padding: 0 20px !important;
                font-family: \${d.font_family};
                font-size: \${d.font_size}px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                cursor: pointer;
            }\`;
        }
    } else if (comp.type === 'shape') {
        if (d.shapeType === 'circle') {
            cssOutput += \`\n#comp-\${comp.id} { border-radius: 50%; }\`;
        }
    }

    let inlineStyle = '';
    if (comp.type === 'text') {
        // remove inline font sizing for texts as they are in css, just in case
    }
    
    htmlOutput += \`        <\${tag} id="comp-\${comp.id}" class="component"\${extraAttrs}>\${inner}</\${tag}>\n\`;
});

htmlOutput += \`    </div>
    <script src="script.js"></script>
</body>
</html>\`;

fs.writeFileSync('index.html', htmlOutput);
fs.writeFileSync('style.css', cssOutput);

const scriptOutput = \`
// Audio player
document.addEventListener('DOMContentLoaded', () => {
    const audioBtn = document.getElementById('audio-btn');
    const audio = document.getElementById('bg-audio');
    let isPlaying = false;

    if (audioBtn && audio) {
        audioBtn.addEventListener('click', () => {
            if (isPlaying) {
                audio.pause();
                audioBtn.querySelector('span').innerText = '🎵 Музыка (Выкл)';
            } else {
                audio.play();
                audioBtn.querySelector('span').innerText = '🎵 Музыка (Вкл)';
            }
            isPlaying = !isPlaying;
        });
    }

    // Timer
    const timerInner = document.querySelector('.timer-inner');
    if (timerInner) {
        const targetDate = new Date(timerInner.getAttribute('data-date')).getTime();
        
        setInterval(() => {
            const now = new Date().getTime();
            const distance = targetDate - now;

            if (distance < 0) {
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            document.getElementById('t-days').innerText = days.toString().padStart(2, '0');
            document.getElementById('t-hours').innerText = hours.toString().padStart(2, '0');
            document.getElementById('t-mins').innerText = minutes.toString().padStart(2, '0');
            document.getElementById('t-secs').innerText = seconds.toString().padStart(2, '0');
        }, 1000);
    }
    
    // Form buttons interactivity
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
            alert('Спасибо за ваш ответ!');
        });
    }
});
\`;

fs.writeFileSync('script.js', scriptOutput);

console.log('Successfully generated index.html, style.css, and script.js');
