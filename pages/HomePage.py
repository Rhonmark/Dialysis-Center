import customtkinter as ctk
from PIL import Image
from tkinter import ttk, messagebox
from components.Inputs import PatientInfoWindow
from components.outputs_patient import ContactInfoRelativeInfo, ContactOptionsPanel, FamilyHistory, Medication, OtherHistory, PatientHistory, PatientInfo, PatientPhoto, PhilHealthAndOtherInfo

from backend.connector import db_connection as db
from components.state import shared_states
from backend.crud import retrieve_form_data

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state
        self.configure(width=1920, height=1080)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, shared_state)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.main_frame = ctk.CTkFrame(self, fg_color="#E8FBFC", width=1600, height=1080)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.pages = {
            "Home": HomePageContent(self.main_frame),
            "Patient": PatientPage(self.main_frame, shared_state),
            "Supply": SupplyPage(self.main_frame),
            "Report": ReportPage(self.main_frame),
            "About": AboutPage(self.main_frame),
            "Settings": SettingsPage(self.main_frame, self.shared_state),
        }

        for page in self.pages.values():
            page.pack(fill="both", expand=True)
            page.pack_forget()

        self.current_page = None
        self.show_page("Home")

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.pack_forget()

        loading_label = ctk.CTkLabel(self.main_frame, text="Loading...", font=("Arial", 24, "bold"))
        loading_label.pack(fill="both", expand=True)

        self.after(10, lambda: self.switch_to_page(page_name, loading_label))

    def switch_to_page(self, page_name, loading_label):
        loading_label.pack_forget()
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)

        if page_name == "Patient":
            self.pages["Patient"].show_table_view()

