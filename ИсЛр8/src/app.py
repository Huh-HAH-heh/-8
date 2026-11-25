import tkinter as tk
from tkinter import ttk
from pathlib import Path
from tkinter import messagebox, simpledialog

try:
    import crud
except ImportError:
    try:
        from college_db import crud
    except ImportError:
        from scripts import crud
DB_FILE = Path(__file__).parent.parent / "data" / "college.db"

def on_search():
    keyword = entry_search.get().strip()
    
    try:
        search_results = crud.search_child_by_keyword(DB_FILE, keyword)
        tree2.delete(*tree2.get_children())
        if not search_results:
            messagebox.showinfo("Результаты поиска", "Найдено: 0 записей.")
            return
        for row in search_results:
            tree2.insert("", tk.END, values=row)
    except Exception as e:
        messagebox.showerror("Ошибка поиска", f"Не удалось выполнить поиск:\n{e}")

def on_reset():
    entry_search.delete(0,tk.END)
    _refresh_all()


def on_edit_selected():
    f_focus = tree1.focus()
    g_focus = tree2.focus()
    
    if not f_focus and not g_focus:
        messagebox.showinfo("Внимание", "Пожалуйста, выберите запись в одной из таблиц для редактирования.")
        return

    if f_focus:
        record_id = tree1.item(f_focus, "values")[0]
        on_add_parent(record_id=record_id)  # Вызываем форму факультета с ID
    else:
        record_id = tree2.item(g_focus, "values")[0]
        on_add_child(record_id=record_id)   # Вызываем форму группы с ID



def _refresh_all():
    tree1.delete(*tree1.get_children())
    tree2.delete(*tree2.get_children())
    
    try:
        
        faculties_data = crud.get_all(DB_FILE, "faculties")
        groups_data = crud.get_all(DB_FILE, "groups_table")
        
 
        for row in faculties_data:
            tree1.insert("", tk.END, values=row)
     
        for row in groups_data:
            tree2.insert("", tk.END, values=row)
            
    except Exception as e:
        print(f"Ошибка при обновлении таблиц: {e}")


def on_add_parent(record_id=None):
    win = tk.Toplevel(root)
    win.title("Редактировать факультет" if record_id else "Добавить факультет")
    win.geometry("350x250")
    win.resizable(False, False)
    win.grab_set()
    
    tk.Label(win, text="№/Код Факультета:").pack(pady=(10, 0))
    entry_num = tk.Entry(win, width=30)
    entry_num.pack()

    tk.Label(win, text="Название факультета:").pack(pady=(5, 0))
    entry_name = tk.Entry(win, width=30)
    entry_name.pack()

    tk.Label(win, text="ФИО Декана:").pack(pady=(5, 0))
    entry_dean = tk.Entry(win, width=30)
    entry_dean.pack()

    # Если это редактирование, подтягиваем текущие значения из БД
    if record_id is not None:
        current = crud.get_by_id(DB_FILE, "faculties", record_id)
        if current:
            entry_num.insert(0, str(current[1]))
            entry_name.insert(0, str(current[2]))
            entry_dean.insert(0, str(current[3]))

    def save():
        try:
            num = entry_num.get().strip()
            name = entry_name.get().strip()
            dean = entry_dean.get().strip()

            if not num or not name or not dean:
                raise ValueError("Все поля должны быть заполнены!")

            if record_id is not None:
                # Шаг 6: Вызов готовой функции обновления
                crud.update_record(DB_FILE, "faculties", record_id, faculty_number=num, name=name, dean=dean)
                msg = "Данные факультета обновлены!"
            else:
                # Шаг 5: Вызов функции создания
                crud.add_parent(DB_FILE, num, name, dean)
                msg = "Факультет успешно добавлен!"
            
            _refresh_all()
            messagebox.showinfo("Успех", msg)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка ввода", str(e))

    tk.Button(win, text="Сохранить", width=15, command=save).pack(pady=15)


def on_add_child(record_id=None):
    win = tk.Toplevel(root)
    win.title("Редактировать группу" if record_id else "Добавить группа")
    win.geometry("350x250")
    win.resizable(False, False)
    win.grab_set()

    tk.Label(win, text="№ Группы:").pack(pady=(10, 0))
    entry_num = tk.Entry(win, width=30)
    entry_num.pack()

    tk.Label(win, text="Код специальности:").pack(pady=(5, 0))
    entry_code = tk.Entry(win, width=30)
    entry_code.pack()

    tk.Label(win, text="ID Факультета (число):").pack(pady=(5, 0))
    entry_fac_id = tk.Entry(win, width=30)
    entry_fac_id.pack()

    if record_id is not None:
        # Редактирование: берем данные из БД
        current = crud.get_by_id(DB_FILE, "groups_table", record_id)
        if current:
            entry_num.insert(0, str(current[1]))
            entry_code.insert(0, str(current[2]))
            entry_fac_id.insert(0, str(current[3]))
    else:
        # Автоподстановка ID родительской записи при создании
        selected_parent = tree1.focus()
        if selected_parent:
            parent_values = tree1.item(selected_parent)["values"]
            entry_fac_id.insert(0, str(parent_values[0]))

    def save():
        try:
            num = entry_num.get().strip()
            code = entry_code.get().strip()
            fac_id_str = entry_fac_id.get().strip()

            if not num or not code or not fac_id_str:
                raise ValueError("Все поля должны быть заполнены!")

            try:
                fac_id = int(fac_id_str)
            except ValueError:
                raise ValueError("Ошибка ввода: ID факультета должно быть числом!")

            if record_id is not None:
                # Шаг 6: Вызов готовой функции обновления
                success = crud.update_record(DB_FILE, "groups_table", record_id, group_number=num, specialty_code=code, faculty_id=fac_id)
                if not success:
                    raise ValueError("Не удалось обновить. Проверьте, существует ли указанный ID факультета.")
                msg = "Данные группы обновлены!"
            else:
                # Шаг 5: Вызов функции создания
                result = crud.add_child(DB_FILE, num, code, fac_id)
                if result is None:
                    raise ValueError(f"Ошибка FK: Родительского факультета с ID {fac_id} не существует!")
                msg = "Группа успешно добавлена!"

            _refresh_all()
            messagebox.showinfo("Успех", msg)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    tk.Button(win, text="Сохранить", width=15, command=save).pack(pady=15)

