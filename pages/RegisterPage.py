import random
import tkinter as tk
import hashlib
from tkinter import ttk
from components.textfields_user_reg import TextField
from PIL import Image, ImageTk
from backend.input_validator import register_validation, null_validator
from components.buttons import CTkButtonSelectable, apply_selected_state
from backend.crud import register_to_db, get_existing_credentials
from backend.connector import db_connection as db
import customtkinter as ctk


class RegisterPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent)

        Title_font = ("Merriweather", 34)
        Header_Font =("Merriweather Sans lgiht", 13 )
        SubTitle_font = ("Merriweather Sans Light" ,15)
        Entry_font = ("Merriweather Sans light" ,12)
        button_font = ("Merriweather Bold",18)
        label_font = ("Merriweather Sans", 14)


        self.columnconfigure(0, weight=2, uniform="group")  
        self.columnconfigure(1, weight=1, uniform="group") 
        self.rowconfigure(0, weight=1)
        self.shared_state = shared_state  

        # Access the selected role
        selected_role = self.shared_state.get("selected_role", "None")
        print(selected_role)

        # Left container 
        left_container = ctk.CTkFrame(self,width=900,height=720)
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
        self.admin_button = CTkButtonSelectable(
            left_container,
            text="Admin",
            selectable=True,
            shared_state=self.shared_state,
            width=250, 
            height=55  
        )
        self.admin_button.place(relx=0.24, rely=0.73, anchor="n") 

        # Staff Button
        self.staff_button = CTkButtonSelectable(
            left_container,
            text="Staff",
            selectable=True,
            shared_state=self.shared_state,
            width=250,  
            height=55   
        )
        self.staff_button.place(relx=0.59, rely=0.73, anchor="n")

        # Apply selected state
        apply_selected_state(self.shared_state, left_container)

        # Right container
        right_container = ctk.CTkFrame(self, fg_color="#1A374D")  
        right_container.grid(row=0, column=1, sticky="nsew")

        # Title label 
        title = ctk.CTkLabel(right_container, text="R E G I S T E R",text_color="#68EDC6", font=Title_font, bg_color="#1A374D")
        title.place(relx=0.5, rely=0, anchor="n", y=50)

        # Subtitle label 
        subtitle = ctk.CTkLabel(
            right_container,
            text="Make sure to create an account first",
            text_color="#FFFFff",
            font=Header_Font,
            bg_color="#1A374D",
              
        )
        subtitle.place(relx=0.5, rely=0.15, anchor="n")

        # Full Name Label
        fullname_label = ctk.CTkLabel(right_container, text="Full Name", font=label_font, text_color="#FFFFFF", bg_color="#1A374D")
        fullname_label.place(relx=0.25, rely=0.2, anchor="n")

        # Full Name Field
        self.fullname_field = ctk.CTkEntry(right_container, placeholder_text="Enter your full name", font=Entry_font, placeholder_text_color="#104E44",text_color="#000000", width=300,height=40,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0)
        self.fullname_field.place(relx=0.5, rely=0.25, anchor="n") 

        #Username Label
        username_label = ctk.CTkLabel(right_container, text="Username", font=label_font,text_color="#FFFFFF", bg_color="#1A374D" )
        username_label.place(relx=0.25, rely=0.32, anchor="n")

        # Username Field
        self.username_field = ctk.CTkEntry(right_container, placeholder_text="Username must be at least 8 characters", font=Entry_font,placeholder_text_color="#104E44",text_color="#000000", width=300,height=40,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0)
        self.username_field.place(relx=0.5, rely=0.37, anchor="n") 

        # Password Label
        password_label = ctk.CTkLabel(right_container, text="Password", font=label_font,text_color="#FFFFFF", bg_color="#1A374D")
        password_label.place(relx=0.25, rely=0.44, anchor="n") 

        # Password Field
        self.password_visible = False 
        self.password_field = ctk.CTkEntry(right_container, placeholder_text="Password must be at least 6 characters",placeholder_text_color="#104E44",text_color="#000000",font=Entry_font, width=300,height=40,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0)
        self.password_field.place(relx=0.5, rely=0.49, anchor="n") 

        # Load eye icons
        self.eye_open_icon = ctk.CTkImage(Image.open("assets/eye_open.png").resize((20, 20)))
        self.eye_closed_icon = ctk.CTkImage(Image.open("assets/eye_closed.png").resize((20, 20)))

        # Eye icon label (Initially Hidden)
        self.eye_label = ctk.CTkLabel(
            master=right_container,
            image=self.eye_closed_icon,
            text="",  # Hide default label text
            cursor="hand2",
            bg_color="#FFFFFF"
        )
        self.eye_label.place_forget()

        # Bind events for toggling
        self.eye_label.bind("<Button-1>", self.toggle_password_visibility)
        self.password_field.bind("<KeyRelease>", self.check_password_input)

        # SecretQuestion Label
        secret_question_label = ctk.CTkLabel(right_container, text="Secret Question", font=label_font, text_color="#FFFFFF", bg_color="#1A374D")
        secret_question_label.place(relx=0.30, rely=0.56, anchor="n") 

        # Secret Question Dropdown
        self.secret_questions = [
            "What is your mother's maiden name?",
            "What was the name of your first pet?",
            "What is the name of your first school?",
            "What is your favorite book?"
        ]

        # Randomly select a question
        self.selected_question = ctk.StringVar(value=random.choice(self.secret_questions))

        # Create the CTkComboBox
        self.secret_question_dropdown = ctk.CTkComboBox(
            master=right_container,
            values=self.secret_questions,
            variable=self.selected_question,
            state="readonly",
            font=("Merriweather Sans", 10),
            text_color="#000000",
            dropdown_text_color="#000000",
            dropdown_fg_color="#fFFFFF",
            dropdown_hover_color="#68EDC6",
            button_color="#68EDC6",
            fg_color="#FFFFFF",
            corner_radius=20,
            bg_color="#1A374D",
            border_width=0,
            width=300, 
            height=30
        )
        self.secret_question_dropdown.place(relx=0.5, rely=0.6, anchor="n")

        # Secret Question Field
        self.secret_question_field = ctk.CTkEntry(right_container, placeholder_text="Enter secret question answer",font=Entry_font, placeholder_text_color="#104E44",text_color="#000000",width=300,height=40,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0, )
        self.secret_question_field.place(relx=0.5, rely=0.65, anchor="n") 

        # Error Label
        self.error_secret_question_label = ctk.CTkLabel(self, text="", font=label_font, text_color="RED", bg_color="#1A374D",height=14)
        self.error_secret_question_label.place(relx=0.84, rely=0.715, anchor="n")

        # Login Button
        login_button = ctk.CTkButton(
            right_container,
            text="Login",
            font=button_font,
            text_color="#FfFFFF",
            command=self.on_login_click,
            width=230,  
            height=50,
            corner_radius=20,
            bg_color="#1A374D",
            fg_color="#68EDC6"
        )
        login_button.place(relx=0.5, rely=0.775, anchor="n")  

        # Signup Button
        signup_button = ctk.CTkButton(
            right_container,
            text="Register",
            font=button_font,
            text_color="#FFFFFF",
            command=self.on_signup_click,
            width=230, 
            height=50,
            corner_radius=20,
            bg_color="#1A374D",
            fg_color="#68EDC6"
        )
        signup_button.place(relx=0.5, rely=0.865, anchor="n")  

    def check_password_input(self, event=None):
        """Shows or hides the eye icon based on user input, ensuring it starts closed."""
        current_text = self.password_field.get().strip()

        if current_text: 
            self.eye_label.place(relx=0.8, rely=0.50, anchor="n") 
            self.password_visible = False 
            self.password_field.configure(show="*")  
            self.eye_label.configure(image=self.eye_closed_icon)  
        else:
            self.eye_label.place_forget()  


    def toggle_password_visibility(self, event=None):
        """Toggles password visibility while maintaining correct icon states."""
        if not self.password_field.get().strip(): 
            return  

        self.password_visible = not self.password_visible  

        if self.password_visible:
            self.password_field.configure(show="")  
            self.eye_label.configure(image=self.eye_open_icon)  
        else:
            self.password_field.configure(show="*")  
            self.eye_label.configure(image=self.eye_closed_icon)  

    def display_error(self, message):
        self.error_secret_question_label.configure(text=message)

    def on_login_click(self):
        self.shared_state["navigate"]("LoginPage")  

    def db_connection():
        connect = db()
        cursor = connect.cursor()
        return connect, cursor

    def on_signup_click(self):
        username = self.username_field.get().strip()
        password = self.password_field.get().strip()
        secret_answer = self.secret_question_field.get().strip()
        full_name = self.fullname_field.get().strip()
        
        fn_val = ' '.join(name.capitalize() for name in full_name.split())

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

            existing_username = get_existing_credentials(username, 'username', table_name='users' )
            if existing_username:
                self.display_error(existing_username)
                return
            
            secret_question = self.selected_question.get().strip()
            hashed_password = hashlib.sha256(password.encode()).hexdigest() 
            hashed_answer = hashlib.sha256(secret_answer.encode()).hexdigest()

            create_user = register_to_db(fn_val, role, username, hashed_password, secret_question, hashed_answer)
            if create_user:
                self.display_error(create_user)
                self.shared_state["navigate"]("LoginPage")  
                return
            self.display_error("")            
            
        except Exception as ve:
            print('Register Page has a problem: ', ve)