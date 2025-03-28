import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API Security
API_KEY = os.getenv("API_KEY")