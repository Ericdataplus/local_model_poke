from openai import OpenAI

client = OpenAI(base_url="http://10.237.108.224:1234/v1", api_key="lm-studio")

try:
    models = client.models.list()
    print("Available models:")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print(f"Error listing models: {e}")
