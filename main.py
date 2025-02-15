import tkinter as tk
from pages.LoginPage import LoginPage
from pages.RegisterPage import RegisterPage
from pages.ForgotPage import ForgotPage

def main():
    root = tk.Tk()
    root.title("Dialysis Center")
    root.geometry("1280x720") 

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1280
    window_height = 720
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)

    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    test_page = LoginPage(root)
    test_page.pack(fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()