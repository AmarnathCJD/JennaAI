import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_KEY', '')