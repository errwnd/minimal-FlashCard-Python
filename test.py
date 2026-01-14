import os

from dotenv import load_dotenv

load_dotenv()  # loads .env into environment

api_key = os.getenv("API_KEY")

print(api_key)  # test only
