from openai import OpenAI
from config.config import get_config
def get_ai(request):
    api_token = get_config().ai.token
    client = OpenAI(
        api_key=api_token,
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model="openrouter/auto",
        messages= [
            {"role": "user", "content": f"{request}"},
        ],
    )

    return response.choices[0].message.content