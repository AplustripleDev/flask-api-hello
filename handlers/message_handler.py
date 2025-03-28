import os
import requests
import re
from .sheet_handler import find_tire_stock
# ถ้าใช้ GPT ให้ import ด้วย
# from .ai_handler import ask_gpt

# ถ้าใช้ .env local:
# from dotenv import load_dotenv
# load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text'].strip()

    # ถ้าใช้ GPT:
    # if user_text.lower().startswith("ถามai:"):
    #     prompt = user_text[7:].strip()
    #     reply_text = ask_gpt(prompt)
    #     send_reply(reply_token, reply_text)
    #     return

    # ตรวจว่ารหัสยางไหม
    if is_tire_code(user_text):
        results = find_tire_stock(user_text)
        if results:
            bubbles = []
            for r in results:
                # เตรียมข้อความฝั่งซ้าย
                text_contents = [
                    {
                        "type": "text",
                        "text": f"{r['brand']} - {r['model']}",
                        "weight": "bold",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": f"รหัสสินค้า: {r['code']}",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"คงเหลือ: {r['qty']} เส้น",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"DOT: {r['dot']}",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"ราคา: {r['price']} บาท",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": "Python by KenDev.",
                        "size": "xs",
                        "color": "#888888",
                        "align": "start"
                    }
                ]

                # จัด layout แนวนอน (ซ้าย = text_contents, ขวา = รูปเล็ก)
                body_contents = [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 4,
                        "spacing": "sm",
                        "contents": text_contents
                    }
                ]

                # ถ้ามีรูป
                if r['img_url']:
                    body_contents.append({
                        "type": "image",
                        "url": r['img_url'],
                        "size": "xxs",
                        "aspectMode": "cover",
                        "align": "end",
                        "action": {
                            "type": "uri",
                            "uri": r['img_url']  # กดแล้วเปิดรูปใหญ่
                        }
                    })

                bubble = {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#FFD700",  # เหลืองเข้ม
                        "contents": [
                            {
                                "type": "text",
                                "text": f"รหัส {user_text}",
                                "weight": "bold",
                                "color": "#000000",
                                "size": "lg"
                            }
                        ]
                    },
                    "body": {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "md",
                        "contents": body_contents
                    }
                }
                bubbles.append(bubble)

            send_flex_reply(reply_token, bubbles)
        else:
            send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        return

    # ถ้าไม่ใช่รหัสยาง → ตอบข้อความทั่วไป
    send_reply(reply_token, f"เจ้านายพิมพ์ว่า: {user_text}")

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
    # ตรวจจับรูปแบบรหัสยางคร่าว ๆ เช่น 185/60R15, 1856015, 33x12.5R15, etc.
    pattern = r'^(\d{3}[\/x\*\-]?\d{2,3}([\/x\*R]?\d{2})?)$'
    return re.match(pattern, text.replace(" ", "").upper()) is not None
