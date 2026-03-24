from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
print(f"Client: {dir(client)}")
print(f"Models: {dir(client.models)}")
