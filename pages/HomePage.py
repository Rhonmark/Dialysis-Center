import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent)
        self.shared_state = shared_state
        
        label = tk.Label(self, text="Welcome to the Home Page", font=("Arial", 24))
        label.pack(pady=20)
        
        logout_button = tk.Button(self, text="Logout", font=("Arial", 14), command=self.logout)
        logout_button.pack(pady=20)
    
    def logout(self):
        """Handles logout and navigates back to the login page."""
        self.shared_state["navigate"]("LoginPage")
