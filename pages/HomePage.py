import threading
import customtkinter as ctk
import tkinter as tk
from PIL import Image
from tkinter import ttk, messagebox
from components.Inputs import PatientInfoWindow
from backend.connector import db_connection as db
from components.input_supply import SupplyWindow
from components.state import shared_states
from backend.crud import retrieve_form_data, db_connection

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class DataRetrieval():

    @staticmethod
    def patient_info_data(patient_id):
        return retrieve_form_data(patient_id, "*", table_name="patient_info")
    
    @staticmethod
    def patient_philhealth_data(patient_id):
        return retrieve_form_data(patient_id, "*", table_name="patient_benefits")
    
    @staticmethod
    def patient_contact_data(patient_id):
        return retrieve_form_data(patient_id, "*", table_name="patient_contact")
    
    @staticmethod
    def patient_relative_data(patient_id):
        return retrieve_form_data(patient_id, "*", table_name="patient_relative")

    @staticmethod
    def patient_family_history(patient_id):
        return retrieve_form_data(patient_id, 
                                  "has_hypertension, has_diabetes, has_malignancy, other_family_history",
                                  table_name='patient_history')
    
    @staticmethod
    def patient_medical_history(patient_id):
        return retrieve_form_data(patient_id, 
                                  "has_kidney_disease, has_urinary_stone, has_recurrent_uti, diabetes_type, other_medical_history",
                                  table_name='patient_history')

    @staticmethod
    def patient_other_history(patient_id):
        return retrieve_form_data(patient_id, 
                                  """
                                    present_illness_history, past_illness_history, first_diagnosis, first_dialysis, mode,
                                    access_type, first_hemodialysis, clinical_impression
                                    """,
                                  table_name='patient_history')
    
    @staticmethod
    def patient_medicines(patient_id):
        try:
            connect, cursor = db_connection()
            cursor.execute(f"""
                SELECT m.medication_name FROM patient_medications pm 
                JOIN medicines m ON m.medication_id = pm.medication_id
                JOIN patient_info pi ON pm.patient_id = pi.patient_id 
                WHERE pi.patient_id = {patient_id}
            """)
            medication_result = cursor.fetchall()
            print(medication_result)
            return medication_result
        except Exception as e:
            print('Error with displaying patient medications found at DataRetrieval class: ', e)
        finally:
            cursor.close()
            connect.close()

    @staticmethod
    def assign_retrieved_data(labels, data):
        null_values = ('type here', 'na', 'n/a', '', ' ')
        for i, label in enumerate(labels):
            value = (
                data[i] 
                if (i < len(data) and 
                    data[i] and 
                    str(data[i]).strip().lower() not in null_values) else "Not Specified")
            label.configure(text=str(value))

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

        self.welcome_label = ctk.CTkLabel(self, text="Welcome Back,", text_color="black", font=("Arial", 30, "bold"))
        self.welcome_label.place(relx=0.2, rely=0.5, anchor="e")

        self.name_label = ctk.CTkLabel(self, text="Tristan!", text_color="black", font=("Arial", 30, "bold"))
        self.name_label.place(relx=0.27, rely=0.5, anchor="e")

        self.namev2_label = ctk.CTkLabel(self, text="Tristan", text_color="black", font=("Arial", 30, "bold"))
        self.namev2_label.place(relx=0.85, rely=0.5, anchor="e")

        profile_img = ctk.CTkImage(light_image=Image.open("assets/profile.png"), size=(42, 42))
        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))

        icon_y = 62 

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

        self.first_frame = ctk.CTkFrame(
            self,
            width=1050,
            height=430,
            fg_color="white",
            corner_radius=20,   
        )
        self.first_frame.place(x=70, y=150)

        top_bar = ctk.CTkFrame(
            self.first_frame,
            width=1050,
            height=20,
            fg_color="#68EDC6",
            corner_radius=0
        )
        top_bar.place(x=0, y=0)

        YItemUsage_label = ctk.CTkLabel(
            self.first_frame,
            text="Yesterday Item Usage",
            font=("Merriweather", 20, "bold")
        )
        YItemUsage_label.place(x=400, y=40)

        self.second_frame = ctk.CTkFrame(
            self,
            width=600,
            height=435,
            fg_color="white",
            corner_radius=20
        )
        self.second_frame.place(x=70, y=610)

        top_bar = ctk.CTkFrame(
            self.second_frame,
            width=600,
            height=20,
            fg_color="#68EDC6",
            corner_radius=0
        )
        top_bar.place(x=0, y=0)

        MUsedItems_label = ctk.CTkLabel(
            self.second_frame,
            text="Most Used Items",
            font=("Merriweather", 20, "bold")
        )

        MUsedItems_label.place(x=210, y=40)

        self.third_frame = ctk.CTkFrame(
            self,
            width=410,
            height=200,
            fg_color="white",
            corner_radius=20
        )
        self.third_frame.place(x=710, y=610)

        RecentManual_label = ctk.CTkLabel(
            self.third_frame,
            text="Recent Manual Backup:",
            font=("Merriweather", 17)
        )
        RecentManual_label.place(x=30, y=45)

        RecentSched_label = ctk.CTkLabel(
            self.third_frame,
            text="Recent Scheduled Backup:",
            font=("Merriweather", 17)
        )
        RecentSched_label.place(x=30, y=75)

        UpcomingSched_label = ctk.CTkLabel(
            self.third_frame,
            text="Upcoming Scheduled Backup:",
            font=("Merriweather", 17)
        )
        UpcomingSched_label.place(x=30, y=105)

        left_bar = ctk.CTkFrame(
            self.third_frame,
            width=20,
            height=370,
            fg_color="#68EDC6",
            corner_radius=0
        )
        left_bar.place(x=0, y=0)

        fourth_frame = ctk.CTkFrame(
            self,
            width=410,
            height=200,
            fg_color="white",
            corner_radius=20
        )
        fourth_frame.place(x=710, y=845)

        top_bar = ctk.CTkFrame(
            fourth_frame,
            width=410,
            height=40,
            fg_color="#68EDC6",
            corner_radius=0
        )
        top_bar.place(x=0, y=0)

        recent_label = ctk.CTkLabel(
            top_bar,
            text="RECENT PATIENT",
            font=("Merriweather", 17, "bold"),
            text_color="white"
        )
        recent_label.place(relx=0.27, rely=0.5, anchor="center")

        first_box = ctk.CTkFrame(
            fourth_frame,
            width=100,
            height=120,
            fg_color="white",
            border_width=2,
            border_color="gray",
            corner_radius=10
        )
        first_box.place(x=30, y=60)

        second_box = ctk.CTkFrame(
            fourth_frame,
            width=100,
            height=120,
            fg_color="white",
            border_width=2,
            border_color="gray",
            corner_radius=10
        )
        second_box.place(x=155, y=60)

        third_box = ctk.CTkFrame(
            fourth_frame,
            width=100,
            height=120,
            fg_color="white",
            border_width=2,
            border_color="gray",
            corner_radius=10
        )
        third_box.place(x=280, y=60)

        fifth_frame = ctk.CTkFrame(
            self,
            width=350,
            height=520,
            fg_color="white",
            corner_radius=20
        )
        fifth_frame.place(x=1200, y=150)

        totalPatients_label = ctk.CTkLabel(
            fifth_frame,
            text="Total Patients",
            font=("Merriweather", 20, "bold")
        )
        totalPatients_label.place(x=100, y=40)

        active_icon_image = ctk.CTkImage(
            light_image=Image.open("assets/active_patients.png"),
            size=(40, 40)
        )

        inactive_icon_image = ctk.CTkImage(
            light_image=Image.open("assets/inactive_patients.png"),
            size=(40, 40)
        )

        active_patients = ctk.CTkFrame(
            fifth_frame,
            width=270,
            height=80,
            fg_color="white",
            border_width=2,
            border_color="gray",
            corner_radius=10
        )
        active_patients.place(x=40, y=300)

        active_icon_label = ctk.CTkLabel(
            active_patients,
            image=active_icon_image,
            text="",
        )
        active_icon_label.place(x=15, y=20)

        inactive_patients = ctk.CTkFrame(
            fifth_frame,
            width=270,
            height=80,
            fg_color="white",
            border_width=2,
            border_color="gray",
            corner_radius=10
        )
        inactive_patients.place(x=40, y=400)

        inactive_icon_label = ctk.CTkLabel(
            inactive_patients,
            image=inactive_icon_image,
            text="",
        )
        inactive_icon_label.place(x=15, y=20)


        sixth_frame = ctk.CTkFrame(
            self,
            width=350,
            height=345,
            fg_color="white",
            corner_radius=20
        )
        sixth_frame.place(x=1200, y=700)

        reminder_label = ctk.CTkLabel(
            sixth_frame,
            text="Reminder",
            font=("Merriweather", 20, "bold")
        )
        reminder_label.place(x=120, y=40)

        reminder_img = Image.open("assets/reminder.png")  
        reminder_ctk_img = ctk.CTkImage(light_image=reminder_img, size=(110, 110))  

        reminder_image_label = ctk.CTkLabel(
            sixth_frame,
            image=reminder_ctk_img,
            text="",  
        )
        reminder_image_label.place(x=120, y=100)  

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

        self.photo_frame = ctk.CTkFrame(
            self.detailed_info_frame,
            width=400,
            height=200,
            fg_color="white",
            corner_radius=20
        )
        self.photo_frame.place(x=50, y=80)
        self.photo_frame.place_forget()

        self.top_frame = ctk.CTkFrame(
            self.photo_frame,
            width=400,
            height=100,
            fg_color="#68EDC6",
            corner_radius=0
        )
        self.top_frame.place(x=0, y=0)

        self.patient_id_label = ctk.CTkLabel(
            self.photo_frame,
            text="Patient ID",
            font=("Merriweather", 14),
            text_color="black"
        )
        self.patient_id_label.place(relx=0.5, rely=0.65, anchor="center")

        self.patient_id_value = ctk.CTkLabel(
            self.photo_frame,
            text="",
            font=("Merriweather", 14),
            text_color="black"
        )
        self.patient_id_value.place(relx=0.5, rely=0.80, anchor="center")

        info_frame = ctk.CTkFrame(
            self.detailed_info_frame,
            width=950,
            height=500,
            fg_color="white",
            corner_radius=20
        )
        info_frame.place(x=600, y=80) 

        left_bar = ctk.CTkFrame(
            info_frame,
            width=20,
            height=500,
            fg_color="#68EDC6",
            corner_radius=0
        )
        left_bar.place(x=0, y=0)

        title_label = ctk.CTkLabel(info_frame, text="Patient Info", font=("Merriweather", 20, "bold"))
        title_label.place(x=50, y=20)

        self.lastname_label = ctk.CTkLabel(info_frame, text="Last Name", font=("Merriweather", 14))
        self.lastname_label.place(x=50, y=70)
        self.lastname_labelv = ctk.CTkLabel(info_frame, text="Lopez", font=("Merriweather", 14, "bold"))
        self.lastname_labelv.place(x=50, y=90)

        self.firstname_label = ctk.CTkLabel(info_frame, text="First Name", font=("Merriweather", 14))
        self.firstname_label.place(x=250, y=70)
        self.firstname_labelv = ctk.CTkLabel(info_frame, text="Juan", font=("Merriweather", 14, "bold"))
        self.firstname_labelv.place(x=250, y=90)

        self.middlename_label = ctk.CTkLabel(info_frame, text="Middle Name", font=("Merriweather", 14))
        self.middlename_label.place(x=500, y=70)
        self.middlename_labelv = ctk.CTkLabel(info_frame, text="Carlos", font=("Merriweather", 14, "bold"))
        self.middlename_labelv.place(x=500, y=90)

        self.status_label = ctk.CTkLabel(info_frame, text="Status", font=("Merriweather", 14))
        self.status_label.place(x=50, y=120)
        self.status_labelv = ctk.CTkLabel(info_frame, text="Active", font=("Merriweather", 14, "bold"))
        self.status_labelv.place(x=50, y=140)

        self.access_type_label = ctk.CTkLabel(info_frame, text="Type of Access", font=("Merriweather", 14))
        self.access_type_label.place(x=250, y=120)
        self.access_type_labelv = ctk.CTkLabel(info_frame, text="Admin", font=("Merriweather", 14, "bold"))
        self.access_type_labelv.place(x=250, y=140)

        self.birthdate_label = ctk.CTkLabel(info_frame, text="Birthdate", font=("Merriweather", 14))
        self.birthdate_label.place(x=500, y=120)
        self.birthdate_labelv = ctk.CTkLabel(info_frame, text="01/01/1980", font=("Merriweather", 14, "bold"))
        self.birthdate_labelv.place(x=500, y=140)

        self.age_label = ctk.CTkLabel(info_frame, text="Age", font=("Merriweather", 14))
        self.age_label.place(x=750, y=120)
        self.age_labelv = ctk.CTkLabel(info_frame, text="45", font=("Merriweather", 14, "bold"))
        self.age_labelv.place(x=750, y=140)

        self.gender_label = ctk.CTkLabel(info_frame, text="Gender", font=("Merriweather", 14))
        self.gender_label.place(x=50, y=170)
        self.gender_labelv = ctk.CTkLabel(info_frame, text="Male", font=("Merriweather", 14, "bold"))
        self.gender_labelv.place(x=50, y=190)

        self.height_label = ctk.CTkLabel(info_frame, text="Height", font=("Merriweather", 14))
        self.height_label.place(x=250, y=170)
        self.height_labelv = ctk.CTkLabel(info_frame, text="5'8\"", font=("Merriweather", 14, "bold"))
        self.height_labelv.place(x=250, y=190)

        self.civil_status_label = ctk.CTkLabel(info_frame, text="Civil Status", font=("Merriweather", 14))
        self.civil_status_label.place(x=500, y=170)
        self.civil_status_labelv = ctk.CTkLabel(info_frame, text="Married", font=("Merriweather", 14, "bold"))
        self.civil_status_labelv.place(x=500, y=190)

        self.religion_label = ctk.CTkLabel(info_frame, text="Religion", font=("Merriweather", 14))
        self.religion_label.place(x=750, y=170)
        self.religion_labelv = ctk.CTkLabel(info_frame, text="Christian", font=("Merriweather", 14, "bold"))
        self.religion_labelv.place(x=750, y=190)

        self.address_label = ctk.CTkLabel(info_frame, text="Complete Address", font=("Merriweather", 14))
        self.address_label.place(x=50, y=230)
        self.address_labelv = ctk.CTkLabel(info_frame, text="1234 Elm St, Quezon City", font=("Merriweather", 14, "bold"))
        self.address_labelv.place(x=50, y=250)

        contact_options_panel = ctk.CTkFrame(
            self.detailed_info_frame,
            width=400,
            height=400,
            fg_color="white",
            corner_radius=20
        )
        contact_options_panel.place(x=50, y=350)  

        left_bar = ctk.CTkFrame(
            contact_options_panel,
            width=20,
            height=400,
            fg_color="#1A374D",
            corner_radius=0
        )
        left_bar.place(x=0, y=0)

        patient_history_btn = ctk.CTkButton(
            contact_options_panel,
            text="Patient History",
            font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_patient_history
        )
        patient_history_btn.place(x=80, y=80)

        medication_btn = ctk.CTkButton(
            contact_options_panel,
            text="Medication",
            font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_medication
        )
        medication_btn.place(x=80, y=150)

        contact_btn = ctk.CTkButton(
            contact_options_panel,
            text="Contact",
            font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_contact_info
        )
        contact_btn.place(x=80, y=220)

        philhealth_info_panel = ctk.CTkFrame(
            self.detailed_info_frame,
            width=950,
            height=300,
            fg_color="white",
            corner_radius=20
        )
        philhealth_info_panel.place(x=600, y=600) 

        left_bar = ctk.CTkFrame(
            philhealth_info_panel,
            width=20,
            height=300,
            fg_color="#68EDC6",
            corner_radius=0
        )
        left_bar.place(x=0, y=0)

        title_label = ctk.CTkLabel(
            philhealth_info_panel,
            text="Phil Health and Other Info",
            font=("Merriweather", 20, "bold")
        )
        title_label.place(x=50, y=20)

        self.philhealth_number_label = ctk.CTkLabel(philhealth_info_panel,text="PhilHealth Number",font=("Merriweather", 14))
        self.philhealth_number_label.place(x=50, y=70)

        self.philhealth_number_labelv = ctk.CTkLabel(philhealth_info_panel,text="PH1234567890",font=("Merriweather", 14, "bold"))
        self.philhealth_number_labelv.place(x=50, y=90)

        self.membership_label = ctk.CTkLabel(philhealth_info_panel,text="Membership",font=("Merriweather", 14))
        self.membership_label.place(x=300, y=70)

        self.membership_labelv = ctk.CTkLabel(philhealth_info_panel,text="Active",font=("Merriweather", 14, "bold"))
        self.membership_labelv.place(x=300, y=90)

        self.pwd_label = ctk.CTkLabel(philhealth_info_panel,text="PWD",font=("Merriweather", 14))
        self.pwd_label.place(x=50, y=120)

        self.pwd_labelv = ctk.CTkLabel(philhealth_info_panel,text="Yes",font=("Merriweather", 14, "bold"))
        self.pwd_labelv.place(x=50, y=140)

        self.pwd_id_label = ctk.CTkLabel(philhealth_info_panel,text="PWD ID Number",font=("Merriweather", 14))
        self.pwd_id_label.place(x=300, y=120)

        self.pwd_id_labelv = ctk.CTkLabel(philhealth_info_panel,text="PWD987654321",font=("Merriweather", 14, "bold"))
        self.pwd_id_labelv.place(x=300, y=140)

        self.senior_label = ctk.CTkLabel(philhealth_info_panel,text="SENIOR",font=("Merriweather", 14))
        self.senior_label.place(x=530, y=120)

        self.senior_labelv = ctk.CTkLabel(philhealth_info_panel,text="No",font=("Merriweather", 14, "bold"))
        self.senior_labelv.place(x=530, y=140)

        self.senior_id_label = ctk.CTkLabel(philhealth_info_panel,text="SENIOR ID Number",font=("Merriweather", 14))
        self.senior_id_label.place(x=730, y=120)

        self.senior_id_labelv = ctk.CTkLabel(philhealth_info_panel,text="None",font=("Merriweather", 14, "bold"))
        self.senior_id_labelv.place(x=730, y=140)

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

        self.button_frame.place(x=20, y=10, anchor="nw")
        self.table_frame.place(x=20, y=60, relwidth=0.95, relheight=0.8)

        self.populate_table(self.fetch_patient_data())

    def open_patient_history(self):
        self.patient_history_window = PatientHistory(self.master)
        self.patient_history_window.place(x=60, y=10)

    def open_medication(self):
        self.medication_window = Medication(self.master)
        self.medication_window.place(x=60, y=10)

    def open_contact_info(self):
        self.contact_info_window = ContactInfoRelativeInfo(self.master)
        self.contact_info_window.place(x=60, y=10)

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
            print("patient id: ", patient_id)
            threading.Thread(target=lambda: self.show_detailed_info(patient_id)).start()

            FamilyHistory().family_history_info(patient_id)
            MedicalHistory().medical_history_info(patient_id)

    def show_detailed_info(self, patient_id):
        self.table_frame.place_forget()
        self.button_frame.place_forget()
        self.patient_id_value.configure(text=patient_id)
        self.display_patient_id(patient_id)
        
        try:
            get_patient_info_data = DataRetrieval.patient_info_data(patient_id)

            get_patient_philhealth_data = DataRetrieval.patient_philhealth_data(patient_id)

            if get_patient_info_data:
                self.display_patient_basic_info(get_patient_info_data)
                print(get_patient_info_data)
            else:
                messagebox.showwarning("No Data", "Patient record not found")

            if get_patient_philhealth_data:
                self.display_patient_philhealth_info(get_patient_philhealth_data)
                print(get_patient_philhealth_data)
            else:
                messagebox.showwarning("No Data", "Patient record not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

        self.detailed_info_frame.place(x=20, y=20, relwidth=0.95, relheight=0.95)

    def display_patient_id(self, patient_id):
        self.photo_frame.place(x=50, y=80)

    def display_patient_basic_info(self, data):
        labels = [
            self.patient_id_value,
            self.lastname_labelv,
            self.firstname_labelv,
            self.middlename_labelv,
            self.status_labelv,
            self.access_type_labelv,
            self.birthdate_labelv,
            self.age_labelv,
            self.gender_labelv,
            self.height_labelv,
            self.civil_status_labelv,
            self.religion_labelv,
            self.address_labelv,
        ]
        DataRetrieval.assign_retrieved_data(labels, data)

    def display_patient_philhealth_info(self, data):
        labels = [  
            self.patient_id_value,
            self.senior_labelv,
            self.pwd_labelv,
            self.philhealth_number_labelv,
            self.membership_labelv,
            self.pwd_id_labelv,
            self.senior_id_labelv
        ]
        DataRetrieval.assign_retrieved_data(labels, data)

    def show_table_view(self):
        self.detailed_info_frame.place_forget()
        self.photo_frame.place_forget()
        self.button_frame.place(x=20, y=10, anchor="nw") 
        self.table_frame.place(x=20, y=60, relwidth=0.95, relheight=0.8)

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

class PatientHistory(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1443, height=1100, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(self, width=20, fg_color="#1A374D", corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self, text="Patient History", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=50, y=20)

        self.family_history = FamilyHistory(self)
        self.family_history.place(x=50, y=70)

        self.medical_history = MedicalHistory(self)
        self.medical_history.place(x=800, y=70)

        self.other_history = OtherHistory(self)
        self.other_history.place(x=50, y=400)

        self.exit_button = create_exit_button(self, command=self.exit_patienthistory)
        self.exit_button.place(x=1330, y=15)


    def exit_patienthistory(self):
        print("Patient History closed")
        self.place_forget()

class Medication(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1400, height=650, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(self, width=20, fg_color="#1A374D", corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        self.canvas, self.scrollbar, self.scrollable_frame = add_scrollable_frame(self)

        self.title_label = ctk.CTkLabel(self, text="Medication", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=50, y=20)

        self.exit_button = create_exit_button(self, command=self.exit_medication)
        self.exit_button.place(x=1330, y=15)

        self.medication_label = ctk.CTkLabel(self.scrollable_frame, text="Drugs Taken", font=("Merriweather", 16))
        self.medication_label.place(x=30, y=35)

        meds = [
            "Amlodipine 10mg",
            "Metformin 500mg",
            "Erythropoietin Injection",
            "Sevelamer 800mg",
            "Calcium Carbonate 500mg"
        ]

        y_position = 60
        for med in meds:
            med_label = ctk.CTkLabel(self.scrollable_frame, text=med, font=("Merriweather", 13), text_color="black")
            med_label.place(x=30, y=y_position)
            y_position += 30

    def exit_medication(self):
        print("Medication closed")
        self.place_forget()

class ContactInfoRelativeInfo(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=980, height=815, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#1A374D",  
            corner_radius=0
        )
        self.left_bar.pack(side="left", fill="y")

        self.contact_info_label = ctk.CTkLabel(self, text="Contact Info", font=("Merriweather", 20, "bold"))
        self.contact_info_label.place(x=50, y=20)

        self.last_name_label = ctk.CTkLabel(self, text="Last Name", font=("Merriweather", 14))
        self.last_name_label.place(x=50, y=70)

        self.last_name_value = ctk.CTkLabel(self, text="Garcia", font=("Merriweather", 14))
        self.last_name_value.place(x=50, y=90)

        self.first_name_label = ctk.CTkLabel(self, text="First Name", font=("Merriweather", 14))
        self.first_name_label.place(x=250, y=70)

        self.first_name_value = ctk.CTkLabel(self, text="Juan", font=("Merriweather", 14))
        self.first_name_value.place(x=250, y=90)

        self.middle_name_label = ctk.CTkLabel(self, text="Middle Name", font=("Merriweather", 14))
        self.middle_name_label.place(x=450, y=70)

        self.middle_name_value = ctk.CTkLabel(self, text="Dela Cruz", font=("Merriweather", 14))
        self.middle_name_value.place(x=450, y=90)

        self.contact_number_label = ctk.CTkLabel(self, text="Contact Number", font=("Merriweather", 14))
        self.contact_number_label.place(x=50, y=120)

        self.contact_number_value = ctk.CTkLabel(self, text="09123456789", font=("Merriweather", 14))
        self.contact_number_value.place(x=50, y=140)

        self.relationship_label = ctk.CTkLabel(self, text="Relationship to the Patient", font=("Merriweather", 14))
        self.relationship_label.place(x=250, y=120)

        self.relationship_value = ctk.CTkLabel(self, text="Brother", font=("Merriweather", 14))
        self.relationship_value.place(x=250, y=140)

        self.complete_address_label = ctk.CTkLabel(self, text="Complete Address", font=("Merriweather", 14))
        self.complete_address_label.place(x=50, y=170)

        self.address_value = ctk.CTkLabel(self, text="123 Barangay St., Cityville", font=("Merriweather", 14))
        self.address_value.place(x=50, y=190)

        self.relative_info_label = ctk.CTkLabel(self, text="Relative Info", font=("Merriweather", 20, "bold"))
        self.relative_info_label.place(x=50, y=230)

        self.relative_last_name_label = ctk.CTkLabel(self, text="Last Name", font=("Merriweather", 14))
        self.relative_last_name_label.place(x=50, y=270)

        self.relative_last_name_value = ctk.CTkLabel(self, text="Garcia", font=("Merriweather", 14))
        self.relative_last_name_value.place(x=50, y=290)

        self.relative_first_name_label = ctk.CTkLabel(self, text="First Name", font=("Merriweather", 14))
        self.relative_first_name_label.place(x=250, y=270)

        self.relative_first_name_value = ctk.CTkLabel(self, text="Maria", font=("Merriweather", 14))
        self.relative_first_name_value.place(x=250, y=290)

        self.relative_middle_name_label = ctk.CTkLabel(self, text="Middle Name", font=("Merriweather", 14))
        self.relative_middle_name_label.place(x=450, y=270)

        self.relative_middle_name_value = ctk.CTkLabel(self, text="Santos", font=("Merriweather", 14))
        self.relative_middle_name_value.place(x=450, y=290)

        self.relative_contact_number_label = ctk.CTkLabel(self, text="Contact Number", font=("Merriweather", 14))
        self.relative_contact_number_label.place(x=50, y=320)

        self.relative_contact_number_value = ctk.CTkLabel(self, text="09234567890", font=("Merriweather", 14))
        self.relative_contact_number_value.place(x=50, y=340)

        self.relative_complete_address_label = ctk.CTkLabel(self, text="Complete Address", font=("Merriweather", 14))
        self.relative_complete_address_label.place(x=50, y=370)

        self.relative_address_value = ctk.CTkLabel(self, text="456 Calle Nueva, Townsville", font=("Merriweather", 14))
        self.relative_address_value.place(x=50, y=390)

        self.exit_button = create_exit_button(self, command=self.exit_panel)
        self.exit_button.place(x=900, y=15)

    def exit_panel(self):
        print("Contact and Relative Info closed")
        self.place_forget()

class FamilyHistory(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=600, height=250, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#68EDC6",  
            corner_radius=0
        )
        self.left_bar.pack(side="left", fill="y")

        self.canvas, self.scrollbar, self.scrollable_frame = add_scrollable_frame(self)

        self.title_label = ctk.CTkLabel(
            self.scrollable_frame, text="Family History", font=("Merriweather", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=10, padx=30)

        self.hypertension_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Hypertension", font=("Merriweather", 14), text_color="black"
        )
        self.hypertension_label.grid(row=2, column=0, pady=1, padx=30, sticky="w" )

        self.diabetes_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Diabetes Mellitus", font=("Merriweather", 14), text_color="black"
        )
        self.diabetes_label.grid(row=3, column=0, pady=1, padx=30, sticky="w")

        self.malignancy_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Malignancy", font=("Merriweather", 14), text_color="black"
        )
        self.malignancy_label.grid(row=4, column=0, pady=1, padx=30, sticky="w")

        self.other_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Other", font=("Merriweather", 14), text_color="black"
        )
        self.other_label.grid(row=5, column=0, pady=1, padx=30, sticky="w")

    def family_history_info(self, patient_id):
        try:
            patient_family_history = DataRetrieval.patient_family_history(patient_id)
            print(patient_family_history)

            if patient_family_history:
                self.display_family_history(patient_family_history)
            else:
                messagebox.showwarning("No Data", "Patient record not foundddd")

        except Exception as e:
            print(e)

    def display_family_history(self, data):
        labels = [
            self.hypertension_label,
            self.diabetes_label,
            self.malignancy_label,
            self.other_label,
        ]
        DataRetrieval.assign_retrieved_data(labels, data)

class MedicalHistory(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=600, height=250, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False) 

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#68EDC6",
            corner_radius=0
        )
        self.left_bar.pack(side="left", fill="y")

        # Add scrollable frame here
        self.canvas, self.scrollbar, self.scrollable_frame = add_scrollable_frame(self)

        self.title_label = ctk.CTkLabel(
            self.scrollable_frame, text="Medical History", font=("Merriweather", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=10, padx=30, sticky="w")

        start_y = 1

        self.kidney_disease_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Kidney Disease", font=("Merriweather", 14), text_color="black"
        )
        self.kidney_disease_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.urinary_stone_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Urinary Stone", font=("Merriweather", 14), text_color="black"
        )
        self.urinary_stone_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.recurrent_uti_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Recurrent UTI", font=("Merriweather", 14), text_color="black"
        )
        self.recurrent_uti_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.diabetes_type_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Diabetes Type", font=("Merriweather", 14), text_color="black"
        )
        self.diabetes_type_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.other_medical_history_label = ctk.CTkLabel(
            self.scrollable_frame, text="• Other", font=("Merriweather", 14), text_color="black"
        )
        self.other_medical_history_label.grid(row=start_y, column=0, sticky="w", padx=30)

    def medical_history_info(self, patient_id):
        try:
            patient_medical_history = DataRetrieval.patient_medical_history(patient_id)
            print(patient_medical_history)
            if patient_medical_history:
                self.display_medical_history(patient_medical_history)
            else:
                messagebox.showwarning("No Data", "Patient record not found")

        except Exception as e:
            print(e)

    def display_medical_history(self, data):
        labels = [
            self.kidney_disease_label,
            self.urinary_stone_label,
            self.recurrent_uti_label,
            self.diabetes_type_label,
            self.other_medical_history_label,
        ]
        DataRetrieval.assign_retrieved_data(labels, data)


