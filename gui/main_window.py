import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from parsers.mtuci_parser import MTUCIParser
from parsers.excel_parser import ExcelParser
from gui.dialogs import ManualInputDialog, FreeTimeDialog, WeekSetupDialog
from gui.template_preview import TemplatePreview
from gui.menu import setup_menu
from gui.toolbar import create_toolbar
from utils.analyzer import ScheduleAnalyzer
from utils.export import export_to_csv
from config import WEEK_DISPLAY, WEEK_CODE
import matplotlib.pyplot as plt

class ScheduleApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Анализатор расписания")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)

        self.lessons = []
        self.free_time = {}
        self.week_type = "both"
        self.week_names = WEEK_DISPLAY
        self.group_entry = None

        self.callbacks = {
            'load_mtuci': self._load_mtuci,
            'load_file': self._load_file,
            'manual_input': self._manual_input,
            'setup_weeks': self._setup_weeks,
            'show_analytics': self._show_analytics,
            'plot_graph': self._plot_graph,
            'set_week': self._set_week,
            'set_free_time': self._set_free_time,
            'show_templates': self._show_templates,
            'export_csv': self._export_csv,
            'show_about': self._show_about,
            'on_close': self._on_close,
        }

        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self):
        self.root.mainloop()

    def _setup_ui(self):
        self.group_entry = create_toolbar(self.root, self.callbacks)
        setup_menu(self.root, self.callbacks)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.tree = ttk.Treeview(tree_frame, height=15)
        scroll_y = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll_x = tk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree["columns"] = ("time", "subject")
        self.tree.heading("#0", text="День")
        self.tree.heading("time", text="Время")
        self.tree.heading("subject", text="Предмет")

        self.tree.column("#0", width=60)
        self.tree.column("time", width=90)
        self.tree.column("subject", width=450)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.output_frame = tk.Frame(main_frame)
        self.output_frame.pack(fill=tk.BOTH, expand=True)

        self.output = tk.Text(self.output_frame, wrap=tk.WORD, font=("Consolas", 9), height=10)
        self.output.pack(fill=tk.BOTH, expand=True)

        scroll_text = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output.yview)
        scroll_text.pack(side=tk.RIGHT, fill=tk.Y)
        self.output.configure(yscrollcommand=scroll_text.set)

    def _update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.lessons:
            return

        a = ScheduleAnalyzer(self.lessons)
        filtered = a.filter_by_week(self.week_type)

        if not filtered:
            return

        days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        by_day = {d: [] for d in days}

        for lesson in filtered:
            by_day[lesson.day].append(lesson)

        for day in days:
            by_day[day].sort(key=lambda x: x.start_time)

        for day in days:
            lessons_count = len(by_day[day])
            if lessons_count > 0:
                day_node = self.tree.insert("", "end", text=f"{day}", open=True)
                for lesson in by_day[day]:
                    time_str = f"{lesson.start_time}-{lesson.end_time}"
                    self.tree.insert(day_node, "end", text="", values=(time_str, lesson.subject))
            else:
                self.tree.insert("", "end", text=f"{day}", open=False)

    def _load_mtuci(self):
        group = self.group_entry.get().strip()
        if not group:
            messagebox.showerror("Ошибка", "Введите номер группы")
            return

        week_choice = simpledialog.askstring(
            "Выбор недели",
            "Какую неделю загрузить?\n\n1 - Обе недели\n2 - Чётная неделя\n3 - Нечётная неделя\n\nВведите 1, 2 или 3:",
            initialvalue="2"
        )

        week_map = {"1": "both", "2": "even", "3": "odd"}
        week_type = week_map.get(week_choice, "even")
        week_names = {"both": "обе", "even": "чётную", "odd": "нечётную"}

        try:
            parser = MTUCIParser()
            self.lessons = parser.parse(group, week_type=week_type)

            if not self.lessons:
                messagebox.showwarning("Предупреждение", f"Нет занятий для {week_names[week_type]} недели")
                return

            if week_type != "both":
                self.week_type = week_type

            self._update_tree()
            self._show_msg(f"Загружено из МТУСИ: {len(self.lessons)} занятий ({week_names[week_type]} неделя)")
            self._show_analytics()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить:\n{e}")

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл расписания",
            filetypes=[
                ("Excel/CSV файлы", "*.xlsx *.xls *.csv"),
                ("Excel файлы", "*.xlsx *.xls"),
                ("CSV файлы", "*.csv"),
                ("Все файлы", "*.*")
            ]
        )
        if not path:
            return
        try:
            parser = ExcelParser()
            self.lessons = parser.parse(path)

            week_choice = simpledialog.askstring(
                "Выбор недели",
                "Какую неделю загрузить?\n\n1 - Обе недели\n2 - Чётная неделя\n3 - Нечётная неделя\n\nВведите 1, 2 или 3:",
                initialvalue="2"
            )
            week_map = {"1": "both", "2": "even", "3": "odd"}
            week_type = week_map.get(week_choice, "both")

            for lesson in self.lessons:
                lesson.week_type = week_type
            self.week_type = week_type

            self._update_tree()
            self._show_msg(f"Загружено из файла: {len(self.lessons)} занятий")
            self._show_analytics()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _manual_input(self):
        dialog = ManualInputDialog(self.root)
        lessons = dialog.show()
        if lessons:
            week_choice = simpledialog.askstring(
                "Выбор недели",
                "Какую неделю загрузить?\n\n1 - Обе недели\n2 - Чётная неделя\n3 - Нечётная неделя\n\nВведите 1, 2 или 3:",
                initialvalue="2"
            )
            week_map = {"1": "both", "2": "even", "3": "odd"}
            week_type = week_map.get(week_choice, "both")

            for l in lessons:
                l.week_type = week_type
            self.lessons = lessons
            self.week_type = week_type
            self._update_tree()
            self._show_msg(f"Загружено из текста: {len(lessons)} занятий")
            self._show_analytics()

    def _setup_weeks(self):
        if not self.lessons:
            messagebox.showwarning("Предупреждение", "Сначала загрузите расписание")
            return

        def on_weeks_saved():
            self._update_tree()
            self._show_analytics()

        dialog = WeekSetupDialog(self.root, self.lessons, on_weeks_saved)
        dialog.show()

    def _export_csv(self):
        export_to_csv(self.lessons, self.root)

    def _show_templates(self):
        preview = TemplatePreview(self.root)
        preview.show()

    def _show_analytics(self):
        if not self.lessons:
            messagebox.showwarning("Ошибка", "Сначала загрузите расписание")
            return

        a = ScheduleAnalyzer(self.lessons)
        filtered = a.filter_by_week(self.week_type)

        if not filtered:
            self._show_msg(f"Нет занятий для недели: {self.week_names.get(self.week_type, 'Обе')}")
            return

        stats = a.get_statistics(filtered)
        windows = a.find_windows(filtered, self.free_time if self.free_time else None)
        free_intervals = a.find_free_intervals(filtered, self.free_time) if self.free_time else []

        out = f"\nНЕДЕЛЯ: {self.week_names.get(self.week_type, 'Обе')}\n"
        out += f"\nВСЕГО ЗАНЯТИЙ: {stats['total']}\n"
        out += "\nРАСПРЕДЕЛЕНИЕ ПО ДНЯМ:\n"
        for d, c in stats['day_counts'].items():
            bar = "#" * min(c, 10)
            out += f"  {d}: {c:2} {bar}\n"
        out += f"\nСАМЫЙ ЗАГРУЖЕННЫЙ ДЕНЬ: {stats['busiest_day']} ({stats['busiest_count']})\n"
        out += f"\nОКНА МЕЖДУ ПАРАМИ ({len(windows)} шт.):\n"
        for w in windows[:10]:
            out += f"  {w['day']}: {w['start']} - {w['end']} ({w['duration']} мин)\n"

        if free_intervals:
            out += "\nСВОБОДНЫЕ ИНТЕРВАЛЫ:\n"
            for fi in free_intervals:
                out += f"  {fi['day']}: {fi['start']} - {fi['end']} ({fi['reason']})\n"
        elif self.free_time:
            out += "\nНет полностью свободных интервалов в указанное время\n"

        self._show_msg(out)

    def _plot_graph(self):
        if not self.lessons:
            messagebox.showwarning("Ошибка", "Сначала загрузите расписание")
            return

        a = ScheduleAnalyzer(self.lessons)
        filtered = a.filter_by_week(self.week_type)

        if not filtered:
            messagebox.showwarning("Ошибка", "Нет данных для графика")
            return

        counts = a.count_by_day(filtered)
        days = list(counts.keys())
        values = list(counts.values())

        plt.figure(figsize=(10, 6))
        bars = plt.bar(days, values, color="skyblue", edgecolor="navy")
        plt.title(f"Нагрузка ({self.week_names.get(self.week_type, 'Обе')} неделя)", fontsize=14)
        plt.xlabel("День недели", fontsize=12)
        plt.ylabel("Количество занятий", fontsize=12)
        plt.grid(axis="y", alpha=0.3)

        for b, v in zip(bars, values):
            plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3, str(v), ha="center", fontweight="bold")

        plt.tight_layout()
        plt.show()

    def _set_week(self):
        win = tk.Toplevel(self.root)
        win.title("Текущая неделя")
        win.geometry("350x250")
        win.resizable(False, False)
        win.grab_set()
        win.transient(self.root)

        tk.Label(win, text="Какая сейчас неделя?", font=("Arial", 12, "bold")).pack(pady=20)

        frame = tk.Frame(win, bg="#f0f0f0", relief=tk.GROOVE, bd=2)
        frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)

        def set_week(week_type, week_name):
            self.week_type = week_type
            win.destroy()
            self._update_tree()
            self._show_msg(f"Текущая неделя: {week_name}")
            self._show_analytics()

        tk.Button(frame, text="Обе недели", command=lambda: set_week("both", "Обе"),
                  bg="#4CAF50", fg="white", width=20).pack(pady=8, fill=tk.X)
        tk.Button(frame, text="Чётная неделя", command=lambda: set_week("even", "Чётная"),
                  bg="#2196F3", fg="white", width=20).pack(pady=8, fill=tk.X)
        tk.Button(frame, text="Нечётная неделя", command=lambda: set_week("odd", "Нечётная"),
                  bg="#FF9800", fg="white", width=20).pack(pady=8, fill=tk.X)

        tk.Button(win, text="Отмена", command=win.destroy, bg="#9E9E9E", fg="white", width=15).pack(pady=15)

    def _set_free_time(self):
        dialog = FreeTimeDialog(self.root, self.free_time)
        ft = dialog.show()
        if ft is not None:
            self.free_time = ft
            self._show_msg(f"Сохранено свободное время для {len(ft)} дней")
            self._show_analytics()

    def _show_msg(self, msg):
        self.output.delete(1.0, tk.END)
        self.output.insert(1.0, msg)

    def _show_about(self):
        messagebox.showinfo("О программе",
                            "Анализатор учебного расписания\n\n"
                            "Возможности:\n"
                            "- Загрузка из МТУСИ\n"
                            "- Загрузка Excel/CSV\n"
                            "- Ручной ввод с Shift+Enter\n"
                            "- Настройка чётных/нечётных недель для каждого занятия\n"
                            "- Экспорт в CSV\n"
                            "- Поиск окон между парами\n"
                            "- Учёт свободного времени\n"
                            "- Визуализация нагрузки")

    def _on_close(self):
        self.root.destroy()