from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client['inventory']

users_collection = db['users']
inventory_collection = db['equipments']  # Assuming 'equipments' contains inventory items
notifications_collection = db['notifications']

def find_user_by_email(email):
    return users_collection.find_one({"email": email})

def find_inventory_by_user_id(user_id):
    return list(inventory_collection.find({"user_id": ObjectId(user_id)}))
