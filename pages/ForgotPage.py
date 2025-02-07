import tkinter as tk
from components.textfields import TextField
from components.buttons import Button
from PIL import Image, ImageTk

class ForgotPage(tk.Frame):
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
        title = tk.Label(right_container, text="FORGOT\nPASSWORD", font=("Arial", 30, "bold"), fg="#68EDC6", bg="#1A374D", justify= "center")
        title.place(relx=0.5, rely=0, anchor="n", y=50)

        # Secret Question label
        secret_question_label = tk.Label(right_container, text="Secret Question", font=("Arial", 12), fg="white", bg="#1A374D")
        secret_question_label.place(relx=0.49, rely=0.41, anchor="n") 

        # Secret Question Answer Field
        secret_question_field = TextField(right_container, placeholder="Enter secret question answer", font=("Arial", 12), width=25)
        secret_question_field.place(relx=0.5, rely=0.45, anchor="n", width=300, height=50) 

        # Enter Button
        enter_button = Button(right_container, text="Enter", command=self.on_enter_click)
        enter_button.place(relx=0.5, rely=0.71, anchor="n", width=230, height=50)

        # Cancel Button
        cancel_button = Button(right_container, text="Cancel", command=self.on_cancel_click)
        cancel_button.place(relx=0.5, rely=0.8, anchor="n", width=230, height=50)

    def on_enter_click(self):
        print("Enter button clicked")

    def on_cancel_click(self):
        from pages.LoginPage import LoginPage 
        self.pack_forget()  
        login_page = LoginPage(self.master)  
        login_page.pack(fill="both", expand=True)
