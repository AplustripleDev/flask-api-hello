import os
import requests
import re
from handlers.ai_handler import ask_gpt
from handlers.sheet_handler import find_tire_stock
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text']

    # ✅ ตอบ AI
    if user_text.lower().startswith('ถามai:'):
        prompt = user_text[7:].strip()
        reply_text = ask_gpt(prompt)
        send_reply(reply_token, reply_text)
        return

    # ✅ ค้นหายาง
    if is_tire_code(user_text):
        results = find_tire_stock(user_text)
        if results:
            bubbles = []
            for r in results:
                bubbles.append({
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            { "type": "text", "text": f"รหัส {user_text}", "weight": "bold", "color": "#b58900", "size": "lg" },
                            { "type": "text", "text": f"{r['brand']} - {r['model']}", "weight": "bold", "size": "md" },
                            { "type": "text", "text": f"รหัสสินค้า: {r['code']}", "size": "sm" },
                            { "type": "text", "text": f"คงเหลือ: {r['qty']} เส้น", "size": "sm" },
                            { "type": "text", "text": f"DOT: {r['dot']}", "size": "sm" },
                            { "type": "text", "text": f"ราคา: {r['price']} บาท", "size": "sm" }
                        ]
                    }
                })
            send_flex_reply(reply_token, bubbles)
        else:
            send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        return

    # ✅ ข้อความทั่วไป
    reply_text = f"เจ้านายพิมพ์ว่า: {user_text}"
    send_reply(reply_token, reply_text)

def send_reply(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": text
        }]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)

def send_flex_reply(reply_token, bubbles):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "flex",
                "altText": "สินค้ารหัสยางที่ค้นหา",
                "contents": {
                    "type": "carousel",
                    "contents": bubbles
                }
            }
        ]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)

def is_tire_code(text):
    pattern = r"^(\d{3}[\/x\*\-]?\d{2,3}[\/x\*R]?\d{2})$"
    return re.match(pattern, text.replace(" ", "")) is not None
