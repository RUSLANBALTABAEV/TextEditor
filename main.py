import sys
import os

# Добавляем пути для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'features'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from texteditor import TextEditor

if __name__ == "__main__":
    editor = TextEditor()
    editor.run()
