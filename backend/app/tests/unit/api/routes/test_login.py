import sys
import os
os.environ["MIRROR_TESTS"] = "True"

# Явное добавление корневой директории проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../..')))

import pytest
from fastapi.testclient import TestClient
from fastapi import Request
from unittest.mock import patch, MagicMock
from backend.app.api.main import app
from backend.app.tests.fake.data import users as data
from backend.app.models import User
from backend.app.service import users as service
from backend.app.api.deps import oauth2_dep
from backend.app.settings import TEMPLATES as templates



# Создаем тестовый клиент
client = TestClient(app)
data.create_fake_users()
print(f"\nСозданные тестовые пользователи: \n {data.get_all()}")


# Мокирование функции получения текущего пользователя
@pytest.fixture
def mock_get_curret_user():
    with patch("backend.app.service.users.get_curret_user") as mock:
        yield mock


@pytest.fixture
def mock_oauth2_dep():
    with patch("backend.app.api.deps.oauth2_dep") as mock:
        yield mock


@pytest.fixture
def mock_get_one_from_db():
    with patch("backend.app.data.users.get_one") as mock:
        yield mock


@pytest.fixture
def mock_decode_jwt():
    with patch("jose.jwt.decode") as mock:
        yield mock


@pytest.fixture
def mock_request_cookies_get():
    with patch("fastapi.request.cookies.get") as mock:
        yield mock


@pytest.fixture
def mock_user_page():
    with patch("backend.app.api.routes.users.user_page") as mock:
        yield mock


@pytest.fixture
def mock_auth_user():
    with patch("backend.app.tests.fake.service.users.auth_user") as mock:
        yield mock


def test_redirect_for_authenticated_user_main_link(mock_oauth2_dep, mock_get_one_from_db, mock_decode_jwt, capsys):
    user = data.get_random()

    mock_get_one_from_db.return_value = user   
    mock_oauth2_dep.return_value = "valid_token"   
    mock_decode_jwt.return_value = {"sub": user.username}

    app.dependency_overrides[oauth2_dep] = lambda: mock_oauth2_dep
        
    response = client.get("/", cookies={"access_token": "valid_token"}, follow_redirects=True)

    captured = capsys.readouterr()

    assert response.status_code == 200
    assert response.url.path == f"/users/{user.username}"
    assert "Redirecting to /users/" in captured.out
    assert len(response.history) > 0
    assert response.history[0].headers["Location"] == f"/users/{user.username}"


def test_redirect_for_unauthorized_user_main_link():    
    response = client.get("/", cookies={"access_token": "not_valid_token"}, follow_redirects=True)

    assert response.status_code == 200
    assert response.url.path == f"/registration"

    assert len(response.history) > 0
    assert response.history[0].headers["Location"] == f"/registration"


def test_redirect_for_unauthorized_user_registration_page(mock_get_one_from_db, capsys):
    user = data.create_fake_name()

    mock_get_one_from_db.return_value = None
        
    response = client.get("/registration", cookies={"access_token": "not_valid_token"}, follow_redirects=True)

    assert response.status_code == 200
    assert response.url.path == f"/registration"


def test_redirect_for_authenticated_user_registration_page(mock_get_curret_user, mock_decode_jwt, mock_oauth2_dep, mock_get_one_from_db):
    user = data.get_random()

    mock_get_curret_user.return_value = user
    mock_oauth2_dep.return_value = "valid_token"  
    mock_decode_jwt.return_value = {"sub": user.username}
    mock_get_one_from_db.return_value = user

    app.dependency_overrides[oauth2_dep] = lambda: mock_oauth2_dep

    response = client.get("/", cookies={"access_token": "valid_token"}, follow_redirects=True)

    assert response.status_code == 200
    assert response.url.path == f"/users/{user.username}"


def test_registration_user():
    user = {"username" : "fake_user",
            "email" : "fake_email@mail.ru",
            "password" : "fake_password"}
     
    response = client.post("/registration", data=user, follow_redirects=True)
    
    assert response.status_code == 200
    assert response.url.path == "/login"

    assert_user = data.get_one(user["username"])

    assert assert_user.username == user["username"]
    assert service.verify_password(user["password"], assert_user.password)
    assert assert_user.email == user["email"]
    assert assert_user.about == ""


def test_login_user(mock_auth_user):
    login_user = User(username="fake_user2", password="fake_pass2", email="fakemail@mail.ru", about="")
    data.create(login_user)

    login_user_data = {"username" : "fake_user2",
                       "password" : "fake_pass2"}
    
    response = client.post("/login", data = login_user_data, follow_redirects = True)

    print(f"Мы тут - {response.url.path}")

    assert response.status_code == 200
    assert response.url.path == f"/users/{login_user.username}"