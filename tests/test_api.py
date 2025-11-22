import requests
import time

API_BASE = "http://10.237.108.224:1234/v1"
API_KEY = "lm-studio"

def test_api():
    print(f"Testing API connection to {API_BASE}...")
    try:
        # Test models endpoint
        start = time.time()
        response = requests.get(f"{API_BASE}/models", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            print(f"✅ API is reachable! (Took {duration:.2f}s)")
            print("Available models:", response.json())
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server. Check the IP and port.")
    except requests.exceptions.Timeout:
        print("❌ Timeout: Server didn't respond in 5 seconds.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
