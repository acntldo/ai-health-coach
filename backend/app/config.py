import os

from dotenv import load_dotenv

# reads the .env in the project root when running locally.
# on vercel there is no file, the values come from project settings
load_dotenv()

# sqlite on a dev machine, hosted postgres when deployed
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coach.db")

USDA_API_KEY = os.getenv("USDA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# comma separated, best choice first. google renames and retires models often,
# so they live in settings, and the next one is tried when one is overloaded
GEMINI_MODELS = [m.strip() for m in os.getenv("GEMINI_MODELS", "").split(",") if m.strip()]

# daily coach messages allowed per device and across everyone. the free gemini
# tier is small, so the overall cap keeps a public link from using it all up
DEVICE_DAILY_LIMIT = int(os.getenv("DEVICE_DAILY_LIMIT", "20"))
GLOBAL_DAILY_LIMIT = int(os.getenv("GLOBAL_DAILY_LIMIT", "200"))