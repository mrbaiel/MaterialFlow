import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_URL = os.getenv('API_URL', '127.0.0.1:8000/api/')
API_TOKEN = os.getenv("API_TOKEN")