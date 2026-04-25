const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Подключение к PostgreSQL через переменную окружения DATABASE_URL
let pool;
if (process.env.DATABASE_URL) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: {
        rejectUnauthorized: false
      }
    });

    // Инициализация таблиц, если они не существуют
    pool.query(`
        CREATE TABLE IF NOT EXISTS rsvps (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS wishes (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    `).catch(err => console.error('Error creating tables:', err));
} else {
    console.error('DATABASE_URL is not set!');
}


// API: Сохранить ответ гостя
app.post('/api/rsvp', async (req, res) => {
    if (!pool) return res.status(500).json({ success: false, error: 'Database not connected (missing DATABASE_URL)' });
    try {
        const { name, status } = req.body;
        if (!name) return res.status(400).json({ success: false, error: 'Name is required' });
        
        const result = await pool.query(
            `INSERT INTO rsvps (name, status) VALUES ($1, $2) RETURNING id`, 
            [name, status || 'Unknown']
        );
        res.json({ success: true, id: result.rows[0].id });
    } catch (err) {
        console.error('RSVP Insert Error:', err);
        res.status(500).json({ success: false, error: err.message });
    }
});

// API: Сохранить пожелание
app.post('/api/wishes', async (req, res) => {
    if (!pool) return res.status(500).json({ success: false, error: 'Database not connected (missing DATABASE_URL)' });
    try {
        const { name, text } = req.body;
        if (!name || !text) return res.status(400).json({ success: false, error: 'Name and text are required' });

        const result = await pool.query(
            `INSERT INTO wishes (name, text) VALUES ($1, $2) RETURNING id`,
            [name, text]
        );
        res.json({ success: true, id: result.rows[0].id });
    } catch (err) {
        console.error('Wish Insert Error:', err);
        res.status(500).json({ success: false, error: err.message });
    }
});

// API: Получить пожелания
app.get('/api/wishes', async (req, res) => {
    if (!pool) return res.status(500).json({ success: false, error: 'Database not connected (missing DATABASE_URL)' });
    try {
        const result = await pool.query(`SELECT name, text, created_at FROM wishes ORDER BY created_at ASC`);
        res.json({ success: true, wishes: result.rows });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// API: Получить ответы (для админки)
app.get('/api/rsvps', async (req, res) => {
    if (!pool) return res.status(500).json({ success: false, error: 'Database not connected (missing DATABASE_URL)' });
    try {
        const result = await pool.query(`SELECT name, status, created_at FROM rsvps ORDER BY created_at DESC`);
        res.json({ success: true, rsvps: result.rows });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// Админ-панель
app.get('/api/admin', async (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Панель управления пригласительным</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; }
            h1 { text-align: center; color: #333; }
            .container { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 30px; }
            .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #4d792e; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .badge-yes { background: #d4edda; color: #155724; padding: 5px 10px; border-radius: 20px; font-weight: bold; }
            .badge-no { background: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 20px; font-weight: bold; }
            .badge-unknown { background: #e2e3e5; color: #383d41; padding: 5px 10px; border-radius: 20px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Ответы гостей и Пожелания</h1>
        <div class="container">
            <div class="card">
                <h2>Список гостей (Ответы)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Дата/Время</th>
                            <th>Имя гостя</th>
                            <th>Статус присутствия</th>
                        </tr>
                    </thead>
                    <tbody id="rsvp-table">
                        <tr><td colspan="3" style="text-align: center;">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>Оставленные пожелания</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Дата/Время</th>
                            <th>Имя</th>
                            <th>Текст пожелания</th>
                        </tr>
                    </thead>
                    <tbody id="wishes-table">
                        <tr><td colspan="3" style="text-align: center;">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            function formatTime(iso) {
                return new Date(iso).toLocaleString('ru-RU');
            }
            
            function getStatusBadge(status) {
                if (status.includes('yes') || status.includes('приду')) return '<span class="badge-yes">Да, придет</span>';
                if (status.includes('no') || status.includes('смогу')) return '<span class="badge-no">Не сможет</span>';
                return '<span class="badge-unknown">' + status + '</span>';
            }

            Promise.all([
                fetch('/api/rsvps').then(r => r.json()),
                fetch('/api/wishes').then(r => r.json())
            ]).then(([rsvpData, wishesData]) => {
                const rTable = document.getElementById('rsvp-table');
                if (rsvpData.rsvps && rsvpData.rsvps.length > 0) {
                    rTable.innerHTML = rsvpData.rsvps.map(r => \`
                        <tr>
                            <td>\${formatTime(r.created_at)}</td>
                            <td><strong>\${r.name}</strong></td>
                            <td>\${getStatusBadge(r.status)}</td>
                        </tr>
                    \`).join('');
                } else {
                    rTable.innerHTML = '<tr><td colspan="3" style="text-align:center;">Ответов пока нет.</td></tr>';
                }

                const wTable = document.getElementById('wishes-table');
                if (wishesData.wishes && wishesData.wishes.length > 0) {
                    wTable.innerHTML = wishesData.wishes.slice().reverse().map(w => \`
                        <tr>
                            <td>\${formatTime(w.created_at)}</td>
                            <td><strong>\${w.name}</strong></td>
                            <td>\${w.text}</td>
                        </tr>
                    \`).join('');
                } else {
                    wTable.innerHTML = '<tr><td colspan="3" style="text-align:center;">Пожеланий пока нет.</td></tr>';
                }
            }).catch(err => {
                console.error(err);
                alert('Ошибка загрузки данных');
            });
        </script>
    </body>
    </html>
  `);
});

// Экспорт для Vercel Serverless Functions
module.exports = app;
