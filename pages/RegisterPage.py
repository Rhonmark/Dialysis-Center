import random
import tkinter as tk
import hashlib
from tkinter import ttk
from components.textfields import TextField
from components.buttons import Button
from PIL import Image, ImageTk
from backend.connector import db_connection as db
from backend.input_validator import register_validation, register_to_db, null_validator


class RegisterPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columnconfigure(0, weight=2, uniform="group")  
        self.columnconfigure(1, weight=1, uniform="group") 
        self.rowconfigure(0, weight=1)

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
        admin_button = Button(
            left_container, 
            text="Admin", 
        )
        admin_button.place(relx=0.24, rely=0.73, anchor="n", width=250, height=55) 

        # Staff Button
        staff_button = Button(
            left_container,
            text="Staff", 
        )
        staff_button.place(relx=0.59, rely=0.73, anchor="n", width=250, height=55) 

        # Right container
        right_container = tk.Frame(self, bg="#1A374D")  
        right_container.grid(row=0, column=1, sticky="nsew")

        # Title label 
        title = tk.Label(right_container, text="REGISTER", font=("Arial", 36, "bold"), fg="#68EDC6", bg="#1A374D")
        title.place(relx=0.5, rely=0, anchor="n", y=50)

        # Subtitle label 
        subtitle = tk.Label(
            right_container,
            text="Make sure to create an\naccount first",
            font=("Arial", 11),
            fg="white",
            bg="#1A374D",
            wraplength=250  
        )
        subtitle.place(relx=0.5, rely=0.15, anchor="n")

        #Username Label
        username_label = tk.Label(right_container, text="Username", font=("Arial", 12), fg="white", bg="#1A374D")
        username_label.place(relx=0.23, rely=0.24, anchor="n")

        # Username Field
        self.username_field = TextField(right_container, placeholder="Username must be at least 8 characters", font=("Arial", 12), width=25)
        self.username_field.place(relx=0.5, rely=0.28, anchor="n", width=300, height=50)  

        #Password Label
        password_label = tk.Label(right_container, text="Password", font=("Arial", 12), fg="white", bg="#1A374D")
        password_label.place(relx=0.23, rely=0.37, anchor="n") 

        # Password Field
        self.password_field = TextField(right_container, placeholder="Password must be at least 6 characters", font=("Arial", 12), width=25)
        self.password_field.place(relx=0.5, rely=0.41, anchor="n", width=300, height=50) 

        #SecretQuestion Label
        secret_question_label = tk.Label(right_container, text="Secret Question", font=("Arial", 12), fg="white", bg="#1A374D")
        secret_question_label.place(relx=0.28, rely=0.5, anchor="n") 

        # Secret Question Dropdown
        self.secret_questions = [
            "What is your mother's maiden name?",
            "What is your Father's maiden name?",
            "What was the name of your first pet?",
            "What is the name of your first school?",
            "What is your favorite book?"
        ]

        # Randomly select a question
        self.selected_question = tk.StringVar(value=random.choice(self.secret_questions))

        # Dropdown menu (Combobox)
        self.secret_question_dropdown = ttk.Combobox(right_container, textvariable=self.selected_question, values=self.secret_questions, state="readonly", font=("Arial", 12))
        self.secret_question_dropdown.place(relx=0.5, rely=0.53, anchor="n", width=300, height=30)

        # Secret Question Field
        self.secret_question_field = TextField(right_container, placeholder="Enter secret question answer", font=("Arial", 12), width=25)
        self.secret_question_field.place(relx=0.5, rely=0.59, anchor="n", width=300, height=50) 

         # Add Login Button
        login_button = Button(right_container, text="Login", command=self.on_login_click)
        login_button.place(relx=0.5, rely=0.71, anchor="n", width=230, height=50)

        # Add Signup Button
        signup_button = Button(right_container, text="Register", command=self.on_signup_click)
        signup_button.place(relx=0.5, rely=0.8, anchor="n", width=230, height=50)

    def on_login_click(self):
        from pages.LoginPage import LoginPage 
        self.pack_forget()  
        register_page = LoginPage(self.master)  
        register_page.pack(fill="both", expand=True) 
        
    def on_signup_click(self):
        username = self.username_field.get().strip()
        password = self.password_field.get().strip()
        secret_answer = self.secret_question_field.get().strip()

        if null_validator(username, password, secret_answer):
            return
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        validation_result = register_validation(username, password, secret_answer)


        if validation_result:
            print(validation_result)
            return      
    
        register_to_db(username, hashed_password, secret_answer)
