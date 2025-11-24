from tkinter import *
from tkinter import simpledialog
from tkinter.messagebox import showinfo, showerror
from datetime import datetime

class EditorCommands:
    def __init__(self, editor):
        self.editor = editor
        
    def undo(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            try:
                text_area.event_generate("<<Undo>>")
            except TclError:
                pass
            
    def redo(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            try:
                text_area.event_generate("<<Redo>>")
            except TclError:
                pass
            
    def cut(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            text_area.event_generate("<<Cut>>")
        
    def copy(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            text_area.event_generate("<<Copy>>")
        
    def paste(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            text_area.event_generate("<<Paste>>")
        
    def delete(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            try:
                text_area.delete(SEL_FIRST, SEL_LAST)
            except TclError:
                pass
        
    def select_all(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            text_area.tag_add(SEL, "1.0", END)
            text_area.mark_set(INSERT, "1.0")
            text_area.see(INSERT)
        
    def insert_datetime(self):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        text_area = self.editor.get_current_text_area()
        if text_area:
            text_area.insert(INSERT, dt_string)
        
    def toggle_word_wrap(self):
        text_area = self.editor.get_current_text_area()
        if text_area:
            current_wrap = text_area.cget('wrap')
            new_wrap = 'none' if current_wrap == 'word' else 'word'
            text_area.config(wrap=new_wrap)
        
    def change_font(self):
        font_window = Toplevel(self.editor.root)
        font_window.title("Выбор шрифта")
        font_window.geometry('300x300')
        font_window.transient(self.editor.root)
        font_window.grab_set()
        
        # Выбор семейства шрифтов
        Label(font_window, text="Шрифт:").pack(pady=5)
        font_list = Listbox(font_window, height=6)
        fonts = ["Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", "Consolas"]
        for font in fonts:
            font_list.insert(END, font)
        font_list.pack(pady=5)
        
        # Размер шрифта
        Label(font_window, text="Размер:").pack(pady=5)
        font_size = Spinbox(font_window, from_=8, to=72, width=10)
        font_size.delete(0, END)
        
        text_area = self.editor.get_current_text_area()
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
                
                for tab_info in self.editor.tab_manager.tabs.values():
                    tab_info['text_area'].config(font=(family, size))
                    
                font_window.destroy()
            except (ValueError, TclError):
                showerror("Ошибка", "Некорректные параметры шрифта")
                
        Button(font_window, text="Применить", command=apply_font).pack(pady=10)
        
    def zoom_in(self):
        for tab_info in self.editor.tab_manager.tabs.values():
            current_font = tab_info['text_area'].cget('font')
            family, size = current_font.split()
            new_size = int(size) + 1
            tab_info['text_area'].config(font=(family, new_size))
        
    def zoom_out(self):
        for tab_info in self.editor.tab_manager.tabs.values():
            current_font = tab_info['text_area'].cget('font')
            family, size = current_font.split()
            new_size = max(8, int(size) - 1)
            tab_info['text_area'].config(font=(family, new_size))
        
    def zoom_reset(self):
        for tab_info in self.editor.tab_manager.tabs.values():
            tab_info['text_area'].config(font=('Arial', 11))
            
    def show_stats(self):
        text_area = self.editor.get_current_text_area()
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
