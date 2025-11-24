from tkinter import ttk, Frame, Text, Scrollbar
from tkinter import TOP, X, BOTH, YES, RIGHT, Y, END
from tkinter.messagebox import askyesnocancel
import os

class TabManager:
    def __init__(self, editor):
        self.editor = editor
        self.root = editor.root
        self.tabs = {}
        self.current_tab_id = None
        self.tab_counter = 1
        
    def setup_tabs(self):
        self.tab_frame = Frame(self.root)
        self.tab_frame.pack(side=TOP, fill=X)
        
        self.tab_control = ttk.Notebook(self.tab_frame)
        self.tab_control.pack(expand=1, fill=BOTH)
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Создаем первую вкладку
        self.new_tab()
        
    def new_tab(self, file_path=None, content=None):
        frame = Frame(self.tab_control)
        
        # Текстовая область для вкладки
        text_area = Text(frame, wrap='word', undo=True, font=('Arial', 11), selectbackground='lightblue')
        scrollbar = Scrollbar(frame, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        text_area.pack(expand=YES, fill=BOTH)
        
        # Привязываем события
        text_area.bind('<KeyRelease>', lambda e: self.on_text_change())
        text_area.bind('<Button-1>', lambda e: self.editor.update_status())
        
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
        
        self.editor.update_status()
        return tab_id

    def on_text_change(self):
        """Обработчик изменения текста"""
        current_tab_info = self.get_current_tab_info()
        if current_tab_info:
            current_tab_info['modified'] = True
        self.editor.update_status()
        
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
                    self.editor.file_manager.save_file()
        
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
        current_frame = self.tab_control.select()
        if current_frame:
            for tab_id, tab_info in self.tabs.items():
                if str(tab_info['frame']) == str(current_frame):
                    self.current_tab_id = tab_id
                    break
        self.editor.update_status()
        
    def get_current_tab_info(self):
        """Возвращает информацию о текущей вкладке"""
        if not self.tabs or not self.current_tab_id:
            return None
        return self.tabs.get(self.current_tab_id)
        
    def get_current_text_area(self):
        """Возвращает текстовую область текущей вкладки"""
        tab_info = self.get_current_tab_info()
        return tab_info['text_area'] if tab_info else None
