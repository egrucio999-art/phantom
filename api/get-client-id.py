import json
import hashlib
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_GET(self):
        # Получаем IP клиента (Vercel передает его в заголовке x-forwarded-for)
        ip = self.headers.get("x-forwarded-for", "0.0.0.0").split(",")[0].strip()
        
        # Хешируем IP и берем последние 4 цифры для номера клиента
        # Используем md5, чтобы номер был стабильным для одного и того же IP
        hash_obj = hashlib.md5(ip.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        client_id = hash_int % 9000 + 1000  # От 1000 до 9999
        
        self._send(200, {
            "client_id": client_id,
            "name": f"Клиент #{client_id}"
        })

    def do_OPTIONS(self):
        self._send(204, {})
