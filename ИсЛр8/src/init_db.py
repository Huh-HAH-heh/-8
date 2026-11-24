import sqlite3
from pathlib import Path

def init_database(db_path: Path):
    # Автоматически создаем папку data/, если её нет
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # МАНДАТОРНО: Включаем поддержку внешних ключей
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Создаем РОДИТЕЛЬСКУЮ таблицу (Факультеты)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_number TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            dean TEXT NOT NULL
        );
    """)
    
    # 2. Создаем ДОЧЕРНЮЮ таблицу (Группы)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_number TEXT NOT NULL UNIQUE,
            specialty_code TEXT NOT NULL,
            faculty_id INTEGER NOT NULL,
            FOREIGN KEY (faculty_id) REFERENCES faculties(id) ON DELETE CASCADE
        );
    """)
    
    # Тестовое наполнение (чтобы таблицы не были пустыми)
    cursor.execute("INSERT OR IGNORE INTO faculties (id, faculty_number, name, dean) VALUES (1, 'ФВТ', 'Факультет вычислительной техники', 'Петров И.И.');")
    cursor.execute("INSERT OR IGNORE INTO groups_table (group_number, specialty_code, faculty_id) VALUES ('ИС-31', '09.02.07', 1);")
    
    conn.commit()
    conn.close()
    print(f"База данных успешно инициализирована по пути: {db_path}")

if __name__ == "__main__":
    DB_FILE = Path(__file__).parent.parent / "data" / "college.db"
    init_database(DB_FILE)
