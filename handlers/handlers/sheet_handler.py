import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 สร้าง Credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# 📒 เปิดชีต "สินค้าคงคลัง"
sheet_url = os.getenv("GOOGLE_SHEET_URL")
spreadsheet = client.open_by_url(sheet_url)
sheet = spreadsheet.worksheet("สินค้าคงคลัง")

def find_tire_stock(text):
    query = text.replace(" ", "").replace("*", "x").replace("-", "")
    values = sheet.get_all_records()

    matches = []
    for row in values:
        bot_code = row.get("รหัสสินค้า bot", "").replace(" ", "").replace("*", "x").replace("-", "")
        if query in bot_code:
            brand = row.get("แบรนด์", "")
            model = row.get("รุ่นยาง", "")
            qty = row.get("จำนวน (เส้น) คงคลัง", "")
            dot = row.get("สัปดาห์ปี (DOT)", "")
            matches.append(f"{brand} {model} - คงเหลือ {qty} เส้น | DOT: {dot}")

    if matches:
        return "\n".join(matches)
    else:
        return "ไม่พบข้อมูลยางที่ค้นหาในคลังนะคะ ลองตรวจสอบรหัสอีกครั้ง~ 😊"
