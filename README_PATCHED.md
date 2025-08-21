
# BrendAI — Patched v5.1

Изменения внутри этого билда:

- Реализована HTML-карточка бренда (`brand_card`) и включена в каталоге.
- `/start` всегда показывает главное меню.
- Добавлен `run_polling.py` для локального запуска без вебхука.
- Обновлён `requirements.txt`.

## Локальный запуск

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=xxxx:yyyy   # Windows: set TELEGRAM_BOT_TOKEN=...
python run_polling.py
```

Патч: 2025-08-21T12:26:47.008690