def on_delete_selected():
    """Обработчик удаления записи"""
    try:
        # Смотрим, какая таблица сейчас активна
        f_focus = tree1.focus()
        g_focus = tree2.focus()
        
        if not f_focus and not g_focus:
            raise ValueError("Пожалуйста, выделите строку в любой из таблиц для удаления.")
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите безвозвратно удалить выбранную запись?")
        if not confirm:
            return    
        if f_focus:
            # Удаляем факультет
            item_data = tree1.item(f_focus)["values"]
            record_id = item_data[0]
            success = crud.delete_record(DB_FILE, "faculties", record_id)
            if not success:
                raise Exception("База данных отклонила удаление. Возможно, у этого факультета есть связанные группы.")
        else:
            # Удаляем группу
            item_data = tree2.item(g_focus)["values"]
            record_id = item_data[0]
            crud.delete_record(DB_FILE, "groups_table", record_id)

        _refresh_all()
        messagebox.showinfo("Успех", "Запись успешно удалена!")

    except ValueError as val_err:
        messagebox.showwarning("Внимание", str(val_err))
    except Exception as e:
        messagebox.showerror("Ошибка удаления", f"Не удалось удалить запись:\n{e}")

# интерфейс
root = tk.Tk()
root.title("Информационная система: Факультеты и Группы")
root.geometry("950x450")

# нарезка
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)


search_frame=tk.LabelFrame(root,text="поиск групп по специальности")
search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

entry_search = tk.Entry(search_frame, width=40)
entry_search.pack(side=tk.LEFT, padx=10, pady=5)

btn_search = tk.Button(search_frame, text="Поиск", width=12, command=on_search)
btn_search.pack(side=tk.LEFT, padx=5)

btn_reset = tk.Button(search_frame, text="Сбросить", width=12, command=on_reset)
btn_reset.pack(side=tk.LEFT, padx=5)

#tree1
tree1_frame = tk.LabelFrame(root, text=" Факультеты (Родительская таблица) ")
tree1_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


tree1 = ttk.Treeview(tree1_frame, columns=("id", "faculty_number", "name", "dean"), show="headings")
tree1.heading("id", text="ID")
tree1.heading("faculty_number", text="№ Факультета")
tree1.heading("name", text="Название факультета")
tree1.heading("dean", text="Декан")

tree1.column("id", width=50, minwidth=40, stretch=tk.NO)
tree1.column("faculty_number", width=100, minwidth=80)
tree1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll1 = ttk.Scrollbar(tree1_frame, orient=tk.VERTICAL, command=tree1.yview)
tree1.configure(yscrollcommand=scroll1.set)
scroll1.pack(side=tk.RIGHT, fill=tk.Y)

#tree2
tree2_frame = tk.LabelFrame(root, text=" Группы (Дочерняя таблица) ")
tree2_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

tree2 = ttk.Treeview(tree2_frame, columns=("id", "group_number", "specialty_code", "faculty_id"), show="headings")
tree2.heading("id", text="ID")
tree2.heading("group_number", text="№ Группы")
tree2.heading("specialty_code", text="Код специальности")
tree2.heading("faculty_id", text="ID Факультета")

tree2.column("id", width=50, minwidth=40, stretch=tk.NO)
tree2.column("faculty_id", width=90, minwidth=80, stretch=tk.NO)
tree2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll2 = ttk.Scrollbar(tree2_frame, orient=tk.VERTICAL, command=tree2.yview)
tree2.configure(yscrollcommand=scroll2.set)
scroll2.pack(side=tk.RIGHT, fill=tk.Y)


buttons_frame = tk.Frame(root)
buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=15)

btn_refresh = tk.Button(buttons_frame, text="Обновить данные", width=18,command=_refresh_all)
btn_refresh.pack(side=tk.LEFT, padx=5)

btn_add_fac = tk.Button(buttons_frame, text="Добавить факультет", width=18,command=on_add_parent)
btn_add_fac.pack(side=tk.LEFT, padx=5)

btn_add_group = tk.Button(buttons_frame, text="Добавить группу", width=18,command=on_add_child)
btn_add_group.pack(side=tk.LEFT, padx=5)

btn_edit = tk.Button(buttons_frame, text="Редактировать", width=15,command=on_edit_selected)
btn_edit.pack(side=tk.LEFT, padx=5)

btn_delete = tk.Button(buttons_frame, text="Удалить выбранное", width=18, fg="red",command=on_delete_selected)
btn_delete.pack(side=tk.RIGHT, padx=5)


if __name__ == "__main__":
    _refresh_all()
    root.mainloop()
    