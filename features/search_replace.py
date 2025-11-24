from tkinter import *
from tkinter.messagebox import showinfo

class SearchReplace:
    def __init__(self, editor):
        self.editor = editor
        self.search_visible = False
        self.replace_visible = False
        
    def setup_search_ui(self):
        # Область поиска
        self.search_frame = Frame(self.editor.root)
        
        Label(self.search_frame, text="Найти:").pack(side=LEFT)
        self.find_entry = Entry(self.search_frame, width=30)
        self.find_entry.pack(side=LEFT, padx=5)
        
        Button(self.search_frame, text="Найти", command=self.find_next).pack(side=LEFT, padx=2)
        Button(self.search_frame, text="Заменить на:", command=self.show_replace).pack(side=LEFT, padx=2)
        Button(self.search_frame, text="✕", command=self.hide_search).pack(side=LEFT, padx=5)
        
        # Область замены
        self.replace_frame = Frame(self.editor.root)
        
        Label(self.replace_frame, text="Заменить на:").pack(side=LEFT)
        self.replace_entry = Entry(self.replace_frame, width=30)
        self.replace_entry.pack(side=LEFT, padx=5)
        
        Button(self.replace_frame, text="Заменить", command=self.replace_next).pack(side=LEFT, padx=2)
        Button(self.replace_frame, text="Заменить все", command=self.replace_all).pack(side=LEFT, padx=2)
        Button(self.replace_frame, text="✕", command=self.hide_replace).pack(side=LEFT, padx=5)
        
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
        text_area = self.editor.get_current_text_area()
        
        if search_term and text_area:
            text_area.tag_remove('found', '1.0', END)
            
            start_pos = text_area.index(INSERT)
            idx = text_area.search(search_term, start_pos, stopindex=END)
            
            if not idx:
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
        text_area = self.editor.get_current_text_area()
        
        if search_term and text_area and text_area.tag_ranges('found'):
            current = text_area.tag_ranges('found')[0]
            text_area.delete(current, f"{current}+{len(search_term)}c")
            text_area.insert(current, replace_term)
            self.find_next()
            
    def replace_all(self):
        search_term = self.find_entry.get()
        replace_term = self.replace_entry.get()
        text_area = self.editor.get_current_text_area()
        
        if search_term and text_area:
            content = text_area.get(1.0, END)
            new_content = content.replace(search_term, replace_term)
            text_area.delete(1.0, END)
            text_area.insert(1.0, new_content)
            showinfo("Замена", "Все вхождения заменены")
