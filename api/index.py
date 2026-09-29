from flask import Flask, request, jsonify
import json
import urllib.request
import urllib.error

app = Flask(__name__)

SUPABASE_URL = "НОВЫЙ_URL"
import os
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

@app.route('/api/reviews', methods=['POST'])
def submit_review():
    try:
        data = request.get_json()
        
        payload = json.dumps({
            "name": data.get('name',''),
            "service": data.get('service',''),
            "rating": data.get('rating',5),
            "text": data.get('text','')
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/reviews",
            data=payload,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            result = response.read()
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/reviews?select=*&order=id.desc&limit=100",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
