# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
FRAMEPACK_API_URL = os.getenv("FRAMEPACK_API_URL", "")
FRAMEPACK_STATUS_URL = os.getenv("FRAMEPACK_STATUS_URL", "")
VIDEO_STORAGE_DIR = os.getenv("VIDEO_STORAGE_DIR", "./videos")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
