import tkinter as tk

class TextField(tk.Entry):
    def __init__(self, parent, placeholder="", width=20, font=("Arial", 12), height=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.placeholder = placeholder
        self.insert(0, placeholder)
        self.configure(fg="grey", justify="center")

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
        self.configure(
            relief="flat",
            bd=0,
            font=font,
            highlightthickness=0,
            bg="#f5f5f5",
        )
        
        self.configure(width=width)
    
        if height:
            self.configure(font=("Arial", height))

    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg="black")  

    def on_focus_out(self, event):
        if self.get() == "":
            self.insert(0, self.placeholder)
            self.configure(fg="grey")
