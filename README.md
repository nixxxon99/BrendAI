# BrendAI — v4.1-full

Готовый к запуску Telegram-бот для продаж/обучения (Aiogram 3 + webhook для Render).

## Быстрый запуск (Render)

**Тип:** Web Service  
**Build:** `pip install -r requirements.txt`  
**Start:** `python main.py`

### Переменные окружения
```
API_TOKEN=<токен из @BotFather>
WEBHOOK_URL=https://<ваш-сервис>.onrender.com
WEBHOOK_SECRET=<любой_секрет_без_пробелов>
TIMEZONE=Asia/Almaty

# (Опционально) Google Vision OCR
GOOGLE_APPLICATION_CREDENTIALS=/opt/render/project/src/.gcv/sa.json
GCV_JSON=<полный JSON ключа сервис-аккаунта одной переменной>
```

Проверьте вебхук:
```
https://api.telegram.org/bot<API_TOKEN>/getWebhookInfo
```

## Локальный тест (long-polling)
```
python run_polling.py
```

## Функции
- 🧠 AI эксперт — оффлайн-ответы по БЗ, «наш/не наш», альтернативы.
- 🔎 Каталог брендов — нечеткий поиск, карточки, альтернативы.
- 📸 Фото-анализ — OCR (Vision → Tesseract fallback).
- 📦 POSM списание — лог в CSV `data/posm_log.csv`.

## Данные
- Портфель CSV кладите в `data/` (авто-детект разделителя и кодировки).
- `VERSION`: v4.1-full
