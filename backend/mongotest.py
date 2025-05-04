import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://julienserbanescu:<pass>@cluster0.6nnhafa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["MyDB"]
collection = db["MyDB"]

collection.insert_one({"name": "Julien", "age": 25, "city": "Paris"})
print("Data inserted successfully!")