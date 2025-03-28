import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def find_tire_stock(query):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # ✅ อ่าน Credentials จาก ENV (Railway Variables)
    creds_json = os.getenv("GCP_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # ✅ เปิดชีต “สินค้าคงคลัง”
    sheet_url = os.getenv("GOOGLE_SHEET_URL")  # ตัวแปรใน Railway
    spreadsheet = client.open_by_url(sheet_url)
    sheet = spreadsheet.worksheet("สินค้าคงคลัง")  # แท็บชื่อ “สินค้าคงคลัง”

    # ✅ แปลงรหัสยางที่ผู้ใช้พิมพ์ให้เป็นรูปแบบ normalize
    query_norm = normalize_tire_code(query)

    # ✅ ดึงข้อมูลทุกแถว
    data = sheet.get_all_records()

    results = []
    for row in data:
        # ------------------------------------------------------
        # สมมติว่าในชีตมีคอลัมน์ชื่อแบบนี้ (ต้องตรงหัวคอลัมน์จริง ๆ):
        # A = “เบอร์ยาง”
        # B = “ชื่อแบรนด์สินค้า”
        # C = “ชื่อรุ่น”
        # D = “จำนวนสินค้า คงคลัง”
        # E = “สัปดาห์ปียาง (DOT)” หรือ “DOT”
        # F = “ราคาสินค้า”
        # G = “รหัสค้นหา” (เจ้านายเรียกอะไรก็ได้ แต่ต้องตรงหัวคอลัมน์)
        # H = “ลิงค์รูปภาพ”
        # ------------------------------------------------------

        raw_search_code = str(row.get("รหัสค้นหา", ""))  # ค่าในคอลัมน์ G
        search_norm = normalize_tire_code(raw_search_code)

        if query_norm == search_norm:
            results.append({
                'tire_code_a': row.get("เบอร์ยาง", ""),            # คอลัมน์ A
                'brand': row.get("ชื่อแบรนด์สินค้า", ""),          # คอลัมน์ B
                'model': row.get("ชื่อรุ่น", ""),                  # คอลัมน์ C
                'qty': row.get("จำนวนสินค้า คงคลัง", ""),          # คอลัมน์ D
                'dot': row.get("สัปดาห์ปียาง (DOT)", ""),         # คอลัมน์ E
                'price': row.get("ราคาสินค้า", "0"),              # คอลัมน์ F
                'search_code': raw_search_code,                     # (G) เอาไว้แสดง
                'img_url': row.get("ลิงค์รูปภาพ", "")              # คอลัมน์ H
            })

    return results

def normalize_tire_code(text):
    """ 
    แปลงรหัสยางให้เป็นรูปแบบเดียวกัน 
    ตัด / R x * . - ช่องว่าง และเป็นตัวพิมพ์ใหญ่ 
    เช่น 185/60R15 -> 1856015 
         145/65/15 -> 1456515 
    """
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
