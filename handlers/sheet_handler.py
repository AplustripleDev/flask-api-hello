import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def find_tire_stock(query):
    # เตรียม Credentials สำหรับ Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)

    # เปิด Google Sheet
    sheet_url = os.getenv("GOOGLE_SHEET_URL")
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
