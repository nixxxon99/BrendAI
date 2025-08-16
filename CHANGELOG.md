## v4.1-full — 2025-08-16
- Починен порядок `from __future__ import annotations` в `routers/ai_helper.py`.
- Унифицированы лейблы кнопок: 🧠/🔎/📸/📦 по всему проекту.
- Добавлены константы лейблов в `app/keyboards/menus.py` и импорт их в `routers/main.py`/`ai_helper.py`.
- Исправлено возможное дублирование алиасов POSM-роутера в `app/bot.py`.
- Обновлён `requirements.txt` (зафиксированы версии).
- Добавлен `run_polling.py` для локального теста без вебхука.
- Обновлены `README.md` и `VERSION`.
