import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def find_tire_stock(query):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # ถ้าใช้ creds.json
    # creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

    # ถ้าใช้ ENV
    # import json
    # import os
    # creds_dict = json.loads(os.getenv("GCP_CREDENTIALS_JSON"))
    # creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)  # ตัวอย่างใช้ไฟล์
    client = gspread.authorize(creds)

    sheet_url = os.getenv("GOOGLE_SHEET_URL")  # ลิงก์เต็มของ Google Sheets
    spreadsheet = client.open_by_url(sheet_url)
    sheet = spreadsheet.worksheet("สินค้าคงคลัง")

    # 🔸 Normalize query ก่อนค้นหา
    normalized_query = normalize_tire_code(query)

    data = sheet.get_all_records()
    results = []
    for row in data:
        raw_code = str(row.get("รหัสสินค้า bot", ""))
        # Normalize รหัสยางจากชีต
        normalized_code = normalize_tire_code(raw_code)
        if normalized_query == normalized_code:
            results.append({
                'brand': row.get("แบรนด์", ""),
                'model': row.get("ชื่อรุ่น", ""),   # ถ้าใช้คอลัมน์ชื่อ "ชื่อรุ่น"
                'code': row.get("รหัสสินค้า", ""),
                'qty': row.get("จำนวน (เส้น) คงเหลือ", ""),
                'dot': row.get("ปีที่ผลิต (DOT)", ""),
                'price': row.get("ราคา", "0")
            })
    return results

def normalize_tire_code(text):
    """
    ฟังก์ชันแปลงรหัสยางให้เป็นรูปแบบเปรียบเทียบง่าย
    เช่น 185/60R15 -> 1856015, 33*12.5R15 -> 33125R15 -> 33125 15 -> ...
    """
    # เอาอักขระ / R x * . ออก หรือแทนด้วย "" เพื่อต่อกัน
    return (
        text.upper()
        .replace("/", "")
        .replace("R", "")
        .replace("X", "")
        .replace("*", "")
        .replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )

