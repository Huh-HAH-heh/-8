import sqlite3
from pathlib import Path

def check_database(db_path: Path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Проверяем статус внешних ключей
    cursor.execute("PRAGMA foreign_keys;")
    fk_status = cursor.fetchone()[0]
    print(f"Внешние ключи включены: {bool(fk_status)}")
    
    # 2. Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    print(f"Список таблиц в БД: {tables}\n")
    
    # 3. Выводим информацию о полях для каждой таблицы
    for table in tables:
        print(f"--- Структура таблицы '{table}' (PRAGMA table_info) ---")
        cursor.execute(f"PRAGMA table_info({table});")
        for col in cursor.fetchall():
            print(f"ID полей: {col[0]} | Имя: {col[1]} | Тип: {col[2]} | NOT NULL: {bool(col[3])} | PK: {bool(col[5])}")
            
        # 4. Выводим информацию о внешних ключах
        print(f"--- Внешние ключи таблицы '{table}' ---")
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fk_list = cursor.fetchall()
        if fk_list:
            for fk in fk_list:
                print(f"Поле {fk[3]} -> Ссылка на таблицу {fk[2]}(id={fk[4]})")
        else:
            print("Внешние ключи отсутствуют")
        print("-" * 50 + "\n")
        
    conn.close()

if __name__ == "__main__":
    DB_FILE = Path(__file__).parent.parent / "data" / "college.db"
    check_database(DB_FILE)
