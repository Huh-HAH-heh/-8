import sqlite3
from pathlib import Path  

ALLOWED_COLUMNS = {
    "faculties": {"faculty_number", "name", "dean"},
    "groups_table": {"group_number", "specialty_code", "faculty_id"}
}

def search_child_by_keyword(db_path, keyword):
    """Поиск по ключевому слову"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        pattern = f"%{keyword}%"
        query = "SELECT * FROM groups_table WHERE specialty_code LIKE ?;"
        cursor.execute(query, (pattern,))
        results = cursor.fetchall()
        return results
    finally:
        conn.close()

def update_record(db_path, table_name, record_id, **fields):
    if not fields:
        return False  
    if table_name not in ALLOWED_COLUMNS:
        raise ValueError(f"Недопустимое имя таблицы: {table_name}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        set_parts = []
        values = []
        for column_name, value in fields.items():
            if column_name not in ALLOWED_COLUMNS[table_name]:
                raise ValueError(f"Попытка инъекции! Поле '{column_name}' запрещено для обновления.")
            set_parts.append(f"{column_name} = ?")
            values.append(value)
        set_string = ", ".join(set_parts)
        query = f"UPDATE {table_name} SET {set_string} WHERE id = ?;"
        values.append(record_id)
        cursor.execute(query, values)
        updated = cursor.rowcount > 0
        conn.commit()
        return updated
    finally:
        conn.close()

def delete_record(db_path, table_name, record_id):
    """Удаление записи"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        query = f"DELETE FROM {table_name} WHERE id = ?;"
        cursor.execute(query, (record_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    except sqlite3.IntegrityError as e:
        print(f"\n[INTEGRITY BLOCK] Запрещено удалять запись из '{table_name}' с ID {record_id}!")
        print(f"Системная причина: На эту запись ссылаются дочерние таблицы. Лог: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_parent(db_path, faculty_number, name, dean):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    query = "INSERT INTO faculties (faculty_number, name, dean) VALUES(?,?,?);"
    cursor.execute(query, (faculty_number, name, dean))
    parent_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return parent_id 

def add_child(db_path, group_number, specialty_code, faculty_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        query = "INSERT INTO groups_table (group_number, specialty_code, faculty_id) VALUES (?, ?, ?);"
        cursor.execute(query, (group_number, specialty_code, faculty_id))
        child_id = cursor.lastrowid
        conn.commit()
        return child_id
    except sqlite3.IntegrityError as e:
        print(f"Ошибка: Не удалось добавить группу {group_number}. Факультета с ID {faculty_id} не существует! ({e})")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_all(db_path, table_name):
    if table_name not in ALLOWED_COLUMNS:
        raise ValueError(f"Недопустимое имя таблицы: {table_name}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"SELECT * FROM {table_name};"
    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()
    return records

def get_by_id(db_path, table_name, record_id):
    if table_name not in ALLOWED_COLUMNS:
        raise ValueError(f"Недопустимое имя таблицы: {table_name}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # ИСПРАВЛЕНО: Убрана лишняя буква 'E' в слове FROM, дописано получение и возврат записи
    query = f"SELECT * FROM {table_name} WHERE id = ?;"
    cursor.execute(query, (record_id,))
    record = cursor.fetchone()
    conn.close()
    return record


# === БЛОК ПРОВЕРКИ ВСЕХ ШАГОВ ===
if __name__ == "__main__":
    DB_FILE = Path(__file__).parent.parent / "data" / "college.db"
    
    print("=== ТЕСТИРОВАНИЕ ОПЕРАЦИЙ CRUD ===")
    
    # 1. Тест создания (Create)
    f_id = add_parent(DB_FILE, "ИТ-ФАК", "Факультет информационных технологий", "Смирнов К.Д.")
    print(f"Родитель добавлен, ID: {f_id}")
    
    g_id = add_child(DB_FILE, "ИС-31", "09.02.07", f_id)
    print(f"Дочерняя запись добавлена, ID: {g_id}")
    
    # Тест защиты внешнего ключа (try-except)
    bad_g_id = add_child(DB_FILE, "ТЕСТ-99", "00.00.00", 99999)
    print(f"Вставка с фальшивым ID вернула: {bad_g_id} (Ожидалось: None)")
    
    # 2. Тест чтения (Read)
    print(f"\nВсе факультеты: {get_all(DB_FILE, 'faculties')}")
    print(f"Поиск по ID={f_id}: {get_by_id(DB_FILE, 'faculties', f_id)}")
    print(f"Поиск по фейк-ID=8888: {get_by_id(DB_FILE, 'faculties', 8888)} (Ожидалось: None)")
    
    # 3. Тест обновления (Update)
    up_res = update_record(DB_FILE, "faculties", f_id, dean="Новый Декан А.А.")
    print(f"\nРезультат обновления записи: {up_res}")
    print(f"Обновленная запись: {get_by_id(DB_FILE, 'faculties', f_id)}")
    
    # 4. Тест поиска (LIKE)
    print(f"\nРезультат поиска по ключевому слову '09': {search_child_by_keyword(DB_FILE, '09')}")
    
    # 5. Тест удаления и контроля связей (Delete)
    print("\nПопытка удалить факультет, у которого есть группа ИС-31:")
    del_res = delete_record(DB_FILE, "faculties", f_id)
    print(f"Результат удаления связанного факультета: {del_res} (Ожидалось: False из-за блокировки)")