class OtherHistory(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1255, height=474, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#68EDC6",
            corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        self.canvas, self.scrollbar, self.scrollable_frame = add_scrollable_frame(self)

        self.title_label = ctk.CTkLabel(self.scrollable_frame, text="Other History", font=("Merriweather", 20, "bold"))
        self.title_label.grid(row=0, column=0, pady=20, padx=30)

        start_y = 1

        self.hpi_label = ctk.CTkLabel(self.scrollable_frame, text="History of Present Illness", font=("Merriweather", 14))
        self.hpi_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.hpi_info = ctk.CTkLabel(self.scrollable_frame, text="Patient experienced persistent fatigue and swelling.", font=("Merriweather", 14), text_color="black")
        self.hpi_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.pmh_label = ctk.CTkLabel(self.scrollable_frame, text="Pertinent Past Medical History", font=("Merriweather", 14))
        self.pmh_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.pmh_info = ctk.CTkLabel(self.scrollable_frame, text="History of hypertension and Type 2 diabetes.", font=("Merriweather", 14), text_color="black")
        self.pmh_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.kidney_disease_date_label = ctk.CTkLabel(self.scrollable_frame, text="Date of first diagnosed having kidney disease", font=("Merriweather", 14))
        self.kidney_disease_date_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.kidney_disease_date_info = ctk.CTkLabel(self.scrollable_frame, text="March 2015", font=("Merriweather", 14), text_color="black")
        self.kidney_disease_date_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.dialysis_date_label = ctk.CTkLabel(self.scrollable_frame, text="Date of first Dialysis", font=("Merriweather", 14))
        self.dialysis_date_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.dialysis_date_info = ctk.CTkLabel(self.scrollable_frame, text="January 2020", font=("Merriweather", 14), text_color="black")
        self.dialysis_date_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        self.mode_label = ctk.CTkLabel(self.scrollable_frame, text="Mode", font=("Merriweather", 14))
        self.mode_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.mode_info = ctk.CTkLabel(self.scrollable_frame, text="Hemodialysis", font=("Merriweather", 14), text_color="black")
        self.mode_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.access_label = ctk.CTkLabel(self.scrollable_frame, text="Access", font=("Merriweather", 14))
        self.access_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.access_info = ctk.CTkLabel(self.scrollable_frame, text="Arteriovenous fistula (AVF)", font=("Merriweather", 14), text_color="black")
        self.access_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.chronic_hemo_date_label = ctk.CTkLabel(self.scrollable_frame, text="Date of first Chronic Hemodialysis (* Leave NA if not)", font=("Merriweather", 14))
        self.chronic_hemo_date_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.chronic_hemo_date_info = ctk.CTkLabel(self.scrollable_frame, text="April 2021", font=("Merriweather", 14), text_color="black")
        self.chronic_hemo_date_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.clinical_impression_label = ctk.CTkLabel(self.scrollable_frame, text="Clinical Impression", font=("Merriweather", 14))
        self.clinical_impression_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.clinical_impression_info = ctk.CTkLabel(self.scrollable_frame, text="End-stage renal disease secondary to diabetes.", font=("Merriweather", 14), text_color="black")
        self.clinical_impression_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

def add_scrollable_frame(parent_frame, width=600, height=250):
        canvas = tk.Canvas(parent_frame, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        scrollbar = ctk.CTkScrollbar(parent_frame, orientation="vertical", command=canvas.yview, fg_color="white", button_color="#1A374D")
        scrollbar.pack(side="right", fill="y", pady=10)

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")
        scrollable_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_canvas(event):
            canvas_width = event.width
            canvas.itemconfig(scrollable_window, width=canvas_width)

        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", resize_canvas)

        return canvas, scrollbar, scrollable_frame

def create_exit_button(parent, command=None):
    image = Image.open("assets/exit.png")
    exit_ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(25, 25))

    exit_button = ctk.CTkButton(
        parent,
        image=exit_ctk_image,
        text="",
        command=command,
        width=40,
        height=40,
        fg_color="transparent"
    )
    exit_button.image = exit_ctk_image 
    return exit_button

class SupplyPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")
        label = ctk.CTkLabel(self, text="Supply Page", font=("Arial", 24))
        label.pack(pady=100)

        self.button_frame = ctk.CTkFrame(self, fg_color="#E8FBFC")
        self.button_frame.pack(pady=10)

        self.add_button = ctk.CTkButton(
            self.button_frame, text="Add", font=ctk.CTkFont("Arial", 16, "bold"),
            width=120, command=self.open_add_window
        )
        self.add_button.pack(side="left", padx=5)

        self.edit_button = ctk.CTkButton(
            self.button_frame, text="Edit", font=ctk.CTkFont("Arial", 16, "bold"),
            width=120, command=self.open_edit_window
        )
        self.edit_button.pack(side="left", padx=5)

    def open_add_window(self):
        SupplyWindow(self)  

    def open_edit_window(self):
        pass  

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
            