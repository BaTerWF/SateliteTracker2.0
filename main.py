from src.database import engine, Base


def init_db():
    # Эта строчка автоматически создаст файл satellites.db и таблицы на основе моделей
    Base.metadata.create_all(bind=engine)
    print(" База данных и таблицы успешно инициализированы!")

def main():
    print("Запуск трекера спутников...")
    init_db()

if __name__ == "__main__":
    main()