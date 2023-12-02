import pytest, sqlite3
from flask import g 
from FDataBase import FDataBase
from app import app, dbase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

DATABASE = '/tmp/flsite.db'
SECRET_KEY = "bbdbsuyfbdt32t411!@3218"

# Connect to DB
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Create DB
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

# def commit_db():
#     db = connect_db()
#     db.commit()
#     db.close()

# Get DB
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

def before_request():
    """ Встановлення з'єднання з БД перед виконуванням запиту """
    global dbase
    db = get_db()
    dbase = FDataBase(db)

def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_successful_login(client):
    with app.app_context():
        before_request()
        dbase.addUser(name='test_user', email='test@example.com', hpsw='test_password')

    response = client.post('/login', data=dict(email='test@example.com', psw='test_password', rm=True))

    assert response.status_code == 200

    with app.app_context():
        before_request()
        dbase.deleteUser(email='test@example.com')

    assert response.status_code == 200


def test_successful_admin_login(client):
    with app.app_context():
        before_request()
        response = client.post('/admin/login', data=dict(user='admin', psw='admin'))

    assert response.status_code == 302

def test_unsuccessful_admin_login(client):
    with app.app_context():
        before_request()
        response = client.post('/admin/login', data=dict(user='admin_invalid', psw='admin_invalid'))

    assert response.status_code == 200


def test_successful_register(client):
    with app.app_context():
        before_request()
        response = client.post('/register', data=dict(name='test2', email='test2@example.com', psw='test2_password', psw2='test2_password'))

    assert response.status_code == 302

    with app.app_context():
        before_request()
        dbase.deleteUser(email='test2@example.com')

    assert response.status_code == 302

# def test_successful_change_profile_data(client):
#     with app.app_context():
#         before_request()
#         dbase.addUser(name='test_user3', email='test3@example.com', hpsw='test3_password')
#     client.post('/login', data=dict(email='test3@example.com', psw='test3_password', rm=True))
#     response = client.post('/uploadata', data=dict(name='test5', email='test5@example.com', psw='test5_password', psw2='test5_password'))

#     assert response.status_code == 302

def test_successful_change_profile_data(client):
    with app.app_context():
        before_request()
        dbase.addUser(name='test_user3', email='test3@example.com', hpsw='test3_password')
        
        client.post('/login', data=dict(email='test3@example.com', psw='test3_password', rm=True))

        response = client.get('/profile')

        if response.status_code == 302 and '/login' in response.location:
            client.post('/login', data=dict(email='test3@example.com', psw='test3_password', rm=True))
            client.get('/profile')
            response2 = client.post('/uploadata', data=dict(name='test5', email='test5@example.com', psw='test3_password', psw2='test3_password'))
            

        assert response2.status_code == 302

        with app.app_context():
            before_request()
            dbase.deleteUser(email='test3@example.com')



    # with app.app_context():
    #     before_request()
    #     delete = dbase.deleteUser(email='test2@example.com')

    # assert response.status_code == 302


# def test_successful_add_post(client):
#     with app.app_context():
#         before_request()
#         dbase.addUser(name='test_user3', email='test3@example.com', hpsw='test3_password')

#     # Логін користувача "вручну"
#     with client:
#         client.post('/login', data=dict(email='test3@example.com', psw='test3_password', rm=True))

#         # Перевірка, що користувач ввійшов в систему
#         current_user.is_authenticated = True

#         # Додавання поста
#         response = client.post('/add_post', data=dict(title='Post Today For Me', url='My Test Link Heh', text='Text for my test with adding my post'))

#         # Перевірка, що пост додано успішно
#         assert response.status_code == 302

#         # Вийти з системи
#         client.get('/logout')

#     # Перевірка, що користувач вийшов з системи
#     assert current_user.is_authenticated == False

#     with app.app_context():
#         before_request()
#         dbase.deleteUser(email='test3@example.com')






    

    

    