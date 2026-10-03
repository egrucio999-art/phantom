"""
Vercel Python Function: приём заявок → Telegram.
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
"""
import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def esc(s):
    for ch in "_*[]()~`>#+-=|{}.!":
        s = s.replace(ch, "\\" + ch)
    return s


def send_tg(name, topic, message, contact):
    if not BOT_TOKEN or not CHAT_ID:
        return False, "not configured"
    text = (
        "🔔 *Новая заявка PHANTOM*\n\n"
        f"👤 Имя: {esc(name)}\n"
        f"📌 Направление: {esc(topic)}\n"
        f"📝 Задача: {esc(message)}\n"
        f"📞 Контакт: {esc(contact)}"
    )
    data = json.dumps({
        "chat_id": CHAT_ID, "text": text,
        "parse_mode": "MarkdownV2", "disable_web_page_preview": True
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return True, r.read().decode("utf-8")
    except Exception as e:
        return False, str(e)


def validate(body):
    name = str(body.get("name", "")).strip()[:100]
    topic = str(body.get("topic", "")).strip()[:100]
    message = str(body.get("message", "")).strip()[:2000]
    contact = str(body.get("contact", "")).strip()[:200]
    if len(name) < 2: return False, "Имя слишком короткое", None
    if len(topic) < 2: return False, "Направление не выбрано", None
    if len(message) < 10: return False, "Сообщение слишком короткое", None
    if len(contact) < 3: return False, "Контакт слишком короткий", None
    return True, None, {"name": name, "topic": topic, "message": message, "contact": contact}


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
        sent, result = send_tg(data["name"], data["topic"], data["message"], data["contact"])
        if sent:
            return self._send(200, {"status": "ok"})
        return self._send(500, {"error": "Не отправлено", "detail": result})

    def do_GET(self):
        self._send(405, {"error": "Method not allowed"})
