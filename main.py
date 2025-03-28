from flask import Flask, request
import os
import base64
import json

# ✅ ฟังก์ชันเพิ่ม padding ก่อน decode base64
def add_padding(base64_str):
    padding_needed = 4 - (len(base64_str) % 4)
    if padding_needed and padding_needed != 4:
        base64_str += "=" * padding_needed
    return base64_str

# ✅ แปลง base64 JSON → credentials.json
credentials_base64 = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if credentials_base64:
    credentials_base64 = add_padding(credentials_base64)  # 🧸เพิ่มบรรทัดนี้ค่ะ
    credentials_json = base64.b64decode(credentials_base64).decode("utf-8")
    with open("credentials.json", "w") as f:
        f.write(credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

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
