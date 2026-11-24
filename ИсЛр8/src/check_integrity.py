import sqlite3
from pathlib import Path

def test_integrity(db_path: Path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Обязательно включаем для этого соединения
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print("Попытка вставить группу со ссылкой на несуществующий факультет (ID 99999)...")
    try:
        cursor.execute("""
            INSERT INTO groups_table (group_number, specialty_code, faculty_id) 
            VALUES ('ТЕСТ-99', '00.00.00', 99999);
        """)
        conn.commit()
        print("РЕЗУЛЬТАТ: Запись вставилась молча — внешний ключ НЕ РАБОТАЕТ! (Ошибка)")
    except sqlite3.IntegrityError as e:
        print(f"РЕЗУЛЬТАТ: Перехвачена ошибка IntegrityError: '{e}'")
        print("Внешний ключ заблокировал некорректную связь. Всё работает ПРАВИЛЬНО!")
        conn.rollback()
        
    conn.close()

if __name__ == "__main__":
    DB_FILE = Path(__file__).parent.parent / "data" / "college.db"
    test_integrity(DB_FILE)
