import time
import os
from tkinter import *
from tkinter.messagebox import showinfo, showerror

class AutoSaveManager:
    def __init__(self, editor):
        self.editor = editor
        
    def toggle_autosave(self):
        """Включает/выключает автосохранение"""
        self.editor.auto_save = not self.editor.auto_save
        if self.editor.auto_save:
            self.start_autosave()
            showinfo("Автосохранение", "Автосохранение включено")
        else:
            showinfo("Автосохранение", "Автосохранение выключено")
            
    def start_autosave(self):
        """Запускает автосохранение"""
        if self.editor.auto_save:
            self.autosave()
            self.editor.root.after(self.editor.auto_save_interval, self.start_autosave)
            
    def autosave(self):
        """Выполняет автосохранение"""
        if self.editor.auto_save:
            for tab_id, tab_info in self.editor.tab_manager.tabs.items():
                if tab_info['file_path'] and tab_info['modified']:
                    try:
                        content = tab_info['text_area'].get(1.0, END)  # Здесь используется END
                        backup_name = f"autosave_{os.path.basename(tab_info['file_path'])}_{int(time.time())}.bak"
                        backup_path = os.path.join(self.editor.backup_dir, backup_name)
                        
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                        self.editor.session_manager.save_session()
                        
                    except Exception as e:
                        print(f"Ошибка автосохранения: {e}")
                        
    def autosave_settings(self):
        """Настройки автосохранения"""
        settings_window = Toplevel(self.editor.root)
        settings_window.title("Настройки автосохранения")
        settings_window.geometry('300x200')
        settings_window.transient(self.editor.root)
        settings_window.grab_set()
        
        Label(settings_window, text="Интервал автосохранения (минуты):").pack(pady=10)
        
        interval_var = StringVar(value=str(self.editor.auto_save_interval // 60000))
        interval_entry = Entry(settings_window, textvariable=interval_var, width=10)
        interval_entry.pack(pady=5)
        
        def save_settings():
            try:
                minutes = int(interval_var.get())
                if minutes < 1:
                    showerror("Ошибка", "Интервал должен быть не менее 1 минуты")
                    return
                    
                self.editor.auto_save_interval = minutes * 60000
                settings_window.destroy()
                showinfo("Настройки", "Интервал автосохранения обновлен")
                
            except ValueError:
                showerror("Ошибка", "Введите корректное число")
                
        Button(settings_window, text="Сохранить", command=save_settings).pack(pady=10)
