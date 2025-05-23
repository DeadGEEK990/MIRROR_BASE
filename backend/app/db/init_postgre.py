from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError  # Импортируем исключение для обработки ошибок подключения
from ..models import Base
from dotenv import load_dotenv
import os


# Новый URL для подключения к базе данных 'mirror_postgre'
DATABASE_URL = os.getenv('DATABASE_URL')

# Инициализация подключения к серверу PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_connection():
    try:
        # Пробуем подключиться к базе данных
        with engine.connect() as conn:
            print("Connection to the database was successful!")
            return True
    except OperationalError as e:
        print(f"Failed to connect to the database. Error: {e}")
        return False

# Проверка подключения
if test_connection():
    # Функция для создания таблиц в базе данных
    def init_db():
        # Создание всех таблиц, если их ещё нет
        Base.metadata.create_all(bind=engine)

    # Создаём таблицы
    init_db()
else:
    print("Unable to initialize the database due to connection failure.")
