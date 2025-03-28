from flask import Flask, request
import os
# ถ้าใช้ .env บนเครื่อง local:
# from dotenv import load_dotenv
# load_dotenv()

from handlers.message_handler import handle_message  # ดึงฟังก์ชันจาก message_handler.py

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Railway LINE Bot", 200

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Webhook is active.", 200

    body = request.get_json()
    print("📩 ได้รับข้อความ:", body)

    if body and "events" in body:
        for event in body["events"]:
            if event.get("type") == "message":
                handle_message(event)

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
