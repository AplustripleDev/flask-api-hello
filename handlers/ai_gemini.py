import google.generativeai as genai
import os
import json

# ✅ โหลด Credential จาก Environment Variable
creds_json = os.getenv("GCP_CREDENTIALS_JSON")

if creds_json:
    credentials = json.loads(creds_json)
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"), credentials=credentials)
else:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gpt(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error in ask_gpt:", e)
        return "ขออภัยค่ะ เกิดข้อผิดพลาดในการตอบคำถามของ AI"
