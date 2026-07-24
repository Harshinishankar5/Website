# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
SUPER_ADMIN_SECRET_KEY = os.getenv("SUPER_ADMIN_SECRET_KEY")

if not ADMIN_SECRET_KEY or not SUPER_ADMIN_SECRET_KEY:
    raise RuntimeError("ADMIN_SECRET_KEY and SUPER_ADMIN_SECRET_KEY must be set in .env")