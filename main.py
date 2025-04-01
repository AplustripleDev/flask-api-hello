from flask import Flask, request, abort
import os
import base64
import json
from handlers.message_handler import handle_message
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

app = Flask(__name__)

# Decode GOOGLE_APPLICATION_CREDENTIALS_JSON (if exists)
def add_padding(base64_str):
    padding_needed = 4 - (len(base64_str) % 4)
    if padding_needed and padding_needed != 4:
        base64_str += "=" * padding_needed
    return base64_str

credentials_base64 = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if credentials_base64:
    credentials_base64 = add_padding(credentials_base64)
    credentials_json = base64.b64decode(credentials_base64).decode("utf-8")
    with open("credentials.json", "w") as f:
        f.write(credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# LINE Config
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    handle_message(event, line_bot_api)

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(debug=True)
