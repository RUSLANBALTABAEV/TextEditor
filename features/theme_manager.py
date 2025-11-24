class ThemeManager:
    def __init__(self, editor):
        self.editor = editor
        
    def change_theme(self, theme_name):
        self.editor.theme = theme_name
        self.apply_theme()
        
    def apply_theme(self):
        if self.editor.theme == "light":
            bg_color = "white"
            fg_color = "black"
            cursor_color = "black"
        elif self.editor.theme == "dark":
            bg_color = "#2b2b2b"
            fg_color = "white"
            cursor_color = "white"
        elif self.editor.theme == "blue":
            bg_color = "#e6f3ff"
            fg_color = "black"
            cursor_color = "black"
            
        for tab_info in self.editor.tab_manager.tabs.values():
            tab_info['text_area'].config(bg=bg_color, fg=fg_color, insertbackground=cursor_color)
            
        self.editor.root.config(bg=bg_color)
