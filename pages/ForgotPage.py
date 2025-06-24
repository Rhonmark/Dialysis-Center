import random
import tkinter as tk
from tkinter import ttk
from components.textfields_user_reg import TextField
from PIL import Image, ImageTk
from backend.input_validator import forgot_validator
from backend.crud import get_login_credentials, set_new_password
from components.buttons import CTkButtonSelectable, apply_selected_state
import hashlib
import customtkinter as ctk


class ForgotPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent)

        Title_font = ("Merriweather", 34)
        Header_Font =("Merriweather Sans light",13 )
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
        
        # Left container 
        left_container = ctk.CTkFrame(self)
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
        except Exception:
            self.canvas.create_text(450, 355, text="Error loading image", fill="red", font=("Arial", 16))

        # logo
        try:
            logo_path = "assets/logo.png" 
            logo_image = Image.open(logo_path).convert("RGBA")  
            logo_image = logo_image.resize((130, 130))  
            self.logo_icon = ImageTk.PhotoImage(logo_image)

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
        title = ctk.CTkLabel(right_container, text="F O R G O T\nP A S S W O R D", font=Title_font, text_color="#68EDC6", bg_color="#1A374D", justify="center")
        title.place(relx=0.5, rely=0, anchor="n", y=50)

        # Step tracking
        self.step = 1

        # Username Label & Field
        self.username_label = ctk.CTkLabel(right_container, text="Username", font=label_font, text_color="white", bg_color="#1A374D")
        self.username_label.place(relx=0.23, rely=0.36, anchor="n")
        self.username_field = ctk.CTkEntry(right_container, placeholder_text="Username must be at least 8 characters", font=Entry_font,placeholder_text_color="#104E44",text_color="#000000", width=300,height=40,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0)
        self.username_field.place(relx=0.5, rely=0.41, anchor="n")  
        
        # Secret Question & Answer Fields (Initially Hidden)
        self.secret_question_label = ctk.CTkLabel(right_container, text="Secret Question", font=label_font, text_color="white", bg_color="#1A374D")
        self.secret_question_field = ctk.CTkEntry(right_container, placeholder_text="Enter secret question answer",  font=Entry_font,placeholder_text_color="#104E44",text_color="#000000", width=300,height=40,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0)
        
        # New Password Fields (Initially Hidden)
        self.new_password_label = ctk.CTkLabel(right_container, text="New Password", font=label_font, text_color="white", bg_color="#1A374D")
        self.new_password_field = ctk.CTkEntry(right_container, placeholder_text="Enter new password",  font=Entry_font,placeholder_text_color="#104E44",text_color="#000000", width=300,height=50,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0)
        self.confirm_password_label = ctk.CTkLabel(right_container, text="Confirm Password", font=label_font, text_color="white", bg_color="#1A374D")
        self.confirm_password_field = ctk.CTkEntry(right_container, placeholder_text="Confirm new password", font=Entry_font,placeholder_text_color="#104E44",text_color="#000000", width=300,height=40,corner_radius=15,bg_color="#1A374D",fg_color="#FFFFFF",border_width=0)

        # Error label
        self.error_label = ctk.CTkLabel(right_container, text="", font=label_font, text_color="red", bg_color="#1A374D")
        self.error_label.place(relx=0.5, rely=0.64, anchor="n")
        
        # Enter Button
        self.enter_button = ctk.CTkButton(
            right_container,
            text="Enter",
            font=button_font,
            text_color="#FfFFFF",
            command=self.on_enter_click,
            width=230,  
            height=50,
            corner_radius=20,
            bg_color="#1A374D",
            fg_color="#68EDC6"
        )
        self.enter_button.place(relx=0.5, rely=0.71, anchor="n")

        # Cancel Button
        self.cancel_button = ctk.CTkButton(
            right_container,
            text="Cancel",
            font=button_font,
            text_color="#FfFFFF",
            command=self.on_cancel_click,
            width=230,  
            height=50,
            corner_radius=20,
            bg_color="#1A374D",
            fg_color="#68EDC6"
        )
        self.cancel_button.place(relx=0.5, rely=0.8, anchor="n")
        self.on_cancel_click

    def display_error(self, message):
        self.error_label.configure(text=message)

    def on_enter_click(self):
        username = self.username_field.get().strip()
        secret_answer = self.secret_question_field.get().strip()
        password = self.new_password_field.get().strip()
        confirm_password = self.confirm_password_field.get().strip()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        retrieved_username = get_login_credentials(username, target_data="username")
        retrieved_question = get_login_credentials(username, target_data="secret_question")
        retrieved_answer = get_login_credentials(username, target_data="secret_answer")
        hashed_answer = hashlib.sha256(secret_answer.encode()).hexdigest()

        try: 
            if self.step == 1:
                if not retrieved_username or username in ['Username must be at least 8 characters']:
                    self.error_label.configure(text="Invalid username!")
                    return
                self.error_label.configure(text="")
                self.secret_question_label.configure(text=f"Secret Question: \n{retrieved_question}")
                self.username_label.place_forget()
                self.username_field.place_forget()
                self.secret_question_label.place(relx=0.5, rely=0.4, anchor="center")
                self.secret_question_field.place(relx=0.5, rely=0.475, anchor="center")
                self.step += 1
                
            elif self.step == 2:
                if retrieved_answer != hashed_answer:
                    self.error_label.configure(text="Incorrect answer!")
                    return
                self.error_label.configure(text="")
                self.secret_question_label.place_forget()
                self.secret_question_field.place_forget()
                self.new_password_label.place(relx=0.27, rely=0.33, anchor="n")
                self.new_password_field.place(relx=0.5, rely=0.37, anchor="n")
                self.confirm_password_label.place(relx=0.30, rely=0.48, anchor="n")
                self.confirm_password_field.place(relx=0.5, rely=0.52, anchor="n")
                self.step += 1

            elif self.step == 3:
                
                forgot_result = forgot_validator(password, confirm_password)
                if forgot_result:
                    self.error_label.configure(text=forgot_result)
                    return  

                set_new_password(hashed_password, username)

                self.shared_state["navigate"]("LoginPage") 
                self.error_label.configure(text="")
                self.step = 1
                self.pack_forget()
        except Exception as e:
            print("Error with forgot password: ", e)


    def on_cancel_click(self):
        self.shared_state["navigate"]("LoginPage") 
        self.pack_forget()  

