from tkinter import *
from tkinter.messagebox import showinfo

class SearchReplace:
    def __init__(self, editor):
        self.editor = editor
        self.search_visible = False
        self.replace_visible = False
        self.current_match = None
        
    def setup_search_ui(self):
        # Область поиска
        self.search_frame = Frame(self.editor.root)
        
        Label(self.search_frame, text="Найти:").pack(side=LEFT)
        self.find_entry = Entry(self.search_frame, width=30)
        self.find_entry.pack(side=LEFT, padx=5)
        self.find_entry.bind('<Return>', lambda e: self.find_next())
        
        Button(self.search_frame, text="Найти", command=self.find_next).pack(side=LEFT, padx=2)
        Button(self.search_frame, text="Заменить на:", command=self.show_replace).pack(side=LEFT, padx=2)
        Button(self.search_frame, text="✕", command=self.hide_search).pack(side=LEFT, padx=5)
        
        # Область замены
        self.replace_frame = Frame(self.editor.root)
        
        Label(self.replace_frame, text="Заменить на:").pack(side=LEFT)
        self.replace_entry = Entry(self.replace_frame, width=30)
        self.replace_entry.pack(side=LEFT, padx=5)
        self.replace_entry.bind('<Return>', lambda e: self.replace_next())
        
        Button(self.replace_frame, text="Заменить", command=self.replace_next).pack(side=LEFT, padx=2)
        Button(self.replace_frame, text="Заменить все", command=self.replace_all).pack(side=LEFT, padx=2)
        Button(self.replace_frame, text="✕", command=self.hide_replace).pack(side=LEFT, padx=5)
        
    def find_text(self):
        """Показывает только панель поиска"""
        if not self.search_visible:
            self.search_frame.pack(side=TOP, fill=X, padx=5, pady=5)
            self.search_visible = True
        # Скрываем панель замены при показе поиска
        if self.replace_visible:
            self.replace_frame.pack_forget()
            self.replace_visible = False
        self.find_entry.focus()
        
    def hide_search(self):
        self.search_frame.pack_forget()
        self.search_visible = False
        # Очищаем подсветку при скрытии
        text_area = self.editor.get_current_text_area()
        if text_area:
            text_area.tag_remove('found', '1.0', END)
            text_area.tag_remove('current', '1.0', END)
        
    def show_replace(self):
        """Показывает только панель замены"""
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
        
        if not search_term or not text_area:
            return
            
        # Убираем предыдущую подсветку
        text_area.tag_remove('found', '1.0', END)
        text_area.tag_remove('current', '1.0', END)
        
        # Начинаем поиск с текущей позиции курсора
        start_pos = text_area.index(INSERT)
        idx = text_area.search(search_term, start_pos, stopindex=END)
        
        # Если не нашли с текущей позиции, ищем с начала
        if not idx:
            idx = text_area.search(search_term, '1.0', stopindex=start_pos)
            
        if idx:
            end_idx = f"{idx}+{len(search_term)}c"
            
            # Подсвечиваем все вхождения
            start = '1.0'
            while True:
                pos = text_area.search(search_term, start, stopindex=END)
                if not pos:
                    break
                end = f"{pos}+{len(search_term)}c"
                text_area.tag_add('found', pos, end)
                start = end
            
            # Подсвечиваем текущее вхождение другим цветом
            text_area.tag_add('current', idx, end_idx)
            text_area.tag_config('found', background='lightyellow')
            text_area.tag_config('current', background='orange')
            
            text_area.mark_set(INSERT, idx)
            text_area.see(idx)
            
            # Сохраняем текущее совпадение для замены
            self.current_match = (idx, end_idx)
        else:
            showinfo("Поиск", "Текст не найден")
            self.current_match = None
                
    def replace_text(self):
        """Функция для вызова из меню/горячих клавиш - показывает ОБЕ панели"""
        # Показываем обе панели
        if not self.search_visible:
            self.search_frame.pack(side=TOP, fill=X, padx=5, pady=5)
            self.search_visible = True
        if not self.replace_visible:
            self.replace_frame.pack(side=TOP, fill=X, padx=5, pady=5)
            self.replace_visible = True
        self.find_entry.focus()
        
    def replace_next(self):
        search_term = self.find_entry.get()
        replace_term = self.replace_entry.get()
        text_area = self.editor.get_current_text_area()
        
        if not search_term:
            showinfo("Замена", "Введите текст для поиска")
            return
            
        if not text_area:
            return
            
        # Если есть текущее совпадение, заменяем его
        if self.current_match:
            start, end = self.current_match
            text_area.delete(start, end)
            text_area.insert(start, replace_term)
            
            # Ищем следующее вхождение после замены
            text_area.mark_set(INSERT, start)
            self.find_next()
        else:
            # Если нет текущего совпадения, ищем первое
            self.find_next()
            
    def replace_all(self):
        search_term = self.find_entry.get()
        replace_term = self.replace_entry.get()
        text_area = self.editor.get_current_text_area()
        
        if not search_term or not text_area:
            return
            
        # Получаем весь текст
        content = text_area.get(1.0, END)
        
        # Считаем количество вхождений до замены
        count_before = content.count(search_term)
        
        if count_before == 0:
            showinfo("Замена", "Текст для замены не найден")
            return
            
        # Заменяем все вхождения
        new_content = content.replace(search_term, replace_term)
        
        # Обновляем текст
        text_area.delete(1.0, END)
        text_area.insert(1.0, new_content)
        
        # Очищаем подсветку
        text_area.tag_remove('found', '1.0', END)
        text_area.tag_remove('current', '1.0', END)
        
        showinfo("Замена", f"Заменено {count_before} вхождений")
        self.current_match = None
