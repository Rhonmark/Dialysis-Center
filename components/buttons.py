import tkinter as tk

class Button(tk.Button):
    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            bg="#68EDC6", 
            fg="white",   
            font=("Arial", 14),  
            command=command,
            **kwargs
        )