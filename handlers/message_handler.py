import os
import requests
import re
from dotenv import load_dotenv  # ✅ ต้องมีบรรทัดนี้
from .sheet_handler import find_tire_stock
from .ai_gemini import ask_gpt

load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text'].strip()

    # 1) ถาม AI → ถ้าขึ้นต้นด้วย "ai"
    if user_text.lower().startswith("ai"):
        prompt = user_text[2:].strip()  # ตัด "ai" ออก
        if prompt:  # ถ้ามีคำถามจริง
            reply_text = ask_gpt(prompt)
            send_reply(reply_token, reply_text)
        return  # ไม่ทำอย่างอื่นต่อ

    # 2) ถ้าเริ่มต้นด้วย "am" → โหมด admin (ราคาทุน)
    if user_text.lower().startswith("am"):
        tire_text = user_text[2:].strip()  # ตัด "am" ออก
        # เช็กว่า tire_text เป็นรหัสยางหรือไม่
        if is_tire_code(tire_text):
            results = find_tire_stock(tire_text)
            if results:
                # ✅ แสดงราคาทุนตามจริง
                send_bubble_stack(reply_token, tire_text, results, admin_mode=True)
            else:
                send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        # ถ้าไม่ใช่รหัสยาง → เงียบ (ไม่ตอบ)
        return

    # 3) โหมดผู้ใช้ทั่วไป → ถ้าเป็นรหัสยาง (ไม่ขึ้นต้นด้วย am)
    if is_tire_code(user_text):
        results = find_tire_stock(user_text)
        if results:
            # ✅ แสดงราคา + 300
            send_bubble_stack(reply_token, user_text, results, admin_mode=False)
        else:
            send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        return

    # 4) ถ้าไม่เข้ากรณีไหนเลย → ไม่ตอบ (เงียบ)
    return


# แก้เริ่มต้นจากตรงนี้ เรื่องไม่ต้อง +300 ในส่วนราคาที่เป็น 0
def send_bubble_stack(reply_token, user_text, results, admin_mode=False):
    """
    สร้าง Bubble เดียว แต่มีหลายรายการ (stack ต่อกันลงมา)
    admin_mode=True → ใช้ราคาทุนตามชีต
    admin_mode=False → บวก 300 ยกเว้นถ้าราคาเป็น 0
    """
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FFD700",
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

    body_contents = []

    for r in results:
        # แปลงราคาเป็นตัวเลข
        cost_price = float(r['price']) if r['price'] else 0.0

        if admin_mode:
            # 🟢 โหมด Admin แสดงราคาทุนจริง
            display_price = cost_price
        else:
            # 🔵 โหมดผู้ใช้ทั่วไป: ถ้าราคา > 0 → บวก 300, ถ้า 0 → ไม่บวก
            if cost_price > 0:
                display_price = cost_price + 300
            else:
                display_price = 0

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
                            "text": f"ราคา: {int(display_price)} บาท",
                            "size": "sm"
                        }
                    ]
                }
            ]
        }

        # ถ้ามีรูป
        if r.get('img_url'):
            row_box["contents"].append({
                "type": "image",
                "url": r['img_url'],
                "size": "sm",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": r['img_url']
                }
            })

        body_contents.append(row_box)

    # เพิ่ม "Python by KenDev." มุมขวาล่าง
    body_contents.append({
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {"type": "filler"},
            {
                "type": "text",
                "text": "Python by KenDev.",
                "size": "xs",
                "color": "#888888",
                "align": "end"
            }
        ]
    })

    bubble["body"]["contents"] = body_contents
    send_flex_reply(reply_token, [bubble])



def send_reply(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
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
# การแก้ไขจบที่ตรงนี้


def is_tire_code(text):
    # ตรวจจับรูปแบบรหัสยาง
    pattern = r'^(\d{3}[\/x\*\-]?\d{2,3}([\/x\*R]?\d{2})?)$'
    return re.match(pattern, text.replace(" ", "").upper()) is not None
