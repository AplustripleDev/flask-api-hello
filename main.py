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


from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400

    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

if __name__ == "__main__":
    app.run()
