from db import users

sample_emails = [
    {"email": "kuldeepverma9755@gmail.com", "name": "Kuldeep verma", "user_id": "kuldeep001"},
    {"email": "shivangiagrawal1999@gmail.com", "name": "Shivangi", "user_id": "kuldeep001"},
    {"email": "kuldeepkd0603@gmail.com", "name": "kuldeep", "user_id": "kuldeep001"}
]

for user in sample_emails:
    users.update_one({"email": user["email"]}, {"$setOnInsert": user}, upsert=True)

print("Seeded users")