from flask import Blueprint, request, jsonify
from flask_login import current_user
from extensions import db
from models import Book
from utils import api_login_required, get_book_for, validate_book

app = Blueprint('api', __name__)

@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Book not found'}), 404

@app.route('/books', methods=['GET'])
@api_login_required
def get_books():
    query = Book.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    results = query.order_by(Book.id).all()
    return jsonify([book.to_dict() for book in results]), 200

@app.route('/books', methods=['POST'])
@api_login_required
def create_book():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'JSON body required'}), 400

    clean, errors = validate_book(data)
    if errors:
        return jsonify({'errors': errors}), 400

    book = Book(user_id=current_user.id, **clean)
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@app.route('/books/<int:id>', methods=['GET'])
@api_login_required
def get_book(id):
    book = get_book_for(current_user, id, allow_admin=True)
    return jsonify(book.to_dict()), 200

@app.route('/books/<int:id>', methods=['PUT'])
@api_login_required
def update_book(id):
    book = get_book_for(current_user, id)

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'JSON body required'}), 400

    clean, errors = validate_book(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400

    for key, value in clean.items():
        setattr(book, key, value)
    db.session.commit()
    return jsonify(book.to_dict()), 200

@app.route('/books/<int:id>', methods=['DELETE'])
@api_login_required
def delete_book(id):
    book = get_book_for(current_user, id, allow_admin=True)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'}), 200
