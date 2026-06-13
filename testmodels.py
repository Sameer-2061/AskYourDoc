import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the API key from your existing .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: API Key not found in .env file.")
    exit()

genai.configure(api_key=api_key)

print("Connecting to Google Servers...\n")
print("These are the EXACT models your API key has access to for text generation:")
print("-" * 60)

try:
    # Fetch all available models
    for m in genai.list_models():
        # Filter only the models that can answer questions (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
    print("-" * 60)
    print("Test Complete.")
except Exception as e:
    print(f"Failed to fetch models. Error: {e}")