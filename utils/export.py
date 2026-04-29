import csv
from tkinter import filedialog, messagebox

def export_to_csv(lessons, parent):
    if not lessons:
        messagebox.showwarning("Нет данных", "Сначала загрузите расписание", parent=parent)
        return False

    path = filedialog.asksaveasfilename(
        title="Сохранить расписание как CSV",
        defaultextension=".csv",
        filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")])

    if not path:
        return False

    try:
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["День", "Предмет", "Начало", "Конец", "Неделя", "Преподаватель", "Аудитория"])

            for lesson in lessons:
                writer.writerow([
                    lesson.day,
                    lesson.subject,
                    lesson.start_time,
                    lesson.end_time,
                    lesson.week_type,
                    lesson.teacher if lesson.teacher else "",
                    lesson.room if lesson.room else ""
                ])

        messagebox.showinfo("Готово",
                            f"Расписание сохранено в:\n{path}\n\nВсего экспортировано занятий: {len(lessons)}",
                            parent=parent)
        return True

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}", parent=parent)
        return False