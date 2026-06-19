from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Имя файла базы данных SQLite
DATABASE_URL = "sqlite:///satellites.db"

# create_engine создает соединение. 
# check_same_thread=False нужен только для SQLite, чтобы не было конфликтов между потоками
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Сессия для выполнения запросов
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех будущих моделей
class Base(DeclarativeBase):
    pass

# Функция-контекст для удобного получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()