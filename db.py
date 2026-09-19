import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# A local MongoDB is the default so the project runs out of the box.
# Point MONGO_URI at a cluster (e.g. Atlas) in .env to use that instead.
DEFAULT_URI = "mongodb://localhost:27017"


def get_db():
    uri = os.environ.get("MONGO_URI", DEFAULT_URI)
    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    return client["inventory"]
