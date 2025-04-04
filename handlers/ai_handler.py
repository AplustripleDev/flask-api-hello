import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gpt(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error in ask_gpt:", e)
        return "ขออภัยค่ะ เกิดข้อผิดพลาดในการตอบคำถามของ AI"
