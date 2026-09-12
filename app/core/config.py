import os
from dotenv import load_dotenv

load_dotenv()

# Application
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set")
