import os
import requests
import re
from .sheet_handler import find_tire_stock

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text'].strip()

    # ตรวจว่ารหัสยางไหม
    if is_tire_code(user_text):
        results = find_tire_stock(user_text)
        if results:
            # 🔴 สร้าง Bubble เดียว
            bubble = {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFD700",  # เหลืองสด
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
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": []
                }
            }

            # สร้าง list เก็บเนื้อหาใน body
            body_contents = []

            # 🟡 วนลูปแต่ละรายการ results
            for r in results:
                # สร้างกล่องแนวนอน (ซ้าย=ข้อความ, ขว=รูป)
                row_box = {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 3,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{r['brand']} - {r['model']}",
                                    "weight": "bold",
                                    "size": "sm"
                                },
                                {
                                    "type": "text",
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
                                }
                            ]
                        }
                    ]
                }

                # ถ้ามีรูป → ใส่รูปทางขวา
                if r.get('img_url'):
                    row_box["contents"].append({
                        "type": "image",
                        "url": r['img_url'],
                        "size": "sm",         # ปรับขนาดรูปตามต้องการ
                        "aspectMode": "cover",
                        "action": {
                            "type": "uri",
                            "uri": r['img_url']  # กดเพื่อเปิดภาพใหญ่
                        }
                    })

                # เพิ่ม row_box เข้าใน body_contents
                body_contents.append(row_box)

            # 🟡 เพิ่ม Text “Python by KenDev.” (มุมขวาล่าง) เป็นอีก 1 บล็อก
            body_contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "filler"  # ดันให้ข้อความไปชิดขวา
                    },
                    {
                        "type": "text",
                        "text": "Python by KenDev.",
                        "size": "xs",
                        "color": "#888888",
                        "align": "end"
                    }
                ]
            })

            # ใส่ body_contents กลับไปใน bubble
            bubble["body"]["contents"] = body_contents

            # ส่ง bubble เดียวใน carousel
            send_flex_reply(reply_token, [bubble])

        else:
            send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        return

    # ถ้าไม่ใช่รหัสยาง
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
    pattern = r'^(\d{3}[\/x\*\-]?\d{2,3}([\/x\*R]?\d{2})?)$'
    return re.match(pattern, text.replace(" ", "").upper()) is not None
