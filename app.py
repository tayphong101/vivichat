from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='public')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/ask', methods=['POST'])
def proxy_ask():
    try:
        data = request.get_json()
        question = data.get('question')
        session_id = data.get('session_id')
        
        if not question or not session_id:
            return jsonify({'error': 'Missing question or session_id'}), 400

        webhook_url = os.getenv('WEBHOOK_URL')
        if not webhook_url:
            return jsonify({'error': 'Webhook URL not configured'}), 500

        response = requests.post(
            webhook_url,
            json={'question': question, 'session_id': session_id},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Error connecting to external API: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)