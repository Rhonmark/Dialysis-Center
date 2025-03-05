from PIL import Image, ImageTk 
import tkinter as tk
from tkinter import ttk
from components.Inputs import PatientInfoWindow
from pages.AddPatientWindow import AddPatientWindow
from backend.connector import db_connection as db
from components.state import shared_states 

class HomePage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#E8FBFC")
        self.shared_state = shared_state
        self.configure(width=1920, height=1080)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)  
        self.rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, shared_state)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # Main content frame
        self.main_frame = tk.Frame(self, bg="#E8FBFC", width=1600, height=1080)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # Cache pages so they are not recreated every time
        self.pages = {
            "Home": HomePageContent(self.main_frame, self.shared_state),
            "Patient": PatientPage(self.main_frame, self.shared_state),
            "Supply": SupplyPage(self.main_frame, self.shared_state),
            "Report": ReportPage(self.main_frame, self.shared_state),
            "About": AboutPage(self.main_frame, self.shared_state),
            "Settings": SettingsPage(self.main_frame, self.shared_state),
        }

        for page in self.pages.values():
            page.pack(fill="both", expand=True)
            page.pack_forget() 

        self.current_page = None
        self.show_page("Home")

    def show_page(self, page_name):
        """Adds a slight delay to show a transition effect when switching pages."""
        if self.current_page:
            self.current_page.pack_forget()

        # Show a temporary "Loading..." message
        loading_label = tk.Label(self.main_frame, text="Loading...", font=("Arial", 24, "bold"), bg="#E8FBFC")
        loading_label.pack(fill="both", expand=True)

        self.after(10, lambda: self.switch_to_page(page_name, loading_label)) 

    def switch_to_page(self, page_name, loading_label):
        """Replaces loading message with the actual page."""
        loading_label.pack_forget()
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)

