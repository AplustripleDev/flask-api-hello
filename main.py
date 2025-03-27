from flask import Flask, request
import requests
import os

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("4456357c2e14d36894e743d5aa12d7d9")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("iGCAgqUelLX+zqtt1arTWZVSY12uEsBXTaY7yHbOHVNJ36lhtsrzGqEIoiquHYt8BSL/GKSHZubytWRw1+uxIDxnv36/VIDNYGW43u/b3+wyfVzyVK7bkpXl58MTJEmwT/q6ahwrJGxCnCw8Vu232QdB04t89/1O/w1cDnyilFU=")

@app.route('/')
def home():
    return "✨ Hello from Railway LINE API ✨"

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    print("📩 ได้รับข้อความ:", body)

    if 'events' in body and body['events']:
        event = body['events'][0]
        reply_token = event['replyToken']
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
        requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)

    return "OK", 200
