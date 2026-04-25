const scrape = require('website-scraper');

const options = {
  urls: ['https://www.shaqyru24.kz/ru/view/a3f9a75e-266b-40c4-964d-5fde5e2c9fb6'],
  directory: './Original_Clone',
  sources: [
    { selector: 'img', attr: 'src' },
    { selector: 'link[rel="stylesheet"]', attr: 'href' },
    { selector: 'script', attr: 'src' }
  ],
  recursive: false,
  maxRecursiveDepth: 0,
  request: {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
  }
};

console.log('Начинаю скачивание сайта...');

scrape(options).then((result) => {
    console.log('Готово! Сайт сохранен в папку Original_Clone.');
    console.log('Скачано файлов:', result[0].savedResources.length);
}).catch((err) => {
    console.error('Ошибка при скачивании:', err);
});
