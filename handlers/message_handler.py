import os
import requests
from dotenv import load_dotenv
from handlers.ai_handler import ask_gpt
from handlers.sheet_handler import find_tire_stock  # ✅ เพิ่มมา
import re

load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text']

    if user_text.lower().startswith("ถามai:"):
        prompt = user_text[7:].strip()
        reply_text = ask_gpt(prompt)

    elif is_tire_code(user_text):  # ✅ ตรวจสอบรหัสยาง
        reply_text = find_tire_stock(user_text)

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

def is_tire_code(text):
    pattern = r'^(\d{3}[\/x*\-]?\d{2,3}[\/x*R]?\d{2})$'
    return re.match(pattern, text.replace(" ", "")) is not None
