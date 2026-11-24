from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from extensions import db
from models import Book, User
from utils import STATUSES, admin_required, get_book_for, validate_book

app = Blueprint('fe', __name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/books')
@login_required
def books():
    query = Book.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    status = request.args.get('status', '')
    if status in STATUSES:
        query = query.filter_by(status=status)

    q = request.args.get('q', '').strip()
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))

    results = query.order_by(Book.title).all()
    return render_template('books.html', books=results, statuses=STATUSES, status=status, q=q)

@app.route('/books/new', methods=['GET', 'POST'])
@login_required
def new_book():
    if request.method == 'GET':
        return render_template('book_form.html', book=None, values={}, statuses=STATUSES)

    data, errors = validate_book(request.form.to_dict())
    if errors:
        for field, message in errors.items():
            flash(f'{field} {message}', 'danger')
        return render_template('book_form.html', book=None, values=request.form, statuses=STATUSES), 400

    book = Book(user_id=current_user.id, **data)
    db.session.add(book)
    db.session.commit()

    flash('Book added', 'success')
    return redirect(url_for('fe.books'))

@app.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = get_book_for(current_user, id)

    if request.method == 'GET':
        return render_template('book_form.html', book=book, values=book.to_dict(), statuses=STATUSES)

    data, errors = validate_book(request.form.to_dict(), partial=True)
    if errors:
        for field, message in errors.items():
            flash(f'{field} {message}', 'danger')
        return render_template('book_form.html', book=book, values=request.form, statuses=STATUSES), 400

    for key, value in data.items():
        setattr(book, key, value)
    db.session.commit()

    flash('Book updated', 'success')
    return redirect(url_for('fe.books'))

@app.route('/books/<int:id>/delete', methods=['POST'])
@login_required
def delete_book(id):
    book = get_book_for(current_user, id, allow_admin=True)
    db.session.delete(book)
    db.session.commit()

    flash('Book deleted', 'success')
    return redirect(url_for('fe.books'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)
