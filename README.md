# PHANTOM Digital Services

Статический сайт конфиденциальных цифровых услуг. Двуязычный (RU / UK).

## Структура

- `index.html` — главная
- `reviews.html` — страница отзывов с фильтрами и пагинацией
- `reviews.json` — отзывы (RU + UK)
- `queue.json` — очередь отзывов для автопубликации
- `lang.js` — переключение языка
- `api/submit-review.py` — Vercel Function, приём формы → Telegram
- `scripts/` — утилиты
- `.github/workflows/add-review.yml` — cron-автодобавление

## Деплой

Vercel подхватывает из GitHub автоматически при push в `main`.

## Переменные окружения

На Vercel должны быть заданы:
- `TELEGRAM_BOT_TOKEN` — токен бота для уведомлений
- `TELEGRAM_CHAT_ID` — ID чата для модерации

## Обновление отзывов

- Добавить новый: отредактировать `reviews.json`, закоммитить.
- Автоматически: cron добавляет из `queue.json` 3 раза в неделю.
- Полный сброс: `python3 scripts/generate_reviews.py`.

## Контакт

Telegram: @kopen005
