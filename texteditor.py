from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
import os
import sys

class TextEditor:
    def __init__(self):
        self.root = Tk()
        self.current_file = None
        self.setup_icon()
        self.setup_ui()
        self.setup_bindings()
        
    def setup_icon(self):
        datafile = "TextEditor.ico"
        if not hasattr(sys, "frozen"):
            datafile = os.path.join(os.path.dirname(__file__), datafile)
        else:
            datafile = os.path.join(sys.prefix, datafile)
        if os.path.exists(datafile):
            self.root.iconbitmap(default=datafile)

    def setup_ui(self):
        self.root.title("Текстовый Редактор - Новый файл")
        self.root.geometry('1000x600')
        
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
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        
        # Меню Формат
        format_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Формат", menu=format_menu)
        format_menu.add_command(label="Перенос слов", command=self.toggle_word_wrap)
        format_menu.add_command(label="Шрифт...", command=self.change_font)
        
        # Меню Справка
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.about, accelerator="F1")
        
        # Текстовая область
        self.text_area = Text(self.root, wrap='word', undo=True, font=('Arial', 11))
        self.scrollbar = Scrollbar(self.root, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text_area.pack(expand=YES, fill=BOTH)
        
        # Статус бар
        self.status_bar = Label(self.root, text="Готово", anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        self.update_status()
        
    def setup_bindings(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<F1>', lambda e: self.about())
        self.root.bind('<Key>', lambda e: self.update_status())
        self.text_area.bind('<Button-1>', lambda e: self.update_status())
        
    def new_file(self):
        if self.check_save():
            self.text_area.delete(1.0, END)
            self.current_file = None
            self.root.title("Текстовый Редактор - Новый файл")
            
    def open_file(self):
        if self.check_save():
            file_path = askopenfilename(
                filetypes=[
                    ("Текстовые файлы", "*.txt"),
                    ("Все файлы", "*.*")
                ]
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    self.text_area.delete(1.0, END)
                    self.text_area.insert(1.0, content)
                    self.current_file = file_path
                    self.root.title(f"Текстовый Редактор - {os.path.basename(file_path)}")
                except Exception as e:
                    showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
                    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_bar.config(text="Файл сохранен")
            except Exception as e:
                showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"Текстовый Редактор - {os.path.basename(file_path)}")
                self.status_bar.config(text="Файл сохранен")
            except Exception as e:
                showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
                
    def check_save(self):
        content = self.text_area.get(1.0, END)
        if len(content) > 1:  # Больше 1 потому что всегда есть символ конца строки
            answer = askyesnocancel("Сохранение", "Сохранить изменения в файле?")
            if answer is None:  # Cancel
                return False
            elif answer:  # Yes
                self.save_file()
        return True
        
    def exit_app(self):
        if self.check_save():
            self.root.destroy()
            
    def undo(self):
        try:
            self.text_area.event_generate("<<Undo>>")
        except TclError:
            pass
            
    def redo(self):
        try:
            self.text_area.event_generate("<<Redo>>")
        except TclError:
            pass
            
    def cut(self):
        self.text_area.event_generate("<<Cut>>")
        
    def copy(self):
        self.text_area.event_generate("<<Copy>>")
        
    def paste(self):
        self.text_area.event_generate("<<Paste>>")
        
    def delete(self):
        self.text_area.delete(SEL_FIRST, SEL_LAST)
        
    def select_all(self):
        self.text_area.tag_add(SEL, "1.0", END)
        self.text_area.mark_set(INSERT, "1.0")
        self.text_area.see(INSERT)
        
    def toggle_word_wrap(self):
        current_wrap = self.text_area.cget('wrap')
        new_wrap = 'none' if current_wrap == 'word' else 'word'
        self.text_area.config(wrap=new_wrap)
        
    def change_font(self):
        font_window = Toplevel(self.root)
        font_window.title("Выбор шрифта")
        font_window.geometry('300x200')
        
        Label(font_window, text="Размер шрифта:").pack(pady=5)
        font_size = Spinbox(font_window, from_=8, to=72, width=10)
        font_size.pack(pady=5)
        font_size.delete(0, END)
        font_size.insert(0, "11")
        
        def apply_font():
            try:
                size = int(font_size.get())
                self.text_area.config(font=('Arial', size))
                font_window.destroy()
            except ValueError:
                showerror("Ошибка", "Некорректный размер шрифта")
                
        Button(font_window, text="Применить", command=apply_font).pack(pady=10)
        
    def about(self):
        showinfo("О программе", 
                "Текстовый редактор\n"
                "Версия 1.0\n\n"
                "Улучшенная версия с дополнительными функциями:\n"
                "- Работа с несколькими файлами\n"
                "- Отмена/повтор действий\n"
                "- Настройка шрифтов\n"
                "- Статус бар")
                
    def update_status(self):
        cursor_pos = self.text_area.index(INSERT)
        line, column = cursor_pos.split('.')
        total_lines = self.text_area.index(END).split('.')[0]
        self.status_bar.config(text=f"Строка: {line}, Колонка: {column} | Всего строк: {int(total_lines)-1}")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    editor = TextEditor()
    editor.run()
