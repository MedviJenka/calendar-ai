import os
from dotenv import load_dotenv


def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv('API_KEY')
    return api_key
