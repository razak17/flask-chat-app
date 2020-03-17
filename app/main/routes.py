from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, join_room, leave_room
from app.main import bp
from flask_login import login_required, current_user
from app.models import User, save_room, add_room_members, get_rooms_for_user, get_room, is_room_member, get_room_members, is_room_admin, update_room, remove_room_members, get_messages
from app import db
from bson.json_util import dumps


@bp.route('/home')
@bp.route('/')
@login_required
def index():
	if current_user.is_authenticated:
		rooms = get_rooms_for_user(current_user.username)
	return render_template('index.html', rooms=rooms)


@bp.route("/room/new", methods=["GET", "POST"])
@login_required
def create_room():
	if request.method == 'POST':
		room_name = request.form.get('room_name')
		usernames = [username.strip() for username in request.form.get('members').split(',')]

		if len(room_name) and len(usernames):
			room_id = save_room(room_name, current_user.username)

			if current_user.username in usernames:
				usernames.remove(current_user.username)
			add_room_members(room_id, room_name, usernames, current_user.username)
			flash("Room created successfully", "success")
		else:
			flash("Failed to create room!", "danger")
	return render_template('create_room.html')


@bp.route("/room/<string:room_id>", methods=["GET", "POST"])
@login_required
def room(room_id):
	room = get_room(room_id)
	if room and is_room_member(room_id, current_user.username):
		room_members = get_room_members(room_id)
		messages = get_messages(room_id)
		return render_template('room.html', username=current_user.username, room=room, room_members=room_members, messages=messages)
	else:
		return "Room not found", 404


@bp.route("/room/<string:room_id>/edit", methods=["GET", "POST"])
@login_required
def edit_room(room_id):
	room = get_room(room_id)
	if room and is_room_admin(room_id, current_user.username):
		existing_room_members = [member['_id']['username'] for member in get_room_members(room_id)]
		room_members_str = ", ".join(existing_room_members)

		if request.method == 'POST':
			room_name = request.form.get('room_name')
			room['name'] = room_name
			update_room(room_id, room_name)

			new_members = [username.strip() for username in request.form.get('members').split(', ')]
			members_to_add = list(set(new_members) - set(existing_room_members))
			members_to_remove = list(set(existing_room_members) - set(new_members))
			if len(members_to_add):
				add_room_members(room_id, room_name, members_to_add, current_user.username)
			if len(members_to_remove):
				remove_room_members(room_id, members_to_remove)
			flash("Room has been updated", "success")
			room_members_str = ", ".join(new_members)

		return render_template('edit_room.html', room=room, room_members_str=room_members_str)
	else:
		return "Room not found", 404

@bp.route("/room/<string:room_id>/history", methods=["GET", "POST"])
@login_required
def chat_history(room_id):
	room = get_room(room_id)
	if room and is_room_member(room_id, current_user.username):
		page = int(request.args.get('page', 0))
		messages = get_messages(room_id, page)
		return dumps(messages)

		# return render_template('room.html', username=current_user.username, room=room, room_members=room_members, messages=messages)
	else:
		return "Room not found", 404