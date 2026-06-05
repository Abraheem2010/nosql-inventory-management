import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_db():
    uri = os.environ.get("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI not set. Create a .env file with your connection string.")
    client = MongoClient(uri)
    return client["inventory"]
