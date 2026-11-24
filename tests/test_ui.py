def test_books_page_redirects_to_login(make_client):
    client = make_client()
    response = client.get('/books')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_register(make_client, get_user):
    client = make_client()
    response = client.post('/register', data={'username': 'alice', 'password': 'secret'})
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
    user = get_user('alice')
    assert user is not None
    assert user['role'] == 'user'
    assert user['password_hash'] != 'secret'

def test_register_duplicate_username(make_client, make_user, count_users):
    make_user('alice')
    client = make_client()
    response = client.post('/register', data={'username': 'alice', 'password': 'other'})
    assert response.status_code == 400
    assert count_users() == 1

def test_login_success(make_client, make_user):
    make_user('alice')
    client = make_client()
    response = client.post('/login', data={'username': 'alice', 'password': 'secret'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/books')
    assert client.get('/books').status_code == 200

def test_login_wrong_password(make_client, make_user):
    make_user('alice')
    client = make_client()
    response = client.post('/login', data={'username': 'alice', 'password': 'wrong'})
    assert response.status_code == 401
    assert client.get('/books').status_code == 302

def test_logout(make_client):
    client = make_client('alice')
    assert client.get('/books').status_code == 200
    response = client.post('/logout')
    assert response.status_code == 302
    assert client.get('/books').status_code == 302

def test_books_page_shows_only_own_books(make_client, make_book):
    alice = make_client('alice')
    make_client('bob')
    make_book('alice', title='Dune')
    make_book('bob', title='Emma', author='Jane Austen')
    response = alice.get('/books')
    assert b'Dune' in response.data
    assert b'Emma' not in response.data

def test_create_book(make_client, get_book):
    alice = make_client('alice')
    response = alice.post('/books/new', data={'title': 'Dune', 'author': 'Frank Herbert', 'status': 'reading', 'rating': '', 'notes': ''}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dune' in response.data
    book = get_book(1)
    assert book is not None
    assert book['title'] == 'Dune'
    assert book['status'] == 'reading'
    assert book['rating'] is None

def test_edit_book(make_client, make_book, get_book):
    alice = make_client('alice')
    book_id = make_book('alice')
    response = alice.post(f'/books/{book_id}/edit', data={'title': 'Dune Messiah', 'author': 'Frank Herbert', 'status': 'done', 'rating': '4', 'notes': 'good'})
    assert response.status_code == 302
    book = get_book(book_id)
    assert book['title'] == 'Dune Messiah'
    assert book['status'] == 'done'
    assert book['rating'] == 4

def test_delete_book(make_client, make_book, get_book):
    alice = make_client('alice')
    book_id = make_book('alice')
    response = alice.post(f'/books/{book_id}/delete')
    assert response.status_code == 302
    assert get_book(book_id) is None

def test_admin_users_forbidden_for_normal_user(make_client):
    alice = make_client('alice')
    response = alice.get('/admin/users')
    assert response.status_code == 403

def test_admin_users_page(make_client):
    admin = make_client('admin', role='admin')
    make_client('alice')
    response = admin.get('/admin/users')
    assert response.status_code == 200
    assert b'alice' in response.data
