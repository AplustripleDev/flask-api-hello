import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests

credentials_info = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))

def ask_gpt(prompt):
    try:
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        access_token = credentials.token

        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
        )

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print("Gemini Error:", response.text)
            return "ขออภัยค่ะ เกิดข้อผิดพลาดในการขอข้อมูลจาก AI 🥺"

    except Exception as e:
        print("Error in ask_gpt:", e)
        return "ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อ AI 😢"
