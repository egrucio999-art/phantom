from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SUPABASE_URL = "https://hkwikcffswxoizyevqsh.supabase.co"
SUPABASE_KEY = "sb_publishable_ChkoCcwWUfiif523Osw2-Q_klJYxRJr"

@app.route('/api/reviews', methods=['POST'])
def submit_review():
    try:
        data = request.get_json()
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/reviews",
            json={
                "name": data.get('name',''),
                "service": data.get('service',''),
                "rating": data.get('rating',5),
                "text": data.get('text','')
            },
            headers=headers
        )
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/reviews?select=*&order=id.desc&limit=100",
            headers=headers
        )
        
        return response.json(), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file('index.html')
