from openai import OpenAI
import time

API_BASE = "http://10.237.108.224:1234/v1"
API_KEY = "lm-studio"
MODEL_NAME = "local-model"

def test_inference():
    print(f"Testing inference at {API_BASE}...")
    client = OpenAI(base_url=API_BASE, api_key=API_KEY)
    
    try:
        start = time.time()
        print("Sending request...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=10,
            timeout=30
        )
        duration = time.time() - start
        print(f"✅ Response received in {duration:.2f}s")
        print(f"Content: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Inference Failed: {e}")

if __name__ == "__main__":
    test_inference()
