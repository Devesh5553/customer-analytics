from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path('.') / '.env'

load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

print(MONGO_URI)
print(DATABASE_NAME)