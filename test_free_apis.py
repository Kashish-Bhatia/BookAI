import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_google_books():
    """Test Google Books API"""
    print("Testing Google Books API...")
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": "Harry Potter", "maxResults": 1}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                book = data['items'][0]['volumeInfo']
                print(f"✅ Google Books API working!")
                print(f"Found: {book.get('title', 'Unknown')}")
            else:
                print("❌ No books found")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_gemini():
    """Test Google Gemini API"""
    print("\nTesting Google Gemini API...")
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ Gemini API key not found in .env file")
        return
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash') # Updated model name
        response = model.generate_content("Say 'Gemini API is working!'")
        print("✅ Gemini API working!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Gemini Error: {e}")

if __name__ == "__main__":
    test_google_books()
    test_gemini()