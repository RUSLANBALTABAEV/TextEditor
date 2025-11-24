from tkinter import *

class Toolbar:
    def __init__(self, editor):
        self.editor = editor
        
    def create_toolbar(self):
        self.toolbar = Frame(self.editor.root, bd=1, relief=RAISED)
        self.toolbar.pack(side=TOP, fill=X)
        
        # Кнопки панели инструментов
        buttons = [
            ("Новый", self.editor.file_manager.new_file, "Создать новый файл"),
            ("Открыть", self.editor.file_manager.open_file, "Открыть файл"),
            ("Сохранить", self.editor.file_manager.save_file, "Сохранить файл"),
            ("+Вкладка", self.editor.tab_manager.new_tab, "Новая вкладка"),
            ("Печать", self.editor.file_manager.print_file, "Печать документа"),
            ("Найти", self.editor.search_replace.find_text, "Найти текст"),
            ("Вырезать", self.editor.editor_commands.cut, "Вырезать выделенный текст"),
            ("Копировать", self.editor.editor_commands.copy, "Копировать выделенный текст"),
            ("Вставить", self.editor.editor_commands.paste, "Вставить текст из буфера"),
        ]
        
        for text, command, tooltip in buttons:
            btn = Button(self.toolbar, text=text, command=command, relief=RAISED, bd=1)
            btn.pack(side=LEFT, padx=2, pady=2)
            self.create_tooltip(btn, tooltip)
            
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
        
    def toggle_toolbar(self):
        if self.toolbar.winfo_ismapped():
            self.toolbar.pack_forget()
        else:
            self.toolbar.pack(side=TOP, fill=X)
