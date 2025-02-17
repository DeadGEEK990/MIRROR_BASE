from backend.app.models import User
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))
from backend.app.tests.fake_db.init import conn, curs, IntegrityError
from backend.app.errors import Duplicate, Missing, MailDuplicate
from faker import Faker


curs.execute("""CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    about TEXT
)""")


def check_duplicate_mail(email : str) -> None:
    qry = "SELECT 1 FROM users WHERE email = :email LIMIT 1"
    params = {"email" : email}
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        raise MailDuplicate(msg = f"Mail {email} already exists")
    return None


def row_to_model(row : tuple) -> User:
    (username, email, password, about) = row
    return User(username = username, email = email, password = password, about = about)


def model_to_dict(user : User) -> dict:
    return user.dict()


def get_one(username : str) -> User:
    qry = "select * from users where username = :username"
    params = {"username": username}
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise Missing(msg = f"User {username} not found")


def get_all() -> list[User]:
    qry = "select * from users"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]


def create(user : User) -> User:
    qry = "insert into users (username, email, password, about) values (:username, :email, :password, :about)"
    params = model_to_dict(user)
    try:
        check_duplicate_mail(user.email)
        curs.execute(qry, params)
    except IntegrityError:
        raise Duplicate(msg = f"User already exists")
    return get_one(user.username)


def modify(user : User) -> User:
    qry = """update users
             set username =: username
                 email =: email
                 password =: password
                 about =: about
             where username =: username_orig"""
    params = model_to_dict(user)
    params["username_orig"] = user.username
    curs.execute(qry, params)
    if curs.rowcount == 1:
        return get_one(user.username)
    else:
        raise Missing(msg = f"User {user.username} not found")


def delete(user : User) -> None:
    qry = "delete from users where username =: username"
    params = {"username" : user.username}
    res = curs.execute(qry, params)
    if curs.rowcount != 1:
        raise Missing(msg = f"User {user.username} not found")
    return


def get_random() -> User:
    qry = "select * from users order by random() limit 1"
    curs.execute(qry)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise Missing(msg = f"Random user not founde")
    

def create_fake_email() -> str:
    fake = Faker()
    email = fake.email()
    return email


def create_fake_password() -> str:
    fake = Faker()
    password = fake.password()
    return password


def create_fake_name() -> str:
    fake = Faker()
    username = fake.user_name()
    return username


def create_fake_user():
    user = User(username = create_fake_name(),
                email = create_fake_email(),
                password = create_fake_password(),
                about = "")
    qry = "insert into users (username, email, password, about) values (:username, :email, :password, :about)"
    params = user.dict()
    curs.execute(qry, params)
    return None


def create_fake_users(count:int = 5):
    for _ in range(count):
        create_fake_user()