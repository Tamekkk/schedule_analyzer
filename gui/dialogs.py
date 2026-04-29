import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Callable
from models.lesson import Lesson
from parsers.text_parser import TextParser
from utils.time_utils import to_min, to_str

DAYS_ORDER = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
WEEK_DISPLAY = {"both": "Обе", "even": "Чётная", "odd": "Нечётная"}
WEEK_CODE = {v: k for k, v in WEEK_DISPLAY.items()}


class ManualInputDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.shift_pressed = False
        self.window = None
        self.text = None

    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Ручной ввод расписания")
        self.window.geometry("700x550")
        self.window.grab_set()

        instr_frame = tk.Frame(self.window, bg="#f0f0f0", relief=tk.GROOVE, bd=1)
        instr_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(instr_frame, text="ФОРМАТ ВВОДА:", font=("Arial", 10, "bold"),
                 bg="#f0f0f0").pack(anchor="w", padx=10, pady=5)
        tk.Label(instr_frame, text="ДЕНЬ ЧЧ:ММ-ЧЧ:ММ ПРЕДМЕТ",
                 font=("Courier", 10), bg="#f0f0f0", fg="blue").pack(anchor="w", padx=10)
        tk.Label(instr_frame, text="Пример: ПН 09:00-10:30 Математика",
                 font=("Courier", 9), bg="#f0f0f0", fg="green").pack(anchor="w", padx=10)
        tk.Label(instr_frame, text="Ctrl+V - вставить | Shift+Enter - новая строка | Enter - загрузить",
                 font=("Arial", 9), bg="#f0f0f0", fg="gray").pack(anchor="w", padx=10)

        self.text = scrolledtext.ScrolledText(self.window, font=("Consolas", 11), height=12)
        self.text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.status = tk.Label(self.window, text="Готов к вводу", fg="green")
        self.status.pack(pady=5)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Загрузить (Enter)", command=self._load,
                  bg="#4CAF50", fg="white", width=18).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена (Esc)", command=self._cancel,
                  bg="#9E9E9E", fg="white", width=12).pack(side=tk.LEFT, padx=5)

        def on_shift_press(e):
            self.shift_pressed = True

        def on_shift_release(e):
            self.shift_pressed = False

        def on_enter(e):
            if self.shift_pressed:
                self.text.insert(tk.INSERT, '\n')
                return 'break'
            else:
                self._load()
                return 'break'

        def on_ctrl_v(e):
            try:
                text = self.parent.clipboard_get()
                self.text.insert(tk.INSERT, text)
                self.status.config(text="Вставлено из буфера", fg="green")
            except:
                self.status.config(text="Не удалось вставить", fg="red")
            return 'break'

        self.text.bind('<Shift_L>', on_shift_press)
        self.text.bind('<Shift_R>', on_shift_press)
        self.text.bind('<KeyRelease-Shift_L>', on_shift_release)
        self.text.bind('<KeyRelease-Shift_R>', on_shift_release)
        self.text.bind('<Return>', on_enter)
        self.text.bind('<Control-v>', on_ctrl_v)
        self.text.bind('<Control-V>', on_ctrl_v)

        self.window.bind('<Escape>', lambda e: self._cancel())

        self.text.focus_set()
        self.window.wait_window()
        return self.result

    def _load(self):
        if not self.text or not self.text.winfo_exists():
            return

        txt = self.text.get(1.0, tk.END).strip()
        if not txt:
            messagebox.showwarning("Ошибка", "Введите расписание", parent=self.window)
            return

        parser = TextParser()
        lessons = parser.parse(txt)

        if not lessons:
            messagebox.showwarning("Ошибка", "Не удалось распознать занятия", parent=self.window)
            return

        self.result = lessons
        self.window.destroy()

    def _cancel(self):
        self.result = None
        if self.window:
            self.window.destroy()


