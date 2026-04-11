import requests
import logging


logger = logging.getLogger(__name__)
def validate_notion_token(token):
    url = "https://api.notion.com/v1/users/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2026-03-11",
    }

    response = requests.get(url, headers=headers)

    if response.ok:
        logger.info("Токен валидный!")
        return True
    else:
        logger.error("Токен невалидный или истёк.")
        return False