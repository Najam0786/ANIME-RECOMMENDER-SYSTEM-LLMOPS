import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_groq_connection():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama3-70b-8192")

    print(f"API Key Present: {bool(api_key)}")
    print(f"Using Model: {model}")

    if not api_key:
        print("Error: GROQ_API_KEY not found")
        return False

    url = "https://api.groq.com/openai/v1/chat/completions"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            },
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Connection successful!")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_groq_connection()