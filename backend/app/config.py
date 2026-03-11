from dotenv import load_dotenv
import os

load_dotenv()

SECRET = os.getenv("JWT_SECRET")

DATABASE_URL = os.getenv("DATABASE_URL")