from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db.users
campaigns = db.campaigns
stages = db.stages
logs = db.logs
rules = db.rules