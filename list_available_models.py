from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- DANH SÁCH CÁC CỨNG/MIỀN MODELS CỦA API KEY ---")
for model in client.models.list():
    if 'imagen' in model.name:
        print(f"Model: {model}")
