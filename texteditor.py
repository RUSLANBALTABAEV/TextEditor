from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter import simpledialog
import os
import sys
import re
from datetime import datetime
import json
import time
import tempfile
import shutil
from pathlib import Path

class TextEditor:
    def __init__(self):
        self.root = Tk()
        self.current_file = None
        self.auto_save = False
        self.auto_save_interval = 300000  # 5 минут
        self.theme = "light"
        self.session_file = "session.json"
        self.backup_dir = "backups"
        self.plugins_dir = "plugins"
        self.tabs = {}
        self.current_tab_id = None
        self.tab_counter = 1
        
        # Создаем необходимые директории
        self.setup_directories()
        
        self.setup_icon()
        self.setup_ui()
        self.setup_bindings()
        self.load_session()
        
    def setup_directories(self):
        """Создает необходимые директории для работы приложения"""
        for directory in [self.backup_dir, self.plugins_dir]:
            os.makedirs(directory, exist_ok=True)
        
    def setup_icon(self):
        datafile = "TextEditor.ico"
        if not hasattr(sys, "frozen"):
            datafile = os.path.join(os.path.dirname(__file__), datafile)
        else:
            datafile = os.path.join(sys.prefix, datafile)
        if os.path.exists(datafile):
            self.root.iconbitmap(default=datafile)

    def setup_ui(self):
        self.root.title("Текстовый Редактор 2.0 - Новый файл")
        self.root.geometry('1200x700')
        
        # Главное меню
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Новая вкладка", command=self.new_tab, accelerator="Ctrl+T")
        file_menu.add_command(label="Закрыть вкладку", command=self.close_tab, accelerator="Ctrl+W")
        file_menu.add_separator()
        
        # Подменю автосохранения
        autosave_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Автосохранение", menu=autosave_menu)
        autosave_menu.add_checkbutton(label="Включить автосохранение", command=self.toggle_autosave)
        autosave_menu.add_command(label="Настройки интервала", command=self.autosave_settings)
        
        file_menu.add_separator()
        file_menu.add_command(label="Печать", command=self.print_file, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_app, accelerator="Ctrl+Q")
        
        # Меню Правка
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Удалить", command=self.delete, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Найти", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Заменить", command=self.replace_text, accelerator="Ctrl+H")
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Дата и время", command=self.insert_datetime, accelerator="F5")
        
        # Меню Формат
        format_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Формат", menu=format_menu)
        format_menu.add_command(label="Перенос слов", command=self.toggle_word_wrap)
        format_menu.add_command(label="Шрифт...", command=self.change_font)
        format_menu.add_separator()
        
        # Подменю Темы
        theme_menu = Menu(format_menu, tearoff=0)
        format_menu.add_cascade(label="Тема", menu=theme_menu)
        theme_menu.add_command(label="Светлая", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Темная", command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label="Синяя", command=lambda: self.change_theme("blue"))
        
        # Меню Вид
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Увеличить шрифт", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Уменьшить шрифт", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Сбросить масштаб", command=self.zoom_reset, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Статус бар", command=self.toggle_statusbar)
        view_menu.add_checkbutton(label="Панель инструментов", command=self.toggle_toolbar)
        
        # Меню Инструменты
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Статистика", command=self.show_stats)
        tools_menu.add_command(label="Проверка орфографии", command=self.spell_check)
        tools_menu.add_separator()
        tools_menu.add_command(label="История версий", command=self.show_version_history)
        tools_menu.add_command(label="Восстановить версию", command=self.restore_version)
        
        # Меню Плагины
        plugins_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Плагины", menu=plugins_menu)
        plugins_menu.add_command(label="Менеджер плагинов", command=self.plugin_manager)
        plugins_menu.add_command(label="Обновить плагины", command=self.refresh_plugins)
        
        # Меню Справка
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Справка", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="Лицензия", command=self.show_license)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self.about)
        
        # Панель инструментов
        self.toolbar = Frame(self.root, bd=1, relief=RAISED)
        self.toolbar.pack(side=TOP, fill=X)
        
        # Кнопки панели инструментов
        buttons = [
            ("Новый", self.new_file, "Создать новый файл"),
            ("Открыть", self.open_file, "Открыть файл"),
            ("Сохранить", self.save_file, "Сохранить файл"),
            ("+Вкладка", self.new_tab, "Новая вкладка"),
            ("Печать", self.print_file, "Печать документа"),
            ("Найти", self.find_text, "Найти текст"),
            ("Вырезать", self.cut, "Вырезать выделенный текст"),
            ("Копировать", self.copy, "Копировать выделенный текст"),
            ("Вставить", self.paste, "Вставить текст из буфера"),
        ]
        
        for text, command, tooltip in buttons:
            btn = Button(self.toolbar, text=text, command=command, relief=RAISED, bd=1)
            btn.pack(side=LEFT, padx=2, pady=2)
            self.create_tooltip(btn, tooltip)
        
        # Панель вкладок
        self.tab_frame = Frame(self.root)
        self.tab_frame.pack(side=TOP, fill=X)
        
        self.tab_control = ttk.Notebook(self.tab_frame)
        self.tab_control.pack(expand=1, fill=BOTH)
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Область поиска
        self.search_frame = Frame(self.root)
        self.search_visible = False
        
        Label(self.search_frame, text="Найти:").pack(side=LEFT)
        self.find_entry = Entry(self.search_frame, width=30)
        self.find_entry.pack(side=LEFT, padx=5)
        
        Button(self.search_frame, text="Найти", command=self.find_next).pack(side=LEFT, padx=2)
        Button(self.search_frame, text="Заменить на:", command=self.show_replace).pack(side=LEFT, padx=2)
        Button(self.search_frame, text="✕", command=self.hide_search).pack(side=LEFT, padx=5)
        
        # Область замены
        self.replace_frame = Frame(self.root)
        self.replace_visible = False
        
        Label(self.replace_frame, text="Заменить на:").pack(side=LEFT)
        self.replace_entry = Entry(self.replace_frame, width=30)
        self.replace_entry.pack(side=LEFT, padx=5)
        
        Button(self.replace_frame, text="Заменить", command=self.replace_next).pack(side=LEFT, padx=2)
        Button(self.replace_frame, text="Заменить все", command=self.replace_all).pack(side=LEFT, padx=2)
        Button(self.replace_frame, text="✕", command=self.hide_replace).pack(side=LEFT, padx=5)
        
        # Статус бар
        self.status_bar = Label(self.root, text="Готово | Строк: 1 | Слов: 0 | Символов: 0", relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        # Создаем первую вкладку ПОСЛЕ создания статус бара
        self.new_tab()
        
        self.apply_theme()
        
        # Загружаем плагины
        self.load_plugins()
        
    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = Label(tooltip, text=text, background="lightyellow", relief='solid', borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def setup_bindings(self):
        # Горячие клавиши
        bindings = [
            ('<Control-n>', self.new_file),
            ('<Control-o>', self.open_file),
            ('<Control-s>', self.save_file),
            ('<Control-Shift-S>', self.save_as_file),
            ('<Control-t>', self.new_tab),
            ('<Control-w>', self.close_tab),
            ('<Control-q>', self.exit_app),
            ('<Control-a>', self.select_all),
            ('<Control-z>', self.undo),
            ('<Control-y>', self.redo),
            ('<Control-x>', self.cut),
            ('<Control-c>', self.copy),
            ('<Control-v>', self.paste),
            ('<Control-f>', self.find_text),
            ('<Control-h>', self.replace_text),
            ('<F1>', self.show_help),
            ('<F5>', self.insert_datetime),
            ('<Control-plus>', self.zoom_in),
            ('<Control-minus>', self.zoom_out),
            ('<Control-0>', self.zoom_reset),
        ]
        
        for key, command in bindings:
            self.root.bind(key, lambda e, cmd=command: cmd())
            
    def get_current_tab_info(self):
        """Возвращает информацию о текущей вкладке"""
        if not self.tabs or not self.current_tab_id:
            return None
        return self.tabs.get(self.current_tab_id)
        
    def get_current_text_area(self):
        """Возвращает текстовую область текущей вкладки"""
        tab_info = self.get_current_tab_info()
        return tab_info['text_area'] if tab_info else None
        
    def new_tab(self, file_path=None, content=None):
        """Создает новую вкладку"""
        frame = Frame(self.tab_control)
        
        # Текстовая область для вкладки
        text_area = Text(frame, wrap='word', undo=True, font=('Arial', 11), selectbackground='lightblue')
        scrollbar = Scrollbar(frame, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        text_area.pack(expand=YES, fill=BOTH)
        
        # Привязываем события
        text_area.bind('<KeyRelease>', lambda e: self.on_text_change())
        text_area.bind('<Button-1>', lambda e: self.update_status())
        
        # Добавляем вкладку
        tab_id = f"tab_{self.tab_counter}"
        self.tab_counter += 1
        
        if file_path:
            tab_name = os.path.basename(file_path)
        else:
            tab_name = f"Новый {len(self.tabs) + 1}"
            
        self.tab_control.add(frame, text=tab_name)
        
        # Сохраняем информацию о вкладке
        self.tabs[tab_id] = {
            'frame': frame,
            'text_area': text_area,
            'scrollbar': scrollbar,
            'file_path': file_path,
            'modified': False,
            'name': tab_name,
            'tab_id': tab_id
        }
        
        # Вставляем содержимое если предоставлено
        if content:
            text_area.insert(1.0, content)
        
        # Переключаемся на новую вкладку
        self.tab_control.select(frame)
        self.current_tab_id = tab_id
        
        self.update_status()
        return tab_id

    def on_text_change(self):
        """Обработчик изменения текста"""
        current_tab_info = self.get_current_tab_info()
        if current_tab_info:
            current_tab_info['modified'] = True
        self.update_status()
        
    def close_tab(self):
        """Закрывает текущую вкладку"""
        if len(self.tabs) <= 1:
            return
            
        current_tab_info = self.get_current_tab_info()
        if not current_tab_info:
            return
            
        # Проверяем сохранить
        if current_tab_info['modified']:
            content = current_tab_info['text_area'].get(1.0, END)
            if len(content.strip()) > 0 and content != '\n':
                answer = askyesnocancel("Сохранение", f"Сохранить изменения в {current_tab_info['name']}?")
                if answer is None:  # Cancel
                    return
                elif answer:  # Yes
                    self.save_file()
        
        # Удаляем вкладку
        self.tab_control.forget(current_tab_info['frame'])
        del self.tabs[self.current_tab_id]
        
        # Выбираем другую вкладку
        if self.tabs:
            self.current_tab_id = next(iter(self.tabs.keys()))
            self.tab_control.select(self.tabs[self.current_tab_id]['frame'])
        else:
            self.current_tab_id = None
            
    def on_tab_changed(self, event):
        """Обработчик смены вкладки"""
        # Находим ID текущей вкладки
        current_frame = self.tab_control.select()
        if current_frame:
            for tab_id, tab_info in self.tabs.items():
                if str(tab_info['frame']) == str(current_frame):
                    self.current_tab_id = tab_id
                    break
        self.update_status()
        
    def new_file(self):
        current_tab_info = self.get_current_tab_info()
        if current_tab_info:
            # Проверяем текущую вкладку перед очисткой
            if current_tab_info['modified']:
                content = current_tab_info['text_area'].get(1.0, END)
                if len(content.strip()) > 0 and content != '\n':
                    answer = askyesnocancel("Сохранение", "Сохранить изменения в текущем файле?")
                    if answer is None:  # Cancel
                        return
                    elif answer:  # Yes
                        self.save_file()
            
            current_tab_info['text_area'].delete(1.0, END)
            current_tab_info['file_path'] = None
            current_tab_info['modified'] = False
            current_tab_info['name'] = "Новый файл"
            self.tab_control.tab(current_tab_info['frame'], text="Новый файл")
            self.root.title("Текстовый Редактор 2.0 - Новый файл")
            self.update_status()
            
    def open_file(self, file_path=None):
        if not file_path:
            file_path = askopenfilename(
                filetypes=[
                    ("Текстовые файлы", "*.txt"),
                    ("Документы Python", "*.py"),
                    ("HTML файлы", "*.html;*.htm"),
                    ("CSS файлы", "*.css"),
                    ("JavaScript файлы", "*.js"),
                    ("Все файлы", "*.*")
                ]
            )
        if file_path:
            try:
                # Попробуем определить кодировку
                encodings = ['utf-8', 'cp1251', 'iso-8859-1', 'windows-1252']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            content = file.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # Если не удалось декодировать, читаем как бинарный и пробуем latin-1
                    with open(file_path, 'rb') as file:
                        content = file.read().decode('latin-1')
                
                # Создаем новую вкладку для файла
                self.new_tab(file_path, content)
                
                # Подсветка синтаксиса для известных типов файлов
                self.apply_syntax_highlighting(file_path)
                
                # Создаем резервную копию
                self.create_backup(file_path, content)
                
            except Exception as e:
                showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
                    
    def apply_syntax_highlighting(self, file_path):
        # Базовая подсветка ключевых слов
        extension = os.path.splitext(file_path)[1].lower()
        text_area = self.get_current_text_area()
        
        if not text_area:
            return
            
        # Очищаем предыдущие теги
        for tag in text_area.tag_names():
            if tag not in ('sel',):
                text_area.tag_delete(tag)
        
        if extension == '.py':
            python_keywords = ['def', 'class', 'import', 'from', 'as', 'if', 'else', 
                              'elif', 'for', 'while', 'return', 'try', 'except', 'finally']
            self.highlight_keywords(python_keywords, 'blue')
            
        elif extension in ('.html', '.htm'):
            html_tags = ['html', 'head', 'body', 'div', 'span', 'p', 'h1', 'h2', 'h3', 
                        'a', 'img', 'table', 'tr', 'td', 'ul', 'ol', 'li']
            self.highlight_keywords(html_tags, 'purple')
            
    def highlight_keywords(self, keywords, color):
        text_area = self.get_current_text_area()
        if not text_area:
            return
            
        content = text_area.get(1.0, END)
        for keyword in keywords:
            start = 1.0
            while True:
                start = text_area.search(r'\b' + keyword + r'\b', start, stopindex=END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                text_area.tag_add(keyword, start, end)
                text_area.tag_config(keyword, foreground=color)
                start = end
                
    def save_file(self):
        current_tab_info = self.get_current_tab_info()
        if not current_tab_info:
            return
            
        file_path = current_tab_info['file_path']
        
        if file_path:
            try:
                content = current_tab_info['text_area'].get(1.0, END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                current_tab_info['modified'] = False
                self.status_bar.config(text="Файл сохранен")
                
                # Создаем версионную копию
                self.create_version(file_path, content)
                
            except Exception as e:
                showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
        else:
            self.save_as_file()
                
    def save_as_file(self):
        current_tab_info = self.get_current_tab_info()
        if not current_tab_info:
            return
            
        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Документы Python", "*.py"),
                ("HTML файлы", "*.html"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            try:
                content = current_tab_info['text_area'].get(1.0, END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                current_tab_info['file_path'] = file_path
                current_tab_info['modified'] = False
                current_tab_info['name'] = os.path.basename(file_path)
                self.tab_control.tab(current_tab_info['frame'], text=current_tab_info['name'])
                self.root.title(f"Текстовый Редактор 2.0 - {current_tab_info['name']}")
                self.status_bar.config(text="Файл сохранен")
                
                # Создаем версионную копию
                self.create_version(file_path, content)
                
            except Exception as e:
                showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
                
    def check_save(self):
        """Проверяет необходимость сохранения во всех вкладках"""
        for tab_info in self.tabs.values():
            content = tab_info['text_area'].get(1.0, END)
            if len(content.strip()) > 0 and content != '\n' and tab_info['modified']:
                answer = askyesnocancel("Сохранение", f"Сохранить изменения в {tab_info['name']}?")
                if answer is None:  # Cancel
                    return False
                elif answer:  # Yes
                    # Сохраняем конкретную вкладку
                    current_tab = self.current_tab_id
                    self.current_tab_id = tab_info['tab_id']
                    self.save_file()
                    self.current_tab_id = current_tab
        return True
        
    def exit_app(self):
        if self.check_save():
            self.save_session()
            self.root.destroy()
            
    def undo(self):
        text_area = self.get_current_text_area()
        if text_area:
            try:
                text_area.event_generate("<<Undo>>")
            except TclError:
                pass
            
    def redo(self):
        text_area = self.get_current_text_area()
        if text_area:
            try:
                text_area.event_generate("<<Redo>>")
            except TclError:
                pass
            
    def cut(self):
        text_area = self.get_current_text_area()
        if text_area:
            text_area.event_generate("<<Cut>>")
        
    def copy(self):
        text_area = self.get_current_text_area()
        if text_area:
            text_area.event_generate("<<Copy>>")
        
    def paste(self):
        text_area = self.get_current_text_area()
        if text_area:
            text_area.event_generate("<<Paste>>")
        
    def delete(self):
        text_area = self.get_current_text_area()
        if text_area:
            try:
                text_area.delete(SEL_FIRST, SEL_LAST)
            except TclError:
                pass
        
    def select_all(self):
        text_area = self.get_current_text_area()
        if text_area:
            text_area.tag_add(SEL, "1.0", END)
            text_area.mark_set(INSERT, "1.0")
            text_area.see(INSERT)
        
    def find_text(self):
        if not self.search_visible:
            self.search_frame.pack(side=TOP, fill=X, padx=5, pady=5)
            self.search_visible = True
            self.find_entry.focus()
        
    def hide_search(self):
        self.search_frame.pack_forget()
        self.search_visible = False
        
    def show_replace(self):
        if not self.replace_visible:
            self.replace_frame.pack(side=TOP, fill=X, padx=5, pady=5)
            self.replace_visible = True
            self.replace_entry.focus()
            
    def hide_replace(self):
        self.replace_frame.pack_forget()
        self.replace_visible = False
        
    def find_next(self):
        search_term = self.find_entry.get()
        text_area = self.get_current_text_area()
        
        if search_term and text_area:
            # Снимаем предыдущее выделение
            text_area.tag_remove('found', '1.0', END)
            
            start_pos = text_area.index(INSERT)
            idx = text_area.search(search_term, start_pos, stopindex=END)
            
            if not idx:
                # Если не нашли от текущей позиции, ищем с начала
                idx = text_area.search(search_term, '1.0', stopindex=END)
                
            if idx:
                end_idx = f"{idx}+{len(search_term)}c"
                text_area.tag_add('found', idx, end_idx)
                text_area.tag_config('found', background='yellow')
                text_area.mark_set(INSERT, idx)
                text_area.see(idx)
            else:
                showinfo("Поиск", "Текст не найден")
                
    def replace_text(self):
        self.find_text()
        self.show_replace()
        
    def replace_next(self):
        search_term = self.find_entry.get()
        replace_term = self.replace_entry.get()
        text_area = self.get_current_text_area()
        
        if search_term and text_area and text_area.tag_ranges('found'):
            current = text_area.tag_ranges('found')[0]
            text_area.delete(current, f"{current}+{len(search_term)}c")
            text_area.insert(current, replace_term)
            self.find_next()
            
    def replace_all(self):
        search_term = self.find_entry.get()
        replace_term = self.replace_entry.get()
        text_area = self.get_current_text_area()
        
        if search_term and text_area:
            content = text_area.get(1.0, END)
            new_content = content.replace(search_term, replace_term)
            text_area.delete(1.0, END)
            text_area.insert(1.0, new_content)
            showinfo("Замена", "Все вхождения заменены")
        
    def insert_datetime(self):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        text_area = self.get_current_text_area()
        if text_area:
            text_area.insert(INSERT, dt_string)
        
    def toggle_word_wrap(self):
        text_area = self.get_current_text_area()
        if text_area:
            current_wrap = text_area.cget('wrap')
            new_wrap = 'none' if current_wrap == 'word' else 'word'
            text_area.config(wrap=new_wrap)
        
    def change_font(self):
        font_window = Toplevel(self.root)
        font_window.title("Выбор шрифта")
        font_window.geometry('300x300')
        font_window.transient(self.root)
        font_window.grab_set()
        
        # Выбор семейства шрифтов
        Label(font_window, text="Шрифт:").pack(pady=5)
        font_family = StringVar(value="Arial")
        font_list = Listbox(font_window, listvariable=font_family, height=6)
        fonts = ["Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", "Consolas"]
        for font in fonts:
            font_list.insert(END, font)
        font_list.pack(pady=5)
        
        # Размер шрифта
        Label(font_window, text="Размер:").pack(pady=5)
        font_size = Spinbox(font_window, from_=8, to=72, width=10)
        font_size.delete(0, END)
        
        text_area = self.get_current_text_area()
        if text_area:
            current_font = text_area.cget('font')
            if len(current_font.split()) > 1:
                current_size = current_font.split()[1]
                font_size.insert(0, current_size)
        
        font_size.pack(pady=5)
        
        def apply_font():
            try:
                family = font_list.get(font_list.curselection())
                size = int(font_size.get())
                
                # Применяем ко всем текстовым областям
                for tab_info in self.tabs.values():
                    tab_info['text_area'].config(font=(family, size))
                    
                font_window.destroy()
            except (ValueError, TclError):
                showerror("Ошибка", "Некорректные параметры шрифта")
                
        Button(font_window, text="Применить", command=apply_font).pack(pady=10)
        
    def change_theme(self, theme_name):
        self.theme = theme_name
        self.apply_theme()
        
    def apply_theme(self):
        if self.theme == "light":
            bg_color = "white"
            fg_color = "black"
            cursor_color = "black"
        elif self.theme == "dark":
            bg_color = "#2b2b2b"
            fg_color = "white"
            cursor_color = "white"
        elif self.theme == "blue":
            bg_color = "#e6f3ff"
            fg_color = "black"
            cursor_color = "black"
            
        # Применяем тему ко всем текстовым областям
        for tab_info in self.tabs.values():
            tab_info['text_area'].config(bg=bg_color, fg=fg_color, insertbackground=cursor_color)
            
        self.root.config(bg=bg_color)
        
    def zoom_in(self):
        for tab_info in self.tabs.values():
            current_font = tab_info['text_area'].cget('font')
            family, size = current_font.split()
            new_size = int(size) + 1
            tab_info['text_area'].config(font=(family, new_size))
        
    def zoom_out(self):
        for tab_info in self.tabs.values():
            current_font = tab_info['text_area'].cget('font')
            family, size = current_font.split()
            new_size = max(8, int(size) - 1)
            tab_info['text_area'].config(font=(family, new_size))
        
    def zoom_reset(self):
        for tab_info in self.tabs.values():
            tab_info['text_area'].config(font=('Arial', 11))
        
    def toggle_statusbar(self):
        if self.status_bar.winfo_ismapped():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(side=BOTTOM, fill=X)
            
    def toggle_toolbar(self):
        if self.toolbar.winfo_ismapped():
            self.toolbar.pack_forget()
        else:
            self.toolbar.pack(side=TOP, fill=X)
            
    def show_stats(self):
        text_area = self.get_current_text_area()
        if text_area:
            content = text_area.get(1.0, END)
            lines = len(content.split('\n'))
            words = len(content.split())
            chars = len(content)
            chars_no_spaces = len(content.replace(' ', '').replace('\n', ''))
            
            showinfo("Статистика", 
                    f"Строк: {lines}\n"
                    f"Слов: {words}\n"
                    f"Символов: {chars}\n"
                    f"Символов (без пробелов): {chars_no_spaces}")
                
    def spell_check(self):
        # Базовая проверка орфографии (можно расширить)
        showinfo("Проверка орфографии", "Функция проверки орфографии в разработке")
        
    def print_file(self):
        # Простая реализация печати через диалог
        try:
            text_area = self.get_current_text_area()
            if text_area:
                content = text_area.get(1.0, END)
                
                import tempfile
                # Создаем временный файл для печати
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                    
                # Открываем диалог печати (Windows)
                if os.name == 'nt':
                    os.startfile(tmp_path, 'print')
                    showinfo("Печать", "Документ отправлен на печать")
                else:
                    showinfo("Печать", f"Содержимое сохранено во временный файл:\n{tmp_path}")
                
        except Exception as e:
            showerror("Ошибка печати", f"Не удалось напечатать документ:\n{str(e)}")
            
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
        help_window = Toplevel(self.root)
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
ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ИЛИ ИНЫХ ДЕЙСТВИЙ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ.
        """
        license_window = Toplevel(self.root)
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
                
    def update_status(self):
        text_area = self.get_current_text_area()
        if text_area and hasattr(self, 'status_bar'):
            cursor_pos = text_area.index(INSERT)
            line, column = cursor_pos.split('.')
            content = text_area.get(1.0, END)
            total_lines = len(content.split('\n'))
            word_count = len(content.split())
            char_count = len(content)
            
            current_tab_info = self.get_current_tab_info()
            file_info = ""
            modified_indicator = ""
            if current_tab_info:
                if current_tab_info['file_path']:
                    file_info = f" - {os.path.basename(current_tab_info['file_path'])}"
                if current_tab_info['modified']:
                    modified_indicator = " [Изменен]"
            
            self.status_bar.config(
                text=f"Строка: {line}, Колонка: {column} | Строк: {total_lines-1} | Слов: {word_count} | Символов: {char_count}{file_info}{modified_indicator}"
            )
        
    # НОВЫЕ ФУНКЦИИ
    
    def toggle_autosave(self):
        """Включает/выключает автосохранение"""
        self.auto_save = not self.auto_save
        if self.auto_save:
            self.start_autosave()
            showinfo("Автосохранение", "Автосохранение включено")
        else:
            showinfo("Автосохранение", "Автосохранение выключено")
            
    def start_autosave(self):
        """Запускает автосохранение"""
        if self.auto_save:
            self.autosave()
            self.root.after(self.auto_save_interval, self.start_autosave)
            
    def autosave(self):
        """Выполняет автосохранение"""
        if self.auto_save:
            for tab_id, tab_info in self.tabs.items():
                if tab_info['file_path'] and tab_info['modified']:
                    try:
                        content = tab_info['text_area'].get(1.0, END)
                        # Создаем автосохраненную копию
                        backup_name = f"autosave_{os.path.basename(tab_info['file_path'])}_{int(time.time())}.bak"
                        backup_path = os.path.join(self.backup_dir, backup_name)
                        
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                        # Сохраняем информацию о сессии
                        self.save_session()
                        
                    except Exception as e:
                        print(f"Ошибка автосохранения: {e}")
                        
    def autosave_settings(self):
        """Настройки автосохранения"""
        settings_window = Toplevel(self.root)
        settings_window.title("Настройки автосохранения")
        settings_window.geometry('300x200')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        Label(settings_window, text="Интервал автосохранения (минуты):").pack(pady=10)
        
        interval_var = StringVar(value=str(self.auto_save_interval // 60000))
        interval_entry = Entry(settings_window, textvariable=interval_var, width=10)
        interval_entry.pack(pady=5)
        
        def save_settings():
            try:
                minutes = int(interval_var.get())
                if minutes < 1:
                    showerror("Ошибка", "Интервал должен быть не менее 1 минуты")
                    return
                    
                self.auto_save_interval = minutes * 60000
                settings_window.destroy()
                showinfo("Настройки", "Интервал автосохранения обновлен")
                
            except ValueError:
                showerror("Ошибка", "Введите корректное число")
                
        Button(settings_window, text="Сохранить", command=save_settings).pack(pady=10)
        
    def save_session(self):
        """Сохраняет текущую сессию"""
        session_data = {
            'tabs': [],
            'theme': self.theme,
            'auto_save': self.auto_save,
            'auto_save_interval': self.auto_save_interval
        }
        
        for tab_info in self.tabs.values():
            tab_data = {
                'file_path': tab_info['file_path'],
                'content': tab_info['text_area'].get(1.0, END),
                'name': tab_info['name']
            }
            session_data['tabs'].append(tab_data)
            
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения сессии: {e}")
            
    def load_session(self):
        """Загружает сохраненную сессию"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    
                # Восстанавливаем настройки
                self.theme = session_data.get('theme', 'light')
                self.auto_save = session_data.get('auto_save', False)
                self.auto_save_interval = session_data.get('auto_save_interval', 300000)
                
                # Восстанавливаем вкладки
                for tab_data in session_data.get('tabs', []):
                    self.new_tab(tab_data['file_path'], tab_data['content'])
                    
                self.apply_theme()
                
                if self.auto_save:
                    self.start_autosave()
                    
        except Exception as e:
            print(f"Ошибка загрузки сессии: {e}")
            
    def create_backup(self, file_path, content):
        """Создает резервную копию файла"""
        try:
            backup_name = f"backup_{os.path.basename(file_path)}_{int(time.time())}.bak"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            
    def create_version(self, file_path, content):
        """Создает версионную копию файла"""
        try:
            version_name = f"v{int(time.time())}_{os.path.basename(file_path)}"
            version_path = os.path.join(self.backup_dir, version_name)
            
            with open(version_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
        except Exception as e:
            print(f"Ошибка создания версии: {e}")
            
    def show_version_history(self):
        """Показывает историю версий текущего файла"""
        current_tab_info = self.get_current_tab_info()
        if not current_tab_info or not current_tab_info['file_path']:
            showinfo("История версий", "Файл не сохранен")
            return
            
        file_path = current_tab_info['file_path']
        
        history_window = Toplevel(self.root)
        history_window.title("История версий")
        history_window.geometry('600x400')
        
        # Получаем список версий
        versions = []
        try:
            for file in os.listdir(self.backup_dir):
                if file.startswith('v') and os.path.basename(file_path) in file:
                    file_time = file.split('_')[0][1:]
                    versions.append((file, datetime.fromtimestamp(int(file_time))))
                    
            versions.sort(key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            showinfo("Ошибка", f"Не удалось загрузить историю версий: {e}")
            return
            
        if not versions:
            showinfo("История версий", "Версии не найдены")
            history_window.destroy()
            return
            
        # Создаем список версий
        listbox = Listbox(history_window)
        for version, timestamp in versions:
            listbox.insert(END, f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {version}")
            
        listbox.pack(expand=True, fill=BOTH, padx=10, pady=10)
        
        def view_version():
            selection = listbox.curselection()
            if selection:
                version_file = versions[selection[0]][0]
                version_path = os.path.join(self.backup_dir, version_file)
                
                try:
                    with open(version_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Показываем содержимое версии
                    view_window = Toplevel(history_window)
                    view_window.title(f"Просмотр версии: {version_file}")
                    view_window.geometry('800x600')
                    
                    text_widget = Text(view_window, wrap='word')
                    scrollbar = Scrollbar(view_window, command=text_widget.yview)
                    text_widget.configure(yscrollcommand=scrollbar.set)
                    
                    text_widget.insert(1.0, content)
                    text_widget.config(state=DISABLED)
                    
                    scrollbar.pack(side=RIGHT, fill=Y)
                    text_widget.pack(expand=True, fill=BOTH, padx=10, pady=10)
                    
                except Exception as e:
                    showerror("Ошибка", f"Не удалось открыть версию: {e}")
                    
        Button(history_window, text="Просмотреть версию", command=view_version).pack(pady=10)
        
    def restore_version(self):
        """Восстанавливает файл из предыдущей версии"""
        current_tab_info = self.get_current_tab_info()
        if not current_tab_info or not current_tab_info['file_path']:
            showinfo("Восстановление", "Файл не сохранен")
            return
            
        # Простой диалог для выбора файла резервной копии
        backup_file = askopenfilename(
            initialdir=self.backup_dir,
            title="Выберите версию для восстановления",
            filetypes=[("Backup files", "*.bak"), ("All files", "*.*")]
        )
        
        if backup_file:
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                current_tab_info['text_area'].delete(1.0, END)
                current_tab_info['text_area'].insert(1.0, content)
                current_tab_info['modified'] = True
                
                showinfo("Восстановление", "Версия успешно восстановлена")
                
            except Exception as e:
                showerror("Ошибка", f"Не удалось восстановить версию: {e}")
                
    def load_plugins(self):
        """Загружает плагины из папки plugins"""
        try:
            if not os.path.exists(self.plugins_dir):
                return
                
            for file in os.listdir(self.plugins_dir):
                if file.endswith('.py'):
                    plugin_path = os.path.join(self.plugins_dir, file)
                    try:
                        # В реальной реализации здесь будет загрузка плагинов
                        print(f"Загружен плагин: {file}")
                    except Exception as e:
                        print(f"Ошибка загрузки плагина {file}: {e}")
                        
        except Exception as e:
            print(f"Ошибка загрузки плагинов: {e}")
            
    def plugin_manager(self):
        """Менеджер плагинов"""
        manager_window = Toplevel(self.root)
        manager_window.title("Менеджер плагинов")
        manager_window.geometry('500x400')
        
        Label(manager_window, text="Доступные плагины:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Список плагинов
        plugins_list = Listbox(manager_window)
        plugins_list.pack(expand=True, fill=BOTH, padx=10, pady=10)
        
        # Заполняем список (в реальной реализации здесь будут реальные плагины)
        plugins_list.insert(END, "Плагин проверки орфографии (в разработке)")
        plugins_list.insert(END, "Плагин экспорта в PDF (в разработке)")
        plugins_list.insert(END, "Плагин синхронизации с облаком (в разработке)")
        
        Label(manager_window, text="Система плагинов находится в разработке", 
              font=('Arial', 10), fg='blue').pack(pady=10)
              
    def refresh_plugins(self):
        """Обновляет список плагинов"""
        showinfo("Плагины", "Список плагинов обновлен")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    editor = TextEditor()
    editor.run()
