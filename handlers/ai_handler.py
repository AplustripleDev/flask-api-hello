import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "คุณคือผู้ช่วยเรื่องยางรถยนต์"},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']
