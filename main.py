from flask import Flask, request
import os
from dotenv import load_dotenv

from handlers.message_handler import handle_message  # ✅ ใช้ handler

load_dotenv()
app = Flask(__name__)

@app.route('/')
def home():
    return "✨ Hello from Railway LINE API ✨"

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.get_json()
    print("📩 ได้รับข้อความ:", body)

    if 'events' in body:
        for event in body['events']:
            if event.get('type') == 'message' and event['message'].get('type') == 'text':
                handle_message(event)

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
