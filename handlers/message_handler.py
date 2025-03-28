import os
import requests
import re
import json
from dotenv import load_dotenv  # ✅ ต้องมีบรรทัดนี้
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from .sheet_handler import find_tire_stock

# โหลด ENV
load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# โหลด Gemini Credentials
credentials_info = json.loads(GOOGLE_CREDENTIALS_JSON)

# AI Gemini Handler
def ask_gpt(prompt):
    try:
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        access_token = credentials.token

        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            }
        )

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print("Gemini Error:", response.text)
            return "ขออภัยค่ะ เกิดข้อผิดพลาดในการขอข้อมูลจาก AI 🥺"

    except Exception as e:
        print("Error in ask_gpt:", e)
        return "ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อ AI 😢"


def handle_message(event):
    reply_token = event['replyToken']
    user_text = event['message']['text'].strip()

    # 1) ถาม AI → ถ้าขึ้นต้นด้วย "ai", "ai:", "ai/", "ai-" อะไรก็ได้
    if re.match(r"^ai[\s:/\-]*", user_text.lower()):
        prompt = re.sub(r"^ai[\s:/\-]*", "", user_text, flags=re.IGNORECASE).strip()
        if prompt:
            reply_text = ask_gpt(prompt)
            send_reply(reply_token, reply_text)
        return

    # 2) ถ้าเริ่มต้นด้วย "am" → โหมด admin (ราคาทุน)
    if user_text.lower().startswith("am"):
        tire_text = user_text[2:].strip()
        if is_tire_code(tire_text):
            results = find_tire_stock(tire_text)
            if results:
                send_bubble_stack(reply_token, tire_text, results, admin_mode=True)
            else:
                send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        return

    # 3) โหมดผู้ใช้ทั่วไป
    if is_tire_code(user_text):
        results = find_tire_stock(user_text)
        if results:
            send_bubble_stack(reply_token, user_text, results, admin_mode=False)
        else:
            send_reply(reply_token, "ไม่พบข้อมูลยางที่ค้นหาในสต็อกนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊")
        return
    return


def send_bubble_stack(reply_token, user_text, results, admin_mode=False):
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
        cost_price = float(r['price']) if r['price'] else 0.0

        if admin_mode:
            display_price = cost_price
        else:
            display_price = cost_price + 300 if cost_price > 0 else 0

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
                        {"type": "text", "text": f"{r['brand']} - {r['model']}", "weight": "bold", "size": "sm"},
                        {"type": "text", "text": f"เบอร์ยาง: {r['tire_code_a']}", "size": "sm"},
                        {"type": "text", "text": f"คงเหลือ: {r['qty']} เส้น", "size": "sm"},
                        {"type": "text", "text": f"DOT: {r['dot']}", "size": "sm"},
                        {"type": "text", "text": f"ราคา: {int(display_price)} บาท", "size": "sm"}
                    ]
                }
            ]
        }

        if r.get('img_url'):
            row_box["contents"].append({
                "type": "image",
                "url": r['img_url'],
                "size": "sm",
                "aspectMode": "cover",
                "action": {"type": "uri", "uri": r['img_url']}
            })

        body_contents.append(row_box)

    body_contents.append({
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {"type": "filler"},
            {"type": "text", "text": "Python by KenDev.", "size": "xs", "color": "#888888", "align": "end"}
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
        "messages": [{"type": "text", "text": text}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)


def send_flex_reply(reply_token, bubbles):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{
            "type": "flex",
            "altText": "สินค้ารหัสยางที่ค้นหา",
            "contents": {"type": "carousel", "contents": bubbles}
        }]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)


def is_tire_code(text):
    pattern = r'^(\d{3}[\/x\*\-]?\d{2,3}([\/x\*R]?\d{2})?)$'
    return re.match(pattern, text.replace(" ", "").upper()) is not None
