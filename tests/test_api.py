def test_get_books_requires_login(make_client):
    client = make_client()
    response = client.get('/api/books')
    assert response.status_code == 401
    assert 'error' in response.get_json()

def test_create_book(make_client):
    client = make_client('gianni')
    response = client.post('/api/books', json={'title': 'Libro Bello', 'author': 'Autore Bello'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Libro Bello'
    assert data['author'] == 'Autore Bello'
    assert data['status'] == 'to-read'
    assert data['rating'] is None
    assert 'id' in data

def test_create_book_missing_title(make_client):
    client = make_client('gianni')
    response = client.post('/api/books', json={'author': 'Autore Bello'})
    assert response.status_code == 400
    assert 'title' in response.get_json()['errors']

def test_list_only_own_books(make_client, make_book):
    gianni = make_client('gianni')
    make_client('giovanni')
    make_book('gianni', title='Libro Bello')
    make_book('giovanni', title='Libro Brutto', author='Autrice Bella')
    response = gianni.get('/api/books')
    assert response.status_code == 200
    titles = [book['title'] for book in response.get_json()]
    assert titles == ['Libro Bello']

def test_admin_lists_all_books(make_client, make_book):
    admin = make_client('admin', role='admin')
    make_client('gianni')
    make_client('giovanni')
    make_book('gianni', title='Libro Bello')
    make_book('giovanni', title='Libro Brutto', author='Autrice Bella')
    response = admin.get('/api/books')
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_get_book_not_found(make_client):
    gianni = make_client('gianni')
    response = gianni.get('/api/books/999')
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_get_other_user_book_forbidden(make_client, make_book):
    gianni = make_client('gianni')
    make_client('giovanni')
    book_id = make_book('giovanni')
    response = gianni.get(f'/api/books/{book_id}')
    assert response.status_code == 403

def test_update_book(make_client, make_book):
    gianni = make_client('gianni')
    book_id = make_book('gianni')
    response = gianni.put(f'/api/books/{book_id}', json={'status': 'done', 'rating': 5})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'done'
    assert data['rating'] == 5
    assert data['title'] == 'Libro Bello'

def test_update_other_user_book_forbidden(make_client, make_book, get_book):
    gianni = make_client('gianni')
    make_client('giovanni')
    book_id = make_book('giovanni')
    response = gianni.put(f'/api/books/{book_id}', json={'status': 'done'})
    assert response.status_code == 403
    assert get_book(book_id)['status'] == 'to-read'

def test_delete_book(make_client, make_book):
    gianni = make_client('gianni')
    book_id = make_book('gianni')
    response = gianni.delete(f'/api/books/{book_id}')
    assert response.status_code == 200
    assert gianni.get(f'/api/books/{book_id}').status_code == 404

def test_delete_other_user_book_forbidden(make_client, make_book, get_book):
    gianni = make_client('gianni')
    make_client('giovanni')
    book_id = make_book('giovanni')
    response = gianni.delete(f'/api/books/{book_id}')
    assert response.status_code == 403
    assert get_book(book_id) is not None

def test_admin_can_delete_other_user_book(make_client, make_book, get_book):
    admin = make_client('admin', role='admin')
    make_client('giovanni')
    book_id = make_book('giovanni')
    response = admin.delete(f'/api/books/{book_id}')
    assert response.status_code == 200
    assert get_book(book_id) is None
