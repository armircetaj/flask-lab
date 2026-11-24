from functools import wraps
from flask import abort, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import Book

STATUSES = ['to-read', 'reading', 'done']

def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

def api_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return wrapper

def get_book_for(user, book_id, allow_admin=False):
    book = db.session.get(Book, book_id)
    if book is None:
        abort(404)
    if book.user_id != user.id and not (allow_admin and user.is_admin):
        abort(403)
    return book

def validate_book(data, partial=False):
    clean = {}
    errors = {}

    if not isinstance(data, dict):
        return clean, {'error': 'Invalid data'}

    for field in ('title', 'author'):
        if field in data:
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                errors[field] = 'must be a non empty text'
            else:
                clean[field] = value.strip()
        elif not partial:
            errors[field] = 'is required'

    if 'status' in data:
        if data['status'] in STATUSES:
            clean['status'] = data['status']
        else:
            errors['status'] = f'must be one of {STATUSES}'

    if 'rating' in data:
        rating = data['rating']
        if rating is None or rating == '':
            clean['rating'] = None
        elif isinstance(rating, (bool, float)):
            errors['rating'] = 'must be an integer between 1 and 5'
        else:
            try:
                rating = int(rating)
            except (TypeError, ValueError):
                errors['rating'] = 'must be an integer between 1 and 5'
            else:
                if 1 <= rating <= 5:
                    clean['rating'] = rating
                else:
                    errors['rating'] = 'must be an integer between 1 and 5'

    if 'notes' in data:
        notes = data['notes']
        if notes is None:
            clean['notes'] = None
        elif isinstance(notes, str):
            clean['notes'] = notes.strip() or None
        else:
            errors['notes'] = 'must be text'

    return clean, errors
