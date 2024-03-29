import os
import tempfile
import pytest
from verba.app import create_app
from verba.db import get_db, init_db
from verba.metadata import metadata
from sqlalchemy import insert, create_engine

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(dir=os.getcwd())

    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test',
        'ENGINE':  create_engine(f"sqlite:///{db_path}"),
    })
    md = metadata()
    users = md.tables['users']
    post = md.tables['post']

    create_user = (insert(users).values(username='test', password='pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', firstname='test', lastname='tester', email='test@test.com'))
    create_user2 = (insert(users).values(username='other', password='pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79', firstname='jon', lastname='doe', email='jonathan@lo.com'))
    insert_post = (insert(post).values(title="test title", author_id="1", firstname="tester", body="test body"))

    with app.app_context():
        init_db()
        get_db().execute(create_user)
        get_db().execute(create_user2)
        get_db().execute(insert_post)
        get_db().commit()
    yield app
    os.close(db_fd)
    os.unlink(db_path)

    
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def cli_runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@test.com', password='test'):
        return self._client.post('/login', data={'email': email, 'password': password})

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)