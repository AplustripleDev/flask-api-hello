import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def find_tire_stock(query):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # ✅ ใช้ ENV Variable สำหรับ creds.json
    creds_json = os.getenv("GCP_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet_url = os.getenv("GOOGLE_SHEET_URL")
    spreadsheet = client.open_by_url(sheet_url)
    sheet = spreadsheet.worksheet("สินค้าคงคลัง")  # เปลี่ยนเป็นชื่อแท็บที่ต้องการ

    # 🔴 ดึงข้อมูลเป็น list of lists
    rows = sheet.get_all_values()
    # rows[0] คือ header เช่น ["รหัสยาง", "แบรนด์", "รุ่น", "คงคลัง", "DOT", "ราคา", "รหัสค้นหา", "ลิงก์ภาพ"]
    # rows[1] เป็นต้นไปคือข้อมูลจริง

    query_norm = normalize_tire_code(query)
    results = []

    # 🟡 วนลูปทีละแถว (ยกเว้นแถว 0 ที่เป็นหัวคอลัมน์)
    for i, row in enumerate(rows):
        if i == 0:
            continue  # ข้ามหัวตาราง

        # row[0] = A, row[1] = B, row[2] = C, ...
        tire_code_a = row[0]  # A
        brand = row[1]        # B
        model = row[2]        # C
        qty = row[3]          # D
        dot = row[4]          # E
        price = row[5]        # F
        search_code = row[6]  # G - ใช้ค้นหา
        img_url = row[7] if len(row) > 7 else ""  # H - เผื่อบางแถวไม่มี

        # 🔍 normalize search_code เทียบกับ query_norm
        search_norm = normalize_tire_code(search_code)
        if search_norm == query_norm:
            results.append({
                'tire_code_a': tire_code_a,
                'brand': brand,
                'model': model,
                'qty': qty,
                'dot': dot,
                'price': price,
                'img_url': img_url
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
