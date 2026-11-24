import pytest
from app import create_app
from config import TestConfig
from extensions import db
from models import User, Book

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    return app

@pytest.fixture
def make_user(app):
    def _make_user(username, password='secret', role='user'):
        with app.app_context():
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user.id
    return _make_user

@pytest.fixture
def make_client(app, make_user):
    def _make_client(username=None, password='secret', role='user'):
        client = app.test_client()
        if username:
            make_user(username, password, role)
            client.post('/login', data={'username': username, 'password': password})
        return client
    return _make_client

@pytest.fixture
def make_book(app):
    def _make_book(username, title='Dune', author='Frank Herbert', **kwargs):
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            book = Book(title=title, author=author, user_id=user.id, **kwargs)
            db.session.add(book)
            db.session.commit()
            return book.id
    return _make_book

@pytest.fixture
def get_book(app):
    def _get_book(book_id):
        with app.app_context():
            book = db.session.get(Book, book_id)
            return book.to_dict() if book else None
    return _get_book

@pytest.fixture
def get_user(app):
    def _get_user(username):
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if user is None:
                return None
            return {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'password_hash': user.password_hash
            }
    return _get_user

@pytest.fixture
def count_users(app):
    def _count_users():
        with app.app_context():
            return User.query.count()
    return _count_users
