import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import sys


# шаблоны ввода
class TemplatePreview:

    def __init__(self, parent):
        self.parent = parent
        self.window = None

    def show(self, template_type="excel"):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Шаблоны ввода")
        self.window.geometry("400x320")
        self.window.resizable(False, False)
        self.window.grab_set()
        self.window.configure(bg="#f0f0f0")

        tk.Label(self.window, text="Выберите шаблон:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0").pack(pady=15)

        btn_frame = tk.Frame(self.window, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Excel шаблон (.xlsx)", command=self._open_excel_template,
                  bg="#4CAF50", fg="white", width=25, height=1).pack(pady=5)

        tk.Button(btn_frame, text="Текстовый шаблон (.txt)", command=self._open_text_template,
                  bg="#FF9800", fg="white", width=25, height=1).pack(pady=5)

        info_frame = tk.Frame(self.window, bg="#E3F2FD", relief=tk.GROOVE, bd=1)
        info_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(info_frame, text="Файлы шаблонов хранятся в папке data/",
                 font=("Arial", 9), bg="#E3F2FD", fg="#1565C0").pack(pady=5)

        tk.Button(self.window, text="Закрыть", command=self.window.destroy,
                  bg="#9E9E9E", fg="white", width=15).pack(pady=10)

    def _get_data_dir(self):
        # определяем где лежит папка data
        if getattr(sys, 'frozen', False):
            # запущено как EXE - берём папку где лежит exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # запущено как скрипт - берём папку проекта
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        data_dir = os.path.join(base_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir

    def _open_excel_template(self):
        data_dir = self._get_data_dir()
        template_path = os.path.join(data_dir, "schedule_template.xlsx")

        if not os.path.exists(template_path):
            messagebox.showinfo("Файл не найден",
                                f"Файл schedule_template.xlsx не обнаружен в папке data/\n\n"
                                f"Положите туда ваш файл")
            return

        self._open_file(template_path)

    def _open_text_template(self):
        data_dir = self._get_data_dir()
        template_path = os.path.join(data_dir, "schedule_template.txt")

        if not os.path.exists(template_path):
            messagebox.showinfo("Файл не найден",
                                f"Файл schedule_template.txt не обнаружен в папке data/\n\n"
                                f"Положите туда ваш файл")
            return

        self._open_file(template_path)

    def _open_file(self, filepath):
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            else:
                subprocess.call(['open', filepath])
        except Exception as e:
            messagebox.showerror("Не удалось открыть", f"Ошибка при открытии файла:\n{e}")