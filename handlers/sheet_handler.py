import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def find_tire_stock(query):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # ✅ ดึง Credentials จาก Environment Variable แทนไฟล์ creds.json
    creds_json = os.getenv("GCP_CREDENTIALS_JSON")  # คีย์เดียวกับที่มีใน Railway
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    client = gspread.authorize(creds)

    sheet_url = os.getenv("GOOGLE_SHEET_URL")
    spreadsheet = client.open_by_url(sheet_url)
    sheet = spreadsheet.worksheet("สินค้าคงคลัง")

    # แปลง query ให้เป็นรูปแบบเปรียบเทียบได้
    query = normalize_tire_code(query)
    data = sheet.get_all_records()

    results = []
    for row in data:
        raw_code = str(row.get("รหัสสินค้า bot", ""))
        normalized_code = normalize_tire_code(raw_code)
        if query == normalized_code:
            results.append({
                'brand': row.get("แบรนด์", ""),
                'model': row.get("ชื่อรุ่น", ""),
                'code': row.get("รหัสสินค้า", ""),
                'qty': row.get("จำนวน (เส้น) คงเหลือ", ""),
                'dot': row.get("ปีที่ผลิต (DOT)", ""),
                'price': row.get("ราคา", "0"),
                'img_url': row.get("ลิงก์ภาพ", "")
            })
    return results

def normalize_tire_code(text):
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
