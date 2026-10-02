import os

from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
UPLOAD_DIR = "uploads"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")