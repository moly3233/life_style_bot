
from openai import OpenAI

client = OpenAI(api_key='sk-a7d977ef3c804f82b5c1fad2897c6208', base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)