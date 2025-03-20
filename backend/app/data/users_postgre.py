from sqlalchemy.orm import Session
from ..models import UserBase, User, pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from ..errors import Duplicate, Missing, MailDuplicate
from sqlalchemy.exc import IntegrityError


def user_to_userbase(user: User) -> UserBase:
    return UserBase(
        username=user.username,
        email=user.email,
        password=user.password,
        about=user.about
    )


def userbase_to_user(userbase: UserBase) -> User:
    return User(
        username=userbase.username,
        email=userbase.email,
        password=userbase.password,
        about=userbase.about
    )


def check_duplicate_mail(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise MailDuplicate(msg=f"Mail {email} already exists")
    return None


def get_one(db: Session, username: str) -> User:
    user = db.query(UserBase).filter(UserBase.username == username).first()
    if user:
        #return userbase_to_user(user)
        return sqlalchemy_to_pydantic(user, User)
    else:
        raise Missing(msg=f"User {username} not found")


def get_all(db: Session) -> list[User]:
    userbase_list = db.query(UserBase).all()
    #return [userbase_to_user(userbase) for userbase in userbase_list]
    return [sqlalchemy_to_pydantic(userbase, User) for userbase in userbase_list]


def create(db: Session, user: User) -> User:
    userbase = pydantic_to_sqlalchemy(user, UserBase)
    try:
        db.add(userbase)
        db.commit()
        db.refresh(userbase)
        
        #return userbase_to_user(userbase)
        return sqlalchemy_to_pydantic(userbase, User)
    except IntegrityError:
        db.rollback()  
        raise Duplicate(msg=f"User with email {user.email} already exists")


def modify(db: Session, user: User) -> User:
    existing_userbase = db.query(UserBase).filter(UserBase.username == user.username).first()
    
    if not existing_userbase:
        raise Missing(msg=f"User {user.username} not found")

    userbase = user_to_userbase(user)

    existing_userbase.username = userbase.username
    existing_userbase.email = userbase.email
    existing_userbase.password = userbase.password
    existing_userbase.about = userbase.about
    
    db.commit()
    db.refresh(existing_userbase)
    
    #return userbase_to_user(existing_userbase)
    return sqlalchemy_to_pydantic(existing_userbase, User)


def delete(db: Session, user: User) -> None:
    #userbase = user_to_userbase(user)
    userbase = pydantic_to_sqlalchemy(user, UserBase)
    
    existing_userbase = db.query(UserBase).filter(UserBase.username == userbase.username).first()
    
    if not existing_userbase:
        raise Missing(msg=f"User {user.username} not found")
    
    db.delete(existing_userbase)
    db.commit()
    
    return None