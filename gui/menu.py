import tkinter as tk

def setup_menu(root, callbacks):
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Файл", menu=file_menu)
    file_menu.add_command(label="Загрузить из МТУСИ", command=callbacks['load_mtuci'])
    file_menu.add_command(label="Загрузить Excel/CSV", command=callbacks['load_file'])
    file_menu.add_command(label="Ручной ввод", command=callbacks['manual_input'])
    file_menu.add_separator()
    file_menu.add_command(label="Экспорт в CSV", command=callbacks['export_csv'])
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=callbacks['on_close'])

    analiz_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Анализ", menu=analiz_menu)
    analiz_menu.add_command(label="Аналитика", command=callbacks['show_analytics'])
    analiz_menu.add_command(label="График", command=callbacks['plot_graph'])
    analiz_menu.add_separator()
    analiz_menu.add_command(label="Настроить недели", command=callbacks['setup_weeks'])
    analiz_menu.add_command(label="Текущая неделя", command=callbacks['set_week'])
    analiz_menu.add_command(label="Свободное время", command=callbacks['set_free_time'])

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Помощь", menu=help_menu)
    help_menu.add_command(label="Шаблоны ввода", command=callbacks['show_templates'])
    help_menu.add_command(label="О программе", command=callbacks['show_about'])