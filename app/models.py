from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.user import User
from bson import ObjectId
from config import Config


client = MongoClient("mongodb+srv://r_17:azq178@chatapp-9ovee.mongodb.net/test?retryWrites=true&w=majority")

chat_db = client.get_database("chatDB")
users_collection = chat_db.get_collection("users")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")
messages_collection = chat_db.get_collection("messages")

def save_user(username, email, password):
	password_hash = generate_password_hash(password)
	users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})

def get_user(username):
	user_data = users_collection.find_one({'_id': username})
	return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None


"""
Room Operations
"""

# Create a new room
def save_room(room_name, created_by):
	room_id = rooms_collection.insert_one(
		{'name': room_name, 'created_by': created_by, 
		'date_created': datetime.utcnow()}).inserted_id
	add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
	return room_id

# update an existing room
def update_room(room_id, room_name):
	rooms_collection.update_one({'_id': ObjectId(room_id)}, 
	{'$set': {'name': room_name} })
	room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, 
		{'$set': {'room_name': room_name} })

# get room details
def get_room(room_id):
	return rooms_collection.find_one({'_id': ObjectId(room_id) })

# add new room member
def add_room_member(room_id, room_name, username, added_by, is_room_admin=True):
	room_members_collection.insert_one(
		{'_id': {'room_id': ObjectId(room_id), 'username': username}, 
		'room_name': room_name, 'added_by': added_by,  
		'date_added': datetime.utcnow(), 'is_room_admin': is_room_admin })

# add multiple new members
def add_room_members(room_id, room_name, usernames, added_by):
	room_members_collection.insert_many(
		[{'_id': {'room_id': ObjectId(room_id), 'username': username}, 
		'room_name': room_name, 'added_by': added_by,  
		'date_added': datetime.utcnow(), 'is_room_admin': False} for username in usernames ])

# remove members from room
def remove_room_members(room_id, usernames):
	room_members_collection.delete_many(
		{'_id': {'$in': [{'room_id': ObjectId(room_id), 
		'username': username} for username in usernames ]}})

# get room members details
def get_room_members(room_id):
	return list(room_members_collection.find({'_id.room_id': ObjectId(room_id)}))

# get rooms a user belongs to
def get_rooms_for_user(username):
	return list(room_members_collection.find({'_id.username': username} ))

# check whether user belongs to a particular room
def is_room_member(room_id, username):
	return room_members_collection.count_documents(
		{'_id': {'room_id': ObjectId(room_id), 'username': username} })

# whether user is admin of a particular room
def is_room_admin(room_id, username):
	return room_members_collection.count_documents(
		{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True })



"""
Messages Operations
"""


def save_message(room_id, text, sender):
	messages_collection.insert_one({
		'room_id': room_id,
		'text': text,
		'sender': sender,
		'date_sent': datetime.utcnow()
		})

MESSAGE_LIMIT = 3

def get_messages(room_id, page=0):
	offset = page * MESSAGE_LIMIT
	messages =  list(messages_collection.find({'room_id': room_id}).sort('_id', DESCENDING).limit(MESSAGE_LIMIT).skip(offset))

	for message in messages:
		message["date_sent"] = message["date_sent"].strftime("[%b %d, %H:%M]")
	return messages[::-1]
