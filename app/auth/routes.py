from app.auth import bp
from app.models import get_user, save_user
from werkzeug.urls import url_parse
from app.auth.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, request, redirect, url_for, flash
from app import db, login


@login.user_loader
def load_user(username):
    return get_user(username)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            save_user(username, email, password)
            return redirect(url_for('auth.login'))
        except DuplicateKeyError:
            flash("User already exists!", "danger")
    return render_template('auth/register.html')



@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)

        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Failed to login!', 'danger')
    return render_template('auth/login.html')


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))



