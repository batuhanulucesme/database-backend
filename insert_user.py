from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['inventory']
users_collection = db['users']

def insert_user(email: str, password: str):
    user = {
        "email": email,
        "password": password
    }
    users_collection.insert_one(user)
    print(f"Inserted user {email} with plaintext password")

# Example usage
if __name__ == "__main__":
    insert_user("test@example.com", "yourpassword")
