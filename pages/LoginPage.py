import tkinter as tk
import hashlib
from components.textfields_user_reg import TextField
from components.buttons import Button
from PIL import Image, ImageTk
from backend.input_validator import login_validation
from backend.crud import get_password_from_db, get_role, get_usernames
from components.buttons import Button, apply_selected_state
from backend.connector import db_connection as db
from components.state import shared_states

class LoginPage(tk.Frame):
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
            image = Image.open("assets/bg.png").convert("RGBA").resize((900, 720))
            self.bg_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        except Exception:
            self.canvas.create_text(450, 355, text="Error loading image", fill="red", font=("Arial", 16))

        # logo
        try:
            logo_image = Image.open("assets/logo.png").convert("RGBA").resize((130, 130))
            self.logo_icon = ImageTk.PhotoImage(logo_image)
            self.canvas.create_image(150, 71, anchor="n", image=self.logo_icon)
        except Exception:
            self.canvas.create_text(450, 100, text="Error loading logo", fill="red", font=("Arial", 12))

        self.canvas.create_text(
            340, 230, text="Welcome to,\nFirst Priority Dialysis Center",
            font=("Arial", 29, "bold"), fill="black", anchor="n"
        )
        self.canvas.create_text(
            290, 330, text="Where needs are always met.",
            font=("Arial", 25), fill="black", anchor="n"
        )

        self.canvas.create_text(
            370, 385,  
            text="Designed to streamline and manage all essential supplies. \nEnsuring that resources are readily available, accurately tracked, \nand organized to support the center's commitment to high-\nquality patient care.",
            font=("Arial", 15),
            fill="black", 
            anchor="n"  
        )

        # Admin Button
        self.admin_button = Button(left_container, text="Admin", selectable=True, shared_state=self.shared_state, command=lambda: self.shared_state.update({"selected_role": "Admin"}))
        self.admin_button.place(relx=0.24, rely=0.73, anchor="n", width=250, height=55)

        # Staff Button
        self.staff_button = Button(left_container, text="Staff", selectable=True, shared_state=self.shared_state, command=lambda: self.shared_state.update({"selected_role": "Staff"}))
        self.staff_button.place(relx=0.59, rely=0.73, anchor="n", width=250, height=55)

        apply_selected_state(shared_state, left_container)

        # Right container
        right_container = tk.Frame(self, bg="#1A374D")  
        right_container.grid(row=0, column=1, sticky="nsew")

        # Title label 
        title = tk.Label(right_container, text="LOGIN", font=("Arial", 36, "bold"), fg="#68EDC6", bg="#1A374D")
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

        # Username Label
        username_label = tk.Label(right_container, text="Username", font=("Arial", 12), fg="white", bg="#1A374D")
        username_label.place(relx=0.23, rely=0.35, anchor="n")
        self.username_field = TextField(right_container, placeholder="Username must be at least 8 characters", font=("Arial", 12), width=25)
        self.username_field.place(relx=0.5, rely=0.39, anchor="n", width=300, height=50)

        # Password Label
        password_label = tk.Label(right_container, text="Password", font=("Arial", 12), fg="white", bg="#1A374D")
        password_label.place(relx=0.23, rely=0.48, anchor="n") 

        # Password Field
        self.password_visible = False 
        self.password_field = TextField(right_container, placeholder="Password must be at least 6 characters", font=("Arial", 12), width=25)
        self.password_field.place(relx=0.5, rely=0.52, anchor="n", width=300, height=50)

        # Load eye icons
        self.eye_open_icon = ImageTk.PhotoImage(Image.open("assets/eye_open.png").resize((20, 20)))
        self.eye_closed_icon = ImageTk.PhotoImage(Image.open("assets/eye_closed.png").resize((20, 20)))

        # Eye icon label (Initially Hidden)
        self.eye_label = tk.Label(right_container, image=self.eye_closed_icon, cursor="hand2", borderwidth=0, highlightthickness=0)
        self.eye_label.place_forget() 

        # Bind events for toggling
        self.eye_label.bind("<Button-1>", self.toggle_password_visibility)
        self.password_field.bind("<KeyRelease>", self.check_password_input)

        # Forgot Password
        forgot_password_label = tk.Label(
            right_container,
            text="Forgot Password?",
            font=("Arial", 12,),
            fg="white",
            bg="#1A374D",
            cursor="hand2"
        )
        forgot_password_label.place(relx=0.7, rely=0.591, anchor="n") 
        forgot_password_label.bind("<Button-1>", self.on_forgot_password_click)

        # Error Label
        self.error_label = tk.Label(right_container, text="", font=("Arial", 12), fg="red", bg="#1A374D")
        self.error_label.place(relx=0.5, rely=0.65, anchor="n")

        # Login Button
        login_button = Button(right_container, text="Login", command=self.on_login_click)
        login_button.place(relx=0.5, rely=0.71, anchor="n", width=230, height=50)

        # Signup Button
        signup_button = Button(right_container, text="Register", command=self.on_signup_click)
        signup_button.place(relx=0.5, rely=0.8, anchor="n", width=230, height=50)

    def check_password_input(self, event=None):
        """Shows or hides the eye icon based on user input, ensuring it starts closed."""
        current_text = self.password_field.get().strip()

        if current_text:  
            self.eye_label.place(relx=0.8, rely=0.54, anchor="n")  
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
        self.error_label.config(text=message)

    def db_connection(self):
        connect = db()
        cursor = connect.cursor()
        return connect, cursor

    def on_login_click(self):
        username = self.username_field.get().strip()
        shared_states['logged_username'] = username    
        password = self.password_field.get().strip()
        user_role = get_role(username)
        selected_role = self.shared_state.get("selected_role", None)  
        stored_user_password = get_password_from_db(username)
        existing_username = get_usernames(username)
        
        try:
            connect, cursor = self.db_connection()
            
            if not selected_role:
                self.display_error("Choose between Admin or Staff!")
                return
            
            validation_result = login_validation(username, password)
            if validation_result:
                self.display_error(validation_result)
                return
            
            if not existing_username:
                self.display_error("Username not found")
                return
            
            if user_role != selected_role:
                self.display_error("Check your roles (Admin or Staff)")
                return

            hash_password = hashlib.sha256(password.encode()).hexdigest()
            if hash_password == stored_user_password:
                
                cursor.execute("""
                    INSERT INTO sessions(employee_id)
                    VALUES ((SELECT employee_id FROM users WHERE username = %s))
                """, (username,)) 
                connect.commit()

                self.display_error("You have successfully logged in")
                print("This is your username state: ", shared_states)
                self.after(2000, lambda: self.shared_state["navigate"]("HomePage"))
            else:
                self.display_error("Invalid Password")

        except Exception as e:
            print(f'Login Page has a problem: ', e)

        finally:
            connect.close()
            cursor.close()

    def on_signup_click(self):
        self.shared_state["navigate"]("RegisterPage")  
        self.pack_forget()  

    def on_forgot_password_click(self, event):
        self.shared_state["navigate"]("ForgotPage") 
        self.pack_forget()  
