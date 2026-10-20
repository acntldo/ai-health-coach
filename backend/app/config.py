import os

from dotenv import load_dotenv

# reads the .env in the project root when running locally
load_dotenv()

# sqlite on a dev machine, hosted postgres when deployed
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coach.db")

USDA_API_KEY = os.getenv("USDA_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# a setting because google renames and retires models often
GEMINI_MODEL = os.getenv("GEMINI_MODEL")