from tkcalendar import DateEntry
import threading
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk
from PIL import Image
from tkinter import ttk, messagebox
from components.Inputs import PatientInfoWindow
from backend.connector import db_connection as db
from components.buttons import CTkButtonSelectable
from components.input_supply import CTkMessageBox, EditStockWindow, QuantityUsedLogsWindow, RestockLogWindow, SupplyWindow
from components.state import login_shared_states
from backend.crud import retrieve_form_data, db_connection
from datetime import datetime
from customtkinter import CTkInputDialog
import datetime
import shutil
import os


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class DataRetrieval():

    # =========== FOR PATIENT DATA RETRIEVAL =========== #

    @staticmethod
    def patient_info_data(patient_id):
        return retrieve_form_data(patient_id, 'patient_id', "*", table_name="patient_info")

    @staticmethod
    def patient_philhealth_data(patient_id):
        return retrieve_form_data(patient_id, 'patient_id', "*", table_name="patient_benefits")
    
    @staticmethod
    def patient_contact_data(patient_id):
        return retrieve_form_data(patient_id, 'patient_id', "*", table_name="patient_contact")
    
    @staticmethod
    def patient_relative_data(patient_id):
        return retrieve_form_data(patient_id, 'patient_id', "*", table_name="patient_relative")

    @staticmethod
    def patient_family_history(patient_id):
        return retrieve_form_data(patient_id, 'patient_id',
                                  "has_hypertension, has_diabetes, has_malignancy, other_family_history",
                                  table_name='patient_history')
    
    @staticmethod
    def patient_medical_history(patient_id):
        return retrieve_form_data(patient_id, 'patient_id',
                                  "has_kidney_disease, has_urinary_stone, has_recurrent_uti, diabetes_type, other_medical_history",
                                  table_name='patient_history')

    @staticmethod
    def patient_other_history(patient_id):
        return retrieve_form_data(patient_id, 'patient_id',
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

    # =========== FOR PATIENT DATA RETRIEVAL =========== #

    # FOR NULL CHECK
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

    # =========== FOR SUPPLY DATA RETRIEVAL =========== #

    @staticmethod
    def supply_information(item_id):
        return retrieve_form_data(item_id, 'item_id', '*', table_name='supply')

    # =========== FOR SUPPLY DATA RETRIEVAL =========== #

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
            "Supply": SupplyPage(self.main_frame, shared_state),
            "Report": ReportPage(self.main_frame),
            "Maintenance": MaintenancePage(self.main_frame),
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
            "Maintenance": "assets/about.png",
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

        # Initialize reminder carousel variables
        self.current_reminder_index = 0
        self.reminder_images = []
        self.reminder_animation_job = None
        self.fade_animation_job = None

        self.navbar = ctk.CTkFrame(self, fg_color="white", height=130)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)
        self.navbar.configure(border_width=0, border_color="black")

        self.dropdown_visible = False 

        self.dropdown_frame = ctk.CTkFrame(self.navbar, fg_color="#f0f0f0", corner_radius=8, width=150, height=100)
        self.dropdown_frame.configure(border_width=1, border_color="gray")
        self.dropdown_frame.place_forget()

        self.welcome_label = ctk.CTkLabel(self.navbar, text="Welcome Back,", text_color="black", font=("Arial", 30, "bold"))
        self.welcome_label.place(relx=0.17, rely=0.5, anchor="e")

        self.name_label = ctk.CTkLabel(self.navbar, text="Tristan!", text_color="black", font=("Arial", 30, "bold"))
        self.name_label.place(relx=0.25, rely=0.5, anchor="e")

         # Search container
        self.search_container = ctk.CTkFrame(
            self.navbar, 
            fg_color="white", 
            corner_radius=25,
            width=300,
            height=50,
            border_width=2.5,
            border_color="#E0E0E0"
        )
        self.search_container.place(x=450, y=70, anchor="w")

        # Search icon
        try:
            search_img = ctk.CTkImage(light_image=Image.open("assets/search.png"), size=(24, 24))
            search_icon = ctk.CTkLabel(self.search_container, image=search_img, text="")
            search_icon.place(x=15, rely=0.5, anchor="w")
        except:
            search_icon = ctk.CTkLabel(
                self.search_container, 
                text="🔍", 
                font=("Arial", 16),
                text_color="#666666"
            )
            search_icon.place(x=15, rely=0.5, anchor="w")

        # Search entry
        self.search_entry = ctk.CTkEntry(   
            self.search_container,
            placeholder_text="Search patient",
            width=170,
            height=40,
            border_width=0,
            fg_color="transparent",
            font=("Arial", 14),
            text_color="#333333",
            placeholder_text_color="#999999"
        )
        self.search_entry.place(x=50, rely=0.5, anchor="w")

        # calendar container
        self.calendar_container = ctk.CTkFrame(
            self.navbar, 
            fg_color="white", 
            corner_radius=25,
            width=250,
            height=50,
            border_width=2.5,
            border_color="#E0E0E0"
        )
        self.calendar_container.place(x=810, y=70, anchor="w")

        # calendar icon
        try:
            calendar_img = ctk.CTkImage(light_image=Image.open("assets/calendar.png"), size=(30, 30))
            calendar_icon = ctk.CTkLabel(self.calendar_container, image=calendar_img, text="")
            calendar_icon.place(x=15, rely=0.5, anchor="w")
        except:
            calendar_icon = ctk.CTkLabel(
                self.calendar_container,
                text="📅",
                font=("Arial", 16),
                text_color="#666666"
            )
            calendar_icon.place(x=25, rely=0.5, anchor="w")

        # Get today's date
        today_date = datetime.datetime.now().strftime("%B %d, %Y") 

        # date label beside the icon
        date_label = ctk.CTkLabel(
            self.calendar_container,
            text=today_date,
            font=("Arial", 20),
            text_color="#333333"
        )
        date_label.place(x=60, rely=0.5, anchor="w")

        self.namev2_label = ctk.CTkLabel(self.navbar, text="Tristan Lopez!", text_color="black", font=("Arial", 30, "bold"))
        self.namev2_label.place(relx=0.85, rely=0.5, anchor="e")

        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))

        icon_y = 62

        notif_btn = ctk.CTkButton(self.navbar, image=notif_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5")
        notif_btn.place(relx=1.0, x=-110, y=icon_y, anchor="center")

        settings_btn = ctk.CTkButton(self.navbar, image=settings_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5", command=self.toggle_dropdown)
        settings_btn.place(relx=1.0, x=-160, y=icon_y, anchor="center")

        ctk.CTkButton(self.dropdown_frame, text="Account Settings", width=140, command=self.open_settings).pack(pady=5)
        ctk.CTkButton(self.dropdown_frame, text="Log Out", width=140, command=self.logout).pack(pady=5)

        self.bottom_line = ctk.CTkFrame(self.navbar, height=1.5, fg_color="black")
        self.bottom_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

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

        # Sixth frame with animated reminder carousel
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

        # Load reminder images 
        try:
            reminder_img1 = Image.open("assets/reminder.png") 
            reminder_img2 = Image.open("assets/reminder2.png")  
            
            self.reminder_images = [
                ctk.CTkImage(light_image=reminder_img1, size=(200, 200)),
                ctk.CTkImage(light_image=reminder_img2, size=(200, 200))
            ]
        except Exception as e:
            # Fallback if second image doesn't exist
            print(f"Warning: Could not load second reminder image: {e}")
            reminder_img = Image.open("assets/reminder.png")
            self.reminder_images = [
                ctk.CTkImage(light_image=reminder_img, size=(200, 200)),
                ctk.CTkImage(light_image=reminder_img, size=(200, 200)) 
            ]

        # Create reminder image label with initial image
        self.reminder_image_label = ctk.CTkLabel(
            sixth_frame,
            image=self.reminder_images[0],
            text="",  
        )
        self.reminder_image_label.place(x=80, y=100)

        # Add carousel indicators
        self.indicator_frame = ctk.CTkFrame(
            sixth_frame,
            width=60,
            height=20,
            fg_color="transparent"
        )
        self.indicator_frame.place(x=145, y=310)

        # Create indicator dots
        self.indicators = []
        for i in range(len(self.reminder_images)):
            indicator = ctk.CTkLabel(
                self.indicator_frame,
                text="●",
                font=("Arial", 16),
                text_color="#68EDC6" if i == 0 else "#D3D3D3",
                width=20,
                height=20
            )
            indicator.place(x=i * 25, y=0)
            self.indicators.append(indicator)

        # Start the carousel animation
        self.start_reminder_carousel()

    def start_reminder_carousel(self):
        """Start the automatic reminder carousel"""
        self.reminder_animation_job = self.after(10000, self.next_reminder)

    def next_reminder(self):
        """Switch to the next reminder with fade animation"""
        if len(self.reminder_images) <= 1:
            return
            
        # Start fade out animation
        self.fade_out_reminder()

    def fade_out_reminder(self):
        """Fade out current reminder image"""
        # Create fade effect by temporarily hiding the image
        self.reminder_image_label.configure(image=None)
        
        # Schedule fade in after a brief moment
        self.fade_animation_job = self.after(200, self.fade_in_next_reminder)

    def fade_in_next_reminder(self):
        """Fade in the next reminder image"""
        # Update to next image
        self.current_reminder_index = (self.current_reminder_index + 1) % len(self.reminder_images)
        
        # Update image
        self.reminder_image_label.configure(image=self.reminder_images[self.current_reminder_index])
        
        # Update indicators
        self.update_indicators()
        
        # Schedule next transition
        self.reminder_animation_job = self.after(10000, self.next_reminder)

    def update_indicators(self):
        """Update the carousel indicator dots"""
        for i, indicator in enumerate(self.indicators):
            if i == self.current_reminder_index:
                indicator.configure(text_color="#68EDC6")  
            else:
                indicator.configure(text_color="#D3D3D3") 

    def stop_reminder_carousel(self):
        """Stop the reminder carousel animation"""
        if self.reminder_animation_job:
            self.after_cancel(self.reminder_animation_job)
            self.reminder_animation_job = None
        if self.fade_animation_job:
            self.after_cancel(self.fade_animation_job)
            self.fade_animation_job = None

    def toggle_dropdown(self):
        if self.dropdown_visible:
            self.dropdown_frame.place_forget()
        else:
            x = self.winfo_rootx() + self.winfo_width() - 180
            y = self.winfo_rooty() + 90
            self.dropdown_frame.place(x=x, y=y)
            self.dropdown_frame.lift() 
        self.dropdown_visible = not self.dropdown_visible

    def open_settings(self):
        print("Opening account settings...")

    def logout(self):
        print("Logging out...")

    def destroy(self):
        """Clean up when the widget is destroyed"""
        self.stop_reminder_carousel()
        super().destroy()

class PatientPage(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state
        self.patient_id = None 

        self.navbar = ctk.CTkFrame(self, fg_color="white", height=130)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)
        self.navbar.configure(border_width=0, border_color="black")

        self.dropdown_visible = False 

        self.dropdown_frame = ctk.CTkFrame(self.navbar, fg_color="#f0f0f0", corner_radius=8, width=150, height=100)
        self.dropdown_frame.configure(border_width=1, border_color="gray")
        self.dropdown_frame.place_forget()

        self.namev2_label = ctk.CTkLabel(self.navbar, text="Tristan Lopez!", text_color="black", font=("Arial", 30, "bold"))
        self.namev2_label.place(relx=0.85, rely=0.5, anchor="e")

        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))

        icon_y = 62

        notif_btn = ctk.CTkButton(self.navbar, image=notif_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5")
        notif_btn.place(relx=1.0, x=-110, y=icon_y, anchor="center")

        settings_btn = ctk.CTkButton(self.navbar, image=settings_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5", command=self.toggle_dropdown)
        settings_btn.place(relx=1.0, x=-160, y=icon_y, anchor="center")

        ctk.CTkButton(self.dropdown_frame, text="Account Settings", width=140, command=self.open_settings).pack(pady=5)
        ctk.CTkButton(self.dropdown_frame, text="Log Out", width=140, command=self.logout).pack(pady=5)

        self.bottom_line = ctk.CTkFrame(self.navbar, height=1.5, fg_color="black")
        self.bottom_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        # Table view setup
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        style.map("Treeview", background=[("selected", "#68EDC6")])

        self.hovered_row = None

        self.button_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")

        # Add Button
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Add",
            font=ctk.CTkFont("Arial", 16, "bold"),
            command=self.open_add_window,
            width=180,  
            height=50    
        )
        self.add_button.pack(side="left", padx=10)

        # Guide Button
        self.guide_button = ctk.CTkButton(
            self.button_frame,
            text="Guide",
            font=ctk.CTkFont("Arial", 16, "bold"),
            width=180,
            height=50
        )
        self.guide_button.pack(side="left", padx=10)

         # Search container
        self.search_container = ctk.CTkFrame(
            self.navbar, 
            fg_color="white", 
            corner_radius=25,
            width=300,
            height=50,
            border_width=2.5,
            border_color="#E0E0E0"
        )
        self.search_container.place(x=450, y=70, anchor="w")

        # Search icon
        try:
            search_img = ctk.CTkImage(light_image=Image.open("assets/search.png"), size=(24, 24))
            search_icon = ctk.CTkLabel(self.search_container, image=search_img, text="")
            search_icon.place(x=15, rely=0.5, anchor="w")
        except:
            search_icon = ctk.CTkLabel(
                self.search_container, 
                text="🔍", 
                font=("Arial", 16),
                text_color="#666666"
            )
            search_icon.place(x=15, rely=0.5, anchor="w")

        # Search entry
        self.search_entry = ctk.CTkEntry(   
            self.search_container,
            placeholder_text="Search patient",
            width=170,
            height=40,
            border_width=0,
            fg_color="transparent",
            font=("Arial", 14),
            text_color="#333333",
            placeholder_text_color="#999999"
        )
        self.search_entry.place(x=50, rely=0.5, anchor="w")

        # calendar container
        self.calendar_container = ctk.CTkFrame(
            self.navbar, 
            fg_color="white", 
            corner_radius=25,
            width=250,
            height=50,
            border_width=2.5,
            border_color="#E0E0E0"
        )
        self.calendar_container.place(x=810, y=70, anchor="w")

        # calendar icon
        try:
            calendar_img = ctk.CTkImage(light_image=Image.open("assets/calendar.png"), size=(30, 30))
            calendar_icon = ctk.CTkLabel(self.calendar_container, image=calendar_img, text="")
            calendar_icon.place(x=15, rely=0.5, anchor="w")
        except:
            calendar_icon = ctk.CTkLabel(
                self.calendar_container,
                text="📅",
                font=("Arial", 16),
                text_color="#666666"
            )
            calendar_icon.place(x=25, rely=0.5, anchor="w")

        # Get today's date
        today_date = datetime.datetime.now().strftime("%B %d, %Y") 

        # date label beside the icon
        date_label = ctk.CTkLabel(
            self.calendar_container,
            text=today_date,
            font=("Arial", 20),
            text_color="#333333"
        )
        date_label.place(x=60, rely=0.5, anchor="w")

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

        # Detailed info frame
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

        quantity_used_btn = ctk.CTkButton(
            contact_options_panel,
            text="Quantity Used",
            font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_quantity_used_info
        )
        quantity_used_btn.place(x=80, y=290)

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
            command=self.open_edit_window,
            hover_color="#013B50")
        self.edit_button_detailed.place(x=1050, y=10)

        self.button_frame.place(x=20, y=50, anchor="nw")  
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)

        self.populate_table(self.fetch_patient_data())

    # Navbar methods 
    def toggle_dropdown(self):
        if self.dropdown_visible:
            self.dropdown_frame.place_forget()
        else:
            x = self.winfo_rootx() + self.winfo_width() - 180
            y = self.winfo_rooty() + 90
            self.dropdown_frame.place(x=x, y=y)
            self.dropdown_frame.lift() 
        self.dropdown_visible = not self.dropdown_visible

    def open_settings(self):
        print("Opening account settings...")

    def logout(self):
        print("Logging out...")
    
    def open_patient_history(self):
        self.patient_history_window = PatientHistory(self.master)
        self.patient_history_window.place(x=60, y=10)

        patient_id = self.patient_id_value.cget("text")

        patient_family_history = DataRetrieval.patient_family_history(patient_id)
        patient_medical_history = DataRetrieval.patient_medical_history(patient_id)
        patient_other_history = DataRetrieval.patient_other_history(patient_id)

        self.patient_history_window.family_history.display_family_history(patient_family_history)
        self.patient_history_window.medical_history.display_medical_history(patient_medical_history)
        self.patient_history_window.other_history.display_other_history(patient_other_history)

    def open_medication(self):
        self.medication_window = Medication(self.master)
        self.medication_window.place(x=60, y=10)
        self.medication_window.medication_info(self.patient_id_value.cget("text"))

    def open_contact_info(self):
        self.contact_info_window = ContactInfoRelativeInfo(self.master)
        self.contact_info_window.place(x=60, y=10)
        self.contact_info_window.contact_relative_info(self.patient_id_value.cget("text"))

    def open_quantity_used_info(self):
        self.quantity_used_window = QuantityUsedInfo(self.master)
        self.quantity_used_window.place(x=60, y=10)

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

            """ContactInfoRelativeInfo().contact_relative_info(patient_id)
            FamilyHistory().family_history_info(patient_id)
            MedicalHistory().medical_history_info(patient_id)
            OtherHistory().other_history_info(patient_id)
            Medication().medication_info(patient_id)"""

            threading.Thread(target=lambda: self.show_detailed_info(patient_id)).start()

    def show_detailed_info(self, patient_id):
        self.table_frame.place_forget()
        self.button_frame.place_forget()
        self.navbar.pack_forget()
        self.patient_id_value.configure(text=patient_id)
        self.display_patient_id(patient_id)
        
        try:
            get_patient_info_data = DataRetrieval.patient_info_data(patient_id)
            get_patient_philhealth_data = DataRetrieval.patient_philhealth_data(patient_id)

            if get_patient_info_data:
                self.display_patient_basic_info(get_patient_info_data)
                print("patient info: ", get_patient_info_data)
            else:
                messagebox.showwarning("No Data", "Patient record not found")

            if get_patient_philhealth_data:
                self.display_patient_philhealth_info(get_patient_philhealth_data)
                print("patient philhealth info: ", get_patient_philhealth_data)
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
        self.button_frame.place(x=20, y=50, anchor="nw") 
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)

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
        self.button_frame.place(x=20, y=50, anchor="nw") 
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8) 
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.populate_table(self.fetch_patient_data())

    def enable_buttons(self):
        self.add_button.configure(state="normal")
        self.edit_button_detailed.configure(state="normal")

    def disable_buttons(self):
        self.add_button.configure(state="disabled")
        self.edit_button_detailed.configure(state="disabled")

    def open_add_window(self, data=None):
        self.disable_buttons()
        self.open_input_window(PatientInfoWindow, data)

    def open_edit_window(self, data=None):
        self.disable_buttons()
        self.open_input_window(PatientInfoWindow, data)

class QuantityUsedInfo(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=980, height=400, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(self, width=20, fg_color="#1A374D", corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self, text="Quantity Used", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=40, y=20)

        self.quantity_used_header = ctk.CTkLabel(self, text="Quantity Used", font=("Merriweather", 16))
        self.quantity_used_header.place(x=60, y=70)

        self.quantity_used_labels = []
        y_position = 100
        for _ in range(10):
            label = ctk.CTkLabel(self, text="", font=("Merriweather", 13), text_color="black")
            label.place(x=60, y=y_position)
            self.quantity_used_labels.append(label)
            y_position += 30

        self.exit_button = create_exit_button(self, command=self.exit_panel)
        self.exit_button.place(x=900, y=15)

    def exit_panel(self):
        print("Quantity Used Info closed")
        self.place_forget()

class PatientHistory(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1443, height=1000, fg_color="white", corner_radius=20, **kwargs)
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
        super().__init__(master, width=980, height=400, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(self, width=20, fg_color="#1A374D", corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self, text="Medication", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=40, y=20)

        self.medication_header = ctk.CTkLabel(self, text="Drugs Taken", font=("Merriweather", 16))
        self.medication_header.place(x=60, y=70)

        self.medication_labels = []
        y_position = 100
        for _ in range(10):
            label = ctk.CTkLabel(self, text="", font=("Merriweather", 13), text_color="black")
            label.place(x=60, y=y_position)
            self.medication_labels.append(label)
            y_position += 30

        self.exit_button = create_exit_button(self, command=self.exit_panel)
        self.exit_button.place(x=900, y=15)

    def exit_panel(self):
        print("Contact and Relative Info closed")
        self.place_forget()

    def medication_info(self, patient_id):
        try:
            medication_data = DataRetrieval.patient_medicines(patient_id)
            print("Medications: ", medication_data)

            if medication_data:
                self.display_medications(medication_data)
            else:
                print("No Data", "No medications found for this patient.")
        except Exception as e:
            print(f"[Error] Failed to retrieve medication info: {e}")

    def display_medications(self, meds):
        for label in self.medication_labels:
            label.configure(text="")

        for i, med in enumerate(meds):
            if i < len(self.medication_labels):
                self.medication_labels[i].configure(text=f"• {med[0]}")

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

    def contact_relative_info(self, patient_id):
        try:
            contact_data = DataRetrieval.patient_contact_data(patient_id)
            relative_data = DataRetrieval.patient_relative_data(patient_id)
            print("contact: ", contact_data)
            print("relative: ", relative_data)

            if contact_data:
                contact_labels = [
                    self.last_name_value,
                    self.first_name_value,
                    self.middle_name_value,
                    self.contact_number_value,
                    self.relationship_value,
                    self.address_value
                ]
                DataRetrieval.assign_retrieved_data(contact_labels, contact_data)
            else:
                messagebox.showwarning("No Data", "Contact information not found.")

            if relative_data:
                relative_labels = [
                    self.relative_last_name_value,
                    self.relative_first_name_value,
                    self.relative_middle_name_value,
                    self.relative_contact_number_value,
                    self.relative_address_value
                ]
                DataRetrieval.assign_retrieved_data(relative_labels, relative_data)
            else:
                messagebox.showwarning("No Data", "Relative information not found.")

        except Exception as e:
            print(f"[Error] Failed to retrieve contact/relative info: {e}")

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
            print("patient family history: ", patient_family_history)

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
            print("patient medical history: ", patient_medical_history)
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

        self.left_bar = ctk.CTkFrame(self, width=20, fg_color="#68EDC6", corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        y_offset = 20
        spacing = 40

        def add_label_pair(text, y):
            label = ctk.CTkLabel(self, text=text, font=("Merriweather", 14))
            label.place(x=30, y=y)
            info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
            info.place(x=50, y=y + 25)
            return info

        self.hpi_info = add_label_pair("History of Present Illness", y_offset)
        y_offset += 70

        self.pmh_info = add_label_pair("Pertinent Past Medical History", y_offset)
        y_offset += 70

        labels = ["Date first diagnosed having kidney disease", "Date of First Dialysis", "Mode", "Access Type"]
        x_positions = [30, 360, 660, 900]

        for i, text in enumerate(labels):
            label = ctk.CTkLabel(self, text=text, font=("Merriweather", 14))
            label.place(x=x_positions[i], y=y_offset)

        y_offset += 25

        self.kidney_disease_date_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.kidney_disease_date_info.place(x=x_positions[0], y=y_offset)
        self.dialysis_date_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.dialysis_date_info.place(x=x_positions[1], y=y_offset)
        self.mode_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.mode_info.place(x=x_positions[2], y=y_offset)
        self.access_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.access_info.place(x=x_positions[3], y=y_offset)

        y_offset += 60

        chd_label = ctk.CTkLabel(self, text="Date of First Chronic Hemodialysis (*Leave NA if not)", font=("Merriweather", 14))
        chd_label.place(x=30, y=y_offset)
        clinical_label = ctk.CTkLabel(self, text="Clinical Impression", font=("Merriweather", 14))
        clinical_label.place(x=660, y=y_offset)

        y_offset += 25

        self.chronic_hemo_date_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.chronic_hemo_date_info.place(x=30, y=y_offset)
        self.clinical_impression_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.clinical_impression_info.place(x=660, y=y_offset)

    def other_history_info(self, patient_id):
        try:
            other_history = DataRetrieval.patient_other_history(patient_id)
            print("patient other history: ", other_history)
            if other_history:
                self.display_other_history(other_history)
            else:
                messagebox.showwarning("No Data", "Patient record not found")
        except Exception as e:
            print(e)

    def display_other_history(self, data):
        labels = [
            self.hpi_info,
            self.pmh_info,
            self.kidney_disease_date_info,
            self.dialysis_date_info,
            self.mode_info,
            self.access_info,
            self.chronic_hemo_date_info,
            self.clinical_impression_info
        ]
        DataRetrieval.assign_retrieved_data(labels, data)

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
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state

        self.navbar = ctk.CTkFrame(self, fg_color="white", height=130)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)
        self.navbar.configure(border_width=0, border_color="black")

        self.dropdown_visible = False 

        self.dropdown_frame = ctk.CTkFrame(self.navbar, fg_color="#f0f0f0", corner_radius=8, width=150, height=100)
        self.dropdown_frame.configure(border_width=1, border_color="gray")
        self.dropdown_frame.place_forget()

        self.namev2_label = ctk.CTkLabel(self.navbar, text="Tristan Lopez!", text_color="black", font=("Arial", 30, "bold"))
        self.namev2_label.place(relx=0.85, rely=0.5, anchor="e")

        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))

        icon_y = 62

        notif_btn = ctk.CTkButton(self.navbar, image=notif_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5")
        notif_btn.place(relx=1.0, x=-110, y=icon_y, anchor="center")

        settings_btn = ctk.CTkButton(self.navbar, image=settings_img, text="", width=40, height=40, fg_color="transparent", hover_color="#f5f5f5", command=self.toggle_dropdown)
        settings_btn.place(relx=1.0, x=-160, y=icon_y, anchor="center")

        ctk.CTkButton(self.dropdown_frame, text="Account Settings", width=140, command=self.open_settings).pack(pady=5)
        ctk.CTkButton(self.dropdown_frame, text="Log Out", width=140, command=self.logout).pack(pady=5)

        self.bottom_line = ctk.CTkFrame(self.navbar, height=1.5, fg_color="black")
        self.bottom_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        
        output_font = ("Merriweather", 15)
        label_font = ("Merriweather Sans bold", 15)
        button_font = ("Merriweather Bold",20)
        title_font = ("Merriweather Bold",20)

        style = ttk.Style()
        style.configure("Treeview", font=label_font, rowheight=35)
        style.configure("Treeview.Heading", font=label_font)
        style.map("Treeview", background=[("selected", "#68EDC6")])

        self.hovered_row = None
        self.selected_supply_id = None
        self.selected_supply_data = None  
        
        # Button Frame
        self.button_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")

         # Add Button
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Add",
            font=ctk.CTkFont("Arial", 16, "bold"),
            command=self.open_add_window,
            width=180,  
            height=50    
        )
        self.add_button.pack(side="left", padx=10)

        # Guide Button
        self.guide_button = ctk.CTkButton(
            self.button_frame,
            text="Guide",
            font=ctk.CTkFont("Arial", 16, "bold"),
            width=180,
            height=50
        )
        self.guide_button.pack(side="left", padx=10)

         # Search container
        self.search_container = ctk.CTkFrame(
            self.navbar, 
            fg_color="white", 
            corner_radius=25,
            width=300,
            height=50,
            border_width=2.5,
            border_color="#E0E0E0"
        )
        self.search_container.place(x=450, y=70, anchor="w")

        # Search icon
        try:
            search_img = ctk.CTkImage(light_image=Image.open("assets/search.png"), size=(24, 24))
            search_icon = ctk.CTkLabel(self.search_container, image=search_img, text="")
            search_icon.place(x=15, rely=0.5, anchor="w")
        except:
            search_icon = ctk.CTkLabel(
                self.search_container, 
                text="🔍", 
                font=("Arial", 16),
                text_color="#666666"
            )
            search_icon.place(x=15, rely=0.5, anchor="w")

        # Search entry
        self.search_entry = ctk.CTkEntry(   
            self.search_container,
            placeholder_text="Search patient",
            width=170,
            height=40,
            border_width=0,
            fg_color="transparent",
            font=("Arial", 14),
            text_color="#333333",
            placeholder_text_color="#999999"
        )
        self.search_entry.place(x=50, rely=0.5, anchor="w")

        # calendar container
        self.calendar_container = ctk.CTkFrame(
            self.navbar, 
            fg_color="white", 
            corner_radius=25,
            width=250,
            height=50,
            border_width=2.5,
            border_color="#E0E0E0"
        )
        self.calendar_container.place(x=810, y=70, anchor="w")

        # calendar icon
        try:
            calendar_img = ctk.CTkImage(light_image=Image.open("assets/calendar.png"), size=(30, 30))
            calendar_icon = ctk.CTkLabel(self.calendar_container, image=calendar_img, text="")
            calendar_icon.place(x=15, rely=0.5, anchor="w")
        except:
            calendar_icon = ctk.CTkLabel(
                self.calendar_container,
                text="📅",
                font=("Arial", 16),
                text_color="#666666"
            )
            calendar_icon.place(x=25, rely=0.5, anchor="w")

        # Get today's date
        today_date = datetime.datetime.now().strftime("%B %d, %Y") 

        # date label beside the icon
        date_label = ctk.CTkLabel(
            self.calendar_container,
            text=today_date,
            font=("Arial", 20),
            text_color="#333333"
        )
        date_label.place(x=60, rely=0.5, anchor="w")

        # Table Frame
        self.table_frame = ctk.CTkFrame(self, fg_color="#1A374D", border_width=2, border_color="black")

        tree_container = ctk.CTkFrame(self.table_frame, fg_color="black")
        tree_container.pack(fill="both", expand=True, padx=1, pady=1)

        columns = ("item_id", "item_name", "category", "current_stock", "restock_date", "date_registered")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        self.tree.pack(side="left", fill="both", expand=True)

        headers = [
            ("ITEM ID", 120),
            ("ITEM NAME", 180),
            ("CATEGORY", 140),
            ("REMAINING STOCK", 150),
            ("DATE RESTOCKED", 150),
            ("DATE REGISTERED", 150),
        ]
        
        for (text, width), col in zip(headers, columns):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ctk.CTkScrollbar(tree_container, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.populate_table(self.fetch_supply_data())
        self.Main_Supply_Frame = ctk.CTkFrame(self, fg_color="#E8FBFC")

        self.back_button = ctk.CTkButton(self.Main_Supply_Frame, text="Back", font=button_font,
            corner_radius=20,
            width=200,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.show_table_view
        )
        self.back_button.place(x=40, y=30)

        # Edit Button
        self.output_edit_button = ctk.CTkButton(
            self.Main_Supply_Frame,
            text="Edit",
            font=button_font,
            corner_radius=20,
            width=200,
            height=40,
            fg_color="#FF8C00",
            hover_color="#FF7F00",
            command=self.open_edit_window 
        )
        self.output_edit_button.place(x=260, y=30)

        self.upload_button = ctk.CTkButton(self.Main_Supply_Frame, text="Upload Photo", font=button_font,
            corner_radius=20,
            width=200,
            height=40,
            fg_color="#00C88D",
            hover_color="#013B50")
        self.upload_button.place(x=1100, y=30)

        # Photo Frame
        self.Suppyphotoframe = ctk.CTkFrame(self.Main_Supply_Frame, 
            width=400,
            height=400,
            fg_color="white",
            corner_radius=20
        )
        self.Suppyphotoframe.place(x=50,y=120)

        self.top_frame = ctk.CTkFrame(
            self.Suppyphotoframe,
            width=400,
            height=250,
            fg_color="#68EDC6",
            corner_radius=0
        )
        self.top_frame.place(x=0, y=0)
        
        # Supply ID Label
        self.supply_id_label = ctk.CTkLabel(
            self.Suppyphotoframe,
            text="Supply ID",
            font=label_font,
            text_color="black",
        )
        self.supply_id_label.place(relx=0.5, rely=0.70, anchor="center")

        # Supply ID Output
        self.supply_id_value = ctk.CTkLabel(
            self.Suppyphotoframe,
            text="",
            font=output_font,
            text_color="black"
        )
        self.supply_id_value.place(relx=0.5, rely=0.80, anchor="center")

        # Supply Info Frame
        supply_info_frame = ctk.CTkFrame(
            self.Main_Supply_Frame,
            width=950,
            height=300,
            fg_color="white",
            corner_radius=20
        )
        supply_info_frame.place(x=600, y=120) 

        left_bar = ctk.CTkFrame(
            supply_info_frame,
            width=20,
            height=300,
            fg_color="#68EDC6",
            bg_color="white",
            corner_radius=20
        )
        left_bar.place(x=0, y=0)

        Supply_title_label = ctk.CTkLabel(supply_info_frame, text="Supply Info", font=title_font)
        Supply_title_label.place(x=40, y=50)

        # Supply Name Label and Output
        self.Supply_Name_Label = ctk.CTkLabel(supply_info_frame, text="Supply Name", font=label_font)
        self.Supply_Name_Label.place(x=80,y=100)
        self.Supply_Name_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.Supply_Name_Output.place(x=80,y=130)

        # Category Label and Output
        self.Category_Label = ctk.CTkLabel(supply_info_frame, text="Category", font=label_font)
        self.Category_Label.place(x=300,y=100)
        self.Category_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.Category_Output.place(x=300,y=130)

        # Last Restock Quantity Label and Output
        self.currentstock_Label = ctk.CTkLabel(supply_info_frame, text="Remaining Stock", font=label_font)
        self.currentstock_Label.place(x=520,y=100)
        self.currentstock_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.currentstock_Output.place(x=520,y=130)

        # Last Restocked Date Label and Output
        self.LastRestock_Date_Label = ctk.CTkLabel(supply_info_frame, text="Last Restock Date", font=label_font)
        self.LastRestock_Date_Label.place(x=740,y=100)
        self.LastRestock_Date_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.LastRestock_Date_Output.place(x=740,y=130)

        # Date Registered Label and Output
        self.Registered_Date_Label = ctk.CTkLabel(supply_info_frame, text="Date Registered", font=label_font)
        self.Registered_Date_Label.place(x=80,y=200)
        self.Registered_Date_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.Registered_Date_Output.place(x=80,y=230)

        # Average Weekly Usage Label and Output
        self.Average_Weekly_Usage_Label = ctk.CTkLabel(supply_info_frame, text="Average Weekly Usage", font=label_font)
        self.Average_Weekly_Usage_Label.place(x=300,y=200)
        self.Average_Weekly_Usage_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.Average_Weekly_Usage_Output.place(x=300,y=230)

        # Delivery Time Label and Output
        self.Delivery_Time_Label = ctk.CTkLabel(supply_info_frame, text="Delivery Time", font=label_font)
        self.Delivery_Time_Label.place(x=520,y=200)
        self.Delivery_Time_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.Delivery_Time_Output.place(x=520,y=230)

        # Storage Meter Frame
        storage_meter_frame = ctk.CTkFrame(
            self.Main_Supply_Frame,
            width=950,
            height=250,
            fg_color="white",
            corner_radius=20
        )
        storage_meter_frame.place(x=600, y=430)

        left_bar = ctk.CTkFrame(
            storage_meter_frame,
            width=20,
            height=250,
            fg_color="#68EDC6",
            bg_color="white",
            corner_radius=20
        )
        left_bar.place(x=0, y=0)

        storageMeter_title_label = ctk.CTkLabel(storage_meter_frame, text="Inventory Quantity", font=title_font)
        storageMeter_title_label.place(x=40, y=20)

        self.StorageMeter = ctk.CTkProgressBar(storage_meter_frame, width=800, height=40, fg_color="white", progress_color="green", border_width=1, border_color="black")
        self.StorageMeter.place(x=100,y=100)

        self.Status_Label = ctk.CTkLabel(storage_meter_frame, text="Status :", font=label_font)
        self.Status_Label.place(x=100,y=180)

        self.Status_Output = ctk.CTkLabel(storage_meter_frame, text="", font=label_font)
        self.Status_Output.place(x=180,y=180)

        self.Available_Items_Label = ctk.CTkLabel(storage_meter_frame, text="Available Items :", font=label_font)
        self.Available_Items_Label.place(x=650,y=180)

        self.Remaining_Output = ctk.CTkLabel(storage_meter_frame, text="", font=label_font)
        self.Remaining_Output.place(x=790,y=180)

        self.Seperator_Output = ctk.CTkLabel(storage_meter_frame, text="/", font=label_font)
        self.Seperator_Output.place(x=830,y=180)

        self.Capacity_Output = ctk.CTkLabel(storage_meter_frame, text="200", font=label_font)
        self.Capacity_Output.place(x=850,y=180)

        # Edit Stock Frame
        self.Edit_Stock_Frame = ctk.CTkFrame(self.Main_Supply_Frame,
                width=450,
                height=350,
                fg_color="white",
                corner_radius=20)
        self.Edit_Stock_Frame.place(x=50, y=700)

        self.Top_bar = ctk.CTkFrame(self.Edit_Stock_Frame,
                width=450,
                height=20,
                fg_color="#68EDC6")
        self.Top_bar.place(y=0)

        # Edit Stock Button
        self.Edit_Stock_Button = ctk.CTkButton(
            self.Edit_Stock_Frame,
            text="Edit Stock",
            width=120,
            height=35,
            fg_color="#68EDC6",
            text_color="black",
            corner_radius=10,
            hover_color="#5DD4B3",
            command=self.open_edit_stock_window
        )
        self.Edit_Stock_Button.place(x=165, y=50)

        # Quantity Used Button
        self.Quantity_Used_Button = ctk.CTkButton(
            self.Edit_Stock_Frame,
            text="Quantity Used",
            width=120,
            height=35,
            fg_color="#FFA07A",  # Optional color
            text_color="black",
            corner_radius=10,
            hover_color="#FF8C69",
            command=self.open_quantity_used_window  
        )
        self.Quantity_Used_Button.place(x=165, y=100)

        # Restock Log Button
        self.Restock_Log_Button = ctk.CTkButton(
            self.Edit_Stock_Frame,
            text="Restock Log",
            width=120,
            height=35,
            fg_color="#ADD8E6",  # Optional color
            text_color="black",
            corner_radius=10,
            hover_color="#87CEEB",
            command=self.open_restock_log_window  
        )
        self.Restock_Log_Button.place(x=165, y=150)

        # Daily Usage Frame
        self.Daily_Usage_Frame = ctk.CTkFrame(self.Main_Supply_Frame,
                width=450,
                height=350,
                fg_color="white",
                corner_radius=20)
        self.Daily_Usage_Frame.place(x=600,y=700)

        self.Top_bar = ctk.CTkFrame(self.Daily_Usage_Frame,
                width=450,
                height=20,
                fg_color="#68EDC6")
        self.Top_bar.place(y=0)

        Daily_Usage_Title = ctk.CTkLabel(self.Daily_Usage_Frame, text="Daily Usage", font=title_font)
        Daily_Usage_Title.place(x=150, y=40)

        # Weekly Usage Frame
        self.Weekly_Usage_Frame = ctk.CTkFrame(self.Main_Supply_Frame,
                width=450,
                height=350,
                fg_color="white",
                corner_radius=20)
        self.Weekly_Usage_Frame.place(x=1100,y=700)

        Weekly_Usage_Title = ctk.CTkLabel(self.Weekly_Usage_Frame, text="Weekly Usage", font=title_font)
        Weekly_Usage_Title.place(x=150, y=40)

        self.Top_bar2 = ctk.CTkFrame(self.Weekly_Usage_Frame,
                width=450,
                height=20,
                fg_color="#68EDC6")
        self.Top_bar2.place(y=0)

        self.button_frame.place(x=20, y=50, anchor="nw")  
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)

    # Navbar methods 
    def toggle_dropdown(self):
        if self.dropdown_visible:
            self.dropdown_frame.place_forget()
        else:
            x = self.winfo_rootx() + self.winfo_width() - 180
            y = self.winfo_rooty() + 90
            self.dropdown_frame.place(x=x, y=y)
            self.dropdown_frame.lift() 
        self.dropdown_visible = not self.dropdown_visible

    def open_settings(self):
        print("Opening account settings...")

    def logout(self):
        print("Logging out...")

    def open_edit_stock_window(self):
        if hasattr(self, 'selected_supply_id') and self.selected_supply_id:
            edit_stock_window = EditStockWindow(self, self.selected_supply_id)
            edit_stock_window.grab_set()
            edit_stock_window.focus_force()
        else:
            print("Please select a supply item first.")

    def fetch_supply_data(self):
        """Fetch supply data from database including all fields"""
        try:
            connect = db()
            cursor = connect.cursor()
            cursor.execute("""
                SELECT item_id, item_name, category, current_stock, restock_date, 
                    date_registered, restock_quantity, average_daily_usage, average_weekly_usage, 
                    average_monthly_usage, delivery_time_days, stock_level_status, max_supply
                FROM supply
            """)
            return cursor.fetchall()
        except Exception as e:
            print("Error fetching supply data:", e)
            return []

    def populate_table(self, data):
        """Populate the table with supply data"""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insert new data
        for row in data:
            self.tree.insert("", "end", values=row)

    def on_row_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            supply_data = self.tree.item(item, 'values')
            self.selected_supply_data = {
                'item_id': supply_data[0],
                'item_name': supply_data[1],
                'category': supply_data[2],
                'current_stock': supply_data[3],  
                'restock_date': supply_data[4],
                'date_registered': supply_data[5],
                'restock_quantity': supply_data[6],  
                'average_daily_usage': supply_data[7] if len(supply_data) > 7 and supply_data[7] else 0,
                'average_weekly_usage': supply_data[8] if len(supply_data) > 8 and supply_data[8] else 0,
                'average_monthly_usage': supply_data[9] if len(supply_data) > 9 and supply_data[9] else 0,
                'delivery_time_days': supply_data[10] if len(supply_data) > 10 and supply_data[10] else 0,
                'stock_level_status': supply_data[11] if len(supply_data) > 11 else '',
                'max_supply': supply_data[12] if len(supply_data) > 12 and supply_data[12] else 0
            }

    def open_quantity_used_window(self):
        if hasattr(self, 'selected_supply_id') and self.selected_supply_id:
            quantity_used_window = QuantityUsedLogsWindow(self, self.selected_supply_id)
            quantity_used_window.grab_set()
            quantity_used_window.focus_force()
        else:
            print("Please select a supply item first.")

    def open_restock_log_window(self):
        if hasattr(self, 'selected_supply_id') and self.selected_supply_id:
            restock_log_window = RestockLogWindow(self, self.selected_supply_id)
            restock_log_window.grab_set()
            restock_log_window.focus_force()
        else:
            print("Please select a supply item first.")

    def on_row_click(self, event):
        """Handle row click to show detailed info"""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            supply_data = self.tree.item(item_id, 'values')
            supply_id = supply_data[0]
            print("Supply ID:", supply_id)
            
            self.selected_supply_id = supply_id
            self.show_detailed_info(supply_data)

    def show_detailed_info(self, supply_data):
        self.table_frame.place_forget()
        self.button_frame.place_forget()
        self.navbar.pack_forget()
        
        # Update supply ID display
        self.supply_id_value.configure(text=supply_data[0])
        
        # Update supply info
        self.Supply_Name_Output.configure(text=supply_data[1])
        self.Category_Output.configure(text=supply_data[2])
        
        # Use current_stock as remaining stock
        current_stock = supply_data[3] if len(supply_data) > 3 else 0
        restock_date = supply_data[4] if supply_data[4] else "N/A"
        date_registered = supply_data[5] if len(supply_data) > 5 else "N/A"
        average_weekly_usage = supply_data[8] if len(supply_data) > 8 else "N/A"
        delivery_time_days = supply_data[10] if len(supply_data) > 10 else "N/A"
        
        # Use max_supply but default to 200 if max_supply <= 200
        max_supply = supply_data[12] if len(supply_data) > 12 and supply_data[12] else 0
        
        # Display current_stock as remaining stock
        self.currentstock_Output.configure(text=str(current_stock))
        self.LastRestock_Date_Output.configure(text=restock_date)
        self.Registered_Date_Output.configure(text=date_registered)
        self.Average_Weekly_Usage_Output.configure(text=str(average_weekly_usage))
        self.Delivery_Time_Output.configure(text=str(delivery_time_days))
        
        # For the meter and status calculations
        try:
            # Convert current_stock to int 
            if current_stock and current_stock != 'None' and str(current_stock).strip():
                current_stock_val = int(current_stock)
            else:
                current_stock_val = 0
                
            # Convert max_supply to int 
            if max_supply and max_supply != 'None' and str(max_supply).strip():
                max_supply_val = int(max_supply)
            else:
                max_supply_val = 0
                
        except (ValueError, TypeError) as e:
            print(f"DEBUG: Conversion error: {e}")
            print(f"DEBUG: current_stock value causing error: '{current_stock}'")
            print(f"DEBUG: max_supply value causing error: '{max_supply}'")
            current_stock_val = 0
            max_supply_val = 0

        # Always use 200 as the base capacity for progress calculation
        base_capacity = 200

        # Always show 200 as the capacity (unless max_supply is specifically higher than 200)
        if max_supply_val > base_capacity:
            capacity_display = max_supply_val
        else:
            capacity_display = base_capacity

        # Update the display
        self.Remaining_Output.configure(text=str(current_stock_val))
        self.Capacity_Output.configure(text=str(capacity_display))

        # Calculate progress based on the base capacity of 200
        progress_value = current_stock_val / base_capacity if base_capacity > 0 else 0
        # Ensure progress doesn't exceed 1.0 (100%)
        progress_value = min(progress_value, 1.0)
        self.StorageMeter.set(progress_value)

        # Calculate stock percentage for status based on the base capacity of 200
        stock_percentage = current_stock_val / base_capacity if base_capacity > 0 else 0

        # Determine status and colors based on percentage
        if stock_percentage == 0:
            self.Status_Output.configure(text="Out of Stock", text_color="#8B0000") 
            self.Remaining_Output.configure(text_color="#8B0000")
            self.StorageMeter.configure(progress_color="#8B0000")
        elif stock_percentage <= 0.25:  # 0-50 items (25% of 200)
            self.Status_Output.configure(text="Very Low Stocks", text_color="red")
            self.Remaining_Output.configure(text_color="red")
            self.StorageMeter.configure(progress_color="red")
        elif stock_percentage <= 0.50:  # 51-100 items (50% of 200)
            self.Status_Output.configure(text="Low Stocks", text_color="orange")
            self.Remaining_Output.configure(text_color="orange")
            self.StorageMeter.configure(progress_color="orange")
        else:  # 101+ items (above 50% of 200)
            self.Status_Output.configure(text="On Stocks", text_color="green")
            self.Remaining_Output.configure(text_color="green")
            self.StorageMeter.configure(progress_color="green")

        self.Main_Supply_Frame.place(x=0, y=0, relwidth=1, relheight=1)

    def show_table_view(self):
        """Return to table view"""
        self.Main_Supply_Frame.place_forget()
        self.button_frame.place(x=20, y=50, anchor="nw")  
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)

    def refresh_table(self):
        """Refresh the table with updated data"""
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)
        self.button_frame.place(x=20, y=50, anchor="nw")
        self.navbar.pack(fill="x", side="top")
        self.populate_table(self.fetch_supply_data())

    def open_add_window(self):
        add_window = SupplyWindow(self)
        add_window.grab_set()
        add_window.focus_force()
        self.wait_window(add_window)
        self.refresh_table()

    # FOR TESTING
    def clear_supply_table(self):
        """Clear all supply data from the table and reset ID to start from 1"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Delete all records from supply table
            cursor.execute("DELETE FROM supply")
 
            cursor.execute("ALTER TABLE supply AUTO_INCREMENT = 1")

            connect.commit()
            
            print("Supply table cleared successfully. Next ID will start from 1.")

            self.populate_table([])
            if hasattr(self, 'Main_Supply_Frame'):
                self.show_table_view()
                
            cursor.close()
            connect.close()
            
            return True
            
        except Exception as e:
            print(f"Error clearing supply table: {e}")
            return False

    def open_edit_window(self):
        """Open edit window with current detailed supply data"""
        if not self.selected_supply_data:
            CTkMessageBox.show_error("Edit Error", "No supply data available to edit.", parent=self)
            return

        edit_window = SupplyWindow(self, edit_data=self.selected_supply_data)
        edit_window.grab_set()
        edit_window.focus_force()
        self.wait_window(edit_window)
        
        # Refresh both table and detailed view
        self.refresh_table()
        
        if hasattr(self, 'selected_supply_id') and self.selected_supply_id:
            self.refresh_detailed_view()

    def refresh_detailed_view(self):
        """Refresh the detailed view with updated data from database"""
        if not self.selected_supply_id:
            return
        
        try:
            connect = db()
            cursor = connect.cursor()
            cursor.execute("""
                SELECT item_id, item_name, category, current_stock, restock_date, 
                    date_registered, restock_quantity, average_daily_usage, average_weekly_usage, 
                    average_monthly_usage, delivery_time_days, stock_level_status, max_supply
                FROM supply
                WHERE item_id = %s
            """, (self.selected_supply_id,))
            
            updated_data = cursor.fetchone()
            if updated_data:
                self.selected_supply_data = {
                    'item_id': updated_data[0],
                    'item_name': updated_data[1],
                    'category': updated_data[2],
                    'current_stock': updated_data[3],
                    'restock_date': updated_data[4],
                    'date_registered': updated_data[5],
                    'restock_quantity': updated_data[6],
                    'average_daily_usage': updated_data[7] if updated_data[7] else 0,
                    'average_weekly_usage': updated_data[8] if updated_data[8] else 0,
                    'average_monthly_usage': updated_data[9] if updated_data[9] else 0,
                    'delivery_time_days': updated_data[10] if updated_data[10] else 0,
                    'stock_level_status': updated_data[11],
                    'max_supply': updated_data[12]
                }
                
                # Refresh the detailed view display
                self.show_detailed_info(updated_data)
                
            cursor.close()
            connect.close()
            
        except Exception as e:
            print("Error refreshing detailed view:", e)

class ReportPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")
        label = ctk.CTkLabel(self, text="Report Page", font=("Arial", 24))
        label.pack(pady=100)

class MaintenancePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")

        output_font = ("Merriweather Sans Bold", 15)
        label_font = ("Merriweather", 15)
        time_label_font = ("Merriweather", 12)
        time_output_font = ("Merriweather Sans Bold", 12)
        button_font = ("Merriweather Bold",15)
        SubTitle_font = ("Merriweather Bold",20)
        Sub_Sub_Title_font = ("Merriweather Bold",15)
        Title_font = ("Merriweather Bold",25)
        Messagebox_font=("Merriweather Sans Bold",15)

        #---------------------------------LEFT-----------------------------------------

        #Maintenance Frame
        Maintenance_MainFrame = ctk.CTkFrame (self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=1000,
                                            height=450,
                                            corner_radius=20
                                            )
        Maintenance_MainFrame.place(x=100,y=180)

        leftbar_frame = ctk.CTkFrame(Maintenance_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#1A374D" ,
                                     width=25,
                                     height=450,
                                     corner_radius=20 )
        leftbar_frame.place(x=0)
        label_Title = ctk.CTkLabel(Maintenance_MainFrame, bg_color="transparent",text="Maintenance",text_color="black",font=Title_font)
        label_Title.place(x=100,y=50)

        #Option Frame
        option_frame = ctk.CTkFrame(Maintenance_MainFrame,
                                    bg_color="transparent" ,
                                    fg_color="#E8FBFC", 
                                    width=800, 
                                    height=180, 
                                    corner_radius=20)
        option_frame.place(x=100,y=150)

        leftbar_frame = ctk.CTkFrame(option_frame,
                                     bg_color="transparent",
                                     fg_color="#68EDC6" ,
                                     width=15,
                                     height=180,
                                     corner_radius=20 )
        leftbar_frame.place(x=0)

        Options_label = ctk.CTkLabel(option_frame,
                                     text="Options",
                                     text_color="black",
                                     bg_color="#FFFFFF",
                                     font=SubTitle_font)
        Options_label.place(x=40,y=30)


        #Current date Frame
        current_date_frame = ctk.CTkFrame(Maintenance_MainFrame,bg_color="transparent" ,fg_color="#E8FBFC", width=250, height=80, corner_radius=20)
        current_date_frame.place(x=100,y=350)

        leftbar_frame = ctk.CTkFrame(current_date_frame,
                                     bg_color="transparent",
                                     fg_color="#1E90FF",
                                     width=10,
                                     height=80,
                                     corner_radius=20 )
        leftbar_frame.place(x=0)

        Current_date_label = ctk.CTkLabel(current_date_frame,bg_color="#E8FBFC",text="Current Date :",text_color="black",font=time_label_font)
        Current_date_label.place(x=50,y=20)

        Current_date_output = ctk.CTkLabel(current_date_frame,bg_color="#E8FBFC",text="06/01/25",text_color="black",font=time_output_font)
        Current_date_output.place(x=150,y=20)

        Current_time_label = ctk.CTkLabel(current_date_frame,bg_color="#E8FBFC",text="Current time :",text_color="black",font=time_label_font)
        Current_time_label.place(x=50,y=50)

        Current_time_output = ctk.CTkLabel(current_date_frame,bg_color="#E8FBFC",text="20 : 00",text_color="black",font=time_output_font)
        Current_time_output.place(x=150,y=50)

        def update_time():
            now = datetime.datetime.now()
            Current_date_output.configure(text=now.strftime("%m - %d - %y"))
            Current_time_output.configure(text=now.strftime("%H : %M :%S"))
            self.after(1000, update_time)

        update_time() 
    

        #Last backup date Frame
        lastBackup_date_frame = ctk.CTkFrame(Maintenance_MainFrame,bg_color="transparent" ,fg_color="#E8FBFC", width=250, height=80, corner_radius=20,)
        lastBackup_date_frame.place(x=375,y=350)

        leftbar_frame = ctk.CTkFrame(lastBackup_date_frame,
                                     bg_color="transparent",
                                     fg_color="#28A745",
                                     width=10,
                                     height=80,
                                     corner_radius=20 )
        leftbar_frame.place(x=0)

        LastBackup_date_label = ctk.CTkLabel(lastBackup_date_frame,bg_color="#E8FBFC",text="Last Backup Date :",text_color="black",font=time_label_font)
        LastBackup_date_label.place(x=30,y=20)

        LastBackup_date_output = ctk.CTkLabel(lastBackup_date_frame,bg_color="#E8FBFC",text="",text_color="black",font=time_output_font)
        LastBackup_date_output.place(x=150,y=20)

        LastBackup_time_label = ctk.CTkLabel(lastBackup_date_frame,bg_color="#E8FBFC",text="Last Backup Time :",text_color="black",font=time_label_font)
        LastBackup_time_label.place(x=30,y=50)

        LastBackup_time_output = ctk.CTkLabel(lastBackup_date_frame,bg_color="#E8FBFC",text="",text_color="black",font=time_output_font)
        LastBackup_time_output.place(x=150,y=50)


        #Next backup date Frame
        NextBackup_date_frame = ctk.CTkFrame(Maintenance_MainFrame,bg_color="transparent" ,fg_color="#E8FBFC", width=250, height=80, corner_radius=20)
        NextBackup_date_frame.place(x=650,y=350)

        leftbar_frame = ctk.CTkFrame(NextBackup_date_frame,
                                     bg_color="transparent",
                                     fg_color="#FFA500",
                                     width=10,
                                     height=80,
                                     corner_radius=20 )
        leftbar_frame.place(x=0)

        NextBackup_date_label = ctk.CTkLabel(NextBackup_date_frame,bg_color="#E8FBFC",text="Next Backup Date :",text_color="black",font=time_label_font)
        NextBackup_date_label.place(x=30,y=20)

        NextBackup_date_output = ctk.CTkLabel(NextBackup_date_frame,bg_color="#E8FBFC",text="",text_color="black",font=time_output_font)
        NextBackup_date_output.place(x=150,y=20)

        NextBackup_time_label = ctk.CTkLabel(NextBackup_date_frame,bg_color="#E8FBFC",text="Next Backup Time :",text_color="black",font=time_label_font)
        NextBackup_time_label.place(x=30,y=50)

        NextBackup_time_output = ctk.CTkLabel(NextBackup_date_frame,bg_color="#E8FBFC",text="",text_color="black",font=time_output_font)
        NextBackup_time_output.place(x=150,y=50)

        def update_last_backup_time():
            now = datetime.datetime.now()
            LastBackup_date_output.configure(text=now.strftime("%Y-%m-%d"))
            LastBackup_time_output.configure(text=now.strftime("%H:%M:%S"))


        def manual_backup_action():
            update_last_backup_time
            CTkMessagebox(
                title="Backup Status",
                message="Manual backup was successful.",
                icon="check",
                option_1="OK",
                header=False,
                width=400,
                height=200,
                button_color="#68EDC6",
                button_text_color="white",
                button_hover_color="#1A374D",
                fg_color="white",
                bg_color="white",
                text_color="black",
                font=Messagebox_font
            )
            print("Manual Back-up was successful")

        
        ManualBackup_Button = ctk.CTkButton(option_frame,
                                            bg_color="transparent",
                                            fg_color="#00C88D",
                                            hover_color="#00B07B",
                                            width=180,
                                            height=70,
                                            corner_radius=20,
                                            text="Manual Backup",
                                            text_color="white",
                                            cursor="hand2",
                                            command=manual_backup_action,
                                            font=button_font)
        ManualBackup_Button.place(x=50,y=80)


        ScheduleBackup_Button = ctk.CTkButton(option_frame,
                                            bg_color="transparent",
                                            fg_color="#145266",
                                            hover_color="#1F6F88",
                                            width=180,
                                            height=70,
                                            corner_radius=20,
                                            text="Schedule Backup",
                                            text_color="white",
                                            cursor="hand2",
                                            font=button_font,
                                            )
        ScheduleBackup_Button.place(x=300,y=80)
        

        BackupLogs_Button = ctk.CTkButton(option_frame,
                                            bg_color="transparent",
                                            fg_color="#103047",
                                            hover_color="#25475A",
                                            width=180,
                                            height=70,
                                            corner_radius=20,
                                            text="View Full History",
                                            text_color="white",
                                            cursor="hand2",
                                            font=button_font)
        BackupLogs_Button.place(x=550,y=80)

        Maintenance_Logs_MainFrame = ctk.CTkFrame (self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=1000,
                                            height=350,
                                            corner_radius=20
                                            )
        Maintenance_Logs_MainFrame.place(x=100,y=650)

        label_Title = ctk.CTkLabel(Maintenance_Logs_MainFrame, bg_color="transparent",text="Latest Backup Logs",text_color="black",font=Title_font)
        label_Title.place(x=100,y=50)

        leftbar_frame = ctk.CTkFrame(Maintenance_Logs_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#1A374D" ,
                                     width=25,
                                     height=350,
                                     corner_radius=20 )
        leftbar_frame.place(x=0)


        
    #---------------------------------RIGHT-----------------------------------------

        #Storage Frame 
        Storage_Level_MainFrame = ctk.CTkFrame (self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=400,
                                            height=225,
                                            corner_radius=20
                                            )
        Storage_Level_MainFrame.place(x=1150,y=180)

        leftbar_frame = ctk.CTkFrame(Storage_Level_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#68EDC6",
                                     width=400,
                                     height=15,
                                     corner_radius=20 )
        leftbar_frame.place(y=0)

        label_Title = ctk.CTkLabel(Storage_Level_MainFrame, bg_color="transparent",text="Storage Space",text_color="black",font=Sub_Sub_Title_font)
        label_Title.place(x=30,y=40)

        current_path = os.getcwd()

        def get_disk_usage(path):
            usage = shutil.disk_usage(path)
            total = usage.total
            used = usage.used
            free = usage.free
            percent_used = used / total * 100
            return total, used, free, percent_used

        progress_bar = ctk.CTkProgressBar(Storage_Level_MainFrame, width=300,height=30)
        progress_bar.place(x=50, y=100)

      
        usage_label = ctk.CTkLabel(Storage_Level_MainFrame, 
                                bg_color="transparent",
                                text="", 
                                text_color="black",
                                font=time_output_font)
        usage_label.place(x=60, y=150)

    
        def update_disk_usage():
            total, used, free, percent_used = get_disk_usage(current_path)
            progress_bar.set(percent_used / 100)
            usage_label.configure(text=f"Used: {percent_used:.2f}%  |  Free: {free // (1024**3)} GB  |  Total: {total // (1024**3)} GB")
            
            self.after(5000, update_disk_usage)

        update_disk_usage()

        #Export Frame/Print Frame
        Print_MainFrame = ctk.CTkFrame (self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=400,
                                            height=225,
                                            corner_radius=20
                                            )
        Print_MainFrame.place(x=1150,y=450)

        leftbar_frame = ctk.CTkFrame(Print_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#68EDC6",
                                     width=400,
                                     height=15,
                                     corner_radius=20 )
        leftbar_frame.place(y=0)

        PrintPDF_Button = ctk.CTkButton(Print_MainFrame,
                                            bg_color="transparent",
                                            fg_color="#E63946",
                                            hover_color="#FF5C5C",
                                            width=200,
                                            height=40,
                                            corner_radius=20,
                                            text="Export PDF File",
                                            text_color="white",
                                            cursor="hand2",
                                            )
        PrintPDF_Button.place(x=100,y=90)


        PrintXLSXX_Button = ctk.CTkButton(Print_MainFrame,
                                            bg_color="transparent",
                                            fg_color="#2AA650",
                                            hover_color="#45C165",
                                            width=200,
                                            height=40,
                                            corner_radius=20,
                                            text="Export XLSXX File",
                                            text_color="white",
                                            cursor="hand2",
                                            
                                            )
        PrintXLSXX_Button.place(x=100,y=150)

        label_Title = ctk.CTkLabel(Print_MainFrame, bg_color="transparent",text="Export Backup Logs",text_color="black",font=Sub_Sub_Title_font)
        label_Title.place(x=30,y=40)

        #Weekly Usage of Backup Frame
        NumberofBackup_1week_MainFrame = ctk.CTkFrame (self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=400,
                                            height=275,
                                            corner_radius=20
                                            )
        NumberofBackup_1week_MainFrame.place(x=1150,y=720)

        leftbar_frame = ctk.CTkFrame(NumberofBackup_1week_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#68EDC6",
                                     width=400,
                                     height=15,
                                     corner_radius=20 )
        leftbar_frame.place(y=0)

        label_Title = ctk.CTkLabel(NumberofBackup_1week_MainFrame, bg_color="transparent",text="No. of Backups per Week",text_color="black",font=Sub_Sub_Title_font)
        label_Title.place(x=30,y=40)

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
            username = login_shared_states.get('logged_username', None)

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