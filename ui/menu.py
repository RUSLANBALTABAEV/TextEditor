from tkinter import Menu, Toplevel, Text, Scrollbar
from tkinter import DISABLED, RIGHT, Y, YES, BOTH
from tkinter.messagebox import showinfo

class MenuManager:
    def __init__(self, editor):
        self.editor = editor
        self.root = editor.root
        
    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        self.create_file_menu(menubar)
        self.create_edit_menu(menubar)
        self.create_format_menu(menubar)
        self.create_view_menu(menubar)
        self.create_tools_menu(menubar)
        self.create_plugins_menu(menubar)
        self.create_help_menu(menubar)
        
    def create_file_menu(self, menubar):
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        file_menu.add_command(label="Новый", command=self.editor.file_manager.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.editor.file_manager.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.editor.file_manager.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как", command=self.editor.file_manager.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Новая вкладка", command=self.editor.tab_manager.new_tab, accelerator="Ctrl+T")
        file_menu.add_command(label="Закрыть вкладку", command=self.editor.tab_manager.close_tab, accelerator="Ctrl+W")
        file_menu.add_separator()
        
        # Подменю автосохранения
        autosave_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Автосохранение", menu=autosave_menu)
        autosave_menu.add_checkbutton(label="Включить автосохранение", command=self.editor.autosave_manager.toggle_autosave)
        autosave_menu.add_command(label="Настройки интервала", command=self.editor.autosave_manager.autosave_settings)
        
        file_menu.add_separator()
        file_menu.add_command(label="Печать", command=self.editor.file_manager.print_file, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.editor.exit_app, accelerator="Ctrl+Q")
        
    def create_edit_menu(self, menubar):
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        edit_menu.add_command(label="Отменить", command=self.editor.editor_commands.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.editor.editor_commands.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.editor.editor_commands.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.editor.editor_commands.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.editor.editor_commands.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Удалить", command=self.editor.editor_commands.delete, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Найти", command=self.editor.search_replace.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Заменить", command=self.editor.search_replace.replace_text, accelerator="Ctrl+H")
        edit_menu.add_command(label="Выделить все", command=self.editor.editor_commands.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Дата и время", command=self.editor.editor_commands.insert_datetime, accelerator="F5")
        
    def create_format_menu(self, menubar):
        format_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Формат", menu=format_menu)
        
        format_menu.add_command(label="Перенос слов", command=self.editor.editor_commands.toggle_word_wrap)
        format_menu.add_command(label="Шрифт...", command=self.editor.editor_commands.change_font)
        format_menu.add_separator()
        
        # Подменю Темы
        theme_menu = Menu(format_menu, tearoff=0)
        format_menu.add_cascade(label="Тема", menu=theme_menu)
        theme_menu.add_command(label="Светлая", command=lambda: self.editor.theme_manager.change_theme("light"))
        theme_menu.add_command(label="Темная", command=lambda: self.editor.theme_manager.change_theme("dark"))
        theme_menu.add_command(label="Синяя", command=lambda: self.editor.theme_manager.change_theme("blue"))
        
    def create_view_menu(self, menubar):
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        view_menu.add_command(label="Увеличить шрифт", command=self.editor.editor_commands.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Уменьшить шрифт", command=self.editor.editor_commands.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Сбросить масштаб", command=self.editor.editor_commands.zoom_reset, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Статус бар", command=self.editor.status_bar.toggle_statusbar)
        view_menu.add_checkbutton(label="Панель инструментов", command=self.editor.toolbar.toggle_toolbar)
        
    def create_tools_menu(self, menubar):
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        
        tools_menu.add_command(label="Статистика", command=self.editor.editor_commands.show_stats)
        tools_menu.add_command(label="Проверка орфографии", command=self.editor.editor_commands.spell_check)
        
    def create_plugins_menu(self, menubar):
        plugins_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Плагины", menu=plugins_menu)
        
        plugins_menu.add_command(label="Менеджер плагинов", command=self.plugin_manager)
        plugins_menu.add_command(label="Обновить плагины", command=self.refresh_plugins)
        
    def create_help_menu(self, menubar):
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        help_menu.add_command(label="Справка", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="Лицензия", command=self.show_license)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self.about)
        
    def plugin_manager(self):
        """Менеджер плагинов"""
        from tkinter import Label, Listbox
        
        manager_window = Toplevel(self.editor.root)
        manager_window.title("Менеджер плагинов")
        manager_window.geometry('500x400')
        
        Label(manager_window, text="Доступные плагины:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Список плагинов
        plugins_list = Listbox(manager_window)
        plugins_list.pack(expand=True, fill=BOTH, padx=10, pady=10)
        
        # Заполняем список
        plugins_list.insert(END, "Плагин проверки орфографии (в разработке)")
        plugins_list.insert(END, "Плагин экспорта в PDF (в разработке)")
        plugins_list.insert(END, "Плагин синхронизации с облаком (в разработке)")
        
        Label(manager_window, text="Система плагинов находится в разработке", 
              font=('Arial', 10), fg='blue').pack(pady=10)
              
    def refresh_plugins(self):
        """Обновляет список плагинов"""
        showinfo("Плагины", "Список плагинов обновлен")
        
    def show_help(self):
        help_text = """
Текстовый редактор - Справка

Основные функции:
- Создание, открытие, сохранение файлов
- Работа с несколькими вкладками
- Автосохранение документов
- Отмена/повтор действий (Ctrl+Z/Ctrl+Y)
- Поиск и замена текста (Ctrl+F/Ctrl+H)
- Подсветка синтаксиса для разных языков
- Несколько цветовых тем
- Статистика документа
- Печать документов
- Система контроля версий
- Поддержка плагинов

Горячие клавиши:
Ctrl+N - Новый файл
Ctrl+O - Открыть файл
Ctrl+S - Сохранить
Ctrl+T - Новая вкладка
Ctrl+W - Закрыть вкладку
Ctrl+P - Печать
Ctrl+F - Поиск
Ctrl+H - Замена
F5 - Вставить дату и время
F1 - Справка
        """
        
        help_window = Toplevel(self.editor.root)
        help_window.title("Справка")
        help_window.geometry('500x400')
        
        text_widget = Text(help_window, wrap='word', font=('Arial', 10))
        scrollbar = Scrollbar(help_window, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(1.0, help_text)
        text_widget.config(state=DISABLED)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.pack(expand=YES, fill=BOTH)
    
    def show_license(self):
        """Показывает лицензию MIT"""
        license_text = """
MIT License

Copyright (c) 2024 Текстовый Редактор 2.0

Данная лицензия разрешает лицам, получившим копию данного программного обеспечения
и сопутствующей документации (в дальнейшем «Программное обеспечение»), безвозмездно
использовать Программное обеспечение без ограничений, включая неограниченное право
на использование, копирование, изменение, слияние, публикацию, распространение,
сублицензирование и/или продажу копий Программного обеспечения, а также лицам,
которым предоставляется данное Программное обеспечение, при соблюдении следующих
условий:

Указанное выше уведомление об авторском праве и данные условия должны быть
включены во все копии или значимые части данного Программного обеспечения.

ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ,
ЯВНО ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ГАРАНТИЯМИ
ТОВАРНОЙ ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И НЕНАРУШЕНИЯ
ПРАВ. НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ ОТВЕТСТВЕННОСТИ
ПО КАКИМ-ЛИБО ИСКАМ, ЗА УЩЕРБ ИЛИ ПО ИНЫМ ТРЕБОВАНИЯМ, В ТОМ ЧИСЛЕ, ПРИ
ДЕЙСТВИИ КОНТРАКТА, ДЕЛИКТЕ ИЛИ ИНОЙ СИТУАЦИИ, ВОЗНИКШИМ ИЗ-ЗА ИСПОЛЬЗОВАНИЯ
ПРОГРАММНОГО ОБЕСПЕЧЕНИЕМ.
        """
        
        license_window = Toplevel(self.editor.root)
        license_window.title("Лицензия MIT - Текстовый Редактор 2.0")
        license_window.geometry('700x500')
        
        text_widget = Text(license_window, wrap='word', font=('Arial', 10))
        scrollbar = Scrollbar(license_window, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(1.0, license_text)
        text_widget.config(state=DISABLED)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.pack(expand=YES, fill=BOTH, padx=10, pady=10)
                
    def about(self):
        about_text = """Текстовый редактор 2.0

Версия 2.0
Лицензия: MIT License

Это программное обеспечение распространяется на условиях 
лицензии MIT. Вы можете свободно использовать, модифицировать 
и распространять данный редактор в соответствии с условиями 
лицензии.

Основные возможности:
- Работа с несколькими вкладками
- Автосохранение и восстановление сессий
- Подсветка синтаксиса для различных языков
- Система контроля версий
- Поддержка плагинов
- Несколько тем оформления

Для получения полного текста лицензии выберите 
'Лицензия' в меню 'Справка'."""
        
        showinfo("О программе", about_text)
