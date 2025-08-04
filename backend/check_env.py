import os
from dotenv import load_dotenv

# Force load with absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

print("DEBUG MONGO_URI:", os.getenv("MONGO_URI"))
