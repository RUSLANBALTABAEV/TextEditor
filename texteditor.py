from tkinter import *
import os
import sys
from core.file_manager import FileManager
from core.tab_manager import TabManager
from core.session_manager import SessionManager
from core.editor_commands import EditorCommands
from ui.menu import MenuManager
from ui.toolbar import Toolbar
from ui.statusbar import StatusBar
from features.search_replace import SearchReplace
from features.autosave import AutoSaveManager
from features.theme_manager import ThemeManager
from utils.constants import *

class TextEditor:
    def __init__(self):
        self.root = Tk()
        self.current_file = None
        self.auto_save = False
        self.auto_save_interval = AUTOSAVE_INTERVAL
        self.theme = DEFAULT_THEME
        self.session_file = SESSION_FILE
        self.backup_dir = BACKUP_DIR
        self.plugins_dir = PLUGINS_DIR
        
        # Создаем необходимые директории
        self.setup_directories()
        
        # Инициализация компонентов
        self.tab_manager = TabManager(self)
        self.file_manager = FileManager(self)
        self.session_manager = SessionManager(self)
        self.editor_commands = EditorCommands(self)
        self.menu_manager = MenuManager(self)
        self.toolbar = Toolbar(self)
        self.status_bar = StatusBar(self)
        self.search_replace = SearchReplace(self)
        self.autosave_manager = AutoSaveManager(self)
        self.theme_manager = ThemeManager(self)
        
        self.setup_icon()
        self.setup_ui()
        self.setup_bindings()
        
        # Загружаем сессию ПОСЛЕ настройки UI
        self.session_manager.load_session()
        
    def setup_directories(self):
        """Создает необходимые директории для работы приложения"""
        # Получаем путь к исполняемому файлу или скрипту
        if getattr(sys, 'frozen', False):
            # Если запущен как .exe
            base_path = os.path.dirname(sys.executable)
        else:
            # Если запущен как скрипт
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.backup_dir = os.path.join(base_path, "backups")
        self.plugins_dir = os.path.join(base_path, "plugins")
        self.session_file = os.path.join(base_path, "session.json")
        
        for directory in [self.backup_dir, self.plugins_dir]:
            os.makedirs(directory, exist_ok=True)
        
    def setup_icon(self):
        datafile = "TextEditor.ico"
        if not hasattr(sys, "frozen"):
            datafile = os.path.join(os.path.dirname(__file__), datafile)
        else:
            datafile = os.path.join(sys.prefix, datafile)
        if os.path.exists(datafile):
            try:
                self.root.iconbitmap(default=datafile)
            except:
                pass  # Игнорируем ошибки с иконкой

    def setup_ui(self):
        self.root.title("Текстовый Редактор 3.4 - Новый файл")
        self.root.geometry('1200x700')
        
        # Создаем компоненты UI
        self.menu_manager.create_menu()
        self.toolbar.create_toolbar()
        self.tab_manager.setup_tabs()
        self.search_replace.setup_search_ui()
        self.status_bar.create_status_bar()
        self.theme_manager.apply_theme()
        
        # Загружаем плагины
        self.load_plugins()
        
    def setup_bindings(self):
         """Привязка горячих клавиш"""
         # Файловые операции
         self.root.bind('<Control-n>', lambda e: self.file_manager.new_file())
         self.root.bind('<Control-o>', lambda e: self.file_manager.open_file())
         self.root.bind('<Control-s>', lambda e: self.file_manager.save_file())
         self.root.bind('<Control-Shift-S>', lambda e: self.file_manager.save_as_file())

         # Управление вкладками
         self.root.bind('<Control-t>', lambda e: self.tab_manager.new_tab())
         self.root.bind('<Control-w>', lambda e: self.tab_manager.close_tab())

         # Печать
         self.root.bind('<Control-p>', lambda e: self.file_manager.print_file())

         # Выход
         self.root.bind('<Control-q>', lambda e: self.exit_app())
         
         # Редактирование
         self.root.bind('<Control-z>', lambda e: self.editor_commands.undo())
         self.root.bind('<Control-y>', lambda e: self.editor_commands.redo())
         self.root.bind('<Control-x>', lambda e: self.editor_commands.cut())
         self.root.bind('<Control-c>', lambda e: self.editor_commands.copy())
         self.root.bind('<Control-v>', lambda e: self.editor_commands.paste())
         self.root.bind('<Control-a>', lambda e: self.editor_commands.select_all())
         self.root.bind('<Control-f>', lambda e: self.search_replace.find_text())
         self.root.bind('<Control-h>', lambda e: self.search_replace.replace_text())
         self.root.bind('<F5>', lambda e: self.editor_commands.insert_datetime())
         self.root.bind('<F1>', lambda e: self.menu_manager.show_help())

         # Масштабирование
         self.root.bind('<Control-plus>', lambda e: self.editor_commands.zoom_in())
         self.root.bind('<Control-minus>', lambda e: self.editor_commands.zoom_out())
         self.root.bind('<Control-0>', lambda e: self.editor_commands.zoom_reset())
        
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
            
    def run(self):
        self.root.mainloop()
        
    # Методы-прокси для доступа к компонентам
    def get_current_tab_info(self):
        return self.tab_manager.get_current_tab_info()
        
    def get_current_text_area(self):
        return self.tab_manager.get_current_text_area()
        
    def update_status(self):
        self.status_bar.update_status()
        
    def apply_theme(self):
        self.theme_manager.apply_theme()
        
    def save_session(self):
        self.session_manager.save_session()
        
    def exit_app(self):
        if self.file_manager.check_save():
            self.save_session()
            self.root.destroy()
