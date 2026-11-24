def test_get_books_requires_login(make_client):
    client = make_client()
    response = client.get('/api/books')
    assert response.status_code == 401
    assert 'error' in response.get_json()

def test_create_book(make_client):
    client = make_client('alice')
    response = client.post('/api/books', json={'title': 'Dune', 'author': 'Frank Herbert'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Dune'
    assert data['author'] == 'Frank Herbert'
    assert data['status'] == 'to-read'
    assert data['rating'] is None
    assert 'id' in data

def test_create_book_missing_title(make_client):
    client = make_client('alice')
    response = client.post('/api/books', json={'author': 'Frank Herbert'})
    assert response.status_code == 400
    assert 'title' in response.get_json()['errors']

def test_list_only_own_books(make_client, make_book):
    alice = make_client('alice')
    make_client('bob')
    make_book('alice', title='Dune')
    make_book('bob', title='Emma', author='Jane Austen')
    response = alice.get('/api/books')
    assert response.status_code == 200
    titles = [book['title'] for book in response.get_json()]
    assert titles == ['Dune']

def test_admin_lists_all_books(make_client, make_book):
    admin = make_client('admin', role='admin')
    make_client('alice')
    make_client('bob')
    make_book('alice', title='Dune')
    make_book('bob', title='Emma', author='Jane Austen')
    response = admin.get('/api/books')
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_get_book_not_found(make_client):
    alice = make_client('alice')
    response = alice.get('/api/books/999')
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_get_other_user_book_forbidden(make_client, make_book):
    alice = make_client('alice')
    make_client('bob')
    book_id = make_book('bob')
    response = alice.get(f'/api/books/{book_id}')
    assert response.status_code == 403

def test_update_book(make_client, make_book):
    alice = make_client('alice')
    book_id = make_book('alice')
    response = alice.put(f'/api/books/{book_id}', json={'status': 'done', 'rating': 5})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'done'
    assert data['rating'] == 5
    assert data['title'] == 'Dune'

def test_update_other_user_book_forbidden(make_client, make_book, get_book):
    alice = make_client('alice')
    make_client('bob')
    book_id = make_book('bob')
    response = alice.put(f'/api/books/{book_id}', json={'status': 'done'})
    assert response.status_code == 403
    assert get_book(book_id)['status'] == 'to-read'

def test_delete_book(make_client, make_book):
    alice = make_client('alice')
    book_id = make_book('alice')
    response = alice.delete(f'/api/books/{book_id}')
    assert response.status_code == 200
    assert alice.get(f'/api/books/{book_id}').status_code == 404

def test_delete_other_user_book_forbidden(make_client, make_book, get_book):
    alice = make_client('alice')
    make_client('bob')
    book_id = make_book('bob')
    response = alice.delete(f'/api/books/{book_id}')
    assert response.status_code == 403
    assert get_book(book_id) is not None

def test_admin_can_delete_other_user_book(make_client, make_book, get_book):
    admin = make_client('admin', role='admin')
    make_client('bob')
    book_id = make_book('bob')
    response = admin.delete(f'/api/books/{book_id}')
    assert response.status_code == 200
    assert get_book(book_id) is None
