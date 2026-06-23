import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print(api_key[:5])   # only test first few characters

client = genai.Client(
    api_key=api_key
)


response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain customer segmentation in one sentence"
)

print(response.text)