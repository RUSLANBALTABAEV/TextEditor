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
        self.session_manager.load_session()
        
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
        # Горячие клавиши будут обрабатываться в соответствующих менеджерах
        pass
        
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
