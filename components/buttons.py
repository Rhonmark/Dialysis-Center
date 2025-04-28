import customtkinter as ctk

class CTkButtonSelectable(ctk.CTkButton):
    def __init__(self, parent, text, command=None, shared_state=None, selectable=False, **kwargs):
        super().__init__(
            parent,
            text=text,
            fg_color="#68EDC6",
            text_color="white",
            font=("Arial", 14),
            command=command,
            corner_radius=15,  
            bg_color="white",  
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
        """Change color on hover if not selected."""
        if self.selectable and not self.is_selected:
            self.configure(fg_color=self.hover_color)

    def on_leave(self, event):
        """Reset color when mouse leaves if not selected."""
        if self.selectable and not self.is_selected:
            self.configure(fg_color=self.default_color)

    def on_click(self, event=None):
        """Handles selection logic when button is clicked."""
        if self.selectable and self.shared_state is not None:
            if self.is_selected:  
                self.deselect()
                self.shared_state["selected_role"] = None  
            else:
                self.select()
                self.shared_state["selected_role"] = self.cget("text")

                for widget in self.master.winfo_children():
                    if isinstance(widget, CTkButtonSelectable) and widget != self and widget.selectable:
                        widget.deselect()

    def select(self):
        """Manually set the button as selected."""
        self.is_selected = True
        self.configure(fg_color=self.selected_color)

    def deselect(self):
        """Reset the button state when unselected."""
        self.is_selected = False
        self.configure(fg_color=self.default_color)


def apply_selected_state(shared_state, parent):
    """Automatically selects the button based on shared_state."""
    selected_role = shared_state.get("selected_role", None)
    
    if selected_role:
        for widget in parent.winfo_children():
            if isinstance(widget, CTkButtonSelectable) and widget.selectable and widget.cget("text") == selected_role:
                widget.select()  
                break
