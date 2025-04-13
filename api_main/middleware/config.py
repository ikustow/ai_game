import os
from dotenv import load_dotenv

load_dotenv()
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")  # путь к JSON-файлу

