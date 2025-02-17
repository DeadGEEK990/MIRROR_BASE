from app.models import User
import os
from app.db.init import conn, curs, IntegrityError
from app.errors import Duplicate, Missing


curs.execute("""create table if not exists users(
             username text primary key,
             email text,
             hash text,
             about text)""")


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
    qry = "insert into users (username, email, hash, about) values (:username, :email, :hash, :about)"
    params = model_to_dict(user)
    try:
        curs.execute(qry, params)
    except IntegrityError:
        raise Duplicate(msg = f"User {user.username} already exists")
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