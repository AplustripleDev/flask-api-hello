import os
import requests
from handlers.ai_handler import ask_gpt  # (เดี๋ยวจะสร้างตามหลัง)
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text']

    if user_text.lower().startswith('ถามai:'):
        prompt = user_text[7:].strip()
        reply_text = ask_gpt(prompt)
    else:
        reply_text = f"เจ้านายพิมพ์ว่า: {user_text}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

    data = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": reply_text
        }]
    }

    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)
