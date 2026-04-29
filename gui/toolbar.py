import tkinter as tk

def _create_tooltip_button(parent, text, command, tooltip_text, color):
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg="white", font=("Arial", 9, "bold"),
                    width=12, relief=tk.RAISED, bd=2)

    def show_tooltip(event):
        tooltip = tk.Toplevel(btn)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        label = tk.Label(tooltip, text=tooltip_text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 9))
        label.pack()

        def hide_tooltip():
            tooltip.destroy()

        btn.tooltip = tooltip
        btn.bind("<Leave>", lambda e: hide_tooltip())

    btn.bind("<Enter>", show_tooltip)
    return btn

def create_toolbar(parent, callbacks):
    top = tk.Frame(parent, bg="#f0f0f0", relief=tk.RAISED, bd=1)
    top.pack(fill=tk.X, padx=5, pady=5)

    group_frame = tk.Frame(top, bg="#f0f0f0")
    group_frame.pack(pady=10)
    tk.Label(group_frame, text="Группа (МТУСИ):", bg="#f0f0f0",
             font=("Arial", 10)).pack(side=tk.LEFT)
    group_entry = tk.Entry(group_frame, width=20, font=("Arial", 10))
    group_entry.pack(side=tk.LEFT, padx=10)
    group_entry.bind("<Return>", lambda e: callbacks['load_mtuci']())

    load_frame = tk.Frame(top, bg="#f0f0f0")
    load_frame.pack(pady=10)

    _create_tooltip_button(load_frame, "МТУСИ", callbacks['load_mtuci'],
                           "Загрузить расписание с сайта МТУСИ\nТребуется номер группы",
                           "#2196F3").pack(side=tk.LEFT, padx=5)

    _create_tooltip_button(load_frame, "Excel/CSV", callbacks['load_file'],
                           "Загрузить расписание из файла\nПоддерживаются: .xlsx, .xls, .csv",
                           "#4CAF50").pack(side=tk.LEFT, padx=5)

    _create_tooltip_button(load_frame, "Ручной ввод", callbacks['manual_input'],
                           "Ввести расписание вручную\nФормат: ДЕНЬ ЧЧ:ММ-ЧЧ:ММ ПРЕДМЕТ",
                           "#FF9800").pack(side=tk.LEFT, padx=5)

    _create_tooltip_button(load_frame, "Недели", callbacks['setup_weeks'],
                           "Настроить чётность для каждого занятия",
                           "#9C27B0").pack(side=tk.LEFT, padx=5)

    _create_tooltip_button(load_frame, "Шаблоны", callbacks['show_templates'],
                           "Показать шаблоны для ввода данных",
                           "#9C27B0").pack(side=tk.LEFT, padx=5)

    _create_tooltip_button(load_frame, "Экспорт CSV", callbacks['export_csv'],
                           "Сохранить расписание в CSV файл\nМожно редактировать в Excel",
                           "#E91E63").pack(side=tk.LEFT, padx=5)

    tool_frame = tk.Frame(top)
    tool_frame.pack(pady=10)

    tk.Button(tool_frame, text="Аналитика", command=callbacks['show_analytics'],
              width=12).pack(side=tk.LEFT, padx=3)
    tk.Button(tool_frame, text="Текущая неделя", command=callbacks['set_week'],
              width=12).pack(side=tk.LEFT, padx=3)
    tk.Button(tool_frame, text="Свободное время", command=callbacks['set_free_time'],
              width=14).pack(side=tk.LEFT, padx=3)
    tk.Button(tool_frame, text="График", command=callbacks['plot_graph'],
              width=10).pack(side=tk.LEFT, padx=3)

    return group_entry