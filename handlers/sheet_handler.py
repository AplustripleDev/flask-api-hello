import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def find_tire_stock(query):
    # 🔐 เตรียม Credentials จาก Environment Variable แทนไฟล์ creds.json
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 1) ดึงค่า JSON ทั้งหมดจาก ENV
    creds_json = os.getenv("GCP_CREDENTIALS_JSON")  
    # 2) แปลงเป็น Dict
    creds_dict = json.loads(creds_json)
    # 3) สร้าง Credentials จาก Dict
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # 📗 เปิด Google Sheet
    sheet_url = os.getenv("GOOGLE_SHEET_URL")  # อย่าลืมตั้งค่าใน Railway เช่นกัน
    spreadsheet = client.open_by_url(sheet_url)
    sheet = spreadsheet.worksheet("สินค้าคงคลัง")

    # แปลง query และดึงข้อมูลทั้งหมด
    query = query.replace(" ", "").replace("*", "x").replace("-", "").upper()
    values = sheet.get_all_records()

    results = []
    for row in values:
        code = str(row.get("รหัสสินค้า bot", "")).replace(" ", "").replace("*", "x").replace("-", "").upper()
        if query == code:
            results.append({
                'brand': row.get("แบรนด์", ""),
                'model': row.get("ชื่อรุ่น", ""),
                'code': row.get("รหัสสินค้า", ""),
                'qty': row.get("จำนวน (เส้น) คงเหลือ", ""),
                'dot': row.get("ปีที่ผลิต (DOT)", ""),
                'price': row.get("ราคา", "0")
            })
    return results
