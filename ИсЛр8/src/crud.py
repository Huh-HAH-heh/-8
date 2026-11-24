import sqlite3
ALLOWED_COLUMS = {
                  "faculties":{"faculty_number","name","dean"},
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
    """ну удаляет"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        query = f"DELETE FROM {table_name} WHERE id = ?;"
        cursor.execute(query, (record_id,))
        
        # сколько изменено строк
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
    cursor.execute(query, (faculty_number,name,dean))
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
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    query = f"SELECT * FROME {table_name};"
    cursor.execute(query)
    records = cursor.fetchall()#все
    conn.close()
    return records
def get_by_id(db_path, table_name, record_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT * FROME {table_name} WHERE id = ?;"
    cursor.execute(query, (record_id,))


if __name__ == "__main__":
    DB_FILE = Path(__file__).parent.parent / "data" / "college.db"
    init_database(DB_FILE)