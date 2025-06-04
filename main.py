import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Dialysis Center")
    
    shared_state = {"selected_role": None, "current_frame": None}

    def navigate_to(page_name):
        """Switch frames dynamically without unnecessary delays."""
        if shared_state["current_frame"]:
            shared_state["current_frame"].pack_forget() 
        
        root.update_idletasks()

        if page_name == "LoginPage":
            from pages.LoginPage import LoginPage
            root.attributes('-fullscreen', False)  
            root.geometry("1280x720")   
            position_window(1280, 720)
            new_page = LoginPage(root, shared_state)
        elif page_name == "RegisterPage":
            from pages.RegisterPage import RegisterPage
            root.geometry("1280x720")
            position_window(1280, 720)
            new_page = RegisterPage(root, shared_state)
        elif page_name == "ForgotPage":
            from pages.ForgotPage import ForgotPage
            root.geometry("1280x720")
            position_window(1280, 720)
            new_page = ForgotPage(root, shared_state)
        elif page_name == "HomePage":
            from pages.HomePage import HomePage
            root.geometry("1920x1080")
            root.attributes('-fullscreen', True)
            position_window(1920, 1080)
            new_page = HomePage(root, shared_state)
        else:
            raise ValueError(f"Unknown page: {page_name}")
        
        shared_state["current_frame"] = new_page 
        new_page.pack(fill="both", expand=True)
        root.update_idletasks() 

    def position_window(width, height):
        """Centers the window on the screen."""
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

    shared_state["navigate"] = navigate_to
    root.geometry("1280x720")
    root.attributes("-toolwindow", False) 
    root.resizable(False, False)  

    position_window(1280, 720)

    navigate_to("HomePage")
    root.mainloop()

# if __name__ == "__main__":
#     main()
