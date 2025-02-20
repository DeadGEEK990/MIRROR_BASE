from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

# Параметры подключения с тайм-аутом
DATABASE_URL = "postgresql://admin:MirrorAdminPass@213.108.21.219:5432/mirror_database"

def test_connection():
    try:
        print("Подключение пытается установиться...")
        # Создаем подключение с указанным тайм-аутом
        engine = create_engine(DATABASE_URL, pool_timeout=10)  # Тайм-аут подключения 10 секунд

        # Пытаемся выполнить запрос для проверки подключения
        with engine.connect() as connection:
            print("Подключение успешно!")
            # Для теста можно выполнить простой запрос
            result = connection.execute("SELECT 1")
            print(f"Результат запроса: {result.scalar()}")
    
    except OperationalError as e:
        print(f"Ошибка подключения: {e}")
    
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")

if __name__ == "__main__":
    start_time = time.time()
    test_connection()
    print(f"Завершено за {time.time() - start_time:.2f} секунд")