from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User

app = Blueprint('auth', __name__)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash('Username and password are required', 'danger')
        return render_template('register.html'), 400

    if User.query.filter_by(username=username).first():
        flash('Username already taken', 'danger')
        return render_template('register.html'), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash('Account created, you can now log in', 'success')
    return redirect(url_for('auth.login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('fe.books'))
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        flash('Wrong username or password', 'danger')
        return render_template('login.html'), 401

    login_user(user)

    next_url = request.args.get('next', '')
    if next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)
    return redirect(url_for('fe.books'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('fe.home'))
