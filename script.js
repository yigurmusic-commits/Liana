
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
    
    let selectedRsvp = null;
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
            selectedRsvp = this.classList.contains('btn-yes') ? 'yes' : 'no';
        });
    });
    
    const submitBtn = document.querySelector('.btn-submit');
    const rsvpNameInput = document.querySelector('.form-container input');
    if(submitBtn && rsvpNameInput) {
        submitBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const name = rsvpNameInput.value.trim();
            if (!name) return alert('Введите имя!');
            if (!selectedRsvp) return alert('Выберите один из вариантов ответа!');

            try {
                const res = await fetch('/api/rsvp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, status: selectedRsvp })
                });
                const data = await res.json();
                if (data.success) {
                    alert('Ваш ответ успешно отправлен!');
                    rsvpNameInput.value = '';
                    selectedRsvp = null;
                    formButtons.forEach(b => {
                        b.style.backgroundColor = 'white';
                        b.style.color = '#161413';
                    });
                } else {
                    alert('Ошибка: ' + data.error);
                }
            } catch (e) {
                console.error(e);
                alert('Ошибка соединения с сервером');
            }
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

    async function loadWishes() {
        if (!wishesItems) return;
        try {
            const res = await fetch('/api/wishes');
            const data = await res.json();
            if (data.success) {
                const wishes = data.wishes || [];
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
        } catch (e) {
            console.error('Error loading wishes:', e);
            wishesItems.innerHTML = '<div style="text-align: center; color: red; margin-top: 20px;">Ошибка загрузки пожеланий.</div>';
        }
    }

    if (openWishesModal && wishesModal) {
        openWishesModal.addEventListener('click', () => {
            wishesModal.style.display = 'flex';
        });
        closeWishesModal.addEventListener('click', () => {
            wishesModal.style.display = 'none';
        });
        submitWish.addEventListener('click', async () => {
            const name = wishName.value.trim();
            const text = wishText.value.trim();
            if (!name || !text) {
                alert('Пожалуйста, заполните все поля!');
                return;
            }
            
            try {
                const res = await fetch('/api/wishes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, text })
                });
                const data = await res.json();
                if (data.success) {
                    wishName.value = '';
                    wishText.value = '';
                    wishesModal.style.display = 'none';
                    loadWishes();
                    alert('Спасибо за ваше пожелание!');
                } else {
                    alert('Ошибка: ' + data.error);
                }
            } catch (e) {
                console.error(e);
                alert('Ошибка соединения с сервером');
            }
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
