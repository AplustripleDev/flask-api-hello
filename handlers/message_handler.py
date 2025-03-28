import os
import requests
import re
from .sheet_handler import find_tire_stock  # เรียกฟังก์ชันจาก sheet_handler.py

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text'].strip()

    # 🔎 Debug Log แสดงข้อความที่ได้รับ
    print("🟢 handle_message() received user_text:", user_text)

    # 🟡 ตรวจว่ารหัสยางไหม
    if is_tire_code(user_text):
        print("🟡 is_tire_code -> True, calling find_tire_stock()")
        results = find_tire_stock(user_text)
        print("🟢 find_tire_stock() returned:", results)

        if results:
            bubbles = []
            for r in results:
                # จัด layout แบบแนวนอน (ซ้ายข้อความ / ขวารูป)
                text_contents = [
                    {
                        "type": "text",
                        # ตัวอย่าง: DUNLOP - AT5
                        "text": f"{r['brand']} - {r['model']}",
                        "weight": "bold",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        # เบอร์ยางจากคอลัมน์ A
                        "text": f"เบอร์ยาง: {r['tire_code_a']}",
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

                # สร้าง body contents
                body_contents = [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 4,
                        "spacing": "sm",
                        "contents": text_contents
                    }
                ]

                # ถ้ามีลิงค์รูปภาพ
                if r['img_url']:
                    body_contents.append({
                        "type": "image",
                        "url": r['img_url'],
                        "size": "xxs",
                        "aspectMode": "cover",
                        "align": "end",
                        "action": {
                            "type": "uri",
                            "uri": r['img_url']
                        }
                    })

                bubble = {
                    "type": "bubble",
                    # ✅ หัวตารางสีเหลือง
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#FFD700",
                        "contents": [
                            {
                                "type": "text",
                                # ตัวอย่าง: รหัส 185/60/15
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

            print("🟢 Sending Flex with bubbles:", bubbles)
            send_flex_reply(reply_token, bubbles)
        else:
            print("🔴 No results found, sending not found message")
            send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        return

    # ถ้าไม่ใช่รหัสยาง
    print("🟡 is_tire_code -> False, sending normal text")
    send_reply(reply_token, f"เจ้านายพิมพ์ว่า: {user_text}")

def send_reply(reply_token, text):
    print(f"🟢 send_reply() -> {text}")
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
    print(f"🟢 send_flex_reply() -> {len(bubbles)} bubble(s)")
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
    # ตรวจจับรูปแบบรหัสยาง (เช่น 185/60/15, 1856015, 33x12.5R15 ฯลฯ)
    pattern = r'^(\d{3}[\/x\*\-]?\d{2,3}([\/x\*R]?\d{2})?)$'
    return re.match(pattern, text.replace(" ", "").upper()) is not None
