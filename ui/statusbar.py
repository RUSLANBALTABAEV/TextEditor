from tkinter import *

class StatusBar:
    def __init__(self, editor):
        self.editor = editor
        
    def create_status_bar(self):
        self.status_bar = Label(self.editor.root, text="Готово | Строк: 1 | Слов: 0 | Символов: 0", relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)
        
    def update_status(self):
        text_area = self.editor.get_current_text_area()
        if text_area and hasattr(self, 'status_bar'):
            cursor_pos = text_area.index(INSERT)
            line, column = cursor_pos.split('.')
            content = text_area.get(1.0, END)
            total_lines = len(content.split('\n'))
            word_count = len(content.split())
            char_count = len(content)
            
            current_tab_info = self.editor.get_current_tab_info()
            file_info = ""
            modified_indicator = ""
            if current_tab_info:
                if current_tab_info['file_path']:
                    file_info = f" - {current_tab_info['file_path']}"
                if current_tab_info['modified']:
                    modified_indicator = " [Изменен]"
            
            self.status_bar.config(
                text=f"Строка: {line}, Колонка: {column} | Строк: {total_lines-1} | Слов: {word_count} | Символов: {char_count}{file_info}{modified_indicator}"
            )
            
    def set_text(self, text):
        self.status_bar.config(text=text)
        
    def toggle_statusbar(self):
        if self.status_bar.winfo_ismapped():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(side=BOTTOM, fill=X)
