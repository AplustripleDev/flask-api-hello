from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # 🟢 โหลดค่าจาก .env

app = Flask(__name__)

# 📦 ดึงค่า ENV มาใช้
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

@app.route('/')
def home():
    return "✨ Hello from Railway LINE API ✨"

# ✅ รองรับ GET และ POST
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook is active.", 200

    body = request.get_json()
    print("📩 ได้รับข้อความ:", body)

    if 'events' in body and body['events']:
        event = body['events'][0]
        reply_token = event.get('replyToken')

        # 🔐 ป้องกันกรณีไม่มี message หรือไม่ใช่ text
        if 'message' in event and event['message'].get('type') == 'text':
            user_msg = event['message']['text']

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
            }
            data = {
                "replyToken": reply_token,
                "messages": [{
                    "type": "text",
                    "text": f"เจ้านายพิมพ์ว่า: {user_msg}"
                }]
            }
            # 💌 ตอบกลับข้อความ
            requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # รับ PORT จาก Railway
    app.run(host="0.0.0.0", port=port)