class FreeTimeDialog:
    def __init__(self, parent, current=None):
        self.parent = parent
        self.current = current or {}
        self.result = None
        self.window = None
        self.entries = {}

    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Свободное время")
        self.window.geometry("300x400")
        self.window.grab_set()

        tk.Label(self.window, text="Формат: ЧЧ:ММ-ЧЧ:ММ").pack(pady=5)
        tk.Label(self.window, text="Пример: 09:00-17:00").pack()

        for d in DAYS_ORDER:
            f = tk.Frame(self.window)
            f.pack(fill=tk.X, padx=20, pady=2)
            tk.Label(f, text=f"{d}:", width=5).pack(side=tk.LEFT)
            e = tk.Entry(f, width=20)
            e.pack(side=tk.LEFT)
            self.entries[d] = e

            if d in self.current:
                start, end = self.current[d]
                e.insert(0, f"{to_str(start)}-{to_str(end)}")

        tk.Button(self.window, text="Сохранить", command=self._save, bg="lightgreen").pack(pady=20)
        tk.Button(self.window, text="Отмена", command=self._cancel).pack(pady=5)

        self.window.wait_window()
        return self.result

    def _save(self):
        ft = {}
        for d, e in self.entries.items():
            val = e.get().strip()
            if val and '-' in val:
                try:
                    s, e2 = val.split('-')
                    start = to_min(s.strip())
                    end = to_min(e2.strip())
                    if start < end:
                        ft[d] = (start, end)
                except:
                    pass
        self.result = ft
        self.window.destroy()

    def _cancel(self):
        self.result = self.current
        self.window.destroy()


class WeekSetupDialog:
    def __init__(self, parent, lessons: List[Lesson], on_save: Callable):
        self.parent = parent
        self.lessons = lessons
        self.on_save = on_save
        self.week_vars = []
        self.window = None

    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Настройка недель для занятий")
        self.window.geometry("850x550")
        self.window.grab_set()

        mass_frame = tk.Frame(self.window)
        mass_frame.pack(fill=tk.X, pady=5, padx=10)

        tk.Label(mass_frame, text="Массово задать для всех занятий:",
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        for code, name in WEEK_DISPLAY.items():
            btn = tk.Button(mass_frame, text=name,
                           command=lambda w=code: self._set_all_weeks(w),
                           width=10)
            btn.pack(side=tk.LEFT, padx=5)

        canvas = tk.Canvas(self.window)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        header = tk.Frame(scrollable_frame)
        header.pack(fill=tk.X, pady=5)
        tk.Label(header, text="День", width=10, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(header, text="Время", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(header, text="Предмет", width=40, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(header, text="Тип недели", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        for i, lesson in enumerate(self.lessons):
            row = tk.Frame(scrollable_frame)
            row.pack(fill=tk.X, pady=2)

            tk.Label(row, text=lesson.day, width=10).pack(side=tk.LEFT, padx=5)
            tk.Label(row, text=f"{lesson.start_time}-{lesson.end_time}", width=15).pack(side=tk.LEFT, padx=5)
            tk.Label(row, text=lesson.subject[:50], width=40, anchor="w").pack(side=tk.LEFT, padx=5)

            display_value = WEEK_DISPLAY.get(lesson.week_type, "Обе")
            var = tk.StringVar(value=display_value)
            self.week_vars.append((var, i))

            combo = ttk.Combobox(row, textvariable=var, values=["Обе", "Чётная", "Нечётная"], width=12, state="readonly")
            combo.pack(side=tk.LEFT, padx=5)

            def make_save(idx, v):
                return lambda e=None: setattr(self.lessons[idx], 'week_type', WEEK_CODE.get(v.get(), "both"))

            combo.bind('<<ComboboxSelected>>', make_save(i, var))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(self.window, text="Сохранить все", command=self._save).pack(pady=10)

    def _set_all_weeks(self, week_code: str):
        for var, _ in self.week_vars:
            var.set(WEEK_DISPLAY[week_code])
        for _, idx in self.week_vars:
            self.lessons[idx].week_type = week_code
        messagebox.showinfo("Готово", f"Для всех занятий установлена неделя: {WEEK_DISPLAY[week_code]}", parent=self.window)

    def _save(self):
        for var, idx in self.week_vars:
            display = var.get()
            code = WEEK_CODE.get(display, "both")
            self.lessons[idx].week_type = code
        self.on_save()
        messagebox.showinfo("Успех", "Настройки недель сохранены", parent=self.window)
        self.window.destroy()