class NavbarTop(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white", height=130)
        self.pack(fill="x", side="top")
        self.pack_propagate(False)
        self.configure(border_width=0, border_color="black") 

        self.welcome_label = ctk.CTkLabel(self, text="Welcome Back, !", text_color="black", font=("Arial", 30, "bold"))
        self.welcome_label.place(relx=0.2, rely=0.5, anchor="e")

        profile_img = ctk.CTkImage(light_image=Image.open("assets/profile.png"), size=(42, 42))
        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))
        search_img = ctk.CTkImage(light_image=Image.open("assets/search.png"), size=(42, 42))
        search_img = ctk.CTkImage(light_image=Image.open("assets/Calendar.png"), size=(42, 42))  

        icon_y = 75 

        profile_btn = ctk.CTkButton(self, image=profile_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5")
        profile_btn.place(relx=1.0, x=-60, y=icon_y, anchor="center")

        notif_btn = ctk.CTkButton(self, image=notif_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5")
        notif_btn.place(relx=1.0, x=-110, y=icon_y, anchor="center")

        settings_btn = ctk.CTkButton(self, image=settings_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5")
        settings_btn.place(relx=1.0, x=-160, y=icon_y, anchor="center")

        self.bottom_line = ctk.CTkFrame(self, height=1.5, fg_color="black")
        self.bottom_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#1A374D", width=300, corner_radius=0)
        self.grid_propagate(False)
        self.shared_state = shared_state

        self.title = ctk.CTkLabel(
            self,
            text="First Priority\nDialysis Center",
            font=("Arial", 18, "bold"),
            text_color="white",
            anchor="w",
            justify="left"
        )
        self.title.place(x=102, y=76)

        logo_img = Image.open("assets/logo.png").resize((80, 80))
        self.logo = ctk.CTkImage(light_image=logo_img, size=(80, 80))
        logo_label = ctk.CTkLabel(self, image=self.logo, text="", fg_color="#1A374D")
        logo_label.place(x=16, y=65)

        self.menu_items = {
            "Home": "assets/home.png",
            "Patient": "assets/patient.png",
            "Supply": "assets/supply.png",
            "Report": "assets/report.png",
            "About": "assets/about.png",
            "Settings": "assets/settings.png"
        }
        self.buttons = {}
        y_offset = 170

        for name, icon_path in self.menu_items.items():
            icon_img = Image.open(icon_path).resize((30, 30))
            icon = ctk.CTkImage(light_image=icon_img, size=(30, 30))
            button = ctk.CTkButton(
                self,
                text=name,
                image=icon,
                anchor="w",
                width=260,
                height=50,
                font=("Arial", 18),
                fg_color="#1A374D",
                text_color="white",
                hover_color="#68EDC6",
                command=lambda name=name: self.navigate(name)
            )
            button.place(x=20, y=y_offset)
            self.buttons[name] = button
            y_offset += 60

        self.highlight_selected("Home")

    def highlight_selected(self, selected):
        for name, button in self.buttons.items():
            if name == selected:
                button.configure(fg_color="#68EDC6", text_color="#1A374D")
            else:
                button.configure(fg_color="#1A374D", text_color="white")

    def navigate(self, page_name):
        if self.master.shared_state.get("modal_open"):
            print("Modal is open, cannot navigate.")
            return

        self.highlight_selected(page_name)
        self.master.show_page(page_name)

class HomePageContent(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")

        navbar = NavbarTop(self)

class PatientPage(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        style.map("Treeview", background=[("selected", "#68EDC6")])

        self.hovered_row = None

        self.button_frame = ctk.CTkFrame(self, fg_color="#E8FBFC")

        self.add_button = ctk.CTkButton(self.button_frame, text="Add", font=ctk.CTkFont("Arial", 16, "bold"),
                                         width=120, command=self.open_add_window)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = ctk.CTkButton(self.button_frame, text="Edit", font=ctk.CTkFont("Arial", 16, "bold"),
                                          width=120, command=self.open_edit_window)
        self.edit_button.pack(side="left", padx=5)

        self.table_frame = ctk.CTkFrame(self, fg_color="#1A374D", border_width=2, border_color="black")

        tree_container = ctk.CTkFrame(self.table_frame, fg_color="black")
        tree_container.pack(fill="both", expand=True, padx=1, pady=1)

        columns = ("patient_id", "patient_name", "age", "gender", "type_of_access", "date_registered")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        self.tree.pack(side="left", fill="both", expand=True)

        headers = [
            ("PATIENT ID", 140),
            ("PATIENT NAME", 200),
            ("AGE", 80),
            ("GENDER", 120),
            ("TYPE OF ACCESS", 180),
            ("DATE REGISTERED", 250)
        ]

        for (text, width), col in zip(headers, columns):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ctk.CTkScrollbar(tree_container, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("hover", background="#68EDC6")
        self.tree.bind("<Motion>", self.on_hover)
        self.tree.bind("<Leave>", self.on_leave)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)

        self.detailed_info_frame = ctk.CTkFrame(self, fg_color="#E8FBFC")

        self.back_button = ctk.CTkButton(self.detailed_info_frame, text="Back", font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50", 
            command=self.show_table_view)
        self.back_button.place(x=10, y=10)

        self.upload_button = ctk.CTkButton(self.detailed_info_frame, text="Upload Photo", font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#00C88D",
            hover_color="#013B50")
        self.upload_button.place(x=700, y=10)

        self.edit_button_detailed = ctk.CTkButton(self.detailed_info_frame, text="Edit Details", font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50")
        self.edit_button_detailed.place(x=1050, y=10)

        self.patienphoto_widget = PatientPhoto(self.detailed_info_frame)
        self.patienphoto_widget.place(x=70, y=80)

        self.patientinfo_widget = PatientInfo(self.detailed_info_frame)
        self.patientinfo_widget.place(x=600, y=80)

        self.optionpanel_widget = ContactOptionsPanel(self.detailed_info_frame)
        self.optionpanel_widget.place(x=70, y=530)

        self.philotherinfo_widget = PhilHealthAndOtherInfo(self.detailed_info_frame)
        self.philotherinfo_widget.place(x=600, y=630)

        self.button_frame.place(x=20, y=10, anchor="nw")
        self.table_frame.place(x=20, y=60, relwidth=0.95, relheight=0.8)
        self.populate_table(self.fetch_patient_data())

    def fetch_patient_data(self):
        try:
            connect = db()
            cursor = connect.cursor()
            cursor.execute("""
                SELECT patient_id, patient_name, age, gender, access_type, date_registered
                FROM patient_list
            """)
            return cursor.fetchall()
        except Exception as e:
            print("Error fetching patient data:", e)
            return []

    def populate_table(self, data):
        for row in data:
            self.tree.insert("", "end", values=row)

    def on_hover(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id != self.hovered_row:
            if self.hovered_row:
                self.tree.item(self.hovered_row, tags=())
            if row_id:
                self.tree.item(row_id, tags=("hover",))
            self.hovered_row = row_id

    def on_leave(self, event):
        if self.hovered_row:
            self.tree.item(self.hovered_row, tags=())
        self.hovered_row = None

    def on_row_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            patient_data = self.tree.item(item_id, 'values')
            patient_id = patient_data[0]
            print(f"Fetching details for Patient ID: {patient_id}")
            self.show_detailed_info(patient_id)

    def show_detailed_info(self, patient_id):
        self.table_frame.place_forget()
        self.button_frame.place_forget()
        detailed_data = self.get_patient_details_from_db(patient_id)
        if detailed_data:
            print(f"Detailed data for Patient ID {patient_id}: {detailed_data}")
            self.patientinfo_widget.update_info(detailed_data)
            self.detailed_info_frame.place(x=20, y=20, relwidth=0.95, relheight=0.95) 
        else:
            self.detailed_info_frame.place(x=20, y=20, relwidth=0.95, relheight=0.95) 

    def show_table_view(self):
        self.detailed_info_frame.place_forget()
        self.button_frame.place(x=20, y=10, anchor="nw") 
        self.table_frame.place(x=20, y=60, relwidth=0.95, relheight=0.8) 

    def get_patient_details_from_db(self, patient_id):
        try:
            connect = db()
            cursor = connect.cursor()
            cursor.execute("""
                SELECT * FROM patient_list WHERE patient_id = %s
            """, (patient_id,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            print("Error fetching patient details:", e)
            return None
        finally:
            if connect:
                connect.close()

    def update_detailed_info_display(self, data):
        self.detailed_info_label.configure(text=f"Detailed Information:\n{data}")

    def open_input_window(self, window_class, data=None):
        input_window = window_class(self.master, data or {})
        input_window.grab_set()
        input_window.focus_force()

        def on_close():
            input_window.destroy()

        input_window.protocol("WM_DELETE_WINDOW", on_close)
        self.wait_window(input_window)
        self.refresh_table()
        self.enable_buttons()

    def refresh_table(self):
        self.detailed_info_frame.place_forget() 
        self.button_frame.place(x=20, y=10, anchor="nw") 
        self.table_frame.place(x=20, y=60, relwidth=0.95, relheight=0.8) 
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.populate_table(self.fetch_patient_data())

    def enable_buttons(self):
        self.add_button.configure(state="normal")
        self.edit_button.configure(state="normal")

    def disable_buttons(self):
        self.add_button.configure(state="disabled")
        self.edit_button.configure(state="disabled")

    def open_add_window(self, data=None):
        self.disable_buttons()
        self.open_input_window(PatientInfoWindow, data)

    def open_edit_window(self, data=None):
        self.disable_buttons()
        self.open_input_window(PatientInfoWindow, data)

class SupplyPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")
        label = ctk.CTkLabel(self, text="Supply Page", font=("Arial", 24))
        label.pack(pady=100)

class ReportPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")
        label = ctk.CTkLabel(self, text="Report Page", font=("Arial", 24))
        label.pack(pady=100)

class AboutPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")
        label = ctk.CTkLabel(self, text="About Page", font=("Arial", 24))
        label.pack(pady=100)

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state

        label = ctk.CTkLabel(self, text="Settings Page", font=ctk.CTkFont(size=24, weight="bold"), text_color="black")
        label.pack(pady=100)

        logout_button = ctk.CTkButton(self, text="Logout", font=ctk.CTkFont(size=16, weight="bold"), command=self.logout)
        logout_button.pack(pady=20)

    def db_connection(self):
        connect = db()
        cursor = connect.cursor()
        return connect, cursor

    def logout(self):
        try:
            connect, cursor = self.db_connection()
            username = shared_states.get('logged_username', None)

            cursor.execute("""
                UPDATE sessions
                SET logout_time = NOW()
                WHERE employee_id = ((SELECT employee_id FROM users WHERE username = %s))
            """, (username,))
            connect.commit()

            cursor.execute("""
                SELECT s.employee_id, s.login_time, s.logout_time
                FROM sessions s
                LEFT JOIN users u ON s.employee_id = u.employee_id
                WHERE u.username = %s
            """, (username, ))
            while(time_result := cursor.fetchone()):
                employee_id, login_time, logout_time = time_result
            else:
                print("Successfully logged out")

            cursor.execute("""
                INSERT INTO sessions_log(employee_id, login_time, logout_time, login_duration)
                VALUES(%s, %s, %s, (SELECT TIMEDIFF(%s, %s)))
            """, (employee_id, login_time, logout_time, logout_time, login_time))
            connect.commit()

            cursor.execute("""
                DELETE FROM sessions
                WHERE employee_id = (SELECT employee_id FROM users WHERE username = %s)
            """, (username, ))
            connect.commit()

            self.shared_state["navigate"]("LoginPage")
        except Exception as e:
            print("Error with logout: ", e)
        finally:
            cursor.close()
            connect.close()
