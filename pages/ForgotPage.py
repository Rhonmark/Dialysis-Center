import random
import tkinter as tk
from tkinter import ttk
from components.textfields import TextField
from components.buttons import Button
from PIL import Image, ImageTk
from backend.input_validator import get_answer_from_db, db_connection, get_username_from_db, forgot_validator
from components.buttons import Button, apply_selected_state

class ForgotPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent)

        self.columnconfigure(0, weight=2, uniform="group")  
        self.columnconfigure(1, weight=1, uniform="group") 
        self.rowconfigure(0, weight=1)
        self.shared_state = shared_state  

        # Access the selected role
        selected_role = self.shared_state.get("selected_role", "None")
        print(selected_role)

        # Left container 
        left_container = tk.Frame(self)
        left_container.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(left_container)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # bg
        try:
            image_path = "assets/bg.png"  
            image = Image.open(image_path).convert("RGBA") 
            image = image.resize((900, 720))
            self.bg_image = ImageTk.PhotoImage(image)

            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        except Exception as e:
            self.canvas.create_text(450, 355, text="Error loading image", fill="red", font=("Arial", 16))

        # logo
        try:
            logo_path = "assets/logo.png" 
            logo_image = Image.open(logo_path).convert("RGBA")  
            logo_image = logo_image.resize((130, 130))  
            self.logo_icon = ImageTk.PhotoImage(logo_image)

            self.canvas.create_image(150, 71, anchor="n", image=self.logo_icon)
        except Exception as e:
            self.canvas.create_text(450, 100, text="Error loading logo", fill="red", font=("Arial", 12))

        self.canvas.create_text(
            340, 230,  
            text="Welcome to, \nFirst Priority Dialysis Center",
            font=("Arial", 29, "bold"),
            fill="black", 
            anchor="n"  
        )

        self.canvas.create_text(
            290, 330, 
            text="Where needs are always met.",
            font=("Arial", 25),
            fill="black", 
            anchor="n"  
        )

        self.canvas.create_text(
            370, 385,  
            text="Designed to streamline and manage all essential supplies. \nEnsuring that resources are readily available, accurately tracked, \nand organized to support the center's commitment to high-\nquality patient care.",
            font=("Arial", 15),
            fill="black", 
            anchor="n"  
        )

        # Admin Button 
        self.admin_button = Button(
            left_container, 
            text="Admin", 
            selectable=True,
            shared_state=self.shared_state
            )
        self.admin_button.place(relx=0.24, rely=0.73, anchor="n", width=250, height=55)

        # Staff Button 
        self.staff_button = Button(
            left_container, 
            text="Staff", 
            selectable=True,
            shared_state=self.shared_state
            )
        self.staff_button.place(relx=0.59, rely=0.73, anchor="n", width=250, height=55)

        apply_selected_state(shared_state, left_container)

        # Right container
        right_container = tk.Frame(self, bg="#1A374D")  
        right_container.grid(row=0, column=1, sticky="nsew")

        # Title label 
        title = tk.Label(right_container, text="FORGOT\nPASSWORD", font=("Arial", 30, "bold"), fg="#68EDC6", bg="#1A374D", justify="center")
        title.place(relx=0.5, rely=0, anchor="n", y=50)

        # Step tracking
        self.step = 1

        # Username Label
        self.username_label = tk.Label(right_container, text="Username", font=("Arial", 12), fg="white", bg="#1A374D")
        self.username_label.place(relx=0.23, rely=0.36, anchor="n")

        # Username Field
        self.username_field = TextField(right_container, placeholder="Username must be at least 8 characters", font=("Arial", 12), width=25)
        self.username_field.place(relx=0.5, rely=0.40, anchor="n", width=300, height=50)  
        
        # Secret Question label (Initially Hidden)
        self.secret_question_label = tk.Label(right_container, text="Secret Question", font=("Arial", 12), fg="white", bg="#1A374D")
        
        # Secret Question Answer Field (Initially Hidden)
        self.secret_question_field = TextField(right_container, placeholder="Enter secret question answer", font=("Arial", 12), width=25)
        
        # New Password Fields (Initially Hidden)
        self.new_password_label = tk.Label(right_container, text="New Password", font=("Arial", 12), fg="white", bg="#1A374D")
        self.new_password_field = TextField(right_container, placeholder="Enter new password", font=("Arial", 12), width=25)
        
        self.confirm_password_label = tk.Label(right_container, text="Confirm Password", font=("Arial", 12), fg="white", bg="#1A374D")
        self.confirm_password_field = TextField(right_container, placeholder="Confirm new password", font=("Arial", 12), width=25)
        
        # Enter Button
        self.enter_button = Button(right_container, text="Enter", command=self.on_enter_click)
        self.enter_button.place(relx=0.5, rely=0.71, anchor="n", width=230, height=50)

        # Cancel Button
        cancel_button = Button(right_container, text="Cancel", command=self.on_cancel_click)
        cancel_button.place(relx=0.5, rely=0.8, anchor="n", width=230, height=50)

    def on_enter_click(self):

        username = self.username_field.get().strip()
        secret_answer = self.secret_question_field.get().strip()
        password = self.new_password_field.get().strip()
        confirm_password = self.confirm_password_field.get().strip()

        retrieved_username = get_username_from_db(username)
        retrieved_answer = get_answer_from_db(username)

        if self.step == 1:
            
            if retrieved_username is None or username in ['Username must be at least 8 characters']:
                return
            
            self.username_label.place_forget()
            self.username_field.place_forget()
            self.secret_question_label.place(relx=0.28, rely=0.36, anchor="n")
            self.secret_question_field.place(relx=0.5, rely=0.40, anchor="n", width=300, height=50)

            self.step += 1

        elif self.step == 2:
            
            if retrieved_answer != secret_answer:
                print("Answer is incorrect...")
                return

            self.secret_question_label.place_forget()
            self.secret_question_field.place_forget()
            self.new_password_label.place(relx=0.27, rely=0.33, anchor="n")
            self.new_password_field.place(relx=0.5, rely=0.37, anchor="n", width=300, height=50)
            self.confirm_password_label.place(relx=0.30, rely=0.48, anchor="n")
            self.confirm_password_field.place(relx=0.5, rely=0.52, anchor="n", width=300, height=50)
            self.step += 1

            forgot_validator(password, confirm_password)

        elif self.step == 3:

            from pages.LoginPage import LoginPage
            print("Redirecting to Login Page...")  

            self.step = 1 # not sure kung need paba ireset yung steps para sure na pagbalik sa forgot pass page e nasa step 1 ulit yung sequence
            
            self.pack_forget()  
            login_page = LoginPage(self.master, self.shared_state)  
            login_page.pack(fill="both", expand=True)


    def on_cancel_click(self):
        from pages.LoginPage import LoginPage 
        self.pack_forget()  
        login_page = LoginPage(self.master, self.shared_state)  
        login_page.pack(fill="both", expand=True)