class Sidebar(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#1A374D", width=300, height=1080)
        self.place(x=0, y=0)

        # Sidebar Title
        self.title = tk.Label(
            self, 
            text="First Priority\nDialysis Center", 
            font=("Arial", 18, "bold"), 
            fg="white", 
            bg="#1A374D",
            justify="left",
            anchor="w"
        )
        self.title.place(x=102, y=76)

        # Sidebar Logo
        self.logo_img = Image.open("assets/logo.png").convert("RGBA")
        self.logo_img = self.logo_img.resize((80, 80), Image.Resampling.LANCZOS)
        self.logo = ImageTk.PhotoImage(self.logo_img)

        self.logo_label = tk.Label(self, image=self.logo, bg="#1A374D")
        self.logo_label.place(x=16, y=65)  # Adjust position for better layout

        # Sidebar Canvas for Menu
        self.canvas = tk.Canvas(self, bg="#1A374D", width=367, height=800, highlightthickness=0)
        self.canvas.place(x=0, y=150) 

        # Load menu icons
        self.icons = {}
        menu_items = {
            "Home": "assets/home.png",
            "Patient": "assets/patient.png",
            "Supply": "assets/supply.png",
            "Report": "assets/report.png",
            "About": "assets/about.png",
            "Settings": "assets/settings.png"
        }

        for key, path in menu_items.items():
            img = Image.open(path).convert("RGBA")  
            img = img.resize((30, 30), Image.Resampling.LANCZOS)
            self.icons[key] = ImageTk.PhotoImage(img)

        # Adjusted positioning for icon and text
        icon_x = 40    # Icon X position (aligned left)
        text_x = 85    # Move text slightly closer to the icon
        y_offset = 50  # Initial Y position for first menu item

        self.buttons = {}

        for item in menu_items.keys():
            # Full-Width Highlight Background
            bg_rect = self.canvas.create_rectangle(0, y_offset, 367, y_offset + 50, fill="#1A374D", outline="")

            # Create icon (centered vertically)
            icon_id = self.canvas.create_image(icon_x, y_offset + 26, image=self.icons[item], anchor="w")

            # Create text (adjusted vertically)
            text_id = self.canvas.create_text(
                text_x, y_offset + 25,  # Ensures text aligns with icon
                text=item, 
                font=("Arial", 20),  
                fill="white", 
                anchor="w"
            )

            # Click event binding
            self.canvas.tag_bind(bg_rect, "<Button-1>", lambda event, name=item: self.navigate(name))
            self.canvas.tag_bind(icon_id, "<Button-1>", lambda event, name=item: self.navigate(name))
            self.canvas.tag_bind(text_id, "<Button-1>", lambda event, name=item: self.navigate(name))

            # Store references
            self.buttons[item] = {"bg_rect": bg_rect, "icon_id": icon_id, "text_id": text_id}
            y_offset += 70  # Increase spacing for next menu item

        self.highlight_selected("Home")

    def highlight_selected(self, selected):
        """Highlights the full button when selected."""
        for name, elements in self.buttons.items():
            if name == selected:
                self.canvas.itemconfig(elements["bg_rect"], fill="#68EDC6")  # Highlight background
                self.canvas.itemconfig(elements["text_id"], fill="#1A374D")  # Change text color
            else:
                self.canvas.itemconfig(elements["bg_rect"], fill="#1A374D")  # Reset background
                self.canvas.itemconfig(elements["text_id"], fill="white")  # Reset text color

    def navigate(self, page_name):
        """Handles menu navigation."""
        self.highlight_selected(page_name)
        self.master.show_page(page_name)

class HomePageContent(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#E8FBFC")
        label = tk.Label(self, text="Welcome to the Home Page", font=("Arial", 24), bg="#E8FBFC")
        label.pack(pady=100)

class PatientPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#E8FBFC")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14))  
        style.configure("Treeview.Heading", font=("Arial", 35, "bold"))  
        style.configure("Treeview", rowheight=35)  

        button_frame = tk.Frame(self, bg="#E8FBFC")
        button_frame.grid(row=0, column=0, pady=10, padx=20, sticky="w")

        add_button = tk.Button(button_frame, text="Add", font=("Arial", 16, "bold"), width=10, command=self.open_add_window)
        add_button.pack(side="left", padx=5)

        edit_button = tk.Button(button_frame, text="Edit", font=("Arial", 16, "bold"), width=10, command=self.open_edit_window)
        edit_button.pack(side="left", padx=5)

        table_frame = tk.Frame(self, bg="#1A374D", highlightbackground="black", highlightthickness=2)
        table_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        tree_container = tk.Frame(table_frame, bg="black")
        tree_container.pack(fill="both", expand=True, padx=1, pady=1)  

        columns = ("patient_id", "patient_name", "date_registered", "condition", "age", "gender")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12, style="Treeview")

        headers = [
            ("PATIENT ID", 140, 55, 12),
            ("PATIENT NAME", 200, 280, 12),
            ("DATE REGISTERED", 350, 620, 12),
            ("CONDITION", 150, 1000, 12),
            ("AGE", 80, 1240, 12),
            ("GENDER", 120, 1400, 12)
        ]

        header_frame = tk.Frame(table_frame, bg="#1A374D", height=58)
        header_frame.place(x=0, y=0, relwidth=1)

        for text, width, x_pos, y_pos in headers:
            label = tk.Label(header_frame, text=text, font=("Arial", 18, "bold"),
                             bg="#1A374D", fg="white", width=width // 10, anchor="w")
            label.place(x=x_pos, y=y_pos, width=width, height=35)

        for (col_name, width, _, _), col_key in zip(headers, columns):
            self.tree.heading(col_key, text=col_name)
            self.tree.column(col_key, width=width, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Sample Data
        self.populate_table([
            ("001", "John Doe", "2024-03-04", "Stable", "30", "Male"),
            ("002", "Jane Smith", "2024-02-28", "Critical", "45", "Female"),
        ])

    def populate_table(self, data):
        """Populates table with data from the backend."""
        for row in data:
            self.tree.insert("", "end", values=row)

    def open_add_window(self):
        PatientInfoWindow(self)

        # meron akong file (AddPatientWindow.py) example sya para sa pag add nung info into table
        # AddPatientWindow(self, self.add_patient)

    def open_edit_window(self):
        PatientInfoWindow(self)

    def add_patient(self, patient_data):
        """Inserts new patient data into the table."""
        self.tree.insert("", "end", values=patient_data)

class SupplyPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#E8FBFC")
        label = tk.Label(self, text="Supply Page", font=("Arial", 24), bg="#E8FBFC")
        label.pack(pady=100)

        self.shared_state = shared_state 

class ReportPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#E8FBFC")
        label = tk.Label(self, text="Report Page", font=("Arial", 24), bg="#E8FBFC")
        label.pack(pady=100)

        self.shared_state = shared_state 

class AboutPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#E8FBFC")
        label = tk.Label(self, text="About Page", font=("Arial", 24), bg="#E8FBFC")
        label.pack(pady=100)

        self.shared_state = shared_state 

class SettingsPage(tk.Frame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, bg="#E8FBFC")
        self.shared_state = shared_state  

        label = tk.Label(self, text="Settings Page", font=("Arial", 24), bg="#E8FBFC")
        label.pack(pady=100)

        logout_button = tk.Button(self, text="Logout", font=("Arial", 16, "bold"), command=self.logout)
        logout_button.pack(pady=20)

    def db_connection(self):
        connect = db()
        cursor = connect.cursor()
        return connect, cursor

    def logout(self):
        try:
            connect, cursor = self.db_connection()  
            username = shared_states.get('logged_username', None)
            print(username)
            # query = """
            #     SELECT 
            # """   

            cursor.execute("""
                UPDATE sessions
                SET logout_time = NOW()
                WHERE employee_id = ((SELECT employee_id FROM users WHERE username = %s))
            """, (username,))
            connect.commit()
            self.shared_state["navigate"]("LoginPage")  
            print("Logout")
        except Exception as e:
            print("Error with logout: ", e)
        finally:
            connect.close()
            cursor.close()
