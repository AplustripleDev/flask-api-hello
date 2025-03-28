import os
import openai

# ดึง API Key จาก Environment Variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "คุณคือผู้ช่วยเรื่องยางรถยนต์ที่ให้คำแนะนำในการเลือกยางและข้อมูลเกี่ยวกับยางรถยนต์"},
                {"role": "user", "content": prompt}
            ]
        )
        # ส่งกลับคำตอบที่ได้จาก ChatGPT
        return response.choices[0].message.content.strip()
    except Exception as e:
        # หากเกิดข้อผิดพลาด จะส่งกลับข้อความ error (หรืออาจไม่ตอบก็ได้ตามเงื่อนไขของระบบ)
        print("Error in ask_gpt:", e)
        return "ขออภัยค่ะ เกิดข้อผิดพลาดในการตอบคำถามของ AI"
