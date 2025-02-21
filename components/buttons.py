import tkinter as tk

class Button(tk.Button):
    def __init__(self, parent, text, command=None, shared_state=None, selectable=False, **kwargs):
        super().__init__(
            parent,
            text=text,
            bg="#68EDC6",
            fg="white",
            font=("Arial", 14),
            command=command,
            **kwargs
        )

        self.default_color = "#68EDC6"  
        self.selected_color = "#4AC3A5" 
        self.hover_color = "#56D6B4" 

        self.is_selected = False
        self.selectable = selectable 
        self.shared_state = shared_state  

        if self.selectable:
            self.bind("<Enter>", self.on_hover)
            self.bind("<Leave>", self.on_leave)
            self.bind("<Button-1>", self.on_click)

    def on_hover(self, event):
        if self.selectable and not self.is_selected:
            self.configure(bg=self.hover_color)

    def on_leave(self, event):
        if self.selectable and not self.is_selected:
            self.configure(bg=self.default_color)

    def on_click(self, event):
        if self.selectable and self.shared_state is not None:
            if self.is_selected:  
                self.deselect()
                self.shared_state["selected_role"] = None  
            else:
                self.is_selected = True
                self.configure(bg=self.selected_color)
                self.shared_state["selected_role"] = self.cget("text")

                for widget in self.master.winfo_children():
                    if isinstance(widget, Button) and widget != self and widget.selectable:
                        widget.deselect()
    def deselect(self):
        if self.selectable:
            self.is_selected = False
            self.configure(bg=self.default_color)

def apply_selected_state(shared_state, parent):
    selected_role = shared_state.get("selected_role", None)
    
    if selected_role:
        for widget in parent.winfo_children():
            if isinstance(widget, Button) and widget.selectable and widget.cget("text") == selected_role:
                widget.on_click(None) 
                break 
