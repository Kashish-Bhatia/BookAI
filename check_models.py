import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    try:
        genai.configure(api_key=api_key)
        print("Available Gemini models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No API key found")