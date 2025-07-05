import requests
import json

def test_api():
    try:
        print("Testing /api/trending...")
        response = requests.get('http://127.0.0.1:5000/api/trending')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Books count: {len(data.get('books', []))}")
            if data.get('books'):
                print(f"First book: {data['books'][0]['title']}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
