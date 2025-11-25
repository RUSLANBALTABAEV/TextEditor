import json
import os
from tkinter import END
from tkinter.messagebox import showerror

class SessionManager:
    def __init__(self, editor):
        self.editor = editor
        
    def save_session(self):
        """Сохраняет текущую сессию"""
        session_data = {
            'tabs': [],
            'theme': self.editor.theme,
            'auto_save': self.editor.auto_save,
            'auto_save_interval': self.editor.auto_save_interval
        }
        
        for tab_info in self.editor.tab_manager.tabs.values():
            tab_data = {
                'file_path': tab_info['file_path'],
                'content': tab_info['text_area'].get(1.0, END),  # Здесь используется END
                'name': tab_info['name']
            }
            session_data['tabs'].append(tab_data)
            
        try:
            with open(self.editor.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения сессии: {e}")
            
    def load_session(self):
        """Загружает сохраненную сессию"""
        try:
            if os.path.exists(self.editor.session_file):
                with open(self.editor.session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    
                # Восстанавливаем настройки
                self.editor.theme = session_data.get('theme', 'light')
                self.editor.auto_save = session_data.get('auto_save', False)
                self.editor.auto_save_interval = session_data.get('auto_save_interval', 300000)
                
                # Восстанавливаем вкладки
                for tab_data in session_data.get('tabs', []):
                    self.editor.tab_manager.new_tab(tab_data['file_path'], tab_data['content'])
                    
                if self.editor.auto_save:
                    self.editor.autosave_manager.start_autosave()
                    
        except Exception as e:
            print(f"Ошибка загрузки сессии: {e}")
