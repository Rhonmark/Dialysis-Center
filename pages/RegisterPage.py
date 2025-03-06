import random
import tkinter as tk
import hashlib
from tkinter import ttk
from components.textfields import TextField
from components.buttons import Button
from PIL import Image, ImageTk
from backend.input_validator import register_validation, null_validator
from components.buttons import Button, apply_selected_state
from pages.LoginPage import LoginPage
from backend.crud import register_to_db, get_usernames
from backend.connector import db_connection as db


class RegisterPage(tk.Frame):
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
            shared_state=self.shared_state,
            command=lambda: self.shared_state.update({"selected_role": "Admin"})
        )
        self.admin_button.place(relx=0.24, rely=0.73, anchor="n", width=250, height=55) 

        # Staff Button
        self.staff_button = Button(
            left_container,
            text="Staff", 
            selectable=True,
            shared_state=self.shared_state,
            command=lambda: self.shared_state.update({"selected_role": "Staff"})
        )
        self.staff_button.place(relx=0.59, rely=0.73, anchor="n", width=250, height=55) 

        apply_selected_state(shared_state, left_container)

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

        # Password Label
        password_label = tk.Label(right_container, text="Password", font=("Arial", 12), fg="white", bg="#1A374D")
        password_label.place(relx=0.23, rely=0.38, anchor="n") 

        # Password Field
        self.password_visible = False 
        self.password_field = TextField(right_container, placeholder="Password must be at least 6 characters", font=("Arial", 12), width=25)
        self.password_field.place(relx=0.5, rely=0.42, anchor="n", width=300, height=50) 

        # Load eye icons
        self.eye_open_icon = ImageTk.PhotoImage(Image.open("assets/eye_open.png").resize((20, 20)))
        self.eye_closed_icon = ImageTk.PhotoImage(Image.open("assets/eye_closed.png").resize((20, 20)))

        # Eye icon label (Initially Hidden)
        self.eye_label = tk.Label(right_container, image=self.eye_closed_icon, cursor="hand2", borderwidth=0, highlightthickness=0)
        self.eye_label.place_forget()  

        # Bind events for toggling
        self.eye_label.bind("<Button-1>", self.toggle_password_visibility)
        self.password_field.bind("<KeyRelease>", self.check_password_input)

        # SecretQuestion Label
        secret_question_label = tk.Label(right_container, text="Secret Question", font=("Arial", 12), fg="white", bg="#1A374D")
        secret_question_label.place(relx=0.28, rely=0.52, anchor="n") 

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
        self.secret_question_dropdown.place(relx=0.5, rely=0.56, anchor="n", width=300, height=30)

        # Secret Question Field
        self.secret_question_field = TextField(right_container, placeholder="Enter secret question answer", font=("Arial", 12), width=25)
        self.secret_question_field.place(relx=0.5, rely=0.62, anchor="n", width=300, height=50) 

        # Error Label
        self.error_secret_question_label = tk.Label(self, text="", font=("Arial", 12), fg="red", bg="#1A374D")
        self.error_secret_question_label.place(relx=0.84, rely=0.71, anchor="n")

         # Add Login Button
        login_button = Button(right_container, text="Login", command=self.on_login_click)
        login_button.place(relx=0.5, rely=0.77, anchor="n", width=230, height=50)

        # Add Signup Button
        signup_button = Button(right_container, text="Register", command=self.on_signup_click)
        signup_button.place(relx=0.5, rely=0.86, anchor="n", width=230, height=50)

    def check_password_input(self, event=None):
        """Shows or hides the eye icon based on user input, ensuring it starts closed."""
        current_text = self.password_field.get().strip()

        if current_text: 
            self.eye_label.place(relx=0.8, rely=0.44, anchor="n") 
            self.password_visible = False 
            self.password_field.config(show="*")  
            self.eye_label.config(image=self.eye_closed_icon)  
        else:
            self.eye_label.place_forget()  


    def toggle_password_visibility(self, event=None):
        """Toggles password visibility while maintaining correct icon states."""
        if not self.password_field.get().strip(): 
            return  

        self.password_visible = not self.password_visible  

        if self.password_visible:
            self.password_field.config(show="")  
            self.eye_label.config(image=self.eye_open_icon)  
        else:
            self.password_field.config(show="*")  
            self.eye_label.config(image=self.eye_closed_icon)  

    def display_error(self, message):
        self.error_secret_question_label.config(text=message)

    def on_login_click(self):
        self.shared_state["navigate"]("LoginPage")  
        self.pack_forget()

    def db_connection():
        connect = db()
        cursor = connect.cursor()
        return connect, cursor

    def on_signup_click(self):
        username = self.username_field.get().strip()
        password = self.password_field.get().strip()
        secret_answer = self.secret_question_field.get().strip()
        
        try: 
            role = self.shared_state.get("selected_role", 'None')
            if not role:
                self.display_error("Choose between Admin or Staff!")
                return
            
            validation_result = register_validation(username, password, secret_answer)
            if validation_result:
                self.display_error(validation_result)
                return
            
            if null_validator(username, password, secret_answer):
                self.display_error("All fields are required!")
                return

            existing_username = get_usernames(username)
            if existing_username:
                self.display_error(existing_username)
                return
            
            secret_question = self.selected_question.get().strip()
            hashed_password = hashlib.sha256(password.encode()).hexdigest() 
            hashed_answer = hashlib.sha256(secret_answer.encode()).hexdigest()
            create_user = register_to_db(role, username, hashed_password, secret_question, hashed_answer)
            if create_user:
                self.display_error(create_user)

                self.shared_state["navigate"]("LoginPage")  
                self.pack_forget()
                return
            self.display_error("")            
            

        except Exception as ve:
            print('Register Page has a problem: ', ve)

