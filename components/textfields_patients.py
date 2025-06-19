import tkinter as tk

class TextField_Patients(tk.Entry):
    def __init__(self, parent, placeholder="Type Here", font=("Merriweather light", 12), **kwargs):
        super().__init__(parent, font=font, **kwargs)
        
        self.placeholder = placeholder
        self.default_fg_color = "gray"
        self.active_fg_color = "black"
        
        self.insert(0, self.placeholder)
        self.config(fg=self.default_fg_color)

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def set_real_value(self, value):
        """Set a real value, not a placeholder"""
        if value and value.strip() and value not in [self.placeholder, 'Type Here', 'type here']:
            self.delete(0, tk.END)
            self.insert(0, value.strip())
            self.config(fg=self.active_fg_color)
            return True
        return False

    def get_real_value(self):
        """Get the real value, excluding placeholder"""
        current = self.get()
        if current == self.placeholder:
            return ""
        return current

    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.active_fg_color)

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.default_fg_color)