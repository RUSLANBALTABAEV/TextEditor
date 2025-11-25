from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror, showinfo, askyesnocancel
from tkinter import END
import os
import tempfile

class FileManager:
    def __init__(self, editor):
        self.editor = editor
        
    def new_file(self):
        current_tab_info = self.editor.get_current_tab_info()
        if current_tab_info:
            # Проверяем текущую вкладку перед очисткой
            if current_tab_info['modified']:
                content = current_tab_info['text_area'].get(1.0, END)
                if len(content.strip()) > 0 and content != '\n':
                    answer = askyesnocancel("Сохранение", "Сохранить изменения в текущем файле?")
                    if answer is None:  # Cancel
                        return
                    elif answer:  # Yes
                        self.save_file()
            
            current_tab_info['text_area'].delete(1.0, END)
            current_tab_info['file_path'] = None
            current_tab_info['modified'] = False
            current_tab_info['name'] = "Новый файл"
            self.editor.tab_manager.tab_control.tab(current_tab_info['frame'], text="Новый файл")
            self.editor.root.title("Текстовый Редактор 3.3 - Новый файл")
            self.editor.update_status()
            
    def open_file(self, file_path=None):
        if not file_path:
            file_path = askopenfilename(
                filetypes=[
                    ("Текстовые файлы", "*.txt"),
                    ("Документы Python", "*.py"),
                    ("HTML файлы", "*.html;*.htm"),
                    ("CSS файлы", "*.css"),
                    ("JavaScript файлы", "*.js"),
                    ("Все файлы", "*.*")
                ]
            )
        if file_path:
            try:
                # Попробуем определить кодировку
                encodings = ['utf-8', 'cp1251', 'iso-8859-1', 'windows-1252']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            content = file.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # Если не удалось декодировать, читаем как бинарный и пробуем latin-1
                    with open(file_path, 'rb') as file:
                        content = file.read().decode('latin-1')
                
                # Создаем новую вкладку для файла
                self.editor.tab_manager.new_tab(file_path, content)
                
            except Exception as e:
                showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
                
    def save_file(self):
        current_tab_info = self.editor.get_current_tab_info()
        if not current_tab_info:
            return
            
        file_path = current_tab_info['file_path']
        
        if file_path:
            try:
                content = current_tab_info['text_area'].get(1.0, END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                current_tab_info['modified'] = False
                self.editor.status_bar.set_text("Файл сохранен")
                
            except Exception as e:
                showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
        else:
            self.save_as_file()
                
    def save_as_file(self):
        current_tab_info = self.editor.get_current_tab_info()
        if not current_tab_info:
            return
            
        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Документы Python", "*.py"),
                ("HTML файлы", "*.html"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            try:
                content = current_tab_info['text_area'].get(1.0, END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                current_tab_info['file_path'] = file_path
                current_tab_info['modified'] = False
                current_tab_info['name'] = os.path.basename(file_path)
                self.editor.tab_manager.tab_control.tab(current_tab_info['frame'], text=current_tab_info['name'])
                self.editor.root.title(f"Текстовый Редактор 3.3 - {current_tab_info['name']}")
                self.editor.status_bar.set_text("Файл сохранен")
                
            except Exception as e:
                showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
                
    def check_save(self):
        """Проверяет необходимость сохранения во всех вкладках"""
        for tab_info in self.editor.tab_manager.tabs.values():
            content = tab_info['text_area'].get(1.0, END)
            if len(content.strip()) > 0 and content != '\n' and tab_info['modified']:
                answer = askyesnocancel("Сохранение", f"Сохранить изменения в {tab_info['name']}?")
                if answer is None:  # Cancel
                    return False
                elif answer:  # Yes
                    # Сохраняем конкретную вкладку
                    current_tab = self.editor.tab_manager.current_tab_id
                    self.editor.tab_manager.current_tab_id = tab_info['tab_id']
                    self.save_file()
                    self.editor.tab_manager.current_tab_id = current_tab
        return True
        
    def print_file(self):
        # Простая реализация печати через диалог
        try:
            text_area = self.editor.get_current_text_area()
            if text_area:
                content = text_area.get(1.0, END)
                
                # Создаем временный файл для печати
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                    
                # Открываем диалог печати (Windows)
                if os.name == 'nt':
                    os.startfile(tmp_path, 'print')
                    showinfo("Печать", "Документ отправлен на печать")
                else:
                    showinfo("Печать", f"Содержимое сохранено во временный файл:\n{tmp_path}")
                
        except Exception as e:
            showerror("Ошибка печати", f"Не удалось напечатать документ:\n{str(e)}")
