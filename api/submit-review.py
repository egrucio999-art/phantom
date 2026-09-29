"""
Vercel Python Serverless Function: приём отзывов → Telegram.
Endpoint: POST /api/submit-review

Токен и chat_id берутся из переменных окружения Vercel:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""
import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_to_telegram(name, service, rating, text):
    if not BOT_TOKEN or not CHAT_ID:
        return False, "Telegram credentials not configured"

    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    message = (
        "🆕 *Новый отзыв на модерацию*\n\n"
        f"*Имя:* {name}\n"
        f"*Направление:* {service}\n"
        f"*Оценка:* {stars} ({rating}/5)\n\n"
        f"*Текст:*\n{text}\n\n"
        "_Скопируй текст, добавь в reviews.json и закоммить_"
    )

    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}"
    except Exception as e:
        return False, str(e)


def validate(body):
    """Возвращает (ok, error_message, cleaned_data)."""
    name = str(body.get("name", "")).strip()[:50]
    service = str(body.get("service", "")).strip()[:50]
    text = str(body.get("text", "")).strip()[:900]
    try:
        rating = int(body.get("rating", 0))
    except (ValueError, TypeError):
        rating = 0

    if len(name) < 2:
        return False, "Имя слишком короткое", None
    if len(text) < 10:
        return False, "Отзыв слишком короткий", None
    if rating < 1 or rating > 5:
        return False, "Оценка от 1 до 5", None

    return True, None, {
        "name": name,
        "service": service or "Другое",
        "rating": rating,
        "text": text
    }


class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self._send(204, {})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw) if raw else {}
        except Exception:
            return self._send(400, {"error": "Invalid JSON"})

        ok, err, data = validate(body)
        if not ok:
            return self._send(400, {"error": err})

        sent, result = send_to_telegram(data["name"], data["service"], data["rating"], data["text"])
        if sent:
            return self._send(200, {"status": "ok"})
        else:
            return self._send(500, {"error": "Не удалось отправить", "detail": result})

    def do_GET(self):
        self._send(405, {"error": "Method not allowed"})
