import threading
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from components.Inputs import PatientInfoWindow
from backend.connector import db_connection as db
from components.buttons import CTkButtonSelectable
from components.input_supply import CTkMessageBox, EditStockWindow, EditUsageWindow, PatientQuantityUsedLogsWindow, QuantityUsedLogsWindow, SupplyWindow
from components.role_access_manager import RoleAccessManager
from components.state import login_shared_states
from backend.crud import retrieve_form_data, db_connection
import datetime 
from datetime import date, timedelta, time
import subprocess
from customtkinter import CTkInputDialog
import shutil
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import font_manager as fm
from dotenv import load_dotenv
import math
import calendar
from pages.pdf_report_generator import PDFReportGenerator

load_dotenv() 

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

report_shared_states = {
    'current_period': 'Overall'
}

class DataRetrieval():

    # =========== FOR PATIENT DATA RETRIEVAL =========== # 

    @staticmethod
    def patient_info_data(patient_id):
        columns = """patient_id, last_name, first_name, middle_name, status, 
                     access_type, birthdate, age, gender, height, civil_status, 
                     religion, address"""
        return retrieve_form_data(patient_id, 'patient_id', columns, table_name="patient_info")

    @staticmethod
    def patient_philhealth_data(patient_id):
        columns = """patient_id, is_senior, is_pwd, philhealth_number, 
                     membership_type, pwd_id, senior_id"""
        return retrieve_form_data(patient_id, 'patient_id', columns, table_name="patient_benefits")
    
    @staticmethod
    def patient_contact_data(patient_id):
        columns = """last_name, first_name, middle_name, 
                     contact_number, relationship, address"""
        return retrieve_form_data(patient_id, 'patient_id', columns, table_name="patient_contact")
    
    @staticmethod
    def patient_relative_data(patient_id):
        columns = """last_name, first_name, middle_name, 
                     contact_number, address"""
        return retrieve_form_data(patient_id, 'patient_id', columns, table_name="patient_relative")

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

        # Refresh recent patient data when navigating to Home page
        if page_name == "Home":
            self.pages["Home"].refresh_recent_patient()
            # refresh patient data and pie chart
            self.pages["Home"].refresh_patient_data_and_chart()
            
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)

        if page_name == "Patient":
            self.pages["Patient"].show_table_view()

    def refresh_all_patient_data(self):
        """Refresh both home page recent patient and patient page table"""
        try:
            # Refresh home page recent patient
            if hasattr(self, 'pages') and 'Home' in self.pages:
                home_page = self.pages['Home']
                if hasattr(home_page, 'refresh_recent_patient'):
                    home_page.refresh_recent_patient()
                    print("✅ Home page recent patient refreshed!")
                
                # refresh the pie chart data
                if hasattr(home_page, 'refresh_patient_data_and_chart'):
                    home_page.refresh_patient_data_and_chart()
            
            # Refresh patient page table
            if hasattr(self, 'pages') and 'Patient' in self.pages:
                patient_page = self.pages['Patient']
                if hasattr(patient_page, 'refresh_table'):
                    patient_page.refresh_table()
                    print("✅ Patient page table refreshed!")
                    
        except Exception as e:
            print(f"❌ Error refreshing patient data: {e}")

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
        self.highlight_selected(page_name)
        self.master.show_page(page_name)

    def disable_buttons(self):
        """Disable all sidebar buttons"""
        for button in self.buttons.values():
            button.configure(state="disabled")

    def enable_buttons(self):
        """Enable all sidebar buttons"""
        for button in self.buttons.values():
            button.configure(state="normal")

class SearchResultsFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=400, height=400, fg_color="white", corner_radius=10, **kwargs)
        self.parent = parent  # Store reference to parent
        self.place_forget()  # Initially hidden
        self.visible = False
        
        # Header Frame
        header_frame = ctk.CTkFrame(self, width=400, height=50, fg_color="#68EDC6", corner_radius=10)
        header_frame.place(x=0, y=0)
        
        header_title = ctk.CTkLabel(
            header_frame, 
            font=("Merriweather", 16, "bold"), 
            text="Search Results", 
            text_color="white"
        )
        header_title.place(x=20, y=15)
        
        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            width=30,
            height=30,
            text="✕",
            fg_color="transparent",
            hover_color="#5AA3A3",
            font=("Arial", 16),
            command=self.hide
        )
        close_btn.place(x=350, y=10)
        
        # Scrollable Results Frame
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            width=380,
            height=330,
            fg_color="#f8f9fa",
            corner_radius=0
        )
        self.results_frame.place(x=10, y=60)
        
        # No results label (initially hidden)
        self.no_results_label = ctk.CTkLabel(
            self.results_frame,
            text="No results found",
            font=("Arial", 14),
            text_color="#666666"
        )
        
    def show_results(self, search_text, results):
        """Display search results in the frame"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not results:
            # Show no results message
            self.no_results_label = ctk.CTkLabel(
                self.results_frame,
                text=f"No results found for '{search_text}'",
                font=("Arial", 14),
                text_color="#666666"
            )
            self.no_results_label.pack(pady=50)
        else:
            # Group results by type
            patients = []
            supplies = []
            
            for result in results:
                name, age, gender, access_type, category, record_type = result
                if record_type == 'patient':
                    patients.append({
                        'name': name,
                        'age': age,
                        'gender': gender,
                        'access_type': access_type
                    })
                elif record_type == 'supply':
                    supplies.append({
                        'name': name,
                        'category': category
                    })
            
            # Display patients section
            if patients:
                patients_header = ctk.CTkLabel(
                    self.results_frame,
                    text=f"👥 PATIENTS ({len(patients)})",
                    font=("Merriweather", 14, "bold"),
                    text_color="#2E7D4F"
                )
                patients_header.pack(anchor="w", padx=10, pady=(10, 5))
                
                for patient in patients:
                    self.create_patient_item(patient)
                    
            # Display supplies section
            if supplies:
                supplies_header = ctk.CTkLabel(
                    self.results_frame,
                    text=f"📦 SUPPLIES ({len(supplies)})",
                    font=("Merriweather", 14, "bold"),
                    text_color="#D2691E"
                )
                supplies_header.pack(anchor="w", padx=10, pady=(15, 5))
                
                for supply in supplies:
                    self.create_supply_item(supply)
        
        # Show the frame
        self.show()
    
    def create_patient_item(self, patient):
        """Create a patient result item"""
        patient_frame = ctk.CTkFrame(
            self.results_frame,
            width=360,
            height=70,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E0E0E0"
        )
        patient_frame.pack(fill="x", padx=10, pady=3)
        patient_frame.pack_propagate(False)
        
        # Patient icon
        icon_frame = ctk.CTkFrame(
            patient_frame,
            width=50,
            height=50,
            fg_color="#E3F2FD",
            corner_radius=25
        )
        icon_frame.place(x=10, y=10)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text="👤",
            font=("Arial", 20)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Patient details
        name_label = ctk.CTkLabel(
            patient_frame,
            text=patient['name'],
            font=("Merriweather", 14, "bold"),
            text_color="black"
        )
        name_label.place(x=70, y=12)
        
        details_text = f"Age: {patient['age']} • Gender: {patient['gender']} • Access: {patient['access_type']}"
        details_label = ctk.CTkLabel(
            patient_frame,
            text=details_text,
            font=("Arial", 11),
            text_color="#666666"
        )
        details_label.place(x=70, y=35)
        
        # View button
        view_btn = ctk.CTkButton(
            patient_frame,
            width=60,
            height=25,
            text="View",
            font=("Arial", 11),
            fg_color="#68EDC6",
            hover_color="#5AA3A3",
            corner_radius=5,
            command=lambda p=patient: self.view_patient(p)
        )
        view_btn.place(x=290, y=22)
    
    def create_supply_item(self, supply):
        """Create a supply result item"""
        supply_frame = ctk.CTkFrame(
            self.results_frame,
            width=360,
            height=60,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E0E0E0"
        )
        supply_frame.pack(fill="x", padx=10, pady=3)
        supply_frame.pack_propagate(False)
        
        # Supply icon
        icon_frame = ctk.CTkFrame(
            supply_frame,
            width=40,
            height=40,
            fg_color="#FFF3E0",
            corner_radius=20
        )
        icon_frame.place(x=10, y=10)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text="📦",
            font=("Arial", 16)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Supply details
        name_label = ctk.CTkLabel(
            supply_frame,
            text=supply['name'],
            font=("Merriweather", 13, "bold"),
            text_color="black"
        )
        name_label.place(x=60, y=10)
        
        category_label = ctk.CTkLabel(
            supply_frame,
            text=f"Category: {supply['category']}",
            font=("Arial", 11),
            text_color="#666666"
        )
        category_label.place(x=60, y=30)
        
        # View button
        view_btn = ctk.CTkButton(
            supply_frame,
            width=60,
            height=25,
            text="View",
            font=("Arial", 11),
            fg_color="#68EDC6",
            hover_color="#5AA3A3",
            corner_radius=5,
            command=lambda s=supply: self.view_supply(s)
        )
        view_btn.place(x=290, y=17)
    
    def view_patient(self, patient):
        """Handle viewing a patient - navigate to patient page and show details"""
        print(f"\n🔍 NAVIGATING TO PATIENT: {patient['name']}")
        
        try:
            # Get patient_id from the database using the patient name
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT patient_id FROM patient_list 
                WHERE patient_name = %s
            """, (patient['name'],))
            
            result = cursor.fetchone()
            
            if result:
                patient_id = result[0]
                print(f"Found patient ID: {patient_id}")
                
                # Hide the search results
                self.hide()
                
                # Navigate through the widget hierarchy to find the main HomePage
                current_widget = self.parent
                homepage = None
                
                # Traverse up the widget hierarchy to find HomePage
                while current_widget:
                    if hasattr(current_widget, '__class__'):
                        class_name = current_widget.__class__.__name__
                        print(f"Checking widget: {class_name}")
                        
                        if class_name == 'HomePage':
                            homepage = current_widget
                            break
                    
                    # Move up the hierarchy
                    current_widget = getattr(current_widget, 'master', None)
                
                if homepage:
                    print("✅ Found HomePage, navigating to Patient page...")
                    
                    # Navigate to Patient page (correct name: "Patient" not "Patients")
                    homepage.show_page('Patient')
                    
                    # Get the patient page and show detailed info
                    if hasattr(homepage, 'pages') and 'Patient' in homepage.pages:
                        patient_page = homepage.pages['Patient']
                        # Use after() to ensure the page is loaded before showing details
                        patient_page.after(100, lambda: patient_page.show_detailed_info(patient_id))
                        print("✅ Scheduled patient detail view")
                    else:
                        print("❌ Patient page not found in homepage.pages")
                        print(f"Available pages: {list(homepage.pages.keys()) if hasattr(homepage, 'pages') else 'No pages found'}")
                        
                else:
                    print("❌ Could not find HomePage in widget hierarchy")
                    
            else:
                print(f"❌ Patient '{patient['name']}' not found in database")
                
        except Exception as e:
            print(f"❌ Error navigating to patient: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()
    
    def view_supply(self, supply):
        """Handle viewing a supply - navigate to supply page and show details"""
        print(f"\n📦 NAVIGATING TO SUPPLY: {supply['name']}")
        
        try:
            # Get supply item_id from the database using the supply name
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT item_id FROM supply 
                WHERE item_name = %s
            """, (supply['name'],))
            
            result = cursor.fetchone()
            
            if result:
                item_id = result[0]
                print(f"Found supply item ID: {item_id}")
                
                # Hide the search results
                self.hide()
                
                # Navigate through the widget hierarchy to find the main HomePage
                current_widget = self.parent
                homepage = None
                
                # Traverse up the widget hierarchy to find HomePage
                while current_widget:
                    if hasattr(current_widget, '__class__'):
                        class_name = current_widget.__class__.__name__
                        print(f"Checking widget: {class_name}")
                        
                        if class_name == 'HomePage':
                            homepage = current_widget
                            break
                    
                    # Move up the hierarchy
                    current_widget = getattr(current_widget, 'master', None)
                
                if homepage:
                    print("✅ Found HomePage, navigating to Supply page...")
                    
                    # Navigate to Supply page
                    homepage.show_page('Supply')
                    
                    # Get the supply page and show detailed info
                    if hasattr(homepage, 'pages') and 'Supply' in homepage.pages:
                        supply_page = homepage.pages['Supply']
                        
                        # Get full supply data from database for detailed view
                        cursor.execute("""
                            SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                                COALESCE(
                                    (SELECT MAX(rl.restock_date) 
                                    FROM restock_logs rl 
                                    WHERE rl.item_id = s.item_id), 
                                    'No Restock'
                                ) as restock_date,
                                s.date_registered, s.restock_quantity, s.average_daily_usage, 
                                s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                                s.stock_level_status, s.max_supply
                            FROM supply s 
                            WHERE s.item_id = %s
                        """, (item_id,))
                        
                        full_supply_data = cursor.fetchone()
                        
                        if full_supply_data:
                            # Set the selected supply ID in the supply page
                            supply_page.selected_supply_id = item_id
                            
                            # Use after() to ensure the page is loaded before showing details
                            supply_page.after(100, lambda: supply_page.show_detailed_info(full_supply_data))
                            print("✅ Scheduled supply detail view")
                        else:
                            print("❌ Could not fetch full supply data")
                    else:
                        print("❌ Supply page not found in homepage.pages")
                        print(f"Available pages: {list(homepage.pages.keys()) if hasattr(homepage, 'pages') else 'No pages found'}")
                        
                else:
                    print("❌ Could not find HomePage in widget hierarchy")
                    
            else:
                print(f"❌ Supply '{supply['name']}' not found in database")
                
        except Exception as e:
            print(f"❌ Error navigating to supply: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def show(self):
        """Show the search results frame"""
        self.place(x=480, y=130)  # Position below search bar
        self.lift()
        self.visible = True
    
    def hide(self):
        """Hide the search results frame"""
        self.place_forget()
        self.visible = False

class HomePageContent(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")

        # Initialize reminder carousel variables
        self.current_reminder_index = 0
        self.reminder_images = []
        self.reminder_animation_job = None
        self.fade_animation_job = None

        # Initialize graph canvases
        self.most_used_canvas = None
        self.yesterday_canvas = None
        self.pie_chart_canvas = None  
        self.yesterday_scrollbar = None  

        # Initialize patient count variables
        self.total_patients = 0
        self.active_patients = 0
        self.inactive_patients = 0

        # Initialize search results frame
        self.search_results_frame = SearchResultsFrame(self)

        def get_name():
            # Commented out backend database call
            username = login_shared_states.get('logged_username', None)

            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT full_name FROM users WHERE username = %s
                """, (username,))

                full_name = cursor.fetchone()[0]

                first_name = full_name.split()[0]

                return first_name, full_name

            except Exception as e:
                print('Error retrieving user full name ', e)
            finally:
                cursor.close()
                connect.close()

            # Static values for testing
            #full_name = "User"
            #first_name = "User"

            return first_name, full_name

        first_name, full_name = get_name()

        # Setup UI
        self.setup_ui(first_name, full_name)
        
        # Load initial graphs and patient data
        self.show_overall_usage()
        self.show_yesterday_usage()
        self.load_patient_data_and_pie_chart()

        self.setup_search_functionality()

    def setup_search_functionality(self):
        """Setup search functionality for the search entry"""
        # Bind the search entry to trigger search on key release
        self.search_entry.bind("<KeyRelease>", self.on_search_key_release)
        self.search_entry.bind("<Return>", self.perform_search)  # Enter key
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)  # Hide results when focus lost
        self.search_entry.bind("<Button-1>", self.on_search_click)  # Show results on click

    def on_search_click(self, event):
        """Handle click on search entry"""
        search_text = self.search_entry.get().strip()
        if len(search_text) >= 2:
            # If there's already text, perform search to show results
            self.perform_search(None)

    def on_search_key_release(self, event):
        """Handle key release events in search entry"""
        search_text = self.search_entry.get().strip()
        
        # Hide results if search is empty
        if len(search_text) == 0:
            self.search_results_frame.hide()
            return
            
        # Only search if there's text and it's more than 1 character
        if len(search_text) >= 2:
            # Add a small delay to avoid searching on every keystroke
            if hasattr(self, 'search_timer'):
                self.after_cancel(self.search_timer)
            self.search_timer = self.after(300, lambda: self.perform_search(None))
        elif len(search_text) == 1:
            # Hide results for single character
            self.search_results_frame.hide()

    def on_search_focus_out(self, event):
        """Handle when search entry loses focus"""
        # Add a small delay before hiding to allow clicking on results
        self.after(200, self.check_and_hide_results)
    
    def check_and_hide_results(self):
        """Check if we should hide the results frame"""
        # Get the widget that currently has focus
        focused_widget = self.focus_get()
        
        # If the focused widget is not part of the search results frame, hide it
        if (focused_widget != self.search_entry and 
            not self.is_widget_in_frame(focused_widget, self.search_results_frame)):
            self.search_results_frame.hide()
    
    def is_widget_in_frame(self, widget, frame):
        """Check if a widget is inside a specific frame"""
        if widget is None:
            return False
        
        parent = widget
        while parent:
            if parent == frame:
                return True
            parent = parent.master
        return False

    def perform_search(self, event):
        """Perform the actual search operation"""
        search_text = self.search_entry.get().strip()
        
        if not search_text or len(search_text) < 2:
            self.search_results_frame.hide()
            return
        
        try:
            connect = db()
            cursor = connect.cursor()

            # Use the existing search query from your code
            cursor.execute("""
                SELECT * FROM (
                    SELECT 
                        patient_name as name,
                        age,
                        gender,
                        access_type,
                        NULL as category,
                        'patient' as record_type
                    FROM patient_list
                        
                    UNION
                        
                    SELECT
                        item_name as name,
                        NULL as age,
                        NULL as gender,
                        NULL as access_type,
                        category,
                        'supply' as record_type
                    FROM supply
                ) AS search_result
                WHERE name LIKE %s
                ORDER BY record_type, name
            """, (f'%{search_text}%',))

            search_results = cursor.fetchall()
            
            # Show results in the search frame
            self.search_results_frame.show_results(search_text, search_results)
            
            # Keep the existing console output for debugging
            print(f"\n=== Search Results for '{search_text}' ===")
            if search_results:
                patients_found = []
                supplies_found = []
                
                for result in search_results:
                    name, age, gender, access_type, category, record_type = result
                    
                    if record_type == 'patient':
                        patients_found.append({
                            'name': name,
                            'age': age,
                            'gender': gender,
                            'access_type': access_type
                        })
                        print(f'🧑 PATIENT: {name} (Age: {age}, Gender: {gender}, Access: {access_type})')
                        
                    elif record_type == 'supply':
                        supplies_found.append({
                            'name': name,
                            'category': category
                        })
                        print(f'📦 SUPPLY: {name} (Category: {category})')
                
                print(f"\nSummary: Found {len(patients_found)} patients and {len(supplies_found)} supplies")
            else:
                print(f"No results found for '{search_text}'")

        except Exception as e:
            print(f'Error performing search: {e}')
            # Show error in search frame
            self.search_results_frame.show_results(search_text, [])
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def load_patient_data_and_pie_chart(self):
        """Load patient data and create pie chart"""
        try:
            connect = db()
            cursor = connect.cursor()

            cursor.execute("""
                SELECT pi.patient_id, pi.status
                FROM patient_info pi
                JOIN (
                    SELECT patient_id
                    FROM item_usage
                    GROUP BY patient_id
                    HAVING DATEDIFF(CURDATE(), MAX(usage_date)) > 30
                ) inactive_patients ON pi.patient_id = inactive_patients.patient_id
                WHERE pi.status = 'Active'
            """)
            #for simulation 
            #HAVING TIMESTAMPDIFF(SECOND, MAX(usage_date), NOW()) > 5

            patients_to_inactivate = cursor.fetchall() 

            for patient in patients_to_inactivate:
                print(f"Patient {patient[0]} has been marked as inactive due to 30 days inactivity.")

            cursor.execute("""
                UPDATE patient_info pi
                JOIN (
                    SELECT patient_id
                    FROM item_usage
                    GROUP BY patient_id
                    HAVING DATEDIFF(CURDATE(), MAX(usage_date)) > 30
                ) inactive_patients ON pi.patient_id = inactive_patients.patient_id
                SET pi.status = 'Inactive'
            """)
            #for simulation 
            #HAVING TIMESTAMPDIFF(SECOND, MAX(usage_date), NOW()) > 5

            connect.commit()

            # Get patient counts 
            cursor.execute("SELECT status, COUNT(*) FROM patient_info GROUP BY status ORDER BY status")
            status_count_result = cursor.fetchall()
            
            if status_count_result:
                labels = [label[0] for label in status_count_result]
                values = [value[1] for value in status_count_result]

                # Initialize values
                self.active_patients = 0
                self.inactive_patients = 0
                
                # Properly map the values based on actual labels
                for i, label in enumerate(labels):
                    if label == 'Active':
                        self.active_patients = values[i]
                    elif label == 'Inactive':
                        self.inactive_patients = values[i]

                self.total_patients = sum(values)

                # print('active:', self.active_patients)
                # print('inactive:', self.inactive_patients)
                # print('total patient:', self.total_patients)

                # Update the labels
                self.update_patient_labels()
                
                # Create pie chart
                self.create_pie_chart(labels, values)
            else:
                # No data found
                self.total_patients = 0
                self.active_patients = 0
                self.inactive_patients = 0
                self.update_patient_labels()
                
                # Create empty pie chart
                self.create_pie_chart([], [])

        except Exception as e:
            print('Error retrieving patient data for pie chart:', e)
            # Set default values on error
            self.total_patients = 0
            self.active_patients = 0
            self.inactive_patients = 0
            self.update_patient_labels()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def create_pie_chart(self, labels, values):
        """Recommended: Clean pie chart with external legend"""
        try:
            if self.pie_chart_canvas:
                self.pie_chart_canvas.get_tk_widget().destroy()

            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            fig = Figure(figsize=(3.2, 2.8), dpi=100)
            ax = fig.add_subplot(111)
            
            if values and sum(values) > 0:
                colors = []
                for label in labels:
                    if label == 'Active':
                        colors.append('#88BD8E')
                    else:
                        colors.append('#F25B5B')
                
                # Clean pie chart - no labels, just percentages
                wedges, texts, autotexts = ax.pie(
                    values, 
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90,
                    pctdistance=0.5,
                    textprops={'fontsize': 13, 'fontproperties': tick_font, 'color': 'white'}
                )
                pass  
                    
            else:
                ax.text(0.5, 0.5, 'No Data', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='gray',
                    weight='bold')
            
            ax.axis('equal')
            fig.tight_layout()

            self.pie_chart_canvas = FigureCanvasTkAgg(fig, self.fifth_frame)
            self.pie_chart_canvas.draw()
            self.pie_chart_canvas.get_tk_widget().place(x=20, y=90, width=320, height=220)

        except Exception as e:
            print('Error creating pie chart:', e)

    def update_patient_labels(self):
        """Update the patient count labels"""
        try:
            # Update total count
            self.total_count_label.configure(text=str(self.total_patients))
            
            # Update active count
            self.active_count.configure(text=str(self.active_patients))
            
            # Update inactive count
            self.inactive_count.configure(text=str(self.inactive_patients))
            
        except Exception as e:
            print('Error updating patient labels:', e)

    def show_overall_usage(self):
        """Show overall usage chart in container"""
        try:
            connect = db()
            query = """
                SELECT
                    s.item_name, 
                    SUM(iu.quantity_used) AS total_used 
                FROM item_usage iu
                JOIN supply s ON iu.item_id = s.item_id
                GROUP BY s.item_name
                ORDER by total_used;
            """

            df = pd.read_sql(query, connect)
            df_10 = df.sort_values(by='total_used', ascending=False).head(10)
            df_10 = df_10.sort_values(by='total_used', ascending=True)

            # Clear existing canvas if it exists
            if self.most_used_canvas:
                self.most_used_canvas.get_tk_widget().destroy()

            # Create new figure
            fig = Figure(figsize=(10, 3.5), dpi=100)
            ax = fig.add_subplot(111)
            
            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            # Create bar chart
            ax.bar(df_10['item_name'], df_10['total_used'], color='#C0DABE')
            ax.tick_params(axis='x', pad=10)
            ax.margins(y=0.15) 
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                        label.set_fontproperties(tick_font)
                        label.set_fontsize(11)
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
                
            fig.tight_layout()

            # Create canvas and embed in frame
            self.most_used_canvas = FigureCanvasTkAgg(fig, self.most_used_frame)
            self.most_used_canvas.draw()
            self.most_used_canvas.get_tk_widget().place(x=20, y=100, width=1010, height=320)

        except Exception as e:
            print('Error retrieving the overall usage', e)
            # Show error message in container
            if hasattr(self, 'most_used_frame'):
                error_label = ctk.CTkLabel(
                    self.most_used_frame,
                    text=f"Error loading data: {str(e)}",
                    font=("Arial", 14),
                    text_color="red"
                )
                error_label.place(x=400, y=250)

        finally: 
            if 'connect' in locals():
                connect.close()

    def show_yesterday_usage(self):
        """Show yesterday's usage chart in container with horizontal scrollbar"""
        try:
            connect = db()
            query = """
                SELECT 
                    s.item_name,
                    DATE(iu.usage_date) AS usage_date, 
                    SUM(iu.quantity_used) AS total_used 
                FROM item_usage iu
                JOIN supply s ON iu.item_id = s.item_id
                GROUP BY iu.item_id, DATE(usage_date)
                ORDER BY total_used;
            """

            df = pd.read_sql(query, connect)
            df['edit_date'] = pd.to_datetime(df['usage_date'])

            from datetime import date, timedelta
            yesterday = date.today() - timedelta(days=1)
            df_yesterday = df[df['edit_date'].dt.date == yesterday]
        
            df_yesterday = df_yesterday.sort_values(by='total_used', ascending=False)

            # Clean up existing canvas and scrollbar
            if self.yesterday_canvas:
                self.yesterday_canvas.get_tk_widget().destroy()
            if hasattr(self, 'yesterday_scrollbar') and self.yesterday_scrollbar:
                self.yesterday_scrollbar.destroy()
                self.yesterday_scrollbar = None

            # Calculate dynamic figure width based on number of items
            num_items = len(df_yesterday)
            if num_items > 0:
                # Base width calculation: minimum 5.5, then add width per item
                min_width = 5.5
                width_per_item = 0.8  # Adjust this to control spacing
                calculated_width = max(min_width, num_items * width_per_item)
                fig_width = min(calculated_width, 20)  # Cap at maximum width
            else:
                fig_width = 5.5

            fig = Figure(figsize=(fig_width, 3.5), dpi=100)
            ax = fig.add_subplot(111)
            
            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            # Create bar chart
            if not df_yesterday.empty:
                bars = ax.bar(df_yesterday['item_name'], df_yesterday['total_used'], color='#C0DABE')
                if num_items > 7:  # Only rotate if many items
                    ax.tick_params(axis='x', pad=10, rotation=45)
                else:
                    ax.tick_params(axis='x', pad=10)
                ax.margins(y=0.15)    
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontproperties(tick_font)
                    label.set_fontsize(11)
                    
                # Add value labels on top of bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{int(height)}', ha='center', va='bottom', 
                           fontproperties=tick_font, fontsize=9)
            else:
                ax.text(0.5, 0.5, 'No data for yesterday', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14, color='gray')
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
                
            fig.tight_layout()

            # Create canvas and embed in frame
            self.yesterday_canvas = FigureCanvasTkAgg(fig, self.yesterday_usage_frame)
            self.yesterday_canvas.draw()
            
            # Get canvas widget
            canvas_widget = self.yesterday_canvas.get_tk_widget()
            
            # Store the canvas position for scrolling
            self.canvas_x_position = 20
            self.canvas_max_width = int(fig_width * 100)
            self.canvas_container_width = 560
            
            if fig_width > 5.5:  # Only add scrolling if content is wider than container
                # Place canvas with full width
                canvas_widget.place(x=self.canvas_x_position, y=100, width=self.canvas_max_width, height=320)
                
                # Create horizontal scrollbar
                self.yesterday_scrollbar = ctk.CTkScrollbar(
                    self.yesterday_usage_frame,
                    orientation="horizontal",
                    width=540,
                    height=20,
                    command=self.on_yesterday_scroll
                )
                self.yesterday_scrollbar.place(x=30, y=405)
                
                # Initialize scrollbar
                visible_portion = min(1.0, self.canvas_container_width / self.canvas_max_width)
                self.yesterday_scrollbar.set(0, visible_portion)
                
            else:
                # No scrolling needed, place normally
                canvas_widget.place(x=20, y=100, width=560, height=320)
                self.yesterday_scrollbar = None

            print(f"✅ Yesterday usage chart created with {num_items} items (width: {fig_width})")

        except Exception as e:
            print('Error retrieving yesterday usage', e)
            # Show error message in container
            if hasattr(self, 'yesterday_usage_frame'):
                error_label = ctk.CTkLabel(
                    self.yesterday_usage_frame,
                    text=f"Error loading data: {str(e)}",
                    font=("Arial", 14),
                    text_color="red"
                )
                error_label.place(x=200, y=250)

        finally: 
            if 'connect' in locals():
                connect.close()

    def on_yesterday_scroll(self, *args):
        """Handle horizontal scrollbar for yesterday usage chart"""
        if not hasattr(self, 'yesterday_canvas') or not self.yesterday_canvas:
            return
            
        canvas_widget = self.yesterday_canvas.get_tk_widget()
        
        if len(args) >= 2:
            command = args[0]
            value = args[1]
            
            if command == "moveto":
                # Scrollbar dragged to specific position
                scroll_position = float(value)
                # Calculate new x position based on scroll
                max_scroll = self.canvas_max_width - self.canvas_container_width
                new_x = 20 - (scroll_position * max_scroll)
                # Ensure canvas doesn't go beyond boundaries
                new_x = max(min(new_x, 20), -(max_scroll))
                
                canvas_widget.place(x=int(new_x), y=100, width=self.canvas_max_width, height=320)
                
            elif command == "scroll":
                # Scrollbar arrow clicked
                current_x = canvas_widget.winfo_x()
                scroll_amount = int(value) * 50  # Scroll step size
                new_x = current_x - scroll_amount
                
                # Ensure canvas doesn't go beyond boundaries
                max_scroll = self.canvas_max_width - self.canvas_container_width
                new_x = max(min(new_x, 20), -(max_scroll))
                
                canvas_widget.place(x=int(new_x), y=100, width=self.canvas_max_width, height=320)
                
                # Update scrollbar position
                scroll_position = (20 - new_x) / max_scroll
                visible_portion = self.canvas_container_width / self.canvas_max_width
                self.yesterday_scrollbar.set(scroll_position, scroll_position + visible_portion)

    def setup_ui(self, first_name, full_name):
        """Setup all the UI elements"""
        self.navbar = ctk.CTkFrame(self, fg_color="white", height=130)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)
        self.navbar.configure(border_width=0, border_color="black")

        self.welcome_label = ctk.CTkLabel(self.navbar, text="Welcome Back,", text_color="black", font=("Arial", 30, "bold"))
        self.welcome_label.place(relx=0.17, rely=0.5, anchor="e")

        # IMPROVED FIRST NAME LABEL - Dynamic font sizing
        # Calculate appropriate font size based on first name length
        first_name_length = len(first_name)
        if first_name_length <= 8:
            first_name_font_size = 30
        elif first_name_length <= 12:
            first_name_font_size = 26
        elif first_name_length <= 16:
            first_name_font_size = 22
        elif first_name_length <= 20:
            first_name_font_size = 18
        else:
            first_name_font_size = 16
            # For very long first names, truncate and add ellipsis
            if first_name_length > 25:
                first_name = first_name[:22] + "..."

        self.name_label = ctk.CTkLabel(
            self.navbar, 
            text=f"{first_name}!", 
            text_color="black", 
            font=("Arial", first_name_font_size, "bold")
        )
        self.name_label.place(relx=0.27, rely=0.5, anchor="e")

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
        self.search_container.place(x=480, y=70, anchor="w")

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

        # Calendar container
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

        # Calendar icon
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
        import datetime
        today_date = datetime.datetime.now().strftime("%B %d, %Y") 

        # Date label beside the icon
        date_label = ctk.CTkLabel(
            self.calendar_container,
            text=today_date,
            font=("Arial", 20),
            text_color="#333333"
        )
        date_label.place(x=60, rely=0.5, anchor="w")

        # IMPROVED FULL NAME LABEL - Dynamic font sizing and better positioning
        # Calculate appropriate font size based on name length
        name_length = len(full_name)
        if name_length <= 15:
            font_size = 24
        elif name_length <= 25:
            font_size = 20
        elif name_length <= 35:
            font_size = 16
        else:
            font_size = 14
            # For very long names, truncate and add ellipsis
            if name_length > 40:
                full_name = full_name[:37] + "..."

        # Position the full name label with more space and better alignment
        self.namev2_label = ctk.CTkLabel(
            self.navbar, 
            text=full_name, 
            text_color="black", 
            font=("Arial", font_size, "bold"),
            wraplength=200  # Allow text wrapping if needed
        )
        
        # Use a fixed position instead of relative to avoid overlap
        # Adjust x position based on screen size or make it responsive
        self.namev2_label.place(x=1120, rely=0.5, anchor="w")

        # Load notification and settings frames
        self.notif_frame = NotificationFrame(self)
        self.settings_frame = SettingsFrame(self)

        # Load images
        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))

        icon_y = 62

        # Notification button - positioned relative to name label
        notif_btn = ctk.CTkButton(
            self.navbar, 
            image=notif_img, 
            text="", 
            width=40, 
            height=40, 
            fg_color="transparent", 
            hover_color="#f5f5f5",
            command=self.notif_frame.toggle
        )
        notif_btn.place(x=1350, y=icon_y, anchor="center")

        # Settings button 
        settings_btn = ctk.CTkButton(
            self.navbar, 
            image=settings_img, 
            text="", 
            width=40, 
            height=40, 
            fg_color="transparent", 
            hover_color="#f5f5f5", 
            command=self.settings_frame.toggle  
        )
        settings_btn.place(x=1400, y=icon_y, anchor="center")


    
        #ctk.CTkButton(self.dropdown_frame, text="Account Settings", width=140, command=self.open_settings).pack(pady=5)
        #ctk.CTkButton(self.dropdown_frame, text="Log Out", width=140, command=self.logout).pack(pady=5)

        self.bottom_line = ctk.CTkFrame(self.navbar, height=1.5, fg_color="black")
        self.bottom_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        
        # Most Used Items Frame
        self.most_used_frame = ctk.CTkFrame(
            self,
            width=1050,
            height=430,
            fg_color="white",
            corner_radius=20,   
        )
        self.most_used_frame.place(x=70, y=150)

        # Top bar for Most Used Items
        most_used_top_bar = ctk.CTkFrame(
            self.most_used_frame,
            width=1050,
            height=20,
            fg_color="#68EDC6",
            corner_radius=0
        )
        most_used_top_bar.place(x=0, y=0)

        # Most Used Items title
        MUsedItems_label = ctk.CTkLabel(
            self.most_used_frame,
            text="Most Used Items",
            font=("Merriweather", 20, "bold")
        )
        MUsedItems_label.place(x=20, y=40)

        # Most Used Items icon 
        try:
            most_used_icon = ctk.CTkImage(light_image=Image.open("assets/refresh.png"), size=(24, 24))
            most_used_icon_btn.place(x=210, y=38)
        except:
            # If icon fails to load, use emoji fallback
            most_used_icon_btn = ctk.CTkButton(
                self.most_used_frame,
                text="🔄",
                font=("Arial", 16),
                width=30,
                height=30,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.show_overall_usage
            )
            most_used_icon_btn.place(x=210, y=38)

        # Subtitle for Most Used Items
        MUsedItems_subtitle = ctk.CTkLabel(
            self.most_used_frame,
            text="Data over time",
            font=("Arial", 12),
            text_color="#666666"
        )
        MUsedItems_subtitle.place(x=20, y=70)

        # Refresh indicator for Most Used Items
        refresh_indicator_most = ctk.CTkLabel(
            self.most_used_frame,
            text="Click refresh icon to update",
            font=("Arial", 10),
            text_color="#888888"
        )
        refresh_indicator_most.place(x=850, y=50)

        # Yesterday Item Usage Frame
        self.yesterday_usage_frame = ctk.CTkFrame(
            self,
            width=600,
            height=430,
            fg_color="white",
            corner_radius=20   
        )
        self.yesterday_usage_frame.place(x=70, y=610)

        # Top bar for Yesterday Item Usage
        yesterday_top_bar = ctk.CTkFrame(
            self.yesterday_usage_frame,
            width=600,
            height=20,
            fg_color="#68EDC6",
            corner_radius=0
        )
        yesterday_top_bar.place(x=0, y=0)

        # Yesterday Item Usage title
        YItemUsage_label = ctk.CTkLabel(
            self.yesterday_usage_frame,
            text="Yesterday Item Usage",
            font=("Merriweather", 20, "bold")
        )
        YItemUsage_label.place(x=20, y=40)

        # Yesterday Item Usage icon 
        try:
            yesterday_icon = ctk.CTkImage(light_image=Image.open("assets/refresh.png"), size=(24, 24))
            yesterday_icon_btn = ctk.CTkButton(
                self.yesterday_usage_frame,
                image=yesterday_icon,
                text="",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.show_yesterday_usage
            )
            yesterday_icon_btn.place(x=240, y=38)
        except:
            # If icon fails to load, use emoji fallback
            yesterday_icon_btn = ctk.CTkButton(
                self.yesterday_usage_frame,
                text="🔄",
                font=("Arial", 16),
                width=30,
                height=30,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.show_yesterday_usage
            )
            yesterday_icon_btn.place(x=240, y=38)

        # Subtitle for Yesterday Item Usage
        from datetime import date, timedelta
        YItemUsage_subtitle = ctk.CTkLabel(
            self.yesterday_usage_frame,
            text=date.today() - timedelta(days=1),
            font=("Arial", 12),
            text_color="#666666"
        )
        YItemUsage_subtitle.place(x=20, y=70)

        # Refresh indicator for Yesterday Item Usage
        refresh_indicator_yesterday = ctk.CTkLabel(
            self.yesterday_usage_frame,
            text="Click refresh icon to update",
            font=("Arial", 10),
            text_color="#888888"
        )
        refresh_indicator_yesterday.place(x=400, y=50)

        # Recent Patient Frame 
        self.fourth_frame = ctk.CTkFrame(
            self,
            width=410,
            height=200,
            fg_color="white",
            corner_radius=20
        )
        self.fourth_frame.place(x=710, y=610)  

        top_bar = ctk.CTkFrame(
            self.fourth_frame,
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

        # Setup patient info boxes
        self.setup_patient_boxes()

        # Backup Information Frame 
        self.backup_frame = ctk.CTkFrame(
            self,
            width=410,
            height=200,
            fg_color="white",
            corner_radius=20
        )
        self.backup_frame.place(x=710, y=845) 

        left_bar = ctk.CTkFrame(
            self.backup_frame,
            width=20,
            height=200,
            fg_color="#68EDC6",
            corner_radius=0
        )
        left_bar.place(x=0, y=0)

        # Backup labels with dates
        RecentManual_label = ctk.CTkLabel(
            self.backup_frame,
            text="Recent Manual Backup:",
            font=("Merriweather", 16, "bold")
        )
        RecentManual_label.place(x=30, y=35)

        RecentManual_date = ctk.CTkLabel(
            self.backup_frame,
            text="11-25-2025",
            font=("Arial", 14),
            text_color="#000000"
        )
        RecentManual_date.place(x=250, y=37)

        RecentSched_label = ctk.CTkLabel(
            self.backup_frame,
            text="Recent Scheduled Backup:",
            font=("Merriweather", 16, "bold")
        )
        RecentSched_label.place(x=30, y=75)

        RecentSched_date = ctk.CTkLabel(
            self.backup_frame,
            text="11-20-2025",
            font=("Arial", 14),
            text_color="#000000"
        )
        RecentSched_date.place(x=270, y=77)

        UpcomingSched_label = ctk.CTkLabel(
            self.backup_frame,
            text="Upcoming Scheduled Backup:",
            font=("Merriweather", 16, "bold")
        )
        UpcomingSched_label.place(x=30, y=115)

        UpcomingSched_date = ctk.CTkLabel(
            self.backup_frame,
            text="12-01-2025",
            font=("Arial", 14),
            text_color="#000000"
        )
        UpcomingSched_date.place(x=295, y=117)

        # Total Patients Frame
        self.fifth_frame = ctk.CTkFrame(
            self,
            width=350,
            height=520,
            fg_color="white",
            corner_radius=20
        )
        self.fifth_frame.place(x=1200, y=150)

        totalPatients_label = ctk.CTkLabel(
            self.fifth_frame,
            text="Total Patients",
            font=("Merriweather", 20, "bold")
        )
        totalPatients_label.place(x=120, y=40)

        # Patient count display 
        self.total_count_label = ctk.CTkLabel(
            self.fifth_frame,
            text="0",  # Will be updated
            font=("Arial", 48, "bold"),
            text_color="#68EDC6"
        )
        self.total_count_label.place(x=40, y=20)

        active_icon_image = ctk.CTkImage(
            light_image=Image.open("assets/active_patients.png"),
            size=(40, 40)
        )

        inactive_icon_image = ctk.CTkImage(
            light_image=Image.open("assets/inactive_patients.png"),
            size=(40, 40)
        )

        active_patients = ctk.CTkFrame(
            self.fifth_frame,
            width=270,
            height=80,
            fg_color="white",
            border_width=2,
            border_color="#4CAF50",
            corner_radius=10
        )
        active_patients.place(x=40, y=320)

        active_icon_label = ctk.CTkLabel(
            active_patients,
            image=active_icon_image,
            text="",
        )
        active_icon_label.place(x=15, y=20)

        self.active_count = ctk.CTkLabel(
            active_patients,
            text="0", 
            font=("Arial", 24, "bold"),
            text_color="#4CAF50"
        )
        self.active_count.place(x=70, y=15)

        active_label = ctk.CTkLabel(
            active_patients,
            text="Active Patients",
            font=("Arial", 12),
            text_color="#666666"
        )
        active_label.place(x=70, y=45)

        inactive_patients = ctk.CTkFrame(
            self.fifth_frame,
            width=270,
            height=80,
            fg_color="white",
            border_width=2,
            border_color="#FF5722",
            corner_radius=10
        )
        inactive_patients.place(x=40, y=420)

        inactive_icon_label = ctk.CTkLabel(
            inactive_patients,
            image=inactive_icon_image,
            text="",
        )
        inactive_icon_label.place(x=15, y=20)

        self.inactive_count = ctk.CTkLabel(
            inactive_patients,
            text="0",  # Will be updated
            font=("Arial", 24, "bold"),
            text_color="#FF5722"
        )
        self.inactive_count.place(x=70, y=15)

        inactive_label = ctk.CTkLabel(
            inactive_patients,
            text="Inactive Patients",
            font=("Arial", 12),
            text_color="#666666"
        )
        inactive_label.place(x=70, y=45)

        # Reminder Frame 
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

        # Start the carousel animation and refresh recent patient
        self.start_reminder_carousel()
        self.refresh_recent_patient()


     # Add method to auto-refresh patient data when needed
    def refresh_patient_data_and_chart(self):
        """Method to be called from other pages when patient data changes"""
        self.load_patient_data_and_pie_chart()
        print("✅ Patient data and pie chart automatically refreshed!")

    def setup_patient_boxes(self):
        # First Patient Box - Name
        self.first_box = ctk.CTkFrame(
            self.fourth_frame,
            width=100,
            height=120,
            fg_color="white",
            border_width=2,
            border_color="#68EDC6",
            corner_radius=10
        )
        self.first_box.place(x=30, y=60)

        name_icon = ctk.CTkLabel(
            self.first_box,
            text="👤",
            font=("Arial", 20)
        )
        name_icon.place(relx=0.5, rely=0.25, anchor="center")

        self.name_value = ctk.CTkLabel(
            self.first_box,
            text="No Patient",
            font=("Merriweather", 10, "bold"),
            text_color="black",
            justify="center"
        )
        self.name_value.place(relx=0.5, rely=0.7, anchor="center")

        # Second Patient Box - Age
        self.second_box = ctk.CTkFrame(
            self.fourth_frame,
            width=100,
            height=120,
            fg_color="white",
            border_width=2,
            border_color="#68EDC6",
            corner_radius=10
        )
        self.second_box.place(x=155, y=60)

        age_label = ctk.CTkLabel(
            self.second_box,
            text="Age",
            font=("Arial", 12),
            text_color="#666666"
        )
        age_label.place(relx=0.5, rely=0.25, anchor="center")

        self.age_value = ctk.CTkLabel(
            self.second_box,
            text="--",
            font=("Merriweather", 20, "bold"),
            text_color="black"
        )
        self.age_value.place(relx=0.5, rely=0.65, anchor="center")

        # Third Patient Box - Gender
        self.third_box = ctk.CTkFrame(
            self.fourth_frame,
            width=100,
            height=120,
            fg_color="white",
            border_width=2,
            border_color="#68EDC6",
            corner_radius=10
        )
        self.third_box.place(x=280, y=60)

        gender_label = ctk.CTkLabel(
            self.third_box,
            text="Gender",
            font=("Arial", 12),
            text_color="#666666"
        )
        gender_label.place(relx=0.5, rely=0.25, anchor="center")

        self.gender_value = ctk.CTkLabel(
            self.third_box,
            text="--",
            font=("Merriweather", 16, "bold"),
            text_color="black"
        )
        self.gender_value.place(relx=0.5, rely=0.65, anchor="center")

    def refresh_recent_patient(self):
        """Refresh the recent patient data from database"""
        try:
            connect = db()
            cursor = connect.cursor()

            cursor.execute("""
                SELECT patient_name, age, gender FROM patient_list
                ORDER BY patient_id DESC
                LIMIT 1 
            """)

            recent_patient = cursor.fetchone()
            
            if recent_patient:
                recent_patient_name = recent_patient[0]
                recent_patient_age = recent_patient[1]
                recent_patient_gender = recent_patient[2]
                
                # Update the labels with fresh data
                self.name_value.configure(text=recent_patient_name)
                self.age_value.configure(text=str(recent_patient_age))
                self.gender_value.configure(text=recent_patient_gender)
                
                print(f"✅ Recent patient refreshed: {recent_patient_name}")
            else:
                # No patients in database
                self.name_value.configure(text="No Patient")
                self.age_value.configure(text="--")
                self.gender_value.configure(text="--")
                print("ℹ️ No patients found in database")

        except Exception as e:
            print('Error retrieving recent patient:', e)
            # Set default values on error
            self.name_value.configure(text="Error")
            self.age_value.configure(text="--")
            self.gender_value.configure(text="--")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

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

    """def toggle_dropdown(self):
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
        print("Logging out...")"""

    def destroy(self):
        """Clean up when the widget is destroyed""" 
        self.stop_reminder_carousel()
        # Clean up matplotlib canvases
        if self.most_used_canvas:
            self.most_used_canvas.get_tk_widget().destroy()
        if self.yesterday_canvas:
            self.yesterday_canvas.get_tk_widget().destroy()
        if self.pie_chart_canvas:
            self.pie_chart_canvas.get_tk_widget().destroy()
        super().destroy() 

class NotificationFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=400, height=400, **kwargs)
        self.place(relx=0.7, rely=0.08)
        self.visible = False  
        self.place_forget()   
        self.lift()

        # Store notification widgets for updates
        self.notification_widgets = []

        # Header Frame
        header_frame = ctk.CTkFrame(self, width=400, height=60, fg_color="#04B17E", corner_radius=0)
        header_frame.place(y=0)
        
        header_title = ctk.CTkLabel(
            header_frame, 
            font=("Merriweather Bold", 18), 
            text="Recent Activity", 
            text_color="#FFFFFF"
        )
        header_title.place(relx=0.1, rely=0.25)
        
        clear_button = ctk.CTkButton(
            header_frame,
            width=70,
            height=30,
            fg_color="#1A374D",
            bg_color="#04B17E",
            text="Refresh",
            font=("Merriweather Bold", 11),
            corner_radius=20,
            command=self.refresh_notifications
        )
        clear_button.place(relx=.8, rely=.5, anchor="center")

        # Scrollable Notification Frame
        self.notification_frame = ctk.CTkScrollableFrame(
            self,
            width=400,
            height=340,
            fg_color="#f4f4f4",
            scrollbar_button_color="#f4f4f4",
            scrollbar_fg_color="#f4f4f4",
            corner_radius=0
        )
        self.notification_frame.place(y=60)

        # Load notifications when created
        self.load_notifications()

    def load_notifications(self):
        """Load real notifications from database"""
        try:
            connect = db()
            cursor = connect.cursor()

            # Get recent notifications from the last 7 days with all fields
            cursor.execute("""
                SELECT 
                    notification_type,
                    user_fullname,
                    item_name,
                    restock_quantity,
                    current_stock,
                    stock_status,
                    patient_id,
                    patient_name,
                    patient_status,
                    notification_timestamp,
                    DATE_FORMAT(notification_timestamp, '%M %d, %Y at %h:%i %p') as formatted_date
                FROM notification_logs 
                WHERE notification_timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY notification_timestamp DESC 
                LIMIT 15
            """)

            notifications = cursor.fetchall()
            
            # Clear existing notifications
            self.clear_notification_widgets()
            
            if notifications:
                for notification in notifications:
                    notif_type, user_fullname, item_name, restock_qty, current_stock, stock_status, patient_id, patient_name, patient_status, timestamp, formatted_date = notification
                    
                    # Build dynamic message based on notification type
                    message = self.build_notification_message(
                        notif_type, user_fullname, item_name, restock_qty, 
                        current_stock, stock_status, patient_id, patient_name, patient_status
                    )
                    
                    self.create_notification_widget(notif_type, message, formatted_date)
            else:
                print("DEBUG: No notifications found in database")
                self.show_no_notifications()
                
        except Exception as e:
            print(f'Error loading notifications: {e}')
            self.show_error_message()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def build_notification_message(self, notif_type, user_fullname, item_name, restock_qty, current_stock, stock_status, patient_id, patient_name, patient_status):
        """Build dynamic notification message based on type and available data"""
        
        # Handle None values properly
        user_fullname = user_fullname or "System"
        item_name = item_name or "Unknown Item"
        patient_name = patient_name or "Unknown Patient"

        if notif_type in ['Item Stock Status Alert', 'Item Usage Recorded'] and item_name != "Unknown Item":
            if current_stock is None or stock_status is None:
                try:
                    connect = db()
                    cursor = connect.cursor()
                    cursor.execute("""
                        SELECT current_stock, stock_level_status 
                        FROM supply 
                        WHERE item_name = %s
                    """, (item_name,))
                    result = cursor.fetchone()
                    if result:
                        current_stock = result[0] if current_stock is None else current_stock
                        stock_status = result[1] if stock_status is None else stock_status
                    cursor.close()
                    connect.close()
                except Exception as e:
                    print(f"Error fetching supply data: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Handle final None values
        stock_status = stock_status or "Unknown Stock Level"
        current_stock = current_stock if current_stock is not None else "Unknown"
        restock_qty = restock_qty if restock_qty is not None else "Unknown"
        patient_id = patient_id or 0
        
        if notif_type == 'New Patient Added':
            return f"{patient_name} was added to the system by {user_fullname}"
        
        elif notif_type == 'Patient Status':
            if patient_status == 'Reactivated':
                return f"{patient_name} is now an active patient again. Reactivated by: {user_fullname}"
            elif patient_status == 'Deactivated':
                return f"{patient_name} is now inactive, go to the patient information to reactivate"
            else:
                return f"{patient_name} status updated by {user_fullname}"
        
        elif notif_type == 'Item Restocked':
            return f"{item_name} was restocked with {restock_qty}. Current stock: {current_stock}"
        
        elif notif_type == 'Item Stock Status Alert':
            return f"{item_name} is at {stock_status} and only has {current_stock} quantities left, please inform the admin"
        
        elif notif_type == 'New Item Added':
            return f"{item_name} was added to the system by {user_fullname}"
        
        elif notif_type == 'Item Usage Recorded':
            return f"{item_name} usage was recorded. Current stock: {current_stock}"
        
        elif notif_type == 'Manual Backup':
            return f"Backup was made by {user_fullname}"
        
        elif notif_type == 'Scheduled Backup':
            return f"Scheduled backup completed successfully"
        
        else:
            # Generic message for unknown types
            return f"{notif_type} by {user_fullname}"

    def clear_notification_widgets(self):
        """Clear all notification widgets"""
        for widget in self.notification_widgets:
            widget.destroy()
        self.notification_widgets.clear()

    def create_notification_widget(self, notif_type, message, formatted_date):
        """Create a notification widget based on type"""
        # Determine colors and icon based on notification type
        color_config = self.get_notification_config(notif_type)
        
        # Create notification container
        notif_box = ctk.CTkFrame(
            self.notification_frame,
            width=350,
            height=70,
            fg_color="#FFFFFF",
            corner_radius=10,
            bg_color="#F4f4f4"
        )
        notif_box.pack(padx=10, pady=(5, 5), fill="x")
        
        # Color coding bar
        color_bar = ctk.CTkFrame(
            notif_box,
            width=8,
            height=70,
            fg_color=color_config['color'],
            corner_radius=0
        )
        color_bar.place(x=0, y=0)
        
        # Icon area
        icon_frame = ctk.CTkFrame(
            notif_box,
            width=50,
            height=50,
            fg_color=color_config['bg_color'],
            corner_radius=25
        )
        icon_frame.place(x=15, y=10)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=color_config['icon'],
            font=("Arial", 20)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Notification title
        title_label = ctk.CTkLabel(
            notif_box,
            text=color_config['title'],
            font=("Merriweather Sans Bold", 11),
            text_color="#000000",
            anchor="w"
        )
        title_label.place(x=75, y=8)
        
        # Notification message
        message_label = ctk.CTkLabel(
            notif_box,
            text=message[:50] + "..." if len(message) > 50 else message,
            font=("Merriweather Sans", 10),
            text_color="#104E44",
            anchor="w"
        )
        message_label.place(x=75, y=28)
        
        # Timestamp
        time_label = ctk.CTkLabel(
            notif_box,
            text=formatted_date,
            font=("Arial", 9),
            text_color="#666666",
            anchor="w"
        )
        time_label.place(x=75, y=48)
        
        # Store widget reference
        self.notification_widgets.append(notif_box)

    def get_notification_config(self, notif_type):
        """Get configuration for different notification types"""
        configs = {
            # Patient related
            'New Patient Added': {
                'color': '#009BB7',
                'bg_color': '#E3F2FD',
                'icon': '👤',
                'title': 'New Patient'
            },
            'Patient Status': {
                'color': '#009BB7',
                'bg_color': '#E3F2FD',
                'icon': '👤',
                'title': 'Patient Update'
            },
            
            # Supply related
            'Item Restocked': {
                'color': '#4CAF50',
                'bg_color': '#E8F5E8',
                'icon': '📦',
                'title': 'Item Restocked'
            },
            'Item Stock Status Alert': {
                'color': '#FF9800',
                'bg_color': '#FFF3E0',
                'icon': '⚠️',
                'title': 'Stock Alert'
            },
            'New Item Added': {
                'color': '#4CAF50',
                'bg_color': '#E8F5E8',
                'icon': '📦',
                'title': 'New Supply Item'
            },
            'Item Usage Recorded': {
                'color': '#2196F3',
                'bg_color': '#E3F2FD',
                'icon': '📊',
                'title': 'Usage Recorded'
            },
            
            # Backup related
            'Manual Backup': {
                'color': '#81D7B1',
                'bg_color': '#E8F5E8',
                'icon': '💾',
                'title': 'Manual Backup'
            },
            'Scheduled Backup': {
                'color': '#81D7B1',
                'bg_color': '#E8F5E8',
                'icon': '🕒',
                'title': 'Scheduled Backup'
            },
            
            # System/Audit related
            'User Login': {
                'color': '#9C27B0',
                'bg_color': '#F3E5F5',
                'icon': '🔐',
                'title': 'User Activity'
            },
            'Data Export': {
                'color': '#FF5722',
                'bg_color': '#FFF3E0',
                'icon': '📤',
                'title': 'Data Export'
            }
        }
        
        # Return default config if type not found
        return configs.get(notif_type, {
            'color': '#666666',
            'bg_color': '#F5F5F5',
            'icon': '📋',
            'title': notif_type  
        })

    def show_no_notifications(self):
        """Show message when no notifications are available"""
        no_notif_frame = ctk.CTkFrame(
            self.notification_frame,
            width=350,
            height=100,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        no_notif_frame.pack(padx=10, pady=20)
        
        icon_label = ctk.CTkLabel(
            no_notif_frame,
            text="🔔",
            font=("Arial", 30),
            text_color="#CCCCCC"
        )
        icon_label.place(relx=0.5, rely=0.3, anchor="center")
        
        message_label = ctk.CTkLabel(
            no_notif_frame,
            text="No recent activity",
            font=("Merriweather Bold", 14),
            text_color="#999999"
        )
        message_label.place(relx=0.5, rely=0.7, anchor="center")
        
        self.notification_widgets.append(no_notif_frame)

    def show_error_message(self):
        """Show error message when loading fails"""
        error_frame = ctk.CTkFrame(
            self.notification_frame,
            width=350,
            height=100,
            fg_color="#FFEBEE",
            corner_radius=10
        )
        error_frame.pack(padx=10, pady=20)
        
        icon_label = ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=("Arial", 30),
            text_color="#F44336"
        )
        icon_label.place(relx=0.5, rely=0.3, anchor="center")
        
        message_label = ctk.CTkLabel(
            error_frame,
            text="Error loading notifications",
            font=("Merriweather Bold", 14),
            text_color="#F44336"
        )
        message_label.place(relx=0.5, rely=0.7, anchor="center")
        
        self.notification_widgets.append(error_frame)

    def refresh_notifications(self):
        """Refresh notifications manually"""
        print("🔄 Refreshing notifications...")
        self.load_notifications()

    def toggle(self):
        """Toggle notification frame visibility"""
        if self.visible:
            self.place_forget()
            self.visible = False
        else:
            # Refresh notifications when opening
            self.load_notifications()
            self.place(relx=0.7, rely=0.08)
            self.lift()
            self.visible = True

    def auto_refresh(self):
        """Auto-refresh notifications every 30 seconds"""
        if self.visible:
            self.load_notifications()
        # Schedule next refresh
        self.after(30000, self.auto_refresh)  # 30 seconds

    def destroy(self):
        """Clean up when destroyed"""
        self.clear_notification_widgets()
        super().destroy()

class PatientSearchResultsFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=400, height=400, fg_color="white", corner_radius=10, **kwargs)
        self.place_forget()  # Initially hidden
        self.visible = False
        self.parent = parent  # Reference to PatientPage
        
        # Header Frame
        header_frame = ctk.CTkFrame(self, width=400, height=50, fg_color="#68EDC6", corner_radius=10)
        header_frame.place(x=0, y=0)
        
        header_title = ctk.CTkLabel(
            header_frame, 
            font=("Merriweather", 16, "bold"), 
            text="Patient Search Results", 
            text_color="white"
        )
        header_title.place(x=20, y=15)
        
        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            width=30,
            height=30,
            text="✕",
            fg_color="transparent",
            hover_color="#5AA3A3",
            font=("Arial", 16),
            command=self.hide
        )
        close_btn.place(x=350, y=10)
        
        # Scrollable Results Frame
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            width=380,
            height=330,
            fg_color="#f8f9fa",
            corner_radius=0
        )
        self.results_frame.place(x=10, y=60)
        
        # No results label (initially hidden)
        self.no_results_label = ctk.CTkLabel(
            self.results_frame,
            text="No results found",
            font=("Arial", 14),
            text_color="#666666"
        )
        
    def show_results(self, search_text, results):
        """Display search results in the frame"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not results:
            # Show no results message
            self.no_results_label = ctk.CTkLabel(
                self.results_frame,
                text=f"No patients found for '{search_text}'",
                font=("Arial", 14),
                text_color="#666666"
            )
            self.no_results_label.pack(pady=50)
        else:
            # Display patients section
            patients_header = ctk.CTkLabel(
                self.results_frame,
                text=f"👥 PATIENTS ({len(results)})",
                font=("Merriweather", 14, "bold"),
                text_color="#2E7D4F"
            )
            patients_header.pack(anchor="w", padx=10, pady=(10, 5))
            
            for patient in results:
                self.create_patient_item(patient)
        
        # Show the frame
        self.show()
    
    def create_patient_item(self, patient):
        """Create a patient result item"""
        patient_frame = ctk.CTkFrame(
            self.results_frame,
            width=360,
            height=80,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E0E0E0"
        )
        patient_frame.pack(fill="x", padx=10, pady=3)
        patient_frame.pack_propagate(False)
        
        # Patient icon
        icon_frame = ctk.CTkFrame(
            patient_frame,
            width=50,
            height=50,
            fg_color="#E3F2FD",
            corner_radius=25
        )
        icon_frame.place(x=10, y=15)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text="👤",
            font=("Arial", 20)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Patient details
        name_label = ctk.CTkLabel(
            patient_frame,
            text=patient['patient_name'],
            font=("Merriweather", 14, "bold"),
            text_color="black"
        )
        name_label.place(x=70, y=12)
        
        details_text = f"Age: {patient['age']} • Gender: {patient['gender']}"
        details_label = ctk.CTkLabel(
            patient_frame,
            text=details_text,
            font=("Arial", 11),
            text_color="#666666"
        )
        details_label.place(x=70, y=32)
        
        access_label = ctk.CTkLabel(
            patient_frame,
            text=f"Access: {patient['access_type']}",
            font=("Arial", 11),
            text_color="#666666"
        )
        access_label.place(x=70, y=50)
        
        # View button
        view_btn = ctk.CTkButton(
            patient_frame,
            width=60,
            height=25,
            text="View",
            font=("Arial", 11),
            fg_color="#68EDC6",
            hover_color="#5AA3A3",
            corner_radius=5,
            command=lambda p=patient: self.view_patient(p)
        )
        view_btn.place(x=290, y=27)
    
    def view_patient(self, patient):
        """Handle viewing a patient - redirect to detailed view"""
        print(f"\n👤 VIEWING PATIENT:")
        print(f"   ID: {patient['patient_id']}")
        print(f"   Name: {patient['patient_name']}")
        print(f"   Age: {patient['age']}")
        print(f"   Gender: {patient['gender']}")
        print(f"   Access Type: {patient['access_type']}")
        print("=" * 40)
        
        # Hide search results
        self.hide()
        
        # Show detailed patient view using existing method
        import threading
        threading.Thread(target=lambda: self.parent.show_detailed_info(patient['patient_id'])).start()
    
    def show(self):
        """Show the search results frame"""
        self.place(x=480, y=130)  # Position below search bar
        self.lift()
        self.visible = True
    
    def hide(self):
        """Hide the search results frame"""
        self.place_forget()
        self.visible = False

class PatientPage(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state
        self.patient_id = None 

        # Initialize search results frame
        self.search_results_frame = PatientSearchResultsFrame(self)

        self.navbar = ctk.CTkFrame(self, fg_color="white", height=130)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)
        self.navbar.configure(border_width=0, border_color="black")

        #self.dropdown_visible = False 

        #self.dropdown_frame = ctk.CTkFrame(self.navbar, fg_color="#f0f0f0", corner_radius=8, width=150, height=100)
        #self.dropdown_frame.configure(border_width=1, border_color="gray")
        #self.dropdown_frame.place_forget()
        
        self.notif_frame = NotificationFrame(self)
        self.settings_frame = SettingsFrame(self)

        # Load images
        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))

        icon_y = 62

        # Notification button
        notif_btn = ctk.CTkButton(
            self.navbar, 
            image=notif_img, 
            text="", 
            width=40, 
            height=40, 
            fg_color="transparent", 
            hover_color="#f5f5f5",
            command=self.notif_frame.toggle
        )
        notif_btn.place(relx=1.0, x=-110, y=icon_y, anchor="center")

        # Settings button 
        settings_btn = ctk.CTkButton(
            self.navbar, 
            image=settings_img, 
            text="", 
            width=40, 
            height=40, 
            fg_color="transparent", 
            hover_color="#f5f5f5", 
            command=self.settings_frame.toggle  
        )
        settings_btn.place(relx=1.0, x=-160, y=icon_y, anchor="center")

        #ctk.CTkButton(self.dropdown_frame, text="Account Settings", width=140, command=self.open_settings).pack(pady=5)
        #ctk.CTkButton(self.dropdown_frame, text="Log Out", width=140, command=self.logout).pack(pady=5)

        self.bottom_line = ctk.CTkFrame(self.navbar, height=1.5, fg_color="black")
        self.bottom_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        # Table view setup
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        style.map("Treeview", background=[("selected", "#68EDC6")])

        self.hovered_row = None

        #Button Frame
        self.button_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")

        button_font = ("Merriweather Bold", 15)
        # Add Button
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Add",
            text_color="#FFFFFF",
            fg_color="#1A374D",
            bg_color="#FFFFFF",
            font=button_font,
            corner_radius=20,
            command=self.open_add_window,
            width=180,  
            height=40    
        )
        self.add_button.pack(side="left", padx=10)

        # Sort dropdown
        self.sort_dropdown = ctk.CTkOptionMenu(
            self.button_frame,
            values=["Patient ID", "Patient Name", "Age", "Gender", "Type of Access", "Date Registered"],
            font=button_font,
            width=180,
            button_color="#1A374D",
            height=40,
            fg_color="#1A374D",
            bg_color="#FFFFFF",
            corner_radius=20,
            command=self.sort_by_option_simple
        )
        self.sort_dropdown.pack(side="left", padx=10)
        self.sort_dropdown.set("        Sort By")
 
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
        self.search_container.place(x=480, y=70, anchor="w")

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

        button_font = ("Merriweather Bold", 15)
        # Edit Usage Button
        self.edit_usage_button = ctk.CTkButton(
            self.navbar,
            text="Edit Usage",
            font=button_font,
            text_color="#FFFFFF",
            width=180,
            height=40,
            fg_color="#1A374D",
            hover_color="#1A374D",
            corner_radius=20,
            command=self.edit_usage_clicked
        )
        self.edit_usage_button.place(x=1100, y=70, anchor="w")

        self.table_frame = ctk.CTkFrame(self, fg_color="#1A374D", border_width=2, border_color="black")

        tree_container = ctk.CTkFrame(self.table_frame, fg_color="black")
        tree_container.pack(fill="both", expand=True, padx=1, pady=1)

        columns = ("patient_id", "patient_name", "age", "gender", "access_type", "date_registered")
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

        # Setup search functionality
        self.setup_search_functionality()

    # Detailed info frame
        self.detailed_info_frame = ctk.CTkFrame(self, fg_color="#E8FBFC")

        title_font=("Merriweather Bold",25)
        label_font=("Merriweather Light",15)
        output_font=("Merriweather Sans Bold",18)

        #Photo Frame
        self.photo_frame = ctk.CTkFrame(
            self.detailed_info_frame,
            width=400,
            height=400,
            fg_color="white",
            corner_radius=20
        )
        
        self.photo_frame.place(x=200,y=200)


        self.top_frame = ctk.CTkFrame(
            self.photo_frame,
            width=400,
            height=250,
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
        self.patient_id_label.place(relx=0.5, rely=0.70, anchor="center")

        self.patient_id_value = ctk.CTkLabel(self.photo_frame,
            text="",
            font=("Merriweather", 14),
            text_color="black"
        )
        self.patient_id_value.place(relx=0.5, rely=0.80, anchor="center")

        #PATIENT INFROMATION
        info_frame = ctk.CTkFrame(
            self.detailed_info_frame,
            width=950,
            height=500,
            fg_color="#FFFFFF",
            corner_radius=25,
            bg_color="#E8FBFC"
        )
        info_frame.place(x=550, y=150) 

        left_bar = ctk.CTkFrame(
            info_frame,
            width=15,
            height=500,
            fg_color="#68EDC6",
            corner_radius=20
        )
        left_bar.place(x=0)

        

        title_label = ctk.CTkLabel(info_frame, text="Patient Info", font=title_font)
        title_label.place(x=50, y=20)

        self.lastname_label = ctk.CTkLabel(info_frame, text="Last Name", font=label_font,height=15)
        self.lastname_label.place(relx=0.125, rely=0.2)
        self.lastname_labelv = ctk.CTkLabel(info_frame, text="Lopez", font=output_font,height=18)
        self.lastname_labelv.place(relx=0.125, rely=0.26)

        self.firstname_label = ctk.CTkLabel(info_frame, text="First Name", font=label_font,height=15)
        self.firstname_label.place(relx=0.35, rely=0.2)
        self.firstname_labelv = ctk.CTkLabel(info_frame, text="Juan", font=output_font,height=18)
        self.firstname_labelv.place(relx=0.35, rely=0.26)

        self.middlename_label = ctk.CTkLabel(info_frame, text="Middle Name", font=label_font,height=15)
        self.middlename_label.place(relx=0.575, rely=0.2)
        self.middlename_labelv = ctk.CTkLabel(info_frame, text="Carlos", font=output_font,height=18)
        self.middlename_labelv.place(relx=0.575, rely=0.26)

        self.status_label = ctk.CTkLabel(info_frame, text="Status", font=label_font,height=15)
        self.status_label.place(relx=0.125, rely=0.4)
        self.status_labelv = ctk.CTkLabel(info_frame, text="Active", font=output_font,height=18)
        self.status_labelv.place(relx=0.125, rely=0.46)

        self.access_type_label = ctk.CTkLabel(info_frame, text="Type of Access", font=label_font,height=15)
        self.access_type_label.place(relx=0.35, rely=0.4)
        self.access_type_labelv = ctk.CTkLabel(info_frame, text="Admin", font=output_font,height=18)
        self.access_type_labelv.place(relx=0.35, rely=0.46)

        self.birthdate_label = ctk.CTkLabel(info_frame, text="Birthdate", font=label_font,height=15)
        self.birthdate_label.place(relx=0.575, rely=0.4)
        self.birthdate_labelv = ctk.CTkLabel(info_frame, text="01/01/1980", font=output_font,height=18)
        self.birthdate_labelv.place(relx=0.575, rely=0.46)

        self.age_label = ctk.CTkLabel(info_frame, text="Age", font=label_font,height=15)
        self.age_label.place(relx=0.8, rely=0.4)
        self.age_labelv = ctk.CTkLabel(info_frame, text="45", font=output_font,height=18)
        self.age_labelv.place(relx=0.8, rely=0.46)

        self.gender_label = ctk.CTkLabel(info_frame, text="Gender", font=label_font,height=15)
        self.gender_label.place(relx=0.125, rely=0.6)
        self.gender_labelv = ctk.CTkLabel(info_frame, text="Male", font=output_font,height=18)
        self.gender_labelv.place(relx=0.125, rely=0.66)

        self.height_label = ctk.CTkLabel(info_frame, text="Height", font=label_font,height=15)
        self.height_label.place(relx=0.35, rely=0.6)
        self.height_labelv = ctk.CTkLabel(info_frame, text="5'8\"", font=output_font,height=18)
        self.height_labelv.place(relx=0.35, rely=0.66)

        self.civil_status_label = ctk.CTkLabel(info_frame, text="Civil Status", font=label_font,height=15)
        self.civil_status_label.place(relx=0.575, rely=0.6)
        self.civil_status_labelv = ctk.CTkLabel(info_frame, text="Married", font=output_font,height=18)
        self.civil_status_labelv.place(relx=0.575, rely=0.66)

        self.religion_label = ctk.CTkLabel(info_frame, text="Religion", font=label_font,height=15)
        self.religion_label.place(relx=0.8, rely=0.6)
        self.religion_labelv = ctk.CTkLabel(info_frame, text="Christian", font=output_font,height=18)
        self.religion_labelv.place(relx=0.8, rely=0.66)

        self.address_label = ctk.CTkLabel(info_frame, text="Complete Address", font=label_font,height=15)
        self.address_label.place(relx=0.125, rely=0.8)
        self.address_labelv = ctk.CTkLabel(info_frame, text="1234 Elm St, Quezon City", font=output_font,height=18)
        self.address_labelv.place(relx=0.125, rely=0.86)

        contact_options_panel = ctk.CTkFrame(
            self.detailed_info_frame,
            width=400,
            height=400,
            fg_color="#FFFFFF",
            corner_radius=25,
            bg_color="#E8FBFC"
        )
        contact_options_panel.place(x=80, y=600)  

        button_font = ("Merriweather Bold", 15)

        left_bar = ctk.CTkFrame(
            contact_options_panel,
            width=15,
            height=400,
            fg_color="#1A374D",
            corner_radius=0
        )
        left_bar.place(x=0, y=0)

        patient_history_btn = ctk.CTkButton(
            contact_options_panel,
            text="Patient History",
            text_color="#FFFFFF",
            font=button_font,
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
            text_color="#FFFFFF",
            font=button_font,
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
            text_color="#FFFFFF",
            font=button_font,
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
            text_color="#FFFFFF",
            font=button_font,
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_quantity_used_info
        )
        quantity_used_btn.place(x=80, y=290)


        #Philhealth Info
        philhealth_info_panel = ctk.CTkFrame(
            self.detailed_info_frame,
            width=950,
            height=300,
            fg_color="white",
            corner_radius=20,
            bg_color="#E8FBFC"
        )
        philhealth_info_panel.place(x=550, y=700) 

        left_bar = ctk.CTkFrame(
            philhealth_info_panel,
            width=15,
            height=300,
            fg_color="#68EDC6",
            corner_radius=20
        )
        left_bar.place(x=0, y=0)

        title_label = ctk.CTkLabel(philhealth_info_panel,text="Phil Health and Other Info",font=title_font)
        title_label.place(x=50, y=20)

        self.philhealth_number_label = ctk.CTkLabel(philhealth_info_panel,text="PhilHealth Number",font=label_font,height=15)
        self.philhealth_number_label.place(relx=.125,rely=.3)
        self.philhealth_number_labelv = ctk.CTkLabel(philhealth_info_panel,text="PH1234567890",font=output_font,height=18)
        self.philhealth_number_labelv.place(relx=.125,rely=.4)

        self.membership_label = ctk.CTkLabel(philhealth_info_panel,text="Membership",font=label_font,height=15)
        self.membership_label.place(relx=.35,rely=.3)
        self.membership_labelv = ctk.CTkLabel(philhealth_info_panel,text="Active",font=output_font,height=18)
        self.membership_labelv.place(relx=.35,rely=.4)

        self.pwd_label = ctk.CTkLabel(philhealth_info_panel,text="PWD",font=label_font,height=15)
        self.pwd_label.place(relx=.125,rely=.6)
        self.pwd_labelv = ctk.CTkLabel(philhealth_info_panel,text="Yes",font=output_font,height=18)
        self.pwd_labelv.place(relx=.125,rely=.7)

        self.pwd_id_label = ctk.CTkLabel(philhealth_info_panel,text="PWD ID No.",font=label_font,height=15)
        self.pwd_id_label.place(relx=.35,rely=.6)
        self.pwd_id_labelv = ctk.CTkLabel(philhealth_info_panel,text="PWD987654321",font=output_font,height=18)
        self.pwd_id_labelv.place(relx=.35,rely=.7)

        self.senior_label = ctk.CTkLabel(philhealth_info_panel,text="SENIOR",font=label_font,height=15)
        self.senior_label.place(relx=.575,rely=.6)
        self.senior_labelv = ctk.CTkLabel(philhealth_info_panel,text="No",font=output_font,height=18)
        self.senior_labelv.place(relx=.575,rely=.7)

        self.senior_id_label = ctk.CTkLabel(philhealth_info_panel,text="SENIOR ID No.",font=label_font,height=15)
        self.senior_id_label.place(relx=.8,rely=.6)
        self.senior_id_labelv = ctk.CTkLabel(philhealth_info_panel,text="None",font=output_font,height=18)
        self.senior_id_labelv.place(relx=.8,rely=.7)

        self.back_button = ctk.CTkButton(self.detailed_info_frame, text="Back", font=button_font,text_color="#FFFFFF",
            corner_radius=20,
            width=200,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50", 
            command=self.show_table_view)
        self.back_button.place(x=10, y=10)

        self.upload_button = ctk.CTkButton(self.detailed_info_frame, text="Upload Photo", font=button_font,text_color="#FFFFFF",
            corner_radius=20,
            width=200,
            height=40,
            fg_color="#00C88D",
            hover_color="#013B50")
        self.upload_button.place(x=700, y=10)

        self.edit_button_detailed = ctk.CTkButton(self.detailed_info_frame, text="Edit Details", font=button_font,text_color="#FFFFFF",
            corner_radius=20,
            width=200,
            height=40,
            fg_color="#01516D",
            command=self.open_edit_window,
            hover_color="#013B50")
        self.edit_button_detailed.place(x=1050, y=10)

        self.button_frame.place(x=20, y=50, anchor="nw")  
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)

        self.populate_table(self.fetch_patient_data())

    def edit_usage_clicked(self):
        """Handle Edit usage button click"""
        print("Edit usage button clicked!")
        try:
            edit_window = EditUsageWindow(self)
            edit_window.grab_set()  
            edit_window.focus_force()
            
            # Wait for window to close, then refresh supply data
            self.wait_window(edit_window)
            
            # Refresh the patient table after usage is recorded
            self.refresh_table()
            
            # Also refresh the supply page table
            self.refresh_supply_page_after_usage()
            
            # If we're in detailed view, refresh that too
            if hasattr(self, 'patient_id_value'):
                current_patient_id = self.patient_id_value.cget("text")
                if current_patient_id:
                    self.refresh_after_update()
                    
                    # Refresh any open quantity used windows
                    self.refresh_quantity_used_windows(current_patient_id)
                    
        except Exception as e:
            print(f"Error opening Edit Usage window: {e}")

    def disable_detailed_buttons(self):
        """Disable buttons in the detailed view"""
        if hasattr(self, 'back_button'):
            self.back_button.configure(state="disabled")
        if hasattr(self, 'upload_button'):
            self.upload_button.configure(state="disabled")  
        if hasattr(self, 'edit_button_detailed'):
            self.edit_button_detailed.configure(state="disabled")
        if hasattr(self, 'edit_usage_button'):
            self.edit_usage_button.configure(state="disabled")

    def enable_detailed_buttons(self):
        """Enable buttons in the detailed view"""
        if hasattr(self, 'back_button'):
            self.back_button.configure(state="normal")
        if hasattr(self, 'upload_button'):
            self.upload_button.configure(state="normal")
        if hasattr(self, 'edit_button_detailed'):
            self.edit_button_detailed.configure(state="normal")
        if hasattr(self, 'edit_usage_button'):
            self.edit_usage_button.configure(state="normal")

    def refresh_quantity_used_windows(self, patient_id):
        """Refresh any open quantity used log windows for the current patient"""
        try:
            print(f"🔍 Looking for quantity used windows for patient {patient_id}...")
            
            # Check stored references first
            if hasattr(self, 'open_quantity_windows') and patient_id in self.open_quantity_windows:
                window = self.open_quantity_windows[patient_id]
                if window and window.winfo_exists():
                    print(f"🔄 Refreshing stored quantity used window for patient {patient_id}")
                    if hasattr(window, 'refresh_table'):
                        window.refresh_table()
                    elif hasattr(window, 'load_usage_data'):
                        window.load_usage_data()
                    elif hasattr(window, 'reload_data'):
                        window.reload_data()
                    print("✅ Stored quantity used window refreshed!")
                    return
            
            # Search through all windows if no stored reference
            windows_to_check = []
            
            # Check direct children
            windows_to_check.extend(self.winfo_children())
            
            # Check master's children (application level)
            if hasattr(self.master, 'winfo_children'):
                windows_to_check.extend(self.master.winfo_children())
                
            # Check master's master children (top level)
            if hasattr(self.master, 'master') and hasattr(self.master.master, 'winfo_children'):
                windows_to_check.extend(self.master.master.winfo_children())
            
            for child in windows_to_check:
                try:
                    class_name = child.__class__.__name__
                    if 'PatientQuantityUsedLogsWindow' in class_name or 'QuantityUsed' in class_name:
                        if hasattr(child, 'patient_id') and str(child.patient_id) == str(patient_id):
                            print(f"🔄 Found and refreshing quantity used window for patient {patient_id}")
                            
                            # Try different refresh method names
                            if hasattr(child, 'refresh_table'):
                                child.refresh_table()
                            elif hasattr(child, 'load_usage_data'):
                                child.load_usage_data()
                            elif hasattr(child, 'reload_data'):
                                child.reload_data()
                            elif hasattr(child, 'refresh_data'):
                                child.refresh_data()
                            else:
                                print(f"⚠️ Quantity used window found but no refresh method available")
                                
                            print("✅ Quantity used window refreshed!")
                            return
                except Exception as e:
                    # Skip this window if there's an error checking it
                    continue
                    
            print(f"ℹ️ No open quantity used windows found for patient {patient_id}")
                            
        except Exception as e:
            print(f"❌ Error refreshing quantity used windows: {e}")

    def refresh_supply_page_after_usage(self):
        """Refresh the supply page table after usage is recorded"""
        try:
            # Access the main application instance and refresh supply page
            if hasattr(self.master, 'master') and hasattr(self.master.master, 'pages'):
                supply_page = self.master.master.pages.get('Supply')
                if supply_page and hasattr(supply_page, 'refresh_table'):
                    print("🔄 Refreshing supply page after usage recording...")
                    supply_page.refresh_table()
                    print("✅ Supply page refreshed successfully!")
                    
                    # If supply page is in detailed view, refresh that too
                    if hasattr(supply_page, 'selected_supply_id') and supply_page.selected_supply_id:
                        supply_page.refresh_detailed_view()
                else:
                    print("❌ Could not find supply page to refresh")
            else:
                print("❌ Could not access main application pages")
        except Exception as e:
            print(f"❌ Error refreshing supply page: {e}")

    # SEARCH FUNCTIONALITY METHODS
    def setup_search_functionality(self):
        """Setup search functionality for the search entry"""
        # Bind the search entry to trigger search on key release
        self.search_entry.bind("<KeyRelease>", self.on_search_key_release)
        self.search_entry.bind("<Return>", self.perform_search)  # Enter key
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)  # Hide results when focus lost
        self.search_entry.bind("<Button-1>", self.on_search_click)  # Show results on click

    def on_search_click(self, event):
        """Handle click on search entry"""
        search_text = self.search_entry.get().strip()
        if len(search_text) >= 2:
            # If there's already text, perform search to show results
            self.perform_search(None)

    def on_search_key_release(self, event):
        """Handle key release events in search entry"""
        search_text = self.search_entry.get().strip()
        
        # Hide results if search is empty
        if len(search_text) == 0:
            self.search_results_frame.hide()
            return
            
        # Only search if there's text and it's more than 1 character
        if len(search_text) >= 2:
            # Add a small delay to avoid searching on every keystroke
            if hasattr(self, 'search_timer'):
                self.after_cancel(self.search_timer)
            self.search_timer = self.after(300, lambda: self.perform_search(None))
        elif len(search_text) == 1:
            # Hide results for single character
            self.search_results_frame.hide()

    def on_search_focus_out(self, event):
        """Handle when search entry loses focus"""
        # Add a small delay before hiding to allow clicking on results
        self.after(200, self.check_and_hide_results)
    
    def check_and_hide_results(self):
        """Check if we should hide the results frame"""
        # Get the widget that currently has focus
        focused_widget = self.focus_get()
        
        # If the focused widget is not part of the search results frame, hide it
        if (focused_widget != self.search_entry and 
            not self.is_widget_in_frame(focused_widget, self.search_results_frame)):
            self.search_results_frame.hide()
    
    def is_widget_in_frame(self, widget, frame):
        """Check if a widget is inside a specific frame"""
        if widget is None:
            return False
        
        parent = widget
        while parent:
            if parent == frame:
                return True
            parent = parent.master
        return False

    def perform_search(self, event):
        """Perform the actual search operation for patients only"""
        search_text = self.search_entry.get().strip()
        
        if not search_text or len(search_text) < 2:
            self.search_results_frame.hide()
            return
        
        try:
            connect = db()
            cursor = connect.cursor()

            # Search only in patient_list table
            cursor.execute("""
                SELECT patient_id, patient_name, age, gender, access_type, date_registered
                FROM patient_list
                WHERE patient_name LIKE %s OR CAST(patient_id AS CHAR) LIKE %s OR gender LIKE %s OR access_type LIKE %s
                ORDER BY patient_name
            """, (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))

            search_results = cursor.fetchall()
            
            # Convert results to patient dictionaries
            patients = []
            for result in search_results:
                patients.append({
                    'patient_id': result[0],
                    'patient_name': result[1],
                    'age': result[2],
                    'gender': result[3],
                    'access_type': result[4],
                    'date_registered': result[5]
                })
            
            # Show results in the search frame
            self.search_results_frame.show_results(search_text, patients)
            
            # Keep the existing console output for debugging
            print(f"\n=== Patient Search Results for '{search_text}' ===")
            if patients:
                for patient in patients:
                    print(f'👥 PATIENT: {patient["patient_name"]} (Age: {patient["age"]}, Gender: {patient["gender"]}, Access: {patient["access_type"]})')
                print(f"\nSummary: Found {len(patients)} patients")
            else:
                print(f"No patients found for '{search_text}'")

        except Exception as e:
            print(f'Error performing patient search: {e}')
            # Show error in search frame
            self.search_results_frame.show_results(search_text, [])
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    # EXISTING METHODS (unchanged)
    def sort_by_option_simple(self, option):
        """Handle sorting for the patient table"""
        print(f"Sorting patients by: {option}")
        
        # Don't sort if "Sort By" placeholder is selected
        if option == "Sort By":
            return
            
        self.perform_sort(option)

    def perform_sort(self, sort_option):
        """Perform the actual sorting based on the selected option for patient table"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Map display names to database column names for patient_list
            column_mapping = {
                "Patient ID": "patient_id",
                "Patient Name": "patient_name",
                "Age": "age",
                "Gender": "gender", 
                "Type of Access": "access_type",
                "Date Registered": "date_registered"
            }
            
            db_column = column_mapping.get(sort_option, "patient_id")
            
            # Special handling for different data types
            if sort_option == "Age":
                # Sort numerically for age
                cursor.execute("""
                    SELECT patient_id, patient_name, age, gender, access_type, date_registered
                    FROM patient_list
                    ORDER BY CAST(age AS UNSIGNED) ASC
                """)
            elif sort_option == "Patient ID":
                # Sort numerically for patient ID
                cursor.execute("""
                    SELECT patient_id, patient_name, age, gender, access_type, date_registered
                    FROM patient_list
                    ORDER BY CAST(patient_id AS UNSIGNED) ASC
                """)
            elif sort_option == "Date Registered":
                # Sort by date (newest first)
                cursor.execute("""
                    SELECT patient_id, patient_name, age, gender, access_type, date_registered
                    FROM patient_list
                    ORDER BY date_registered ASC
                """)
            else:
                # Standard alphabetical sorting for other columns
                cursor.execute(f"""
                    SELECT patient_id, patient_name, age, gender, access_type, date_registered
                    FROM patient_list
                    ORDER BY {db_column} ASC
                """)
            
            sorted_data = cursor.fetchall()
            
            # Clear and repopulate the table with sorted data
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            for row in sorted_data:
                self.tree.insert("", "end", values=row)
            
            # Update the dropdown text to show current sort
            self.sort_dropdown.set(f"{sort_option}")
            
            print(f"Patient table sorted by: {sort_option}")
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            print(f'Error sorting patients by {sort_option}:', e)
            # Reset dropdown on error
            self.sort_dropdown.set("Sort By")

    # Navbar methods 
    """def toggle_dropdown(self):
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
        print("Logging out...")"""
    
    def open_patient_history(self):
        # Get reference to sidebar from main app
        sidebar = None
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'sidebar'):
            sidebar = self.master.master.sidebar
        
        self.patient_history_window = PatientHistory(self.master, sidebar=sidebar, patient_page=self)
        self.patient_history_window.place(relx=.5,rely=.5,anchor="center")

        patient_id = self.patient_id_value.cget("text")

        patient_family_history = DataRetrieval.patient_family_history(patient_id)
        patient_medical_history = DataRetrieval.patient_medical_history(patient_id)
        patient_other_history = DataRetrieval.patient_other_history(patient_id)

        self.patient_history_window.family_history.display_family_history(patient_family_history)
        self.patient_history_window.medical_history.display_medical_history(patient_medical_history)
        self.patient_history_window.other_history.display_other_history(patient_other_history)

    def open_medication(self):
        sidebar = None
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'sidebar'):
            sidebar = self.master.master.sidebar
        
        self.medication_window = Medication(self.master, sidebar=sidebar, patient_page=self)
        self.medication_window.place(relx=.5,rely=.5,anchor="center")
        self.medication_window.medication_info(self.patient_id_value.cget("text"))

    def open_contact_info(self):
        sidebar = None
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'sidebar'):
            sidebar = self.master.master.sidebar
        
        self.contact_info_window = ContactInfoRelativeInfo(self.master, sidebar=sidebar, patient_page=self)
        self.contact_info_window.place(relx=.5,rely=.5,anchor="center")
        self.contact_info_window.contact_relative_info(self.patient_id_value.cget("text"))

    def open_quantity_used_info(self):
        # Get the current patient ID from the detailed view
        patient_id = self.patient_id_value.cget("text")
        
        if patient_id:
            print(f"Opening quantity used logs for patient ID: {patient_id}")
            
            # Create and show the Patient Quantity Used Logs window
            quantity_used_window = PatientQuantityUsedLogsWindow(self, patient_id)
            
            # Store reference to the window for potential refreshing
            if not hasattr(self, 'open_quantity_windows'):
                self.open_quantity_windows = {}
            self.open_quantity_windows[patient_id] = quantity_used_window
            
            quantity_used_window.grab_set()
            quantity_used_window.focus_force()
            
            # Clean up reference when window closes
            def on_window_close():
                if hasattr(self, 'open_quantity_windows') and patient_id in self.open_quantity_windows:
                    del self.open_quantity_windows[patient_id]
            
            quantity_used_window.protocol("WM_DELETE_WINDOW", lambda: [quantity_used_window.destroy(), on_window_close()])
            
        else:
            print("No patient selected - cannot open quantity used logs")

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
            else:
                messagebox.showwarning("No Data", "Patient record not found")

            if get_patient_philhealth_data:
                self.display_patient_philhealth_info(get_patient_philhealth_data)
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

    def refresh_after_update(self):
        """Called after a patient is updated to refresh the table and view"""
        print("🔄 Refreshing patient data after update...")
        
        # Store current patient_id if we were viewing details
        current_patient_id = self.patient_id_value.cget("text") if hasattr(self, 'patient_id_value') else None
        
        # Refresh the table
        self.refresh_table()
        
        # Trigger automatic refresh of home page pie chart
        # Access the main HomePage instance and refresh patient data
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'pages'):
            home_page = self.master.master.pages.get('Home')
            if home_page and hasattr(home_page, 'refresh_patient_data_and_chart'):
                home_page.refresh_patient_data_and_chart()
        
        # If we were viewing a patient's details, refresh that view too
        if current_patient_id:
            self.show_detailed_info(current_patient_id)
        
        print("✅ Patient data refreshed successfully!")

    def open_input_window(self, window_class, data=None):
        input_window = window_class(self.master, data or {})
        input_window.grab_set()
        input_window.focus_force()

        def on_close():
            input_window.destroy()
            # Automatically refresh after any patient input operation
            self.refresh_after_update()

        input_window.protocol("WM_DELETE_WINDOW", on_close)
        self.wait_window(input_window)
        self.refresh_table()
        self.enable_buttons()
        
        # Additional refresh after input window closes
        self.refresh_after_update()

    def refresh_table(self):
        """Refresh the patient table with latest data"""
        try:
            print("🔄 Refreshing patient table with latest data...")
            
            # Make sure we're in table view first
            self.detailed_info_frame.place_forget()
            self.photo_frame.place_forget()
            
            # Show the table and navigation elements
            self.button_frame.place(x=20, y=50, anchor="nw") 
            self.navbar.pack(fill="x", side="top")
            self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)
            
            # Clear existing table data
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Fetch fresh data and populate table
            fresh_data = self.fetch_patient_data()
            self.populate_table(fresh_data)
            
            print("✅ Patient table refreshed with latest data")
            
        except Exception as e:
            print(f"❌ Error refreshing patient table: {e}")   

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
        """Open edit window with current patient data"""
        self.disable_buttons()
        
        # Get the current patient ID
        patient_id = self.patient_id_value.cget("text")
        
        if patient_id:
            # Fetch all patient data for editing
            edit_data = {
                'patient_id': patient_id,
                'edit_mode': True
            }
            
            # Open PatientInfoWindow in edit mode
            edit_window = PatientInfoWindow(self.master, edit_data)
            edit_window.grab_set()
            edit_window.focus_force()
            
            def on_close():
                edit_window.destroy()
                self.enable_buttons()
                # Refresh data after edit window closes
                self.refresh_after_update()
            
            edit_window.protocol("WM_DELETE_WINDOW", on_close)
            self.wait_window(edit_window)
            self.enable_buttons()
            
            # Refresh data after editing
            self.refresh_after_update()
        else:
            print("No patient selected for editing")
            self.enable_buttons()

class PatientHistory(ctk.CTkFrame):
    def __init__(self, master=None, sidebar=None, patient_page=None, **kwargs):
        super().__init__(master, width=1400, height=930, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)
        self.sidebar = sidebar 
        self.patient_page = patient_page  

        self.left_bar = ctk.CTkFrame(self, width=20, fg_color="#1A374D", corner_radius=20)
        self.left_bar.place(x=0)

        self.title_label = ctk.CTkLabel(self, text="Patient History", font=("Merriweather Bold", 25))
        self.title_label.place(x=50, y=30)

        self.family_history = FamilyHistory(self)
        self.family_history.place(relx=.075,rely=.125)

        self.medical_history = MedicalHistory(self)
        self.medical_history.place(relx=.5,rely=.125)

        self.other_history = OtherHistory(self)
        self.other_history.place(relx=.075,rely=.525)

        self.exit_button = create_exit_button(self, command=self.exit_patienthistory)
        self.exit_button.place(x=1300, y=20)
        
        # Disable sidebar and patient page buttons when window opens
        if self.sidebar:
            self.sidebar.disable_buttons()
        if self.patient_page:
            self.patient_page.disable_detailed_buttons()

    def exit_patienthistory(self):
        print("Patient History closed")
        # Enable sidebar and patient page buttons when window closes
        if self.sidebar:
            self.sidebar.enable_buttons()
        if self.patient_page:
            self.patient_page.enable_detailed_buttons()
        self.place_forget()


class Medication(ctk.CTkFrame):
    def __init__(self, master=None, sidebar=None, patient_page=None, **kwargs):
        super().__init__(master, width=980, height=400, fg_color="white", corner_radius=0,**kwargs)
        self.pack_propagate(False)
        self.sidebar = sidebar 
        self.patient_page = patient_page  

        title_font=("Merriweather Bold",25)
        label_font=("Merriweather Light",15)
        output_font=("Merriweather Sans Bold",18)

        self.left_bar = ctk.CTkFrame(self, width=20, height=400,fg_color="#1A374D", corner_radius=0)
        self.left_bar.place(x=0)

        self.title_label = ctk.CTkLabel(self, text="Medication", font=title_font)
        self.title_label.place(x=50, y=20)

        self.medication_header = ctk.CTkLabel(self, text="Drugs Taken", font=label_font)
        self.medication_header.place(x=60, y=70)

        self.medication_labels = []
        y_position = 100
        for _ in range(10):
            label = ctk.CTkLabel(self, text="", font=output_font, text_color="black")
            label.place(x=100, y=y_position)
            self.medication_labels.append(label)
            y_position += 30

        self.exit_button = create_exit_button(self, command=self.exit_panel)
        self.exit_button.place(x=900, y=15)

        # Disable sidebar and patient page buttons when window opens
        if self.sidebar:
            self.sidebar.disable_buttons()
        if self.patient_page:
            self.patient_page.disable_detailed_buttons()

    def exit_panel(self):
        print("Medication closed")
        # Enable sidebar and patient page buttons when window closes
        if self.sidebar:
            self.sidebar.enable_buttons()
        if self.patient_page:
            self.patient_page.enable_detailed_buttons()
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
    def __init__(self, master=None, sidebar=None, patient_page=None, **kwargs):
        super().__init__(master, width=980, height=815, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)
        self.sidebar = sidebar 
        self.patient_page = patient_page  

        self.left_bar = ctk.CTkFrame(self, width=15,height=815, fg_color="#68EDC6", corner_radius=0,)
        self.left_bar.place(x=0)

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

        # Disable sidebar and patient page buttons when window opens
        if self.sidebar:
            self.sidebar.disable_buttons()
        if self.patient_page:
            self.patient_page.disable_detailed_buttons()

    def exit_panel(self):
        print("Contact and Relative Info closed")
        # Enable sidebar and patient page buttons when window closes
        if self.sidebar:
            self.sidebar.enable_buttons()
        if self.patient_page:
            self.patient_page.enable_detailed_buttons()
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


class FamilyHistory(ctk.CTkScrollableFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=500, height=250, fg_color="white", corner_radius=20,scrollbar_button_color="#BBBBBB",scrollbar_button_hover_color="#979797",**kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(self, width=15,height=250, fg_color="#68EDC6", corner_radius=0,)
        self.left_bar.place(x=0)

        self.title_label = ctk.CTkLabel(
            self, text="Family History", font=("Merriweather", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=10, padx=30)

        self.hypertension_label = ctk.CTkLabel(
            self, text="• Hypertension", font=("Merriweather", 14), text_color="black"
        )
        self.hypertension_label.grid(row=2, column=0, pady=1, padx=30, sticky="w" )

        self.diabetes_label = ctk.CTkLabel(
            self, text="• Diabetes Mellitus", font=("Merriweather", 14), text_color="black"
        )
        self.diabetes_label.grid(row=3, column=0, pady=1, padx=30, sticky="w")

        self.malignancy_label = ctk.CTkLabel(
            self, text="• Malignancy", font=("Merriweather", 14), text_color="black"
        )
        self.malignancy_label.grid(row=4, column=0, pady=1, padx=30, sticky="w")

        self.other_label = ctk.CTkLabel(
            self, text="• Other", font=("Merriweather", 14), text_color="black"
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

class MedicalHistory(ctk.CTkScrollableFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=500, height=250, fg_color="white", corner_radius=20 ,scrollbar_button_color="#BBBBBB",scrollbar_button_hover_color="#979797",**kwargs)
        self.pack_propagate(False) 

        self.left_bar = ctk.CTkFrame(self, width=15,height=250, fg_color="#68EDC6", corner_radius=20)
        self.left_bar.place(x=0)
    

        self.title_label = ctk.CTkLabel(
            self, text="Medical History", font=("Merriweather", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=10, padx=30, sticky="w")

        start_y = 1

        self.kidney_disease_label = ctk.CTkLabel(
            self, text="• Kidney Disease", font=("Merriweather", 14), text_color="black"
        )
        self.kidney_disease_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.urinary_stone_label = ctk.CTkLabel(
            self, text="• Urinary Stone", font=("Merriweather", 14), text_color="black"
        )
        self.urinary_stone_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.recurrent_uti_label = ctk.CTkLabel(
            self, text="• Recurrent UTI", font=("Merriweather", 14), text_color="black"
        )
        self.recurrent_uti_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.diabetes_type_label = ctk.CTkLabel(
            self, text="• Diabetes Type", font=("Merriweather", 14), text_color="black"
        )
        self.diabetes_type_label.grid(row=start_y, column=0, sticky="w", padx=30)
        start_y += 1

        self.other_medical_history_label = ctk.CTkLabel(
            self, text="• Other", font=("Merriweather", 14), text_color="black"
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

class OtherHistory(ctk.CTkScrollableFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1080, height=400, fg_color="#FFFFFF", corner_radius=20,
                        scrollbar_button_color="#BBBBBB", scrollbar_button_hover_color="#979797", **kwargs)
        self.pack_propagate(False)

        # Left bar - using place since it's relative to the frame border
        self.left_bar = ctk.CTkFrame(self, width=15, height=400, fg_color="#68EDC6", corner_radius=20)
        self.left_bar.place(x=0, y=0)

        # Configure grid weights for proper layout
        self.grid_columnconfigure(0, weight=1)
        
        current_row = 0
        
        # Title
        title_label = ctk.CTkLabel(self, text="Other History", font=("Merriweather", 20, "bold"))
        title_label.grid(row=current_row, column=0, pady=(20, 10), padx=(30, 10), sticky="w")
        current_row += 1

        # History of Present Illness
        hpi_label = ctk.CTkLabel(self, text="History of Present Illness", font=("Merriweather", 14))
        hpi_label.grid(row=current_row, column=0, pady=(10, 5), padx=(30, 10), sticky="w")
        current_row += 1
        
        self.hpi_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.hpi_info.grid(row=current_row, column=0, pady=(0, 15), padx=(50, 10), sticky="w")
        current_row += 1

        # Pertinent Past Medical History
        pmh_label = ctk.CTkLabel(self, text="Pertinent Past Medical History", font=("Merriweather", 14))
        pmh_label.grid(row=current_row, column=0, pady=(10, 5), padx=(30, 10), sticky="w")
        current_row += 1
        
        self.pmh_info = ctk.CTkLabel(self, text="", font=("Merriweather", 14), text_color="black")
        self.pmh_info.grid(row=current_row, column=0, pady=(0, 15), padx=(50, 10), sticky="w")
        current_row += 1

        # Create a frame for the four-column layout
        details_frame = ctk.CTkFrame(self, fg_color="transparent")
        details_frame.grid(row=current_row, column=0, pady=10, padx=(30, 10), sticky="ew")
        
        # Configure columns for the details frame
        for i in range(4):
            details_frame.grid_columnconfigure(i, weight=1)
        
        # Headers for the four columns
        headers = ["Date first diagnosed having kidney disease", "Date of First Dialysis", "Mode", "Access Type"]
        header_labels = []
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(details_frame, text=header, font=("Merriweather", 14))
            label.grid(row=0, column=i, pady=(0, 5), padx=10, sticky="w")
            header_labels.append(label)
        
        # Value labels for the four columns
        self.kidney_disease_date_info = ctk.CTkLabel(details_frame, text="", font=("Merriweather", 14), text_color="black")
        self.kidney_disease_date_info.grid(row=1, column=0, pady=(0, 15), padx=10, sticky="w")
        
        self.dialysis_date_info = ctk.CTkLabel(details_frame, text="", font=("Merriweather", 14), text_color="black")
        self.dialysis_date_info.grid(row=1, column=1, pady=(0, 15), padx=10, sticky="w")
        
        self.mode_info = ctk.CTkLabel(details_frame, text="", font=("Merriweather", 14), text_color="black")
        self.mode_info.grid(row=1, column=2, pady=(0, 15), padx=10, sticky="w")
        
        self.access_info = ctk.CTkLabel(details_frame, text="", font=("Merriweather", 14), text_color="black")
        self.access_info.grid(row=1, column=3, pady=(0, 15), padx=10, sticky="w")
        
        current_row += 1

        # Create frame for the bottom two fields
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=current_row, column=0, pady=10, padx=(30, 10), sticky="ew")
        
        # Configure columns for bottom frame
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        # Chronic Hemodialysis Date
        chd_label = ctk.CTkLabel(bottom_frame, text="Date of First Chronic Hemodialysis (*Leave NA if not)", 
                                font=("Merriweather", 14))
        chd_label.grid(row=0, column=0, pady=(0, 5), padx=10, sticky="w")
        
        self.chronic_hemo_date_info = ctk.CTkLabel(bottom_frame, text="", font=("Merriweather", 14), text_color="black")
        self.chronic_hemo_date_info.grid(row=1, column=0, pady=(0, 15), padx=10, sticky="w")

        # Clinical Impression
        clinical_label = ctk.CTkLabel(bottom_frame, text="Clinical Impression", font=("Merriweather", 14))
        clinical_label.grid(row=0, column=1, pady=(0, 5), padx=10, sticky="w")
        
        self.clinical_impression_info = ctk.CTkLabel(bottom_frame, text="", font=("Merriweather", 14), text_color="black")
        self.clinical_impression_info.grid(row=1, column=1, pady=(0, 15), padx=10, sticky="w")

    def other_history_info(self, patient_id):
        try:
            other_history = DataRetrieval.patient_other_history(patient_id)
            print("patient other history: ", other_history)
            if other_history:
                self.display_other_history(other_history)
            else:
                print("No Data - Patient record not found")  
        except Exception as e:
            print(f"Error in other_history_info: {e}")

    def display_other_history(self, data):
        """Display the other history data in the labels"""
        
        # Make sure we have data to display
        if not data:
            print("No other history data to display")
            return
        
        try:
            # Clear all labels first
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
            
            # Clear existing text
            for label in labels:
                label.configure(text="")
            
            # Now assign the data to each label
            # Assuming data is a list/tuple with values in this order:
            # [hpi, pmh, kidney_disease_date, dialysis_date, mode, access, chronic_hemo_date, clinical_impression]
            
            if len(data) >= 1 and data[0]:
                self.hpi_info.configure(text=str(data[0]))
            
            if len(data) >= 2 and data[1]:
                self.pmh_info.configure(text=str(data[1]))
            
            if len(data) >= 3 and data[2]:
                self.kidney_disease_date_info.configure(text=str(data[2]))
            
            if len(data) >= 4 and data[3]:
                self.dialysis_date_info.configure(text=str(data[3]))
            
            if len(data) >= 5 and data[4]:
                self.mode_info.configure(text=str(data[4]))
            
            if len(data) >= 6 and data[5]:
                self.access_info.configure(text=str(data[5]))
            
            if len(data) >= 7 and data[6]:
                self.chronic_hemo_date_info.configure(text=str(data[6]))
            
            if len(data) >= 8 and data[7]:
                self.clinical_impression_info.configure(text=str(data[7]))
            
            print("✅ Other history data displayed successfully")
            
        except Exception as e:
            print(f"❌ Error displaying other history data: {e}")
            print(f"Data received: {data}")

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

class SupplySearchResultsFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=400, height=400, fg_color="white", corner_radius=10, **kwargs)
        self.place_forget()  # Initially hidden
        self.visible = False
        self.parent = parent  # Reference to SupplyPage
        
        # Header Frame
        header_frame = ctk.CTkFrame(self, width=400, height=50, fg_color="#68EDC6", corner_radius=10)
        header_frame.place(x=0, y=0)
        
        header_title = ctk.CTkLabel(
            header_frame, 
            font=("Merriweather", 16, "bold"), 
            text="Supply Search Results", 
            text_color="white"
        )
        header_title.place(x=20, y=15)
        
        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            width=30,
            height=30,
            text="✕",
            fg_color="transparent",
            hover_color="#5AA3A3",
            font=("Arial", 16),
            command=self.hide
        )
        close_btn.place(x=350, y=10)
        
        # Scrollable Results Frame
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            width=380,
            height=330,
            fg_color="#f8f9fa",
            corner_radius=0
        )
        self.results_frame.place(x=10, y=60)
        
        # No results label (initially hidden)
        self.no_results_label = ctk.CTkLabel(
            self.results_frame,
            text="No results found",
            font=("Arial", 14),
            text_color="#666666"
        )
        
    def show_results(self, search_text, results):
        """Display search results in the frame"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not results:
            # Show no results message
            self.no_results_label = ctk.CTkLabel(
                self.results_frame,
                text=f"No supplies found for '{search_text}'",
                font=("Arial", 14),
                text_color="#666666"
            )
            self.no_results_label.pack(pady=50)
        else:
            # Display supplies section
            supplies_header = ctk.CTkLabel(
                self.results_frame,
                text=f"📦 SUPPLIES ({len(results)})",
                font=("Merriweather", 14, "bold"),
                text_color="#D2691E"
            )
            supplies_header.pack(anchor="w", padx=10, pady=(10, 5))
            
            for supply in results:
                self.create_supply_item(supply)
        
        # Show the frame
        self.show()
    
    def create_supply_item(self, supply):
        """Create a supply result item"""
        supply_frame = ctk.CTkFrame(
            self.results_frame,
            width=360,
            height=80,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E0E0E0"
        )
        supply_frame.pack(fill="x", padx=10, pady=3)
        supply_frame.pack_propagate(False)
        
        # Supply icon
        icon_frame = ctk.CTkFrame(
            supply_frame,
            width=50,
            height=50,
            fg_color="#FFF3E0",
            corner_radius=25
        )
        icon_frame.place(x=10, y=15)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text="📦",
            font=("Arial", 20)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Supply details
        name_label = ctk.CTkLabel(
            supply_frame,
            text=supply['item_name'],
            font=("Merriweather", 14, "bold"),
            text_color="black"
        )
        name_label.place(x=70, y=12)
        
        category_label = ctk.CTkLabel(
            supply_frame,
            text=f"Category: {supply['category']}",
            font=("Arial", 11),
            text_color="#666666"
        )
        category_label.place(x=70, y=32)
        
        stock_label = ctk.CTkLabel(
            supply_frame,
            text=f"Stock: {supply['current_stock']}",
            font=("Arial", 11),
            text_color="#666666"
        )
        stock_label.place(x=70, y=50)
        
        # View button
        view_btn = ctk.CTkButton(
            supply_frame,
            width=60,
            height=25,
            text="View",
            font=("Arial", 11),
            fg_color="#68EDC6",
            hover_color="#5AA3A3",
            corner_radius=5,
            command=lambda s=supply: self.view_supply(s)
        )
        view_btn.place(x=290, y=27)
    
    def view_supply(self, supply):
        """Handle viewing a supply - redirect to detailed view"""
        print(f"\n📦 VIEWING SUPPLY:")
        print(f"   ID: {supply['item_id']}")
        print(f"   Name: {supply['item_name']}")
        print(f"   Category: {supply['category']}")
        print(f"   Stock: {supply['current_stock']}")
        print("=" * 40)
        
        # Hide search results
        self.hide()
        
        # Set the selected supply in parent and show detailed view
        self.parent.selected_supply_id = supply['item_id']
        
        # Get full supply data and show detailed view
        try:
            connect = db()
            cursor = connect.cursor()
            cursor.execute("""
                SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                    COALESCE(
                        (SELECT MAX(rl.restock_date) 
                        FROM restock_logs rl 
                        WHERE rl.item_id = s.item_id), 
                        'No Restock'
                    ) as restock_date,
                    s.date_registered, s.restock_quantity, s.average_daily_usage, 
                    s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                    s.stock_level_status, s.max_supply
                FROM supply s 
                WHERE s.item_id = %s
            """, (supply['item_id'],))
            
            full_supply_data = cursor.fetchone()
            if full_supply_data:
                self.parent.show_detailed_info(full_supply_data)
            cursor.close()
            connect.close()
        except Exception as e:
            print("Error fetching supply details:", e)
    
    def show(self):
        """Show the search results frame"""
        self.place(x=480, y=130)  # Position below search bar
        self.lift()
        self.visible = True
    
    def hide(self):
        """Hide the search results frame"""
        self.place_forget()
        self.visible = False

class SupplyPage(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state

        # Initialize search results frame
        self.search_results_frame = SupplySearchResultsFrame(self)

        # RBAC
        self.role_manager = RoleAccessManager()

        self.navbar = ctk.CTkFrame(self, fg_color="white", height=130)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)
        self.navbar.configure(border_width=0, border_color="black")

        #self.dropdown_visible = False 

        #self.dropdown_frame = ctk.CTkFrame(self.navbar, fg_color="#f0f0f0", corner_radius=8, width=150, height=100)
        #self.dropdown_frame.configure(border_width=1, border_color="gray")
        #self.dropdown_frame.place_forget()

        self.notif_frame = NotificationFrame(self)
        self.settings_frame = SettingsFrame(self)

        # Load images
        notif_img = ctk.CTkImage(light_image=Image.open("assets/notif.png"), size=(42, 42))
        settings_img = ctk.CTkImage(light_image=Image.open("assets/settingsv2.png"), size=(42, 42))

        icon_y = 62

        # Notification button
        notif_btn = ctk.CTkButton(
            self.navbar, 
            image=notif_img, 
            text="", 
            width=40, 
            height=40, 
            fg_color="transparent", 
            hover_color="#f5f5f5",
            command=self.notif_frame.toggle
        )
        notif_btn.place(relx=1.0, x=-110, y=icon_y, anchor="center")

        # Settings button 
        settings_btn = ctk.CTkButton(
            self.navbar, 
            image=settings_img, 
            text="", 
            width=40, 
            height=40, 
            fg_color="transparent", 
            hover_color="#f5f5f5", 
            command=self.settings_frame.toggle  
        )
        settings_btn.place(relx=1.0, x=-160, y=icon_y, anchor="center")
        #ctk.CTkButton(self.dropdown_frame, text="Account Settings", width=140, command=self.open_settings).pack(pady=5)
        #ctk.CTkButton(self.dropdown_frame, text="Log Out", width=140, command=self.logout).pack(pady=5)

        self.bottom_line = ctk.CTkFrame(self.navbar, height=1.5, fg_color="black")
        self.bottom_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        
        output_font = ("Merriweather", 15)
        label_font = ("Merriweather Sans bold", 15)
        button_font = ("Merriweather Bold",15)
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
            font=button_font,
            text_color="#FFFFFF",
            fg_color="#1A374D",
            bg_color="#FFFFFF",
            command=self.open_add_window,
            width=180,  
            height=40,
            corner_radius=20    
        )
        self.add_button.pack(side="left", padx=10)

        # Sort dropdown
        self.sort_dropdown = ctk.CTkOptionMenu(
            self.button_frame,
            text_color="#FFFFFF",
            fg_color="#1A374D",
            button_color="#1A374D",
            bg_color="#FFFFFF",
            values=["Item ID", "Item Name", "Category", "Remaining Stock", "Restock Date", "Date Registered"],
            font=button_font,
            width=180,
            height=40,
            corner_radius=20,
            command=self.sort_by_option_simple
        )
        self.sort_dropdown.pack(side="left", padx=10)
        self.sort_dropdown.set("        Sort By")

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
        self.search_container.place(x=480, y=70, anchor="w")

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
            placeholder_text="Search supply",
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
        import datetime
        today_date = datetime.datetime.now().strftime("%B %d, %Y") 

        # date label beside the icon
        date_label = ctk.CTkLabel(
            self.calendar_container,
            text=today_date,
            font=("Arial", 20),
            text_color="#333333"
        )
        date_label.place(x=60, rely=0.5, anchor="w")

        # Edit Stock Button
        self.edit_stock_button = ctk.CTkButton(
            self.navbar,
            text="Edit Stock",
            font=button_font,
            width=180,
            height=40,
            fg_color="#1A374D",
            hover_color="#00C88D",
            text_color="white",
            corner_radius=20,
        )
        self.edit_stock_button.place(x=1100, y=70, anchor="w")

        # Setup admin-only access for the button
        self.role_manager.setup_admin_only_button(
            button=self.edit_stock_button,
            parent_widget=self,
            command_callback=self.edit_stock_clicked,
            tooltip_text="Only Admin can access Edit Stock function"
        )

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
            ("RESTOCK DATE", 150),        
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

        # Setup search functionality
        self.setup_search_functionality()

        # Rest of your existing UI code...
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
            fg_color="#1A374D",
            hover_color="#00C88D",
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
            width=1000,
            height=350, 
            fg_color="white",
            corner_radius=20
        )
        supply_info_frame.place(x=550, y=120) 

        Infooutput_font = ("Merriweather Sans Bold", 18)
        Infolabel_font = ("Merriweather ", 15)
        Infotitle_font = ("Merriweather Bold",25)

        left_bar = ctk.CTkFrame(
            supply_info_frame,
            width=20,
            height=350,  
            fg_color="#68EDC6",
            bg_color="white",
            corner_radius=20
        )
        left_bar.place(x=0, y=0)

        Supply_title_label = ctk.CTkLabel(supply_info_frame, text="Supply Info", font=Infotitle_font)
        Supply_title_label.place(x=50, y=20)

        # FIRST ROW - Supply Name, Category, Remaining Stock
        # Supply Name Label and Output
        self.Supply_Name_Label = ctk.CTkLabel(supply_info_frame, text="Supply Name", font=Infolabel_font)
        self.Supply_Name_Label.place(relx=.125,rely=.2)
        self.Supply_Name_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Supply_Name_Output.place(relx=.125,rely=.26)

        # Category Label and Output
        self.Category_Label = ctk.CTkLabel(supply_info_frame, text="Category", font=Infolabel_font)
        self.Category_Label.place(relx=.425,rely=.2)
        self.Category_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Category_Output.place(relx=.425,rely=.26)

        # Remaining Stock Label and Output
        self.currentstock_Label = ctk.CTkLabel(supply_info_frame, text="Remaining Stock", font=Infolabel_font)
        self.currentstock_Label.place(relx=.725,rely=.2)
        self.currentstock_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.currentstock_Output.place(relx=.725,rely=.26)

        # SECOND ROW - Date Registered, Average Weekly Usage, Delivery Time
        # Date Registered Label and Output
        self.Registered_Date_Label = ctk.CTkLabel(supply_info_frame, text="Date Registered", font=Infolabel_font)
        self.Registered_Date_Label.place(relx=.125,rely=.5)
        self.Registered_Date_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Registered_Date_Output.place(relx=.125,rely=.56)

        # Average Weekly Usage Label and Output
        self.Average_Weekly_Usage_Label = ctk.CTkLabel(supply_info_frame, text="Average Weekly Usage", font=Infolabel_font)
        self.Average_Weekly_Usage_Label.place(relx=.425,rely=.5)
        self.Average_Weekly_Usage_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Average_Weekly_Usage_Output.place(relx=.425,rely=.56)

        # Delivery Time Label and Output
        self.Delivery_Time_Label = ctk.CTkLabel(supply_info_frame, text="Delivery Time", font=Infolabel_font)
        self.Delivery_Time_Label.place(relx=.725,rely=.5)
        self.Delivery_Time_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Delivery_Time_Output.place(relx=.725,rely=.56)

        # THIRD ROW - Supplier Name, Previous Restock Expiry, Current Restock Expiry
        # Supplier Name Label and Output
        self.Supplier_Name_Label = ctk.CTkLabel(supply_info_frame, text="Supplier Name", font=Infolabel_font)
        self.Supplier_Name_Label.place(relx=.125,rely=.8)
        self.Supplier_Name_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Supplier_Name_Output.place(relx=.125,rely=.86)

        # Previous Restock Expiry Label and Output
        self.Previous_Restock_Expiry_Label = ctk.CTkLabel(supply_info_frame, text="Previous Restock Expiry", font=Infolabel_font)
        self.Previous_Restock_Expiry_Label.place(relx=.425,rely=.8)
        self.Previous_Restock_Expiry_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Previous_Restock_Expiry_Output.place(relx=.425,rely=.86)

        # Current Restock Expiry Label and Output
        self.Current_Restock_Expiry_Label = ctk.CTkLabel(supply_info_frame, text="Current Restock Expiry", font=Infolabel_font)
        self.Current_Restock_Expiry_Label.place(relx=.725,rely=.8)
        self.Current_Restock_Expiry_Output = ctk.CTkLabel(supply_info_frame, text="", font=Infooutput_font)
        self.Current_Restock_Expiry_Output.place(relx=.725,rely=.87)

        Progresstitle_font = ("Merriweather Bold",25)

        # Storage Meter Frame
        storage_meter_frame = ctk.CTkFrame(
            self.Main_Supply_Frame,
            width=1000,
            height=184,
            fg_color="white",
            corner_radius=20
        )
        storage_meter_frame.place(x=550, y=485)


        storageMeter_title_label = ctk.CTkLabel(storage_meter_frame, text="Inventory Quantity", font=Progresstitle_font)
        storageMeter_title_label.place(x=40, y=20)

        self.StorageMeter = ctk.CTkProgressBar(storage_meter_frame, width=720, height=40, fg_color="white", progress_color="green", border_width=1, border_color="black")
        self.StorageMeter.place(relx=.5,rely=.5,anchor="center")

        self.Status_Label = ctk.CTkLabel(storage_meter_frame, text="Status :", font=label_font)
        self.Status_Label.place(x=100,rely=.7)

        self.Status_Output = ctk.CTkLabel(storage_meter_frame, text="", font=label_font)
        self.Status_Output.place(x=180,rely=.7)

        self.Available_Items_Label = ctk.CTkLabel(storage_meter_frame, text="Available Items :", font=label_font)
        self.Available_Items_Label.place(x=650,rely=.7)

        self.Remaining_Output = ctk.CTkLabel(storage_meter_frame, text="", font=label_font)
        self.Remaining_Output.place(x=790,rely=.7)

        self.Seperator_Output = ctk.CTkLabel(storage_meter_frame, text="/", font=label_font)
        self.Seperator_Output.place(x=830,rely=.7)

        self.Capacity_Output = ctk.CTkLabel(storage_meter_frame, text="", font=label_font)
        self.Capacity_Output.place(x=850,rely=.7)

        # Edit Stock Frame
        self.Edit_Stock_Frame = ctk.CTkFrame(self.Main_Supply_Frame,
                width=400,
                height=200,
                fg_color="white",
                corner_radius=20)
        self.Edit_Stock_Frame.place(x=50, y=550)

        self.Top_bar = ctk.CTkFrame(self.Edit_Stock_Frame,
                width=400,
                height=20,
                fg_color="#68EDC6")
        self.Top_bar.place(y=0)

        # Edit Stock Button
        """self.Edit_Stock_Button = ctk.CTkButton(
            self.Edit_Stock_Frame,
            text="Edit Stock",
            width=150,
            height=50,
            fg_color="#1A374D",
            text_color="white",
            corner_radius=10,
            hover_color="#5DD4B3",
            command=self.open_edit_stock_window
        )
        self.Edit_Stock_Button.place(x=130, y=50)"""

        # def quantity_used_supply(item_id):
        #     try:
        #         connect = db()
        #         cursor = connect.cursor()

        #         cursor.execute("""
        #             SELECT pl.patient_id, pl.patient_name, pl.age, pl.gender, pl.access_type, iu.quantity_used, iu.usage_date, iu.usage_time, iu.usage_timestamp
        #             FROM patient_list pl JOIN item_usage iu ON pl.patient_id = iu.patient_id
        #             WHERE iu.item_id = %s
        #             ORDER BY iu.usage_timestamp DESC
        #         """, (item_id,))

        #         quantity_used_result = cursor.fetchall()
        #         for i in quantity_used_result:
        #             print(i)

        #     except Exception as e:
        #         print('Error retrieving quantiity used table for supply ', e)
        #     finally:
        #         cursor.close()
        #         connect.close()

        # quantity_used_supply(133)

        def quantity_used_patient(patient_id):
            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT iu.item_id, s.item_name, s.category, iu.quantity_used, iu.usage_date, iu.usage_time 
                    FROM item_usage iu JOIN supply s ON iu.item_id = s.item_id
                    WHERE iu.patient_id = %s
                    ORDER BY iu.usage_date DESC	
                """, (patient_id,))

                quantity_used_result = cursor.fetchall()
                for i in quantity_used_result:
                    print(i)

            except Exception as e:
                print('Error retrieving quantiity used table for patient ', e)
            finally:
                cursor.close()
                connect.close()
                
        print('SEPARATOR================================')
        quantity_used_patient(63)

        # Quantity Used Button
        self.Quantity_Used_Button = ctk.CTkButton(
            self.Edit_Stock_Frame,
            text="Quantity Used",
            width=150,
            height=50,
            font=button_font,
            fg_color="#1A374D", 
            text_color="white",
            corner_radius=10,
            hover_color="#5DD4B3",
            command=self.open_quantity_used_window  
        )
        self.Quantity_Used_Button.place(x=130, y=120)

        # Reminder Frame
        self.Reminder_Frame = ctk.CTkFrame(self.Main_Supply_Frame,
                width=400,
                height=230,
                fg_color="white",
                corner_radius=20)
        self.Reminder_Frame.place(x=50, y=780)

        # Reminder icon and label container
        self.reminder_header_frame = ctk.CTkFrame(self.Reminder_Frame,
                width=380,
                height=40,
                fg_color="transparent")
        self.reminder_header_frame.place(x=10, y=30)

        # Reminder icon
        try:
            reminder_img = ctk.CTkImage(light_image=Image.open("assets/reminderr.png"), size=(24, 24))
            reminder_icon = ctk.CTkLabel(self.reminder_header_frame, image=reminder_img, text="")
            reminder_icon.place(x=10, y=8)
        except:
            # Fallback if reminder icon not found
            reminder_icon = ctk.CTkLabel(
                self.reminder_header_frame, 
                text="⚠️", 
                font=("Arial", 20),
                text_color="#FF8C00"
            )
            reminder_icon.place(x=10, y=8)

        # Reminder Label
        self.reminder_title = ctk.CTkLabel(
            self.reminder_header_frame,
            text="Reminder",
            font=("Merriweather Bold", 16),
            text_color="#333333"
        )
        self.reminder_title.place(x=45, y=8)

        # Reminder text content
        self.reminder_text1 = ctk.CTkLabel(
            self.Reminder_Frame,
            text="Always check for the status level of any item as it may result to a stock out.",
            font=("Merriweather", 12),
            text_color="#666666",
            wraplength=360,
            justify="left"
        )
        self.reminder_text1.place(x=20, y=80)

        self.reminder_text2 = ctk.CTkLabel(
            self.Reminder_Frame,
            text="Please inform the admin when status is at Low Stock Level, the likeliness of a stock out increases when the status reaches Critical Stock Level.",
            font=("Merriweather", 12),
            text_color="#666666",
            wraplength=360,
            justify="left"
        )
        self.reminder_text2.place(x=20, y=125)

        # Restock Logs Frame
        self.Restock_Logs_Frame = ctk.CTkFrame(self.Main_Supply_Frame,
                width=1000,
                height=320,
                fg_color="white",
                corner_radius=20)
        self.Restock_Logs_Frame.place(x=550, y=690)

        # Top bar for restock logs frame
        self.Restock_Logs_Top_bar = ctk.CTkFrame(self.Restock_Logs_Frame,
                width=1000,
                height=20,
                fg_color="#68EDC6")
        self.Restock_Logs_Top_bar.place(y=0)

        # Restock Logs Title
        self.restock_logs_title = ctk.CTkLabel(
            self.Restock_Logs_Frame,
            text="Restock Logs -  ",
            font=("Merriweather Bold", 18),
            text_color="#333333"
        )
        self.restock_logs_title.place(x=20, y=35)

        # Item name label 
        self.restock_logs_item_name = ctk.CTkLabel(
            self.Restock_Logs_Frame,
            text="syringe",
            font=("Merriweather Bold", 18),
            text_color="#1A374D"
        )
        self.restock_logs_item_name.place(x=140, y=35)

        self.restock_reminder_container = ctk.CTkFrame(
            self.Restock_Logs_Frame,
            fg_color="transparent",
            width=280,
            height=50
        )
        self.restock_reminder_container.place(x=730, y=37)

        # Reminder text
        self.restock_reminder_text1 = ctk.CTkLabel(
            self.restock_reminder_container,
            text="If there are discrepancies \nplease contact the developers",
            font=("Merriweather", 10),
            text_color="#666666"
        )
        self.restock_reminder_text1.place(x=0, y=5)

        # Reminder icon
        try:
            restock_reminder_img = ctk.CTkImage(light_image=Image.open("assets/reminderrr.png"), size=(24, 24))
            self.restock_reminder_icon = ctk.CTkLabel(
                self.restock_reminder_container, 
                image=restock_reminder_img, 
                text=""
            )
            self.restock_reminder_icon.place(x=148, y=6) 
        except:
            # Fallback if reminder icon not found
            self.restock_reminder_icon = ctk.CTkLabel(
                self.restock_reminder_container, 
                text="⚠️", 
                font=("Arial", 18),
                text_color="#FF8C00"
            )
            self.restock_reminder_icon.place(x=250, y=12)

        
        # Information text
        self.restock_logs_info = ctk.CTkLabel(
            self.Restock_Logs_Frame,
            text="Information about restock logs will appear here",
            font=("Merriweather", 12),
            text_color="#666666"
        )
        self.restock_logs_info.place(x=20, y=70)

        # Table Frame for restock logs
        self.restock_table_frame = ctk.CTkFrame(self.Restock_Logs_Frame, fg_color="#1A374D", border_width=2, border_color="black")
        self.restock_table_frame.place(x=20, y=100, relwidth=0.925, relheight=0.725)

        restock_tree_container = ctk.CTkFrame(self.restock_table_frame, fg_color="black")
        restock_tree_container.pack(fill="both", expand=True, padx=1, pady=1)

        # Create the restock logs treeview
        restock_columns = ("restock_quantity", "restock_date")
        self.restock_tree = ttk.Treeview(restock_tree_container, columns=restock_columns, show="headings", height=8)
        self.restock_tree.pack(side="left", fill="both", expand=True)

        # Configure headers for restock table
        restock_headers = [
            ("RESTOCK QUANTITY", 220),
            ("RESTOCK DATE", 250),
        ]

        for (text, width), col in zip(restock_headers, restock_columns):
            self.restock_tree.heading(col, text=text)
            self.restock_tree.column(col, width=width, anchor="center")

        restock_scrollbar = ctk.CTkScrollbar(restock_tree_container, orientation="vertical", command=self.restock_tree.yview)
        self.restock_tree.configure(yscrollcommand=restock_scrollbar.set)
        restock_scrollbar.pack(side="right", fill="y")

        self.button_frame.place(x=20, y=50, anchor="nw")  
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8)

    def edit_stock_clicked(self):
        """Handle Edit Stock button click - now this will only be called if user is Admin"""
        print("✅ Edit Stock button clicked by Admin!")
        try:
            edit_window = EditStockWindow(self)
            edit_window.grab_set()  
        except Exception as e:
            print(f"❌ Error opening Edit Stock window: {e}")

    # SEARCH FUNCTIONALITY METHODS
    def setup_search_functionality(self):
        """Setup search functionality for the search entry"""
        # Bind the search entry to trigger search on key release
        self.search_entry.bind("<KeyRelease>", self.on_search_key_release)
        self.search_entry.bind("<Return>", self.perform_search)  # Enter key
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)  # Hide results when focus lost
        self.search_entry.bind("<Button-1>", self.on_search_click)  # Show results on click

    def on_search_click(self, event):
        """Handle click on search entry"""
        search_text = self.search_entry.get().strip()
        if len(search_text) >= 2:
            # If there's already text, perform search to show results
            self.perform_search(None)

    def on_search_key_release(self, event):
        """Handle key release events in search entry"""
        search_text = self.search_entry.get().strip()
        
        # Hide results if search is empty
        if len(search_text) == 0:
            self.search_results_frame.hide()
            return
            
        # Only search if there's text and it's more than 1 character
        if len(search_text) >= 2:
            # Add a small delay to avoid searching on every keystroke
            if hasattr(self, 'search_timer'):
                self.after_cancel(self.search_timer)
            self.search_timer = self.after(300, lambda: self.perform_search(None))
        elif len(search_text) == 1:
            # Hide results for single character
            self.search_results_frame.hide()

    def on_search_focus_out(self, event):
        """Handle when search entry loses focus"""
        # Add a small delay before hiding to allow clicking on results
        self.after(200, self.check_and_hide_results)
    
    def check_and_hide_results(self):
        """Check if we should hide the results frame"""
        # Get the widget that currently has focus
        focused_widget = self.focus_get()
        
        # If the focused widget is not part of the search results frame, hide it
        if (focused_widget != self.search_entry and 
            not self.is_widget_in_frame(focused_widget, self.search_results_frame)):
            self.search_results_frame.hide()
    
    def is_widget_in_frame(self, widget, frame):
        """Check if a widget is inside a specific frame"""
        if widget is None:
            return False
        
        parent = widget
        while parent:
            if parent == frame:
                return True
            parent = parent.master
        return False

    def perform_search(self, event):
        """Perform the actual search operation for supplies only"""
        search_text = self.search_entry.get().strip()
        
        if not search_text or len(search_text) < 2:
            self.search_results_frame.hide()
            return
        
        try:
            connect = db()
            cursor = connect.cursor()

            # Search only in supply table
            cursor.execute("""
                SELECT item_id, item_name, category, current_stock, 
                    COALESCE(
                        (SELECT MAX(rl.restock_date) 
                        FROM restock_logs rl 
                        WHERE rl.item_id = s.item_id), 
                        'No Restock'
                    ) as restock_date,
                    date_registered
                FROM supply s
                WHERE item_name LIKE %s OR category LIKE %s
                ORDER BY item_name
            """, (f'%{search_text}%', f'%{search_text}%'))

            search_results = cursor.fetchall()
            
            # Convert results to supply dictionaries
            supplies = []
            for result in search_results:
                supplies.append({
                    'item_id': result[0],
                    'item_name': result[1],
                    'category': result[2],
                    'current_stock': result[3],
                    'restock_date': result[4],
                    'date_registered': result[5]
                })
            
            # Show results in the search frame
            self.search_results_frame.show_results(search_text, supplies)
            
            # Keep the existing console output for debugging
            print(f"\n=== Supply Search Results for '{search_text}' ===")
            if supplies:
                for supply in supplies:
                    print(f'📦 SUPPLY: {supply["item_name"]} (Category: {supply["category"]}, Stock: {supply["current_stock"]})')
                print(f"\nSummary: Found {len(supplies)} supplies")
            else:
                print(f"No supplies found for '{search_text}'")

        except Exception as e:
            print(f'Error performing supply search: {e}')
            # Show error in search frame
            self.search_results_frame.show_results(search_text, [])
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()
    
    # EXISTING METHODS (unchanged)
    def perform_sort(self, sort_option):
        """Perform the actual sorting based on the selected option"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Map display names to database column names
            column_mapping = {
                "Item ID": "item_id",
                "Item Name": "item_name", 
                "Category": "category",
                "Remaining Stock": "current_stock",
                "Restock Date": "restock_date",
                "Date Registered": "date_registered"
            }
            
            db_column = column_mapping.get(sort_option, "item_id")
            
            # Special handling for restock_date since it's from a subquery
            if sort_option == "Restock Date":
                cursor.execute("""
                    SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                        COALESCE(
                            (SELECT MAX(rl.restock_date) 
                            FROM restock_logs rl 
                            WHERE rl.item_id = s.item_id), 
                            'No Restock'
                        ) as restock_date,
                        s.date_registered, s.restock_quantity, s.average_daily_usage, 
                        s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                        s.stock_level_status, s.max_supply
                    FROM supply s
                    ORDER BY 
                        CASE 
                            WHEN COALESCE(
                                (SELECT MAX(rl.restock_date) 
                                FROM restock_logs rl 
                                WHERE rl.item_id = s.item_id), 
                                'No Restock'
                            ) = 'No Restock' THEN 1 
                            ELSE 0 
                        END,
                        COALESCE(
                            (SELECT MAX(rl.restock_date) 
                            FROM restock_logs rl 
                            WHERE rl.item_id = s.item_id), 
                            '1900-01-01'
                        ) ASC
                """)
            elif sort_option == "Remaining Stock":
                # Sort numerically for stock quantities
                cursor.execute("""
                    SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                        COALESCE(
                            (SELECT MAX(rl.restock_date) 
                            FROM restock_logs rl 
                            WHERE rl.item_id = s.item_id), 
                            'No Restock'
                        ) as restock_date,
                        s.date_registered, s.restock_quantity, s.average_daily_usage, 
                        s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                        s.stock_level_status, s.max_supply
                    FROM supply s
                    ORDER BY s.current_stock ASC
                """)
            else:
                # Standard sorting for other columns
                cursor.execute(f"""
                    SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                        COALESCE(
                            (SELECT MAX(rl.restock_date) 
                            FROM restock_logs rl 
                            WHERE rl.item_id = s.item_id), 
                            'No Restock'
                        ) as restock_date,
                        s.date_registered, s.restock_quantity, s.average_daily_usage, 
                        s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                        s.stock_level_status, s.max_supply
                    FROM supply s
                    ORDER BY s.{db_column} ASC
                """)
            
            sorted_data = cursor.fetchall()
            
            # Update the table with sorted data
            self.populate_table(sorted_data)
            
            # Update the dropdown text to show current sort
            self.sort_dropdown.set(f"{sort_option}")
            
            print(f"Table sorted by: {sort_option}")
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            print(f'Error sorting by {sort_option}:', e)
            # Reset dropdown on error
            self.sort_dropdown.set("Sort By")

    def sort_by_option_simple(self, option):
        """Handle sorting for the simple dropdown"""
        print(f"Sorting by: {option}")
        
        if option == "Sort By":
            return
            
        self.perform_sort(option)

    # Navbar methods 
    """def toggle_dropdown(self):
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
        print("Logging out...")"""

    """def open_edit_stock_window(self):
        if hasattr(self, 'selected_supply_id') and self.selected_supply_id:
            edit_stock_window = EditStockWindow(self, self.selected_supply_id)
            edit_stock_window.grab_set()
            edit_stock_window.focus_force()
        else:
            print("Please select a supply item first.")"""

    def fetch_supply_data(self):
        """Fetch supply data from database including all fields"""
        try:
            connect = db()
            cursor = connect.cursor()
            cursor.execute("""
                SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                    COALESCE(
                        (SELECT MAX(rl.restock_date) 
                        FROM restock_logs rl 
                        WHERE rl.item_id = s.item_id), 
                        'No Restock'
                    ) as restock_date,
                    s.date_registered, s.restock_quantity, s.average_daily_usage, 
                    s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                    s.stock_level_status, s.max_supply, s.new_expiry_date, 
                    s.previous_expiry_date, s.supplier_name
                FROM supply s
            """)
            return cursor.fetchall()
        except Exception as e:
            print("Error fetching supply data:", e)
            return []

    def populate_table(self, data):
        """Populate the table with supply data including restock_date"""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for row in data:
            # Show: item_id, item_name, category, current_stock, restock_date, date_registered
            display_row = (row[0], row[1], row[2], row[3], row[4], row[5])
            self.tree.insert("", "end", values=display_row)

    def on_row_select(self, event):
        """Handle row selection with all fields"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            supply_data = self.tree.item(item, 'values')
            
            # Get full data from database using item_id
            try:
                connect = db()
                cursor = connect.cursor()
                cursor.execute("""
                    SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                        COALESCE(
                            (SELECT MAX(rl.restock_date) 
                            FROM restock_logs rl 
                            WHERE rl.item_id = s.item_id), 
                            'No Restock'
                        ) as restock_date,
                        s.date_registered, s.restock_quantity, s.average_daily_usage, 
                        s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                        s.stock_level_status, s.max_supply, s.new_expiry_date, 
                        s.previous_expiry_date, s.supplier_name
                    FROM supply s 
                    WHERE s.item_id = %s
                """, (supply_data[0],))
                
                full_data = cursor.fetchone()
                if full_data:
                    self.selected_supply_data = {
                        'item_id': full_data[0],
                        'item_name': full_data[1],
                        'category': full_data[2],
                        'current_stock': full_data[3],
                        'restock_date': full_data[4],         
                        'date_registered': full_data[5],      
                        'restock_quantity': full_data[6],       
                        'average_daily_usage': full_data[7] if full_data[7] else 0,
                        'average_weekly_usage': full_data[8] if full_data[8] else 0,
                        'average_monthly_usage': full_data[9] if full_data[9] else 0,
                        'delivery_time_days': full_data[10] if full_data[10] else 0,
                        'stock_level_status': full_data[11],
                        'max_supply': full_data[12] if full_data[12] else 0,
                        'new_expiry_date': full_data[13] if full_data[13] else None,
                        'previous_expiry_date': full_data[14] if full_data[14] else None,
                        'supplier_name': full_data[15] if full_data[15] else "N/A"
                    }
                cursor.close()
                connect.close()
            except Exception as e:
                print("Error fetching full supply data:", e)

    def open_quantity_used_window(self):
        if hasattr(self, 'selected_supply_id') and self.selected_supply_id:
            quantity_used_window = QuantityUsedLogsWindow(self, self.selected_supply_id)
            quantity_used_window.grab_set()
            quantity_used_window.focus_force()
        else:
            print("Please select a supply item first.")

        item_id = self.selected_supply_id
        
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute(f"""
                SELECT pl.patient_id, pl.patient_name, pl.age, pl.gender, pl.access_type, s.item_name, iu.quantity_used, iu.usage_date, iu.usage_time
                FROM item_usage iu
                JOIN patient_list pl ON iu.patient_id = pl.patient_id
                JOIN supply s ON iu.item_id = s.item_id
                WHERE s.item_id = %s
            """, (item_id,))

            data_result = cursor.fetchall()
            print(data_result)

        except Exception as e:
            print('Error retrieving the stock used data ', e)

        finally: 
            cursor.close()
            connect.close()

    def fetch_restock_logs(self, item_id):
        """Fetch restock logs for a specific item"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT restock_quantity, restock_date 
                FROM restock_logs
                WHERE item_id = %s
                ORDER BY restock_date DESC
            """, (item_id,))
            
            data_result = cursor.fetchall()
            cursor.close()
            connect.close()
            return data_result
            
        except Exception as e:
            print('Error retrieving the restock log data:', e)
            return []

    def populate_restock_logs(self, item_id, item_name):
        """Populate the restock logs table with data for the selected item"""
        # Update the item name in the restock logs title
        self.restock_logs_item_name.configure(text=item_name)
        
        # Clear existing data in restock logs table
        for row in self.restock_tree.get_children():
            self.restock_tree.delete(row)
        
        # Fetch and populate restock logs data
        restock_data = self.fetch_restock_logs(item_id)
        
        if restock_data:
            # Update info text
            self.restock_logs_info.configure(
                text=f"Showing {len(restock_data)} restock entries for {item_name}"
            )
            
            # Insert data into the restock logs table
            for row in restock_data:
                # Format the data: (restock_quantity, restock_date)
                self.restock_tree.insert("", "end", values=row)
        else:
            # No restock logs found
            self.restock_logs_info.configure(
                text=f"No restock logs found for {item_name}"
            )

    def on_row_click(self, event):
        """Handle row click to show detailed info with all fields"""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            supply_data = self.tree.item(item_id, 'values')
            supply_id = supply_data[0]
            print("Supply ID:", supply_id)
            
            self.selected_supply_id = supply_id
            
            try:
                connect = db()
                cursor = connect.cursor()
                cursor.execute("""
                    SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                        COALESCE(
                            (SELECT MAX(rl.restock_date) 
                            FROM restock_logs rl 
                            WHERE rl.item_id = s.item_id), 
                            'No Restock'
                        ) as restock_date,
                        s.date_registered, s.restock_quantity, s.average_daily_usage, 
                        s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                        s.stock_level_status, s.max_supply, s.new_expiry_date, 
                        s.previous_expiry_date, s.supplier_name
                    FROM supply s 
                    WHERE s.item_id = %s
                """, (supply_id,))
                full_supply_data = cursor.fetchone()
                if full_supply_data:
                    self.show_detailed_info(full_supply_data)
                cursor.close()
                connect.close()
            except Exception as e:
                print("Error fetching supply details:", e)

    def show_detailed_info(self, supply_data):
        self.table_frame.place_forget()
        self.button_frame.place_forget()
        self.navbar.pack_forget()
        
        # Update supply ID display
        self.supply_id_value.configure(text=supply_data[0])
        
        # Update supply info
        self.Supply_Name_Output.configure(text=supply_data[1])
        self.Category_Output.configure(text=supply_data[2])
        
        # Get data safely with updated indices
        current_stock = supply_data[3] if len(supply_data) > 3 else 0
        restock_date = supply_data[4] if len(supply_data) > 4 and supply_data[4] else "No Restock" 
        date_registered = supply_data[5] if len(supply_data) > 5 and supply_data[5] else "N/A"     
        average_weekly_usage = supply_data[8] if len(supply_data) > 8 and supply_data[8] else "N/A" 
        delivery_time_days = supply_data[10] if len(supply_data) > 10 and supply_data[10] else "N/A" 
        max_supply = supply_data[12] if len(supply_data) > 12 and supply_data[12] else 0
        
        # Handle expiry dates properly - check for NULL/None values
        current_restock_expiry = supply_data[13] if len(supply_data) > 13 and supply_data[13] is not None and supply_data[13] != '' else "N/A"
        previous_restock_expiry = supply_data[14] if len(supply_data) > 14 and supply_data[14] is not None and supply_data[14] != '' else "N/A"
        supplier_name = supply_data[15] if len(supply_data) > 15 and supply_data[15] else "N/A"
        
        # Debug print to see what we're getting
        print(f"DEBUG - Raw expiry data:")
        print(f"  current_restock_expiry (index 13): {supply_data[13] if len(supply_data) > 13 else 'Not found'}")
        print(f"  previous_restock_expiry (index 14): {supply_data[14] if len(supply_data) > 14 else 'Not found'}")
        print(f"  After processing:")
        print(f"  current_restock_expiry: {current_restock_expiry}")
        print(f"  previous_restock_expiry: {previous_restock_expiry}")
        
        # Display all the fields
        self.currentstock_Output.configure(text=str(current_stock))
        self.Registered_Date_Output.configure(text=date_registered)
        self.Average_Weekly_Usage_Output.configure(text=str(average_weekly_usage))
        self.Delivery_Time_Output.configure(text=str(delivery_time_days))

        self.Current_Restock_Expiry_Output.configure(text=str(current_restock_expiry))
        self.Previous_Restock_Expiry_Output.configure(text=str(previous_restock_expiry))
        self.Supplier_Name_Output.configure(text=str(supplier_name))
        
        # For the meter and status calculations using max_supply
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
                max_supply_val = current_stock_val  # If no max_supply, use current stock
                
        except (ValueError, TypeError) as e:
            print(f"DEBUG: Conversion error: {e}")
            print(f"DEBUG: current_stock value causing error: '{current_stock}'")
            print(f"DEBUG: max_supply value causing error: '{max_supply}'")
            current_stock_val = 0
            max_supply_val = 0

        supply_id = supply_data[0]

        # Ensure max_supply_val is not zero to avoid division by zero
        if max_supply_val == 0:
            max_supply_val = current_stock_val if current_stock_val > 0 else 1

        # Update the display - show current_stock/max_supply
        self.Remaining_Output.configure(text=str(current_stock_val))
        self.Capacity_Output.configure(text=str(max_supply_val))

        # Calculate progress based on max_supply
        progress_value = current_stock_val / max_supply_val if max_supply_val > 0 else 0
        # Ensure progress doesn't exceed 1.0 (100%)
        progress_value = min(progress_value, 1.0)
        self.StorageMeter.set(progress_value)

        # Handle average_weekly_usage for calculations
        if average_weekly_usage == "N/A" or average_weekly_usage is None or average_weekly_usage == 0:
            # Skip stock level calculations if no usage data
            status_text = "No Usage Data"
            status_color = "#666666"
            progress_color = "#666666"
            remaining_color = "#666666"
        else:
            # Daily usage for standard dev
            avg_daily_usage = average_weekly_usage / 7 
                
            # Standard 20% 
            daily_standard_dev_estimate = avg_daily_usage * 0.2
            
            # Handle delivery_time_days
            if delivery_time_days == "N/A" or delivery_time_days is None:
                delivery_time_days = 7  # Default to 7 days
            
            import math
            safety_stock = 2.33 * daily_standard_dev_estimate * math.sqrt(delivery_time_days)
            reorder_point = (avg_daily_usage * delivery_time_days) + safety_stock

            # Stock level
            low_stock_level = reorder_point
            critical_stock_level = 0.50 * reorder_point
            good_level = reorder_point * 1.7

            if current_stock == 0:
                status_text = "Out of Stock"
                status_color = "#8B0000"  
                progress_color = "#8B0000"
                remaining_color = "#8B0000"
            elif current_stock <= critical_stock_level:  
                status_text = "Critical Stock Level"
                status_color = "#FF0000"  
                progress_color = "#FF0000"
                remaining_color = "#FF0000"
            elif current_stock <= low_stock_level:  
                status_text = "Low Stock Level"
                status_color = "#FF8C00"  
                progress_color = "#FF8C00"
                remaining_color = "#FF8C00"
            elif current_stock <= good_level:  
                status_text = "Good Stock Level"
                status_color = "#28A745" 
                progress_color = "#28A745"
                remaining_color = "#28A745"
            else:  
                status_text = "Excellent Stock Level"
                status_color = "#27D810"  
                progress_color = "#27D810"
                remaining_color = "#27D810"

        # Apply the colors
        self.Status_Output.configure(text=status_text, text_color=status_color)
        self.Remaining_Output.configure(text_color=remaining_color)
        self.StorageMeter.configure(progress_color=progress_color)

        # Populate restock logs for the selected item
        item_id = supply_data[0]
        item_name = supply_data[1]
        self.populate_restock_logs(item_id, item_name)

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

    def open_edit_window(self):
        """Open edit window with current detailed supply data"""
        if not self.selected_supply_data:
            print("No Supply Data to edit")
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
            print(f"🔄 Refreshing detailed view for supply ID: {self.selected_supply_id}")
            
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT s.item_id, s.item_name, s.category, s.current_stock, 
                    COALESCE(
                        (SELECT MAX(rl.restock_date) 
                        FROM restock_logs rl 
                        WHERE rl.item_id = s.item_id), 
                        'No Restock'
                    ) as restock_date,
                    s.date_registered, s.restock_quantity, s.average_daily_usage, 
                    s.average_weekly_usage, s.average_monthly_usage, s.delivery_time_days, 
                    s.stock_level_status, s.max_supply, s.new_expiry_date, 
                    s.previous_expiry_date, s.supplier_name
                FROM supply s 
                WHERE s.item_id = %s
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
                    'max_supply': updated_data[12] if updated_data[12] else 0,
                    'new_expiry_date': updated_data[13] if updated_data[13] else None,
                    'previous_expiry_date': updated_data[14] if updated_data[14] else None,
                    'supplier_name': updated_data[15] if updated_data[15] else "N/A"
                }
                
                # Refresh the detailed info display
                self.show_detailed_info(updated_data)
                print("✅ Supply detailed view refreshed successfully!")
            else:
                print("❌ No data found for the selected supply item")
                
            cursor.close()
            connect.close()
            
        except Exception as e:
            print(f"❌ Error refreshing detailed view: {e}")

class ReportPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#EFEFEF")

        label_font = ("Merriweather Sans Bold", 9)
        Title_font = ("Merriweather Bold", 13)
        TypeReport_font = ("Merriweather Bold", 12)
        NumberOuput_font = ("Poppins Regular" ,19)
        DateOutput_font = ("Poppins Regular" ,15)
        SubLabel_font = ("Merriweather Sans Light" ,9)
        SubSubLabel_font = ("Poppins Regular" ,9)

        def data_count(column, value, table_name, period=None, date_column=None, join_table=None, join_condition=None):
            from datetime import datetime, timedelta
            import calendar
            try:
                connect = db()
                cursor = connect.cursor()
                
                if period and date_column:
                    today = datetime.now().date()

                    if period.lower() == 'today':
                        if join_table and join_condition:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM {table_name}
                                JOIN {join_table} ON {join_condition}
                                WHERE {table_name}.{column} = '{value}' 
                                AND DATE({join_table}.{date_column}) = '{today}'
                            """)
                        else:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM {table_name}
                                WHERE {column} = '{value}' 
                                AND DATE({date_column}) = '{today}'
                            """)
                    
                    elif period.lower() == 'weekly':
                        days_since_monday = today.weekday()
                        start_of_week = today - timedelta(days=days_since_monday)
                        end_of_week = start_of_week + timedelta(days=6)
                        
                        if join_table and join_condition:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM {table_name}
                                JOIN {join_table} ON {join_condition}
                                WHERE {table_name}.{column} = '{value}' 
                                AND {join_table}.{date_column} >= '{start_of_week}' 
                                AND {join_table}.{date_column} <= '{end_of_week}'
                            """)
                        else:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM {table_name}
                                WHERE {column} = '{value}' 
                                AND {date_column} >= '{start_of_week}' 
                                AND {date_column} <= '{end_of_week}'
                            """)
                        
                    elif period.lower() == 'monthly':
                        start_of_month = today.replace(day=1)
                        last_day = calendar.monthrange(today.year, today.month)[1]
                        end_of_month = today.replace(day=last_day)
                        
                        if join_table and join_condition:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM {table_name}
                                JOIN {join_table} ON {join_condition}
                                WHERE {table_name}.{column} = '{value}' 
                                AND {join_table}.{date_column} >= '{start_of_month}' 
                                AND {join_table}.{date_column} <= '{end_of_month}'
                            """)
                        else:
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM {table_name}
                                WHERE {column} = '{value}' 
                                AND {date_column} >= '{start_of_month}' 
                                AND {date_column} <= '{end_of_month}'
                            """)
                else:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name}
                        WHERE {column} = '{value}'
                    """)
                
                count_result = cursor.fetchone()
                count = count_result[0] if count_result else 0
            
                if period and date_column:
                    if period.lower() == 'today':
                        today = datetime.now()
                        formatted_today = today.strftime("%B %d, %Y")
                        date_range = f"{formatted_today}"
                    elif period.lower() == 'weekly':
                        date_range = f"{start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}"
                    elif period.lower() == 'monthly':
                        date_range = f"{start_of_month.strftime('%B %Y')}"
                    
                    return {
                        'count': count,
                        'date_range': date_range,
                        'period': period.lower()
                    }
                else:
                    return count
                
            except Exception as e:
                print(f'Error finding column ({column}), value ({value}) in table: {table_name}', e)
                return 0
            finally:
                cursor.close()
                connect.close()

        def data_count_no_join(column, value, table_name, period=None, date_column=None):
            from datetime import datetime, timedelta
            import calendar

            try:
                connect = db()
                cursor = connect.cursor()
                
                if period and date_column:
                    today = datetime.now().date()

                    if period.lower() == 'today':
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {column} = '{value}'  
                            AND {date_column} = '{today}'
                        """)
                    
                    elif period.lower() == 'weekly':
                        days_since_monday = today.weekday()
                        start_of_week = today - timedelta(days=days_since_monday)
                        end_of_week = start_of_week + timedelta(days=6)
                        
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {column} = '{value}' 
                            AND {date_column} >= '{start_of_week}' 
                            AND {date_column} <= '{end_of_week}'
                        """)
                        
                    elif period.lower() == 'monthly':
                        start_of_month = today.replace(day=1)
                        last_day = calendar.monthrange(today.year, today.month)[1]
                        end_of_month = today.replace(day=last_day)
                        
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {column} = '{value}' 
                            AND {date_column} >= '{start_of_month}' 
                            AND {date_column} <= '{end_of_month}'
                        """)
                        
                    else:
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {column} = '{value}'
                        """)
                
                count_result = cursor.fetchone()
                return count_result[0] if count_result else 0
                
            except Exception as e:
                print(f'Error finding column ({column}), value ({value}) in table: {table_name}', e)
                return 0
            finally:
                cursor.close()
                connect.close()

        def overall_data_count(table_name, period=None, date_column=None):
            from datetime import datetime, timedelta
            import calendar

            try:
                connect = db()
                cursor = connect.cursor()
                
                if period and date_column:
                    today = datetime.now().date()
                    
                    if period.lower() == 'today':
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {date_column} = '{today}' 
                        """)
                    
                    elif period.lower() == 'weekly':
                        days_since_monday = today.weekday()
                        start_of_week = today - timedelta(days=days_since_monday)
                        end_of_week = start_of_week + timedelta(days=6)
                        
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {date_column} >= '{start_of_week}' 
                            AND {date_column} <= '{end_of_week}'
                        """)
                        
                    elif period.lower() == 'monthly':
                        start_of_month = today.replace(day=1)
                        last_day = calendar.monthrange(today.year, today.month)[1]
                        end_of_month = today.replace(day=last_day)
                        
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {date_column} >= '{start_of_month}' 
                            AND {date_column} <= '{end_of_month}'
                        """)

                    else:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                
                count_result = cursor.fetchone()
                return count_result[0] if count_result else 0
                
            except Exception as e:
                print(f'Error finding data in table: {table_name}', e)
                return 0
            
            finally:
                cursor.close()
                connect.close()

        def date_desc_order(column, id, table_name, period=None, date_column=None):
            from datetime import datetime, timedelta
            import calendar

            try:
                connect = db()
                cursor = connect.cursor(dictionary=True)  
                
                query = f"SELECT {column} FROM {table_name}"
                
                if period and date_column:
                    today = datetime.now().date()

                    if period.lower() == 'today':
                        query += f" WHERE {date_column} = '{today}'"
                    
                    elif period.lower() == 'weekly':
                        days_since_monday = today.weekday()
                        start_of_week = today - timedelta(days=days_since_monday)
                        end_of_week = start_of_week + timedelta(days=6)
                        
                        query += f"""
                            WHERE {date_column} >= '{start_of_week}' 
                            AND {date_column} <= '{end_of_week}'
                        """
                        
                    elif period.lower() == 'monthly':
                        start_of_month = today.replace(day=1)
                        last_day = calendar.monthrange(today.year, today.month)[1]
                        end_of_month = today.replace(day=last_day)
                        
                        query += f"""
                            WHERE {date_column} >= '{start_of_month}' 
                            AND {date_column} <= '{end_of_month}'
                        """

                query += f" ORDER BY {date_column or column} DESC LIMIT 1"
                
                cursor.execute(query)
                result = cursor.fetchone()
                
                return result[column] if result else None
                
            except Exception as e:
                print(f'Error finding most recent date in table: {table_name}', e)
                return None
            
            finally:
                cursor.close()
                connect.close()

        def notif_count(value, table_name, period=None, date_column=None):
            from datetime import datetime, timedelta
            import calendar

            try:
                connect = db()
                cursor = connect.cursor()

                list_value = [f"notification_type = '{identifiers}'" for identifiers in value]
                actual_values = ' OR '.join(list_value)

                if period and date_column:
                    today = datetime.now()  
                    now_today = datetime.now().date() 

                    if period.lower() == 'today':
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE ({actual_values})
                            AND DATE({date_column}) = '{now_today}' 
                        """)
                    
                    elif period.lower() == 'weekly':
                        days_since_monday = today.weekday()
                        start_of_week = (today - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                        end_of_week = (start_of_week + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999)
                        
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE ({actual_values})
                            AND {date_column} >= '{start_of_week}' 
                            AND {date_column} <= '{end_of_week}'
                        """)
                        
                    elif period.lower() == 'monthly':
                        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        last_day = calendar.monthrange(today.year, today.month)[1]
                        end_of_month = today.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999)
                        
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE ({actual_values})
                            AND {date_column} >= '{start_of_month}' 
                            AND {date_column} <= '{end_of_month}'
                        """)
                        
                    else:
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE ({actual_values})
                        """)
                
                count_result = cursor.fetchone()    
                return count_result[0] if count_result else 0
                
            except Exception as e:
                print(f'Error finding values in table: {table_name}', e)
                return 0
            finally:
                cursor.close()
                connect.close()
        
        self.low_stock_canvas = None
        self.critical_stock_canvas = None

    #Patient Report
        PatientReport_frame = ctk.CTkFrame(self,
                                        width=245,
                                        height=335,
                                        corner_radius=20,
                                        fg_color="#FFFFFF",
                                        bg_color="transparent")
        PatientReport_frame.place(x=70,y=60)
        left_bar = ctk.CTkFrame(PatientReport_frame,width=20,height=335,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        PateintReport_title = ctk.CTkLabel(PatientReport_frame,font=Title_font,text="Patient Report")
        PateintReport_title.place(x=43,y=17)

        #Active
        Activepatient_BG = ctk.CTkFrame(PatientReport_frame,width=145,height=62.5,corner_radius=10,fg_color="#88BD8E",bg_color="transparent")
        Activepatient_BG.place(x=55,y=65)

         #Output for Active User - NOW DYNAMIC
        PatientIcon_image = ctk.CTkImage(Image.open("assets/PatientIcon.png"), size=(15,15))
        self.ActivePatientCount = ctk.CTkLabel(Activepatient_BG,font=NumberOuput_font,text='',text_color="#fFFFFF",fg_color="transparent",image=PatientIcon_image,compound='right')
        self.ActivePatientCount.place(relx=.5,rely=.45,anchor="center")
        PatientCount_SubLabel = ctk.CTkLabel(Activepatient_BG,font=SubLabel_font,text="Patient",text_color="#FfFFFF",fg_color="transparent",height=10)
        PatientCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        ActiveLabel_bg = ctk.CTkFrame(PatientReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB")
        ActiveLabel_bg.place(x=58,y=140)
        ActiveLabel = ctk.CTkLabel(ActiveLabel_bg,font=label_font,text="Active",text_color="#104E44",bg_color="transparent",height=10)
        ActiveLabel.place(relx=.5,rely=.5,anchor="center")

        #InActive
        Inactivepatient_BG = ctk.CTkFrame(PatientReport_frame,width=145,height=62.5,corner_radius=10,fg_color="#F25B5B",bg_color="transparent")
        Inactivepatient_BG.place(x=55,y=197)

        #Output for Inactive User - NOW DYNAMIC
        PatientIcon_image = ctk.CTkImage(Image.open("assets/PatientIcon.png"), size=(15,15))
        self.InactivePatientCount = ctk.CTkLabel(Inactivepatient_BG,font=NumberOuput_font,text='',text_color="#fFFFFF",fg_color="transparent",image=PatientIcon_image,compound='right')
        self.InactivePatientCount.place(relx=.5,rely=.45,anchor="center")
        PatientCount_SubLabel = ctk.CTkLabel(Inactivepatient_BG,font=SubLabel_font,text="Patient",text_color="#FfFFFF",fg_color="transparent",height=10)
        PatientCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        InactiveLabel_bg = ctk.CTkFrame(PatientReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB")
        InactiveLabel_bg.place(x=58,y=270)
        InactiveLabel = ctk.CTkLabel(InactiveLabel_bg,font=label_font,text="Inactive",text_color="#104E44",bg_color="transparent",height=10)
        InactiveLabel.place(relx=.5,rely=.4,anchor="center")

#------------------------------------------------------------------------------------------------------------------------------------------
    #Patient Table (Smaller - 2 columns only)
        self.patient_frame = ctk.CTkFrame(self,
                                           width=420,
                                           height=335,
                                           corner_radius=20,
                                           fg_color="#FFFFFF",
                                           bg_color="transparent")
        self.patient_frame.place(x=355,y=60)
        
        # Patient Table Header
        patient_header_frame = ctk.CTkFrame(self.patient_frame,
                                          width=400,
                                          height=40,
                                          corner_radius=10,
                                          fg_color="#88BD8E")
        patient_header_frame.place(x=10, y=10)
        
        # Header labels - Name and Status only
        patient_name_header = ctk.CTkLabel(patient_header_frame, text="Name", 
                                         font=("Merriweather Bold", 12), text_color="white")
        patient_name_header.place(x=30, y=10)
        
        patient_status_header = ctk.CTkLabel(patient_header_frame, text="Status", 
                                           font=("Merriweather Bold", 12), text_color="white")
        patient_status_header.place(x=280, y=10)
        
        # Scrollable frame for patient data
        self.patient_scrollable_frame = ctk.CTkScrollableFrame(self.patient_frame,
                                                             width=400,
                                                             height=270,
                                                             corner_radius=0,
                                                             fg_color="transparent")
        self.patient_scrollable_frame.place(x=10, y=55)
        
        # Load initial patient data
        self.load_patient_data()

#------------------------------------------------------------------------------------------------------------------------------------------
    #Supply Table 
        self.supply_frame = ctk.CTkFrame(self,
                                             width=740,
                                             height=335,
                                             corner_radius=20,
                                             fg_color="#FFFFFF",
                                             bg_color="transparent")
        self.supply_frame.place(x=815,y=60)
        
        # Supply Table Header
        supply_header_frame = ctk.CTkFrame(self.supply_frame,
                                         width=720,
                                         height=40,
                                         corner_radius=10,
                                         fg_color="#1A374D")
        supply_header_frame.place(x=10, y=10)
        
        # Header labels - Item, Reorder Qty, Status, Supplier
        supply_item_header = ctk.CTkLabel(supply_header_frame, text="Item", 
                                        font=("Merriweather Bold", 12), text_color="white")
        supply_item_header.place(x=30, y=10)
        
        supply_reorder_header = ctk.CTkLabel(supply_header_frame, text="Reorder Qty", 
                                           font=("Merriweather Bold", 12), text_color="white")
        supply_reorder_header.place(x=180, y=10)
        
        supply_status_header = ctk.CTkLabel(supply_header_frame, text="Status", 
                                          font=("Merriweather Bold", 12), text_color="white")
        supply_status_header.place(x=320, y=10)
        
        supply_supplier_header = ctk.CTkLabel(supply_header_frame, text="Supplier", 
                                            font=("Merriweather Bold", 12), text_color="white")
        supply_supplier_header.place(x=480, y=10)
        
        # Scrollable frame for supply data
        self.supply_scrollable_frame = ctk.CTkScrollableFrame(self.supply_frame,
                                                            width=720,
                                                            height=270,
                                                            corner_radius=0,
                                                            fg_color="transparent")
        self.supply_scrollable_frame.place(x=10, y=55)
        
        # Load initial supply data
        self.load_supply_data()

#------------------------------------------------------------------------------------------------------------------------------------------

    #Supply Report
        SupplyReport_frame = ctk.CTkFrame(self,
                                          width=730,
                                          height=165,
                                          corner_radius=20,
                                          fg_color="#FFFFFF",
                                          bg_color="transparent")
        SupplyReport_frame.place(x=70,y=435)
        left_bar = ctk.CTkFrame(SupplyReport_frame,width=20,height=165,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        SupplyReport_title = ctk.CTkLabel(SupplyReport_frame,font=Title_font,text="Supply Report")
        SupplyReport_title.place(x=43,y=17)

        SupplyCount_BG = ctk.CTkFrame(SupplyReport_frame,width=165,height=55,corner_radius=10,fg_color="#818C7D",bg_color="transparent")
        SupplyCount_BG.place(x=70,y=65)

        #Output Supply Count - NOW DYNAMIC
        SupplyCountIcon_image = ctk.CTkImage(Image.open("assets/SupplyCountIcon.png"), size=(15,15))
        self.SupplyCount = ctk.CTkLabel(SupplyCount_BG,font=NumberOuput_font,text='',text_color="#fFFFFF",fg_color="transparent",image=SupplyCountIcon_image,compound='right')
        self.SupplyCount.place(relx=.5,rely=.45,anchor="center")
        SupplyCount_SubLabel = ctk.CTkLabel(SupplyCount_BG,font=SubLabel_font,text="Items",text_color="#FfFFFF",fg_color="transparent",height=10)
        SupplyCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        SupplyCountLabel_bg = ctk.CTkFrame(SupplyReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        SupplyCountLabel_bg.place(x=79,y=125)
        SupplyCountLabel = ctk.CTkLabel(SupplyCountLabel_bg,font=label_font,text="Supply Count",text_color="#104E44",bg_color="transparent",height=10)
        SupplyCountLabel.place(relx=.5,rely=.4,anchor="center")

        Lowstock_BG = ctk.CTkFrame(SupplyReport_frame,width=165,height=55,corner_radius=10,fg_color="#D08B40",bg_color="transparent")
        Lowstock_BG.place(x=285,y=65)

        #Output Low Stock - NOW DYNAMIC
        LowStockIcon_image = ctk.CTkImage(Image.open("assets/LowStockIcon.png"), size=(15,15))
        self.LowStockCount = ctk.CTkLabel(Lowstock_BG,font=NumberOuput_font,text='',text_color="#fFFFFF",fg_color="transparent",image=LowStockIcon_image,compound='right')
        self.LowStockCount.place(relx=.5,rely=.45,anchor="center")
        LowStockCount_SubLabel = ctk.CTkLabel(Lowstock_BG,font=SubLabel_font,text="Items",text_color="#FfFFFF",fg_color="transparent",height=10)
        LowStockCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        LowStockLabel_bg = ctk.CTkFrame(SupplyReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        LowStockLabel_bg.place(x=295,y=125)
        LowStockLabel = ctk.CTkLabel(LowStockLabel_bg,font=label_font,text="Low Stock",text_color="#104E44",bg_color="transparent",height=10)
        LowStockLabel.place(relx=.5,rely=.4,anchor="center")

        CriticalStock_BG = ctk.CTkFrame(SupplyReport_frame,width=165,height=55,corner_radius=10,fg_color="#AC1616",bg_color="transparent")
        CriticalStock_BG.place(x=495,y=65)

        #Output Critical Stock - NOW DYNAMIC
        CriticalStockIcon_image = ctk.CTkImage(Image.open("assets/CriticalStockIcon.png"), size=(15,15))
        self.CriticalStockCount = ctk.CTkLabel(CriticalStock_BG,font=NumberOuput_font,text='',text_color="#fFFFFF",fg_color="transparent",image=CriticalStockIcon_image,compound='right')
        self.CriticalStockCount.place(relx=.5,rely=.45,anchor="center")
        CriticalStockCount_SubLabel = ctk.CTkLabel(CriticalStock_BG,font=SubLabel_font,text="Items",text_color="#FfFFFF",fg_color="transparent",height=10)
        CriticalStockCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        CriticalStockLabel_bg = ctk.CTkFrame(SupplyReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        CriticalStockLabel_bg.place(x=507,y=125)
        CriticalStockLabel = ctk.CTkLabel(CriticalStockLabel_bg,font=label_font,text="Critical Stock",text_color="#104E44",bg_color="transparent",height=10)
        CriticalStockLabel.place(relx=.5,rely=.4,anchor="center")

#------------------------------------------------------------------------------------------------------------------------------------------

    #Backup Report

        BackupReport_frame = ctk.CTkFrame(self,
                                        width=515,
                                        height=165,
                                        corner_radius=20,
                                        fg_color="#FFFFFF",
                                        bg_color="transparent")
        BackupReport_frame.place(x=830,y=435)
        left_bar = ctk.CTkFrame(BackupReport_frame,width=20,height=165,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        BackupReport_title = ctk.CTkLabel(BackupReport_frame,font=Title_font,text="Backup Report")
        BackupReport_title.place(x=43,y=17)

        BackupCount_BG = ctk.CTkFrame(BackupReport_frame,width=155,height=55,corner_radius=10,fg_color="#818C7D",bg_color="transparent")
        BackupCount_BG.place(x=70,y=65)

        #Output Backup Count
        BackupIcon_image = ctk.CTkImage(Image.open("assets/BackupIcon.png"), size=(15,15))
        self.BackupCount = ctk.CTkLabel(BackupCount_BG,font=NumberOuput_font,text="",text_color="#fFFFFF",fg_color="transparent",image=BackupIcon_image,compound='right')
        self.BackupCount.place(relx=.5,rely=.45,anchor="center")
        BackupCount_SubLabel = ctk.CTkLabel(BackupCount_BG,font=SubLabel_font,text="Backups",text_color="#FfFFFF",fg_color="transparent",height=10)
        BackupCount_SubLabel.place(relx=.5,rely=.7,anchor="center")
        
        BackupCountLabel_bg = ctk.CTkFrame(BackupReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        BackupCountLabel_bg.place(x=77,y=125)
        BackupCountLabel = ctk.CTkLabel(BackupCountLabel_bg,font=label_font,text="Backup Count",text_color="#104E44",bg_color="transparent",height=10)
        BackupCountLabel.place(relx=.5,rely=.4,anchor="center")

        MostRecentBackup_BG = ctk.CTkFrame(BackupReport_frame,width=195,height=55,corner_radius=10,fg_color="#90C587",bg_color="transparent")
        MostRecentBackup_BG.place(x=265,y=65)

        #Output Recent backup Date
        CalendarIcon_image = ctk.CTkImage(Image.open("assets/Calendaricon.png"), size=(18,18))
        self.RecentBackupDate = ctk.CTkLabel(MostRecentBackup_BG,font=DateOutput_font,text="",text_color="#FFFFFF",fg_color="transparent",image=CalendarIcon_image,compound='right')
        self.RecentBackupDate.place(relx=.5,rely=.45,anchor="center")
        RecentBackup_SubLabel = ctk.CTkLabel(MostRecentBackup_BG,font=SubLabel_font,text="yyyy - mm - dd",text_color="#FFFFFF",fg_color="transparent",height=10)
        RecentBackup_SubLabel.place(relx=.5,rely=.7,anchor="center")

        MostRecentlabel_bg = ctk.CTkFrame(BackupReport_frame,width=185,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        MostRecentlabel_bg.place(x=270,y=125)
        MostRecentLabel = ctk.CTkLabel(MostRecentlabel_bg,font=label_font,text="Most Recent Backup",text_color="#104E44",bg_color="transparent",height=0)
        MostRecentLabel.place(relx=.5,rely=.4,anchor="center")

#------------------------------------------------------------------------------------------------------------------------------------------

    #Interval
        Interval_frame = ctk.CTkFrame(self,
                                           width=175,
                                           height=165,
                                           corner_radius=20,
                                           fg_color="#FFFFFF",
                                           bg_color="transparent")
        Interval_frame.place(x=1380,y=435)
        
        topbar_frame = ctk.CTkFrame(Interval_frame,width=175,height=10,fg_color="#AC1616",corner_radius=20)
        topbar_frame.place(y=0)

        interval_title = ctk.CTkLabel(Interval_frame,text="Report Summary",text_color="#104E44",font=("Merriweather Bold",11))
        interval_title.place(relx=.125,rely=.125)

        msg_label = ctk.CTkLabel(Interval_frame,font=SubSubLabel_font,text="Choose a date range to view.",text_color="#104E44")
        msg_label.place(relx=.125,rely=.25)

    
        def on_interval_selected(choice):
            print(f"Selected Summary Date Report: {choice}")
            type_label.configure(text=choice)
            from datetime import datetime

            report_shared_states['current_period'] = choice

            supply_identifiers = ['Item Restocked', 'Item Stock Status Alert', 'New Item Added', 'Item Usage Recorded']
            patient_identifier =  ['Patient Status', 'New Patient Added']
            backup_identifier = ['Manual Backup', 'Scheduled Backup']
            
            # Initialize viewing_date for all cases
            viewing_date = "All Data"  # Default value for Overall
            
            # Update patient counts based on selected interval
            if choice == "Today":
                self.active_patient = data_count(
                    column='status', 
                    value='Active', 
                    table_name='patient_info',
                    period='today', 
                    date_column='date_registered',
                    join_table='patient_list',
                    join_condition='patient_info.patient_id = patient_list.patient_id'
                )

                viewing_date = self.active_patient['date_range']
                
                self.inactive_patient = data_count(
                    column='status', 
                    value='Inactive',
                    table_name='patient_info',
                    period='today', 
                    date_column='date_registered',
                    join_table='patient_list',
                    join_condition='patient_info.patient_id = patient_list.patient_id' 
                )

                self.supply_overall_count = overall_data_count(
                    table_name='supply', 
                    period='today', 
                    date_column='date_registered')

                self.lowstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Low Stock Level', 
                    table_name='supply', 
                    period='today', 
                    date_column='status_update')

                self.criticalstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Critical Stock Level', 
                    table_name='supply', 
                    period='today', 
                    date_column='status_update')
                
                self.backup_overall_count = overall_data_count(
                    table_name='backup_logs', 
                    period='today', 
                    date_column='last_date')
                
                self.most_recent_backup = date_desc_order(
                    column='last_date', 
                    id='backup_id', 
                    table_name='backup_logs', 
                    period='today', 
                    date_column='last_date')

                self.supplies_notif = notif_count(
                    value=supply_identifiers, 
                    table_name='notification_logs', 
                    period='today', 
                    date_column='notification_timestamp')
                
                self.patient_notif = notif_count(
                    value=patient_identifier, 
                    table_name='notification_logs', 
                    period='today', 
                    date_column='notification_timestamp')
                
                self.backup_notif = notif_count(
                    value=backup_identifier, 
                    table_name='notification_logs', 
                    period='today',  
                    date_column='notification_timestamp')
                
                self.low_stock_graph(period='today', date_column='status_update')
                self.critical_stock_graph(period='today', date_column='status_update')

            elif choice == "Weekly":
                self.active_patient = data_count(
                    column='status', 
                    value='Active', 
                    table_name='patient_info',
                    period='weekly', 
                    date_column='date_registered',
                    join_table='patient_list',
                    join_condition='patient_info.patient_id = patient_list.patient_id'  
                )

                viewing_date = self.active_patient['date_range']

                self.inactive_patient = data_count(
                    column='status', 
                    value='Inactive',
                    table_name='patient_info',
                    period='weekly', 
                    date_column='date_registered',
                    join_table='patient_list',
                    join_condition='patient_info.patient_id = patient_list.patient_id'  
                )

                self.supply_overall_count = overall_data_count(
                    table_name='supply', 
                    period='weekly', 
                    date_column='date_registered')

                self.lowstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Low Stock Level', 
                    table_name='supply', 
                    period='weekly', 
                    date_column='status_update')

                self.criticalstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Critical Stock Level', 
                    table_name='supply', 
                    period='weekly', 
                    date_column='status_update')
                
                self.backup_overall_count = overall_data_count(
                    table_name='backup_logs', 
                    period='weekly', 
                    date_column='last_date')
                
                self.most_recent_backup = date_desc_order(
                    column='last_date', 
                    id='backup_id', 
                    table_name='backup_logs', 
                    period='weekly', 
                    date_column='last_date')
                
                self.supplies_notif = notif_count(
                    value=supply_identifiers, 
                    table_name='notification_logs', 
                    period='weekly', 
                    date_column='notification_timestamp')
                
                self.patient_notif = notif_count(
                    value=patient_identifier, 
                    table_name='notification_logs', 
                    period='weekly', 
                    date_column='notification_timestamp')
                
                self.backup_notif = notif_count(
                    value=backup_identifier, 
                    table_name='notification_logs', 
                    period='weekly', 
                    date_column='notification_timestamp')

                self.low_stock_graph(period='weekly', date_column='status_update')
                self.critical_stock_graph(period='weekly', date_column='status_update')

            elif choice == "Monthly":
                # Monthly filtering
                self.active_patient = data_count(
                    column='status', 
                    value='Active', 
                    table_name='patient_info',
                    period='monthly', 
                    date_column='date_registered',
                    join_table='patient_list',
                    join_condition='patient_info.patient_id = patient_list.patient_id'  
                )

                viewing_date = self.active_patient['date_range']

                self.inactive_patient = data_count(
                    column='status', 
                    value='Inactive',  
                    table_name='patient_info',
                    period='monthly', 
                    date_column='date_registered',
                    join_table='patient_list',
                    join_condition='patient_info.patient_id = patient_list.patient_id'  
                )

                self.supply_overall_count = overall_data_count(
                    table_name='supply', 
                    period='monthly', 
                    date_column='date_registered')

                self.lowstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Low Stock Level', 
                    table_name='supply', 
                    period='monthly', 
                    date_column='status_update')

                self.criticalstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Critical Stock Level', 
                    table_name='supply', 
                    period='monthly', 
                    date_column='status_update')
                
                self.backup_overall_count = overall_data_count(
                    table_name='backup_logs', 
                    period='monthly', 
                    date_column='last_date')
                
                self.most_recent_backup = date_desc_order(
                    column='last_date', 
                    id='backup_id', 
                    table_name='backup_logs', 
                    period='monthly', 
                    date_column='last_date')
                
                self.supplies_notif = notif_count(
                    value=supply_identifiers, 
                    table_name='notification_logs', 
                    period='monthly', 
                    date_column='notification_timestamp')
                
                self.patient_notif = notif_count(
                    value=patient_identifier, 
                    table_name='notification_logs', 
                    period='monthly', 
                    date_column='notification_timestamp')
                
                self.backup_notif = notif_count(
                    value=backup_identifier, 
                    table_name='notification_logs', 
                    period='monthly', 
                    date_column='notification_timestamp')
                
                self.low_stock_graph(period='monthly', date_column='status_update')
                self.critical_stock_graph(period='monthly', date_column='status_update')

            elif choice == "Overall":
                # No period filtering - show all data
                self.active_patient = data_count(
                    column='status', 
                    value='Active', 
                    table_name='patient_info'
                )
                
                self.inactive_patient = data_count(
                    column='status', 
                    value='Inactive',  
                    table_name='patient_info'
                )

                self.supply_overall_count = overall_data_count(
                    table_name='supply', 
                    period='current', 
                    date_column='date_registered')

                self.lowstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Low Stock Level', 
                    table_name='supply', 
                    period='current', 
                    date_column='date_registered')

                self.criticalstock_count = data_count_no_join(
                    column='stock_level_status', 
                    value='Critical Stock Level', 
                    table_name='supply', 
                    period='current', 
                    date_column='date_registered')
                
                self.backup_overall_count = overall_data_count(
                    table_name='backup_logs', 
                    period='current', 
                    date_column='last_date')
                
                self.most_recent_backup = date_desc_order(
                    column='last_date', 
                    id='backup_id', 
                    table_name='backup_logs', 
                    period='current', 
                    date_column='last_date')

                self.supplies_notif = notif_count(
                    value=supply_identifiers, 
                    table_name='notification_logs', 
                    period='current', 
                    date_column='notification_timestamp')
                
                self.patient_notif = notif_count(
                    value=patient_identifier, 
                    table_name='notification_logs', 
                    period='current', 
                    date_column='notification_timestamp')
                
                self.backup_notif = notif_count(
                    value=backup_identifier, 
                    table_name='notification_logs', 
                    period='current', 
                    date_column='notification_timestamp')
                
                self.low_stock_graph(period='current', date_column='date_registered')
                self.critical_stock_graph(period='current', date_column='date_registered')
                
                # Set viewing_date for Overall
                viewing_date = "All Data"

            # Update the UI labels with new counts
            # Handle the case where data_count returns a dictionary (with period info)
            if isinstance(self.active_patient, dict):
                active_count = self.active_patient['count']
            else:
                active_count = self.active_patient
                
            if isinstance(self.inactive_patient, dict):
                inactive_count = self.inactive_patient['count']
            else:
                inactive_count = self.inactive_patient

            if isinstance(self.supply_overall_count, dict):
                supply_overall_count = self.supply_overall_count['count']
            else:
                supply_overall_count = self.supply_overall_count

            if isinstance(self.lowstock_count, dict):
                lowstock_count = self.lowstock_count['count']
            else:
                lowstock_count = self.lowstock_count
                
            if isinstance(self.criticalstock_count, dict):
                criticalstock_count = self.criticalstock_count['count']
            else:
                criticalstock_count = self.criticalstock_count

            if isinstance(self.backup_overall_count, dict):
                backup_overall_count = self.backup_overall_count['count']
            else:
                backup_overall_count = self.backup_overall_count
            
            most_recent_backup = self.most_recent_backup

            supplies_notif = self.supplies_notif
            patient_notif = self.patient_notif
            backup_notif = self.backup_notif

            # Update the labels on the UI
            self.ActivePatientCount.configure(text=str(active_count))
            self.InactivePatientCount.configure(text=str(inactive_count))

            self.SupplyCount.configure(text=str(supply_overall_count))
            self.LowStockCount.configure(text=str(lowstock_count))
            self.CriticalStockCount.configure(text=str(criticalstock_count))

            self.BackupCount.configure(text=str(backup_overall_count))
            self.RecentBackupDate.configure(text=str(most_recent_backup))

            self.StockLevelCount.configure(text=str(supplies_notif))
            self.PatientNotificationCount.configure(text=str(patient_notif))
            self.RecentNotificationCount.configure(text=str(backup_notif))

            self.view_label.configure(text=str(viewing_date))
            
            # Refresh tables with new data based on selection
            self.load_patient_data()
            self.load_supply_data()
            
            print(f"Updated counts - Active: {active_count}, Inactive: {inactive_count}")
            

        type_label = ctk.CTkLabel(Interval_frame,font=TypeReport_font,text="",text_color="#104E44",height=12)
        type_label.place(relx=.5,rely=.72,anchor="center")

        #Options
        Interval_Dropdown = ctk.CTkComboBox(Interval_frame,command=on_interval_selected,
                                            width=150,height=20,values=["Today","Weekly","Monthly", "Overall"],font=label_font,fg_color="#FFFFFF",corner_radius=10,bg_color="#FFFFFF",dropdown_fg_color="#FFFFFF",button_color="#88BD8E",button_hover_color="#1A374D",dropdown_font=label_font)
        Interval_Dropdown.place(relx=.5,rely=.55,anchor="center")

        # view_label = ctk.CTkLabel(Interval_frame,font=SubLabel_font,text="Viewing By",text_color="#104E44",height=10)
        # view_label.place(relx=.5,rely=.825,anchor="center")
        self.view_label = ctk.CTkLabel(Interval_frame,font=SubLabel_font,text="",text_color="#104E44",height=10)
        self.view_label.place(relx=.5,rely=.825,anchor="center")

    #Low Stock Level items
        self.LowOnStock_frame = ctk.CTkFrame(self,
                                        width=580,
                                        height=390,
                                        corner_radius=20,
                                        fg_color="#FFFFFF",
                                        bg_color="transparent")
        self.LowOnStock_frame.place(x=70,y=645)

        # Top bar for Low Stock Frame
        low_stock_top_bar = ctk.CTkFrame(
            self.LowOnStock_frame,
            width=630,
            height=20,
            fg_color="#D08B40",
            corner_radius=0
        )
        low_stock_top_bar.place(x=0, y=0)

        LowonStock_title = ctk.CTkLabel(self.LowOnStock_frame,font=Title_font,text="Low Stock Level Items")
        LowonStock_title.place(x=20,y=40)

        LowonStock_sublabel = ctk.CTkLabel(self.LowOnStock_frame,font=SubSubLabel_font,text="Current Data")
        LowonStock_sublabel.place(x=20,y=65)

    #Critical Stock Level Items
        self.CriticalStock_frame = ctk.CTkFrame(self,
                                           width=580,
                                           height=390,
                                           corner_radius=20,
                                           fg_color="#FFFFFF",
                                           bg_color="transparent")
        self.CriticalStock_frame.place(x=695,y=645)

        # Top bar for Critical Stock Frame
        critical_stock_top_bar = ctk.CTkFrame(
            self.CriticalStock_frame,
            width=630,
            height=20,
            fg_color="#AC1616",
            corner_radius=0
        )
        critical_stock_top_bar.place(x=0, y=0)

        CriticalStock_title = ctk.CTkLabel(self.CriticalStock_frame,font=Title_font,text="Critical Stock Level Items")
        CriticalStock_title.place(x=20,y=40)

        CriticalStock_sublabel = ctk.CTkLabel(self.CriticalStock_frame,font=SubSubLabel_font,text="Current Data")
        CriticalStock_sublabel.place(x=20,y=65)

#------------------------------------------------------------------------------------------------------------------------------------------

    #Notification Report
        NotificationReport_frame = ctk.CTkFrame(self,
                                                width=240,
                                                height=390,
                                                corner_radius=20,
                                                fg_color="#FFFFFF",
                                                bg_color="transparent")
        NotificationReport_frame.place(x=1325,y=645)
        left_bar = ctk.CTkFrame(NotificationReport_frame,width=20,height=390,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        NotificationReport_title = ctk.CTkLabel(NotificationReport_frame,font=Title_font,text="Notification Report")
        NotificationReport_title.place(x=43,y=17)

        Stocklevels_BG = ctk.CTkFrame(NotificationReport_frame,width=155,height=55,corner_radius=10,fg_color="#538A8C",bg_color="transparent")
        Stocklevels_BG.place(x=55,y=65)

         #Output for Stock Levels
        StockLevelIcon_image = ctk.CTkImage(Image.open("assets/LowStockIcon.png"), size=(15,15))
        self.StockLevelCount = ctk.CTkLabel(Stocklevels_BG,font=NumberOuput_font,text="",text_color="#fFFFFF",fg_color="transparent",image=StockLevelIcon_image,compound='right')
        self.StockLevelCount.place(relx=.5,rely=.45,anchor="center")
        StockCount_SubLabel = ctk.CTkLabel(Stocklevels_BG,font=SubLabel_font,text="Notifications",text_color="#FfFFFF",fg_color="transparent",height=10)
        StockCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        StocklevelsLabel_bg = ctk.CTkFrame(NotificationReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        StocklevelsLabel_bg.place(x=62,y=125)
        StockLevelsLabel = ctk.CTkLabel(StocklevelsLabel_bg,font=label_font,text="Supplies",text_color="#104E44",bg_color="transparent",height=11)
        StockLevelsLabel.place(relx=.5,rely=.4,anchor="center")


        PatientInformation_BG = ctk.CTkFrame(NotificationReport_frame,width=155,height=55,corner_radius=10,fg_color="#57CFBB",bg_color="transparent")
        PatientInformation_BG.place(x=55,y=175)

         #Output for Patient Information
        PatientNotificationIcon_image = ctk.CTkImage(Image.open("assets/PatientNotificationIcon.png"), size=(15,15))
        self.PatientNotificationCount = ctk.CTkLabel(PatientInformation_BG,font=NumberOuput_font,text="",text_color="#fFFFFF",bg_color="#57CFBB",image=PatientNotificationIcon_image,compound='right')
        self.PatientNotificationCount.place(relx=.5,rely=.45,anchor="center")
        PatientNotification_SubLabel = ctk.CTkLabel(PatientInformation_BG,font=SubLabel_font,text="Notifications",text_color="#FfFFFF",fg_color="transparent",height=10)
        PatientNotification_SubLabel.place(relx=.5,rely=.7,anchor="center")

        PatientInfolabel_bg = ctk.CTkFrame(NotificationReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        PatientInfolabel_bg.place(x=62,y=235)
        PatientInfoLabel = ctk.CTkLabel(PatientInfolabel_bg,font=label_font,text="Patient Information",text_color="#104E44",bg_color="transparent",height=11)
        PatientInfoLabel.place(relx=.5,rely=.4,anchor="center")

        RecentBackup_BG = ctk.CTkFrame(NotificationReport_frame,width=155,height=55,corner_radius=10,fg_color="#AB8C6F",bg_color="transparent")
        RecentBackup_BG.place(x=55,y=280)

         #Output for Backup
        BackupNotificationIcon_image = ctk.CTkImage(Image.open("assets/BackupNotificationIcon.png"), size=(15,15))
        self.RecentNotificationCount = ctk.CTkLabel(RecentBackup_BG,font=NumberOuput_font,text="",text_color="#fFFFFF",bg_color="#AB8C6F",image=BackupNotificationIcon_image,compound='right')
        self.RecentNotificationCount.place(relx=.5,rely=.45,anchor="center")
        BackupNotification_SubLabel = ctk.CTkLabel(RecentBackup_BG,font=SubLabel_font,text="Notifications",text_color="#FfFFFF",fg_color="transparent",height=10)
        BackupNotification_SubLabel.place(relx=.5,rely=.7,anchor="center")


        RecentBackuplabel_bg = ctk.CTkFrame(NotificationReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        RecentBackuplabel_bg.place(x=62,y=340)
        RecentBackuplabel = ctk.CTkLabel(RecentBackuplabel_bg,font=label_font,text="Back Up",text_color="#104E44",bg_color="transparent",height=11)
        RecentBackuplabel.place(relx=.5,rely=.4,anchor="center")

        # Set default value to "Overall" and trigger the selection
        Interval_Dropdown.set("Overall") 
        on_interval_selected("Overall") 

        # Load initial graphs

    def load_patient_data(self):
        """Load patient data from database with Name and Status columns"""
        try:    
            connect = db()
            cursor = connect.cursor()
            
            # Query to get all patients with patient name and status
            cursor.execute("""
                SELECT pl.patient_name, pi.status FROM patient_list pl
                JOIN patient_info pi ON pl.patient_id = pi.patient_id
                ORDER BY pi.status
            """)
            patients = cursor.fetchall()
            
            # Clear existing data
            for widget in self.patient_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Add patient rows
            for i, (name, status) in enumerate(patients):
                # Create row frame 
                row_frame = ctk.CTkFrame(self.patient_scrollable_frame,
                                    width=380, 
                                    height=35,
                                    corner_radius=5,
                                    fg_color="#F8F9FA" if i % 2 == 0 else "#FFFFFF")
                row_frame.pack(fill="x", pady=2, padx=5)
                row_frame.pack_propagate(False)
                
                # Patient Name 
                name_label = ctk.CTkLabel(row_frame, text=name,
                                        font=("Poppins Regular", 10),
                                        text_color="#333333",
                                        width=220,  
                                        anchor="w")
                name_label.place(x=15, y=7) 
                
                # Status with color coding 
                status_color = "#88BD8E" if status == "Active" else "#F25B5B"
                status_label = ctk.CTkLabel(row_frame, text=status,
                                        font=("Poppins Regular", 10),
                                        text_color=status_color,
                                        width=80)
                status_label.place(x=280, y=7) 
                
        except Exception as e:
            print(f'Error loading patient data: {e}')
            # Show error message
            error_label = ctk.CTkLabel(self.patient_scrollable_frame,
                                    text=f"Error loading data: {str(e)}",
                                    font=("Arial", 12),
                                    text_color="red")
            error_label.pack(pady=20)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def load_supply_data(self):
        """Load supply data from database showing items that need reordering"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Query to get supplies that are low stock or critical stock
            cursor.execute("""
                SELECT item_name, reorder_quantity, stock_level_status, supplier_name FROM supply
                WHERE stock_level_status = 'Critical Stock Level' OR stock_level_status = 'Low Stock Level'
                ORDER BY stock_level_status, supplier_name
            """)
            supplies = cursor.fetchall()
            
            # Clear existing data
            for widget in self.supply_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Add supply rows
            for i, (item_name, reorder_qty, status, supplier_name) in enumerate(supplies):
                # Create row frame
                row_frame = ctk.CTkFrame(self.supply_scrollable_frame,
                                       width=700,
                                       height=35,
                                       corner_radius=5,
                                       fg_color="#F8F9FA" if i % 2 == 0 else "#FFFFFF")
                row_frame.pack(fill="x", pady=2, padx=5)
                row_frame.pack_propagate(False)
                
                # Item Name
                item_label = ctk.CTkLabel(row_frame, text=item_name,
                                        font=("Poppins Regular", 10),
                                        text_color="#333333",
                                        width=140,
                                        anchor="w")
                item_label.place(x=15, y=7)
                
                # Reorder Quantity
                reorder_label = ctk.CTkLabel(row_frame, text=str(reorder_qty),
                                           font=("Poppins Regular", 10),
                                           text_color="#333333",
                                           width=70)
                reorder_label.place(x=170, y=7)
                
                # Status with color coding
                if status == "Critical Stock Level":
                    status_color = "#AC1616"
                elif status == "Low Stock Level":
                    status_color = "#D08B40"
                else:
                    status_color = "#88BD8E"
                    
                status_label = ctk.CTkLabel(row_frame, text=status,
                                          font=("Poppins Regular", 10),
                                          text_color=status_color,
                                          width=100)
                status_label.place(x=280, y=7)
                
                # Supplier - Handle blank/empty supplier names
                display_supplier = supplier_name if supplier_name and supplier_name.strip() else "None"
                supplier_label = ctk.CTkLabel(row_frame, text=display_supplier,
                                            font=("Poppins Regular", 10),
                                            text_color="#333333",
                                            width=160,
                                            anchor="w")
                supplier_label.place(x=480, y=7)
                
        except Exception as e:
            print(f'Error loading supply data: {e}')
            # Show error message
            error_label = ctk.CTkLabel(self.supply_scrollable_frame,
                                    text=f"Error loading data: {str(e)}",
                                    font=("Arial", 12),
                                    text_color="red")
            error_label.pack(pady=20)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()
                
    def refresh_data(self):
        """Refresh all data counts and update the labels"""

        # Refresh patient table
        self.load_patient_data()
        # Refresh supply table
        self.load_supply_data()
        print('Data refreshed successfully')

    def low_stock_graph(self, period=None, date_column=None):
        """Show low stock items chart in LowOnStock_frame with horizontal scrolling (using yesterday usage logic)"""
        from datetime import datetime, timedelta
        import calendar
        try:
            today = datetime.now().date()

            if period.lower() == 'today':
                date_filter = f"AND {date_column} = '{today}'"
            elif period.lower() == 'weekly':
                start = today - timedelta(days=today.weekday())
                end = start + timedelta(days=6)
                date_filter = f"AND {date_column} >= '{start}' AND {date_column} <= '{end}'"
            elif period.lower() == 'monthly':
                start = today.replace(day=1)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end = today.replace(day=last_day)
                date_filter = f"AND {date_column} >= '{start}' AND {date_column} <= '{end}'"
            else:
                date_filter = ""
            
            connect = db()
            query = f"""
                SELECT item_name, current_stock FROM supply
                WHERE stock_level_status = 'Low Stock Level'
                {date_filter}
                ORDER BY current_stock DESC
            """

            df = pd.read_sql(query, connect)
            df = df.sort_values(by='current_stock', ascending=True) 

            # Clean up existing canvas and scrollbar
            if self.low_stock_canvas:
                self.low_stock_canvas.get_tk_widget().destroy()
            if hasattr(self, 'low_stock_scrollbar') and self.low_stock_scrollbar:
                self.low_stock_scrollbar.destroy()
                self.low_stock_scrollbar = None

            # Calculate dynamic figure width based on number of items 
            num_items = len(df)
            if num_items > 0:
                # Base width calculation: minimum 5.5, then add width per item
                min_width = 5.5
                width_per_item = 0.8  # Same as yesterday usage
                calculated_width = max(min_width, num_items * width_per_item)
                fig_width = min(calculated_width, 20)  # Cap at maximum width
            else:
                fig_width = 5.5

            # Create new figure
            fig = Figure(figsize=(fig_width, 3.0), dpi=100)
            ax = fig.add_subplot(111)
            
            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            if not df.empty:
                # Create bar chart
                bars = ax.bar(df['item_name'], df['current_stock'], color='#D08B40')
                if num_items > 7:  # Only rotate if many items 
                    ax.tick_params(axis='x', pad=10, rotation=45)
                else:
                    ax.tick_params(axis='x', pad=10)
                ax.margins(y=0.15)
                
                # Set font for labels
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontproperties(tick_font)
                    label.set_fontsize(11)
                    
                # Add value labels on top of bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{int(height)}', ha='center', va='bottom', 
                        fontproperties=tick_font, fontsize=9)
                        
            else:
                # No low stock items
                ax.text(0.5, 0.5, 'No Low Stock Items', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14, color='gray',
                    weight='bold')

            # Remove spines for cleaner look
            for spine in ax.spines.values():
                spine.set_visible(False)
                
            fig.tight_layout()

            # Create canvas and embed in LowOnStock_frame
            self.low_stock_canvas = FigureCanvasTkAgg(fig, self.LowOnStock_frame)
            self.low_stock_canvas.draw()
            
            # Get canvas widget
            canvas_widget = self.low_stock_canvas.get_tk_widget()
            
            # Store the canvas position for scrolling 
            self.low_stock_canvas_x_position = 20
            self.low_stock_canvas_max_width = int(fig_width * 100)
            self.low_stock_canvas_container_width = 485  # Container width for low stock frame
            
            if fig_width > 5.5:  # Only add scrolling if content is wider than container
                # Place canvas with full width
                canvas_widget.place(x=self.low_stock_canvas_x_position, y=95, width=self.low_stock_canvas_max_width, height=280)
                
                # Create horizontal scrollbar
                self.low_stock_scrollbar = ctk.CTkScrollbar(
                    self.LowOnStock_frame,
                    orientation="horizontal",
                    width=465,
                    height=20,
                    command=self.on_low_stock_scroll
                )
                self.low_stock_scrollbar.place(x=30, y=360)
                
                # Initialize scrollbar
                visible_portion = min(1.0, self.low_stock_canvas_container_width / self.low_stock_canvas_max_width)
                self.low_stock_scrollbar.set(0, visible_portion)
                
            else:
                # No scrolling needed, place normally
                canvas_widget.place(x=20, y=95, width=485, height=280)
                self.low_stock_scrollbar = None

            print(f"✅ Low stock chart created with {num_items} items (width: {fig_width})")

        except Exception as e:
            print('Error retrieving low stock levels graph:', e)
            # Show error message in frame
            if hasattr(self, 'LowOnStock_frame'):
                error_label = ctk.CTkLabel(
                    self.LowOnStock_frame,
                    text=f"Error loading data: {str(e)}",
                    font=("Arial", 12),
                    text_color="red"
                )
                error_label.place(x=150, y=200)
        finally:
            if 'connect' in locals():
                connect.close()

    def on_low_stock_scroll(self, *args):
        """Handle horizontal scrollbar for low stock chart (EXACT COPY OF YESTERDAY USAGE LOGIC)"""
        if not hasattr(self, 'low_stock_canvas') or not self.low_stock_canvas:
            return
            
        canvas_widget = self.low_stock_canvas.get_tk_widget()
        
        if len(args) >= 2:
            command = args[0]
            value = args[1]
            
            if command == "moveto":
                # Scrollbar dragged to specific position
                scroll_position = float(value)
                # Calculate new x position based on scroll
                max_scroll = self.low_stock_canvas_max_width - self.low_stock_canvas_container_width
                new_x = 20 - (scroll_position * max_scroll)
                # Ensure canvas doesn't go beyond boundaries
                new_x = max(min(new_x, 20), -(max_scroll))
                
                canvas_widget.place(x=int(new_x), y=95, width=self.low_stock_canvas_max_width, height=280)
                
            elif command == "scroll":
                # Scrollbar arrow clicked
                current_x = canvas_widget.winfo_x()
                scroll_amount = int(value) * 50  # Scroll step size
                new_x = current_x - scroll_amount
                
                # Ensure canvas doesn't go beyond boundaries
                max_scroll = self.low_stock_canvas_max_width - self.low_stock_canvas_container_width
                new_x = max(min(new_x, 20), -(max_scroll))
                
                canvas_widget.place(x=int(new_x), y=95, width=self.low_stock_canvas_max_width, height=280)
                
                # Update scrollbar position
                scroll_position = (20 - new_x) / max_scroll
                visible_portion = self.low_stock_canvas_container_width / self.low_stock_canvas_max_width
                self.low_stock_scrollbar.set(scroll_position, scroll_position + visible_portion)

    def critical_stock_graph(self, period=None, date_column=None):
        """Show critical stock items chart in CriticalStock_frame with horizontal scrolling (using yesterday usage logic)"""
        from datetime import datetime, timedelta
        import calendar
        try:
            today = datetime.now().date()

            if period.lower() == 'today':
                date_filter = f"AND {date_column} = '{today}'"
            elif period.lower() == 'weekly':
                start = today - timedelta(days=today.weekday())
                end = start + timedelta(days=6)
                date_filter = f"AND {date_column} >= '{start}' AND {date_column} <= '{end}'"
            elif period.lower() == 'monthly':
                start = today.replace(day=1)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end = today.replace(day=last_day)
                date_filter = f"AND {date_column} >= '{start}' AND {date_column} <= '{end}'"
            else:
                date_filter = ""

            connect = db()
            query = f"""
                SELECT item_name, current_stock FROM supply
                WHERE stock_level_status = 'Critical Stock Level'
                {date_filter}
                ORDER BY current_stock DESC
            """

            df = pd.read_sql(query, connect)
            df = df.sort_values(by='current_stock', ascending=True)  # Sort like yesterday usage

            # Clean up existing canvas and scrollbar
            if self.critical_stock_canvas:
                self.critical_stock_canvas.get_tk_widget().destroy()
            if hasattr(self, 'critical_stock_scrollbar') and self.critical_stock_scrollbar:
                self.critical_stock_scrollbar.destroy()
                self.critical_stock_scrollbar = None

            # Calculate dynamic figure width based on number of items (SAME AS YESTERDAY USAGE)
            num_items = len(df)
            if num_items > 0:
                # Base width calculation: minimum 5.5, then add width per item
                min_width = 5.5
                width_per_item = 0.8  # Same as yesterday usage
                calculated_width = max(min_width, num_items * width_per_item)
                fig_width = min(calculated_width, 20)  # Cap at maximum width
            else:
                fig_width = 5.5

            # Create new figure
            fig = Figure(figsize=(fig_width, 3.0), dpi=100)
            ax = fig.add_subplot(111)

            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            if not df.empty:
                # Create bar chart with red color for critical items
                bars = ax.bar(df['item_name'], df['current_stock'], color='#AC1616')
                if num_items > 7:  # Only rotate if many items (SAME AS YESTERDAY USAGE)
                    ax.tick_params(axis='x', pad=10, rotation=45)
                else:
                    ax.tick_params(axis='x', pad=10)
                ax.margins(y=0.15)
                
                # Set font for labels
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontproperties(tick_font)
                    label.set_fontsize(11)
                    
                # Add value labels on top of bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{int(height)}', ha='center', va='bottom', 
                        fontproperties=tick_font, fontsize=9)
                        
            else:
                # No critical stock items
                ax.text(0.5, 0.5, 'No Critical Stock Items', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14, color='gray',
                    weight='bold')

            # Remove spines for cleaner look
            for spine in ax.spines.values():
                spine.set_visible(False)
                
            fig.tight_layout()

            # Create canvas and embed in CriticalStock_frame
            self.critical_stock_canvas = FigureCanvasTkAgg(fig, self.CriticalStock_frame)
            self.critical_stock_canvas.draw()
            
            # Get canvas widget
            canvas_widget = self.critical_stock_canvas.get_tk_widget()
            
            # Store the canvas position for scrolling (SAME AS YESTERDAY USAGE)
            self.critical_stock_canvas_x_position = 20
            self.critical_stock_canvas_max_width = int(fig_width * 100)
            self.critical_stock_canvas_container_width = 485  # Container width for critical stock frame
            
            if fig_width > 5.5:  # Only add scrolling if content is wider than container (SAME AS YESTERDAY USAGE)
                # Place canvas with full width
                canvas_widget.place(x=self.critical_stock_canvas_x_position, y=95, width=self.critical_stock_canvas_max_width, height=280)
                
                # Create horizontal scrollbar
                self.critical_stock_scrollbar = ctk.CTkScrollbar(
                    self.CriticalStock_frame,
                    orientation="horizontal",
                    width=465,
                    height=20,
                    command=self.on_critical_stock_scroll
                )
                self.critical_stock_scrollbar.place(x=30, y=360)
                
                # Initialize scrollbar (SAME AS YESTERDAY USAGE)
                visible_portion = min(1.0, self.critical_stock_canvas_container_width / self.critical_stock_canvas_max_width)
                self.critical_stock_scrollbar.set(0, visible_portion)
                
            else:
                # No scrolling needed, place normally
                canvas_widget.place(x=20, y=95, width=485, height=280)
                self.critical_stock_scrollbar = None

            print(f"✅ Critical stock chart created with {num_items} items (width: {fig_width})")

        except Exception as e:
            print('Error retrieving critical stock levels graph:', e)
            # Show error message in frame
            if hasattr(self, 'CriticalStock_frame'):
                error_label = ctk.CTkLabel(
                    self.CriticalStock_frame,
                    text=f"Error loading data: {str(e)}",
                    font=("Arial", 12),
                    text_color="red"
                )
                error_label.place(x=150, y=200)
        finally:
            if 'connect' in locals():
                connect.close()

    def on_critical_stock_scroll(self, *args):
        """Handle horizontal scrollbar for critical stock chart (EXACT COPY OF YESTERDAY USAGE LOGIC)"""
        if not hasattr(self, 'critical_stock_canvas') or not self.critical_stock_canvas:
            return
            
        canvas_widget = self.critical_stock_canvas.get_tk_widget()
        
        if len(args) >= 2:
            command = args[0]
            value = args[1]
            
            if command == "moveto":
                # Scrollbar dragged to specific position
                scroll_position = float(value)
                # Calculate new x position based on scroll
                max_scroll = self.critical_stock_canvas_max_width - self.critical_stock_canvas_container_width
                new_x = 20 - (scroll_position * max_scroll)
                # Ensure canvas doesn't go beyond boundaries
                new_x = max(min(new_x, 20), -(max_scroll))
                
                canvas_widget.place(x=int(new_x), y=95, width=self.critical_stock_canvas_max_width, height=280)
                
            elif command == "scroll":
                # Scrollbar arrow clicked
                current_x = canvas_widget.winfo_x()
                scroll_amount = int(value) * 50  # Scroll step size
                new_x = current_x - scroll_amount
                
                # Ensure canvas doesn't go beyond boundaries
                max_scroll = self.critical_stock_canvas_max_width - self.critical_stock_canvas_container_width
                new_x = max(min(new_x, 20), -(max_scroll))
                
                canvas_widget.place(x=int(new_x), y=95, width=self.critical_stock_canvas_max_width, height=280)
                
                # Update scrollbar position
                scroll_position = (20 - new_x) / max_scroll
                visible_portion = self.critical_stock_canvas_container_width / self.critical_stock_canvas_max_width
                self.critical_stock_scrollbar.set(scroll_position, scroll_position + visible_portion)

    def destroy(self):
        """Clean up when the widget is destroyed"""
        # Clean up matplotlib canvases  
        if self.low_stock_canvas:
            self.low_stock_canvas.get_tk_widget().destroy()
        if self.critical_stock_canvas:
            self.critical_stock_canvas.get_tk_widget().destroy()
        super().destroy()

class MaintenancePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#E8FBFC")

        # Initialize backup variables
        self.backup_timer = None
        self.backup_destination = None
        self.schedule_backup_frame = None

        # RBAC
        self.role_manager = RoleAccessManager()

        output_font = ("Merriweather Sans Bold", 15)
        label_font = ("Merriweather", 15)
        time_label_font = ("Merriweather Sans", 10)
        time_output_font = ("Merriweather Sans Bold", 10)
        button_font = ("Poppins",11)
        SubTitle_font = ("Merriweather Bold",14)
        sublabel_font=("Poppins",10)
        Sub_Sub_Title_font = ("Merriweather Bold",15)
        Title_font = ("Merriweather Bold",15)

        # Maintenance Frame
        Maintenance_MainFrame = ctk.CTkFrame(self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=1000,
                                            height=480,
                                            corner_radius=20)
        Maintenance_MainFrame.place(x=100,y=120)

        leftbar_frame = ctk.CTkFrame(Maintenance_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#1A374D",
                                     width=25,
                                     height=480,
                                     corner_radius=20)
        leftbar_frame.place(x=0)

        # Title
        Maintenace_label = ctk.CTkLabel(Maintenance_MainFrame, 
                                       bg_color="transparent",
                                       text="Maintenance",
                                       text_color="black",
                                       font=Title_font,
                                       height=15)
        Maintenace_label.place(x=80,y=30)
        
        maintenance_sublabel = ctk.CTkLabel(Maintenance_MainFrame, 
                                          bg_color="transparent",
                                          text="Maintenance Section is for Backup Scheduling",
                                          text_color="#104E44",
                                          font=sublabel_font,
                                          height=10)
        maintenance_sublabel.place(x=80,y=60)

        username = login_shared_states.get('logged_username', None)

        def choose_destination_folder():
            """Choose a destination folder for backup"""
            root = tk.Tk()
            root.withdraw() 
            
            folder_path = filedialog.askdirectory(
                title="Choose Backup Destination Folder"
            )
            root.destroy() 
            
            if folder_path:
                self.backup_destination = folder_path
                print(f"✅ Backup destination set to: {folder_path}")
                messagebox.showinfo("Destination Set", f"Backup destination set to:\n{folder_path}")
                return folder_path
            else:
                print("No folder selected.")
                return None

        # Choose Destination Button 
        ChooseDestination_Button = ctk.CTkButton(Maintenance_MainFrame,
                                                bg_color="transparent",
                                                fg_color="#3B71AC",
                                                hover_color="#5A6268",
                                                width=150,
                                                height=35,
                                                corner_radius=15,
                                                text="Choose Destination",
                                                text_color="white",
                                                cursor="hand2",
                                                command=choose_destination_folder,
                                                font=("Merriweather Sans", 10,"italic"))
        ChooseDestination_Button.place(x=820, y=30)

        # Stop Schedule Button
        stop_schedule_button = ctk.CTkButton(Maintenance_MainFrame,
                                           bg_color="transparent",
                                           fg_color="#DC3545",
                                           hover_color="#C82333",
                                           width=120,
                                           height=35,
                                           corner_radius=15,
                                           text="Stop Schedule",
                                           text_color="white",
                                           cursor="hand2",
                                           command=self.stop_scheduled_backup,
                                           font=("Merriweather Sans", 10))
        stop_schedule_button.place(x=650, y=30)

        # Option Frame
        option_frame = ctk.CTkFrame(Maintenance_MainFrame,
                                    bg_color="transparent",
                                    fg_color="#FFFFFF", 
                                    width=800, 
                                    height=180, 
                                    corner_radius=20,
                                    border_width=2,
                                    border_color="#BBBBBB")
        option_frame.place(x=100,y=100)

        backupoptions_label = ctk.CTkLabel(option_frame,
                                         text="Backup",
                                         text_color="black",
                                         bg_color="#FFFFFF",
                                         font=SubTitle_font)
        backupoptions_label.place(x=40,y=20)

        backupoptions_sublabel = ctk.CTkLabel(option_frame,
                                            text="Select Scheduling option.",
                                            text_color="black",
                                            bg_color="#FFFFFF",
                                            font=sublabel_font)
        backupoptions_sublabel.place(x=40,y=40)

        def find_mysqldump():
            """Find mysqldump executable in common locations"""
            common_paths = [
                "mysqldump",  # If it's in PATH
                r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
                r"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe",
                r"C:\xampp\mysql\bin\mysqldump.exe",
                r"C:\wamp64\bin\mysql\mysql8.0.21\bin\mysqldump.exe",
                r"C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin\mysqldump.exe"
            ]
            
            for path in common_paths:
                if shutil.which(path) or os.path.exists(path):
                    return path
            
            return None

        def perform_automatic_backup(filename_prefix="scheduled_backup"):
            """Perform automatic backup to chosen destination"""
            if not self.backup_destination:
                print("❌ No backup destination set!")
                return False
                
            try:
                # Generate filename with timestamp - USE datetime.datetime.now()
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{filename_prefix}_{timestamp}.sql"
                file_path = os.path.join(self.backup_destination, filename)
                
                # Find mysqldump
                mysqldump_path = find_mysqldump()
                if not mysqldump_path:
                    print("❌ mysqldump not found!")
                    return False
                
                print(f"🔄 Starting automatic backup to: {file_path}")
                
                # Run mysqldump
                with open(file_path, "w", encoding='utf-8') as backup_file:
                    result = subprocess.run([
                        mysqldump_path,
                        "-u", DB_USER,
                        f"-p{DB_PASSWORD}",
                        "--routines",
                        "--triggers",
                        DB_NAME
                    ], stdout=backup_file, stderr=subprocess.PIPE, text=True)
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "Unknown error occurred"
                    print(f"❌ Automatic backup failed: {error_msg}")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return False
                
                # Log backup to database
                now = datetime.datetime.now()  # USE datetime.datetime.now()
                connect = db() 
                cursor = connect.cursor()
                
                cursor.execute("""
                    SELECT employee_id, full_name FROM users WHERE username = %s
                """, (username,))
                
                result = cursor.fetchone()
                if result:
                    employee_id_u, full_name = result
                    
                    cursor.execute("""
                        INSERT INTO backup_logs (
                            employee_id, employee_name, backup_source, last_date, last_time
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, (
                        employee_id_u,
                        full_name,
                        f"Auto: {filename}",
                        now.date(),
                        now.time()
                    ))
                    
                    connect.commit()
                    
                    # Update display
                    self.update_last_backup_time()
                    self.load_backup_logs_table()
                    self.load_employee_backup_table()
                
                cursor.close()
                connect.close()
                
                file_size = os.path.getsize(file_path) / (1024 * 1024)  
                print(f"✅ Automatic backup successful!")
                print(f"   File: {filename}")
                print(f"   Location: {self.backup_destination}")
                print(f"   Size: {file_size:.2f} MB")
                print(f"   Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True
                
            except Exception as e:
                print(f"❌ Automatic backup error: {str(e)}")
                return False

        def start_scheduled_backup(interval_seconds, filename_prefix):
            """Start the scheduled backup with given interval"""
            print(f"🕒 Next backup in {interval_seconds} seconds...")

            now = datetime.datetime.now()
            right_now = now.strftime('%Y-%m-%d %H:%M:%S')

            connect = db() 
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT full_name FROM users WHERE username = %s
            """, (username,))

            full_name = cursor.fetchone()[0]


            def backup_loop():
                success = perform_automatic_backup(filename_prefix)
                if success:
                    cursor.execute("""  
                        INSERT INTO notification_logs (user_fullname, notification_type, notification_timestamp)
                        VALUES (%s, %s, %s)
                    """, (full_name, 'Scheduled Backup', right_now))
                    
                    connect.commit()

                    print(f"""
                        Scheduled Backup

                        Backup was made by {full_name}.
                        
                        {right_now}
                    """)
                else:
                    print(f"❌ Scheduled backup failed!")
                
                # Schedule next backup
                self.backup_timer = self.after(interval_seconds * 1000, backup_loop)
                
                # Update next backup time
                next_backup = datetime.datetime.now() + timedelta(seconds=interval_seconds)  # USE datetime.datetime.now()
                self.update_next_backup_time(next_backup)
                print(f"🕒 Next backup scheduled for: {next_backup.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Start the backup loop
            self.backup_timer = self.after(interval_seconds * 1000, backup_loop)
            
            # Update next backup time
            next_backup = datetime.datetime.now() + timedelta(seconds=interval_seconds)  # USE datetime.datetime.now()
            self.update_next_backup_time(next_backup)

        def manual_backup_action(username):
            """Enhanced manual backup with custom filename"""
            try:
                if not self.backup_destination:
                    messagebox.showwarning("No Destination", "Please choose a backup destination folder first.")
                    return
                
                # Create input dialog for filename
                filename_dialog = CTkInputDialog(
                    text="Enter backup filename (without extension):",
                    title="Backup Filename"
                )
                filename = filename_dialog.get_input()
                
                if not filename:
                    messagebox.showwarning("Backup Cancelled", "No filename provided. Backup cancelled.")
                    return
                
                # Add timestamp to filename
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')  # USE datetime.datetime.now()
                default_filename = f"{filename}_{timestamp}.sql"
                file_path = os.path.join(self.backup_destination, default_filename)
                
                # Find mysqldump
                mysqldump_path = find_mysqldump()
                if not mysqldump_path:
                    messagebox.showerror(
                        "MySQL Error", 
                        "mysqldump not found!\n\n"
                        "Please ensure MySQL is installed and add its bin folder to your system PATH."
                    )
                    return
                
                # Show progress message
                progress_window = tk.Toplevel()
                progress_window.title("Backup in Progress")
                progress_window.geometry("300x100")
                progress_window.resizable(False, False)
                progress_window.transient(self)
                progress_window.grab_set()
                
                progress_label = tk.Label(progress_window, text="Creating backup...\nPlease wait...")
                progress_label.pack(expand=True)
                progress_window.update()
                
                # Run mysqldump
                with open(file_path, "w", encoding='utf-8') as backup_file:
                    result = subprocess.run([
                        mysqldump_path,
                        "-u", DB_USER,
                        f"-p{DB_PASSWORD}",
                        "--routines",
                        "--triggers",
                        DB_NAME
                    ], stdout=backup_file, stderr=subprocess.PIPE, text=True)
                
                progress_window.destroy()
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "Unknown error occurred"
                    messagebox.showerror("Backup Failed", f"Database backup failed!\n\nError: {error_msg}")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return
                
                # Log backup to database
                now = datetime.datetime.now()  # USE datetime.datetime.now()
                connect = db() 
                cursor = connect.cursor()
                
                cursor.execute("""
                    SELECT employee_id, full_name FROM users WHERE username = %s
                """, (username,))

                right_now = now.strftime('%Y-%m-%d %H:%M:%S')

                result = cursor.fetchone()
                if result:
                    employee_id_u, full_name = result
                    
                    cursor.execute("""
                        INSERT INTO backup_logs (
                            employee_id, employee_name, backup_source, last_date, last_time
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, (
                        employee_id_u,
                        full_name,
                        file_path,
                        now.date(),
                        now.time()
                    ))

                    cursor.execute("""  
                        INSERT INTO notification_logs (user_fullname, notification_type, notification_timestamp)
                        VALUES (%s, %s, %s)
                    """, (full_name, 'Manual Backup', right_now))
                    
                    connect.commit()

                    print(f"""
                        Manual Backup

                        Backup was made by {full_name}.
                        
                        {right_now}
                    """)
                    
                    # Update display
                    self.update_last_backup_time()
                    self.load_backup_logs_table()
                    self.load_employee_backup_table()
                
                cursor.close()
                connect.close()
                
                # Show success message
                file_size = os.path.getsize(file_path) / (1024 * 1024)  
                messagebox.showinfo(
                    "Backup Successful", 
                    f"Database backup completed successfully!\n\n"
                    f"File: {default_filename}\n"
                    f"Location: {self.backup_destination}\n"
                    f"Size: {file_size:.2f} MB\n"
                    f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
            except Exception as e:
                messagebox.showerror("Backup Error", f"An unexpected error occurred:\n\n{str(e)}")

        def on_manual_backup_click():
            username = login_shared_states.get('logged_username', None)
            if username:
                manual_backup_action(username)
            else:
                messagebox.showerror("Error", "No user logged in!")

        def schedule_backup_action():
            """Create Schedule Backup Frame with time input"""
            if self.schedule_backup_frame:
                self.schedule_backup_frame.destroy()
                
            self.schedule_backup_frame = ctk.CTkFrame(self,
                                               bg_color="transparent",
                                               fg_color="#FFFFFF",
                                               width=1000,
                                               height=450,
                                               corner_radius=20)
            self.schedule_backup_frame.place(x=100, y=180)
            
            # Left bar for Schedule Frame
            leftbar_frame = ctk.CTkFrame(self.schedule_backup_frame,
                                       bg_color="transparent",
                                       fg_color="#1A374D",
                                       width=25,
                                       height=450,
                                       corner_radius=20)
            leftbar_frame.place(x=0)
            
            # Title
            title_label = ctk.CTkLabel(self.schedule_backup_frame,
                                     bg_color="transparent",
                                     text="Schedule Backup",
                                     text_color="black",
                                     font=Title_font)
            title_label.place(x=100, y=50)
            
            # Subtitle
            subtitle_label = ctk.CTkLabel(self.schedule_backup_frame,
                                        bg_color="transparent",
                                        text="Set the time interval for automatic backup scheduling.",
                                        text_color="black",
                                        font=sublabel_font)
            subtitle_label.place(x=100, y=80)
            
            # Destination status
            dest_status = "✅ Set" if self.backup_destination else "❌ Not Set"
            dest_label = ctk.CTkLabel(self.schedule_backup_frame,
                                    bg_color="transparent",
                                    text=f"Backup Destination: {dest_status}",
                                    text_color="#28A745" if self.backup_destination else "#DC3545",
                                    font=("Merriweather", 12, "bold"))
            dest_label.place(x=100, y=110)
            
            # Time Section
            time_label = ctk.CTkLabel(self.schedule_backup_frame,
                                    bg_color="transparent",
                                    text="Time Interval (HH:MM:SS)",
                                    text_color="black",
                                    font=("Merriweather Sans bold", 18))
            time_label.place(x=100, y=150)
            
            # Time input frame
            time_frame = ctk.CTkFrame(self.schedule_backup_frame, fg_color="transparent")
            time_frame.place(x=100, y=200)
            
            # Hour Entry
            hour_label = ctk.CTkLabel(time_frame, text="Hours", font=("Merriweather", 14))
            hour_label.grid(row=0, column=0, padx=10, pady=5)
            self.entry_hour = ctk.CTkEntry(time_frame,
                                         width=80,
                                         height=40,
                                         placeholder_text="00",
                                         font=("Merriweather light", 16),
                                         justify="center")
            self.entry_hour.grid(row=1, column=0, padx=10, pady=5)
            
            # Colon separator 1
            colon1_label = ctk.CTkLabel(time_frame, text=":", font=("Merriweather Bold", 24))
            colon1_label.grid(row=1, column=1, padx=5)
            
            # Minute Entry
            minute_label = ctk.CTkLabel(time_frame, text="Minutes", font=("Merriweather", 14))
            minute_label.grid(row=0, column=2, padx=10, pady=5)
            self.entry_minute = ctk.CTkEntry(time_frame,
                                           width=80,
                                           height=40,
                                           placeholder_text="00",
                                           font=("Merriweather light", 16),
                                           justify="center")
            self.entry_minute.grid(row=1, column=2, padx=10, pady=5)
            
            # Colon separator 2
            colon2_label = ctk.CTkLabel(time_frame, text=":", font=("Merriweather Bold", 24))
            colon2_label.grid(row=1, column=3, padx=5)
            
            # Second Entry
            second_label = ctk.CTkLabel(time_frame, text="Seconds", font=("Merriweather", 14))
            second_label.grid(row=0, column=4, padx=10, pady=5)
            self.entry_second = ctk.CTkEntry(time_frame,
                                           width=80,
                                           height=40,
                                           placeholder_text="00",
                                           font=("Merriweather light", 16),
                                           justify="center")
            self.entry_second.grid(row=1, column=4, padx=10, pady=5)
            
            # Test Example
            example_label = ctk.CTkLabel(self.schedule_backup_frame,
                                       bg_color="transparent",
                                       text="Example: 00:00:10 = Every 10 seconds (for testing)",
                                       text_color="#FF6B6B",
                                       font=("Arial", 12, "bold"))
            example_label.place(x=100, y=290)
            
            # Filename input
            filename_label = ctk.CTkLabel(self.schedule_backup_frame,
                                        bg_color="transparent",
                                        text="Backup Filename Prefix (optional)",
                                        text_color="black",
                                        font=("Merriweather Sans bold", 15))
            filename_label.place(x=100, y=330)
            
            self.entry_filename = ctk.CTkEntry(self.schedule_backup_frame,
                                             width=300,
                                             height=35,
                                             placeholder_text="scheduled_backup",
                                             font=("Merriweather light", 12))
            self.entry_filename.place(x=100, y=360)

            def validate_and_schedule():
                """Validate inputs and start scheduled backup"""
                if not self.backup_destination:
                    messagebox.showerror("No Destination", "Please choose a backup destination folder first using 'Choose Destination' button.")
                    return
                
                try:
                    # Get values
                    hour = self.entry_hour.get() or "0"
                    minute = self.entry_minute.get() or "0"
                    second = self.entry_second.get() or "0"
                    filename = self.entry_filename.get() or "scheduled_backup"
                    
                    # Validate time inputs
                    try:
                        hour_int = int(hour)
                        minute_int = int(minute)
                        second_int = int(second)
                        
                        if not (0 <= hour_int <= 23):
                            raise ValueError("Hours must be between 0-23")
                        if not (0 <= minute_int <= 59):
                            raise ValueError("Minutes must be between 0-59")
                        if not (0 <= second_int <= 59):
                            raise ValueError("Seconds must be between 0-59")
                        
                        # Check if at least one value is greater than 0
                        if hour_int == 0 and minute_int == 0 and second_int == 0:
                            raise ValueError("Time interval cannot be 00:00:00")
                            
                    except ValueError as e:
                        messagebox.showerror("Invalid Time", f"Please enter valid time values.\n\n{str(e)}")
                        return
                    
                    # Calculate total seconds
                    total_seconds = hour_int * 3600 + minute_int * 60 + second_int
                    
                    # Stop any existing backup timer
                    if self.backup_timer:
                        self.after_cancel(self.backup_timer)
                        print("🛑 Cancelled previous backup schedule")
                    
                    # Start scheduled backup
                    start_scheduled_backup(total_seconds, filename)
                    
                    messagebox.showinfo(
                        "Schedule Started", 
                        f"Backup scheduled successfully!\n\n"
                        f"Interval: {hour_int:02d}:{minute_int:02d}:{second_int:02d} ({total_seconds} seconds)\n"
                        f"Destination: {self.backup_destination}\n"
                        f"Filename Prefix: {filename}\n\n"
                        f"First backup will start in {total_seconds} seconds.\n"
                        f"Check console for backup progress."
                    )
                    
                    # Return to main maintenance view
                    back_to_maintenance()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")
            
            def back_to_maintenance():
                """Return to main maintenance view"""
                if self.schedule_backup_frame:
                    self.schedule_backup_frame.destroy()
                    self.schedule_backup_frame = None
            
            # Back Button
            back_button = ctk.CTkButton(self.schedule_backup_frame,
                                      bg_color="transparent",
                                      fg_color="#6C757D",
                                      hover_color="#5A6268",
                                      width=100,
                                      height=35,
                                      corner_radius=15,
                                      text="Back",
                                      text_color="white",
                                      cursor="hand2",
                                      command=back_to_maintenance,
                                      font=("Merriweather Bold", 12))
            back_button.place(x=100, y=410)
            
            # Schedule Button 
            schedule_button = ctk.CTkButton(self.schedule_backup_frame,
                                          bg_color="transparent",
                                          fg_color="#00C88D",
                                          hover_color="#00B07B",
                                          width=120,
                                          height=40,
                                          corner_radius=15,
                                          text="Start Schedule",
                                          text_color="white",
                                          cursor="hand2",
                                          command=validate_and_schedule,
                                          font=("Merriweather Bold", 14))
            schedule_button.place(x=850, y=405)

        # Backup option buttons
        try:
            ManualBackupIcon_image = ctk.CTkImage(Image.open("assets/ManualBackupIcon.png"), size=(20,20))
        except:
            ManualBackupIcon_image = None
            
        ManualBackup_Button = ctk.CTkButton(option_frame,
                                            image=ManualBackupIcon_image,
                                            compound="left",
                                            bg_color="transparent",
                                            fg_color="#00C88D",
                                            hover_color="#00B07B",
                                            width=180,
                                            height=60,
                                            corner_radius=20,
                                            text="Manual\nBackup",
                                            text_color="white",
                                            cursor="hand2",
                                            command=on_manual_backup_click,
                                            font=button_font)
        ManualBackup_Button.place(x=50,y=80)

        try:
            ScheduleBackup_image = ctk.CTkImage(Image.open("assets/ScheduleBackup.png"), size=(20,20))
        except:
            ScheduleBackup_image = None
            
        ScheduleBackup_Button = ctk.CTkButton(option_frame,
                                            image=ScheduleBackup_image,
                                            compound="left",
                                            bg_color="transparent",
                                            fg_color="#145266",
                                            hover_color="#1F6F88",
                                            width=180,
                                            height=60,
                                            corner_radius=20,
                                            text="Schedule\nBackup",
                                            text_color="white",
                                            cursor="hand2",
                                            command=schedule_backup_action,
                                            font=button_font)
        ScheduleBackup_Button.place(x=300,y=80)

        def find_mysql():
            """Find mysql executable in common locations for import"""
            common_paths = [
                "mysql",  # If it's in PATH
                r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
                r"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe",
                r"C:\xampp\mysql\bin\mysql.exe",
                r"C:\wamp64\bin\mysql\mysql8.0.21\bin\mysql.exe",
                r"C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin\mysql.exe"
            ]
            
            for path in common_paths:
                if shutil.which(path) or os.path.exists(path):
                    return path
            
            return None

        def import_backup_action():
            """Import backup from SQL file"""
            try:
                # Choose SQL file to import
                root = tk.Tk()
                root.withdraw()
                
                file_path = filedialog.askopenfilename(
                    title="Select Backup File to Import",
                    filetypes=[
                        ("SQL files", "*.sql"),
                        ("All files", "*.*")
                    ]
                )
                
                root.destroy()
                
                if not file_path:
                    messagebox.showwarning("Import Cancelled", "No file selected.")
                    return
                
                # Confirm import action
                confirm = messagebox.askyesno(
                    "Confirm Import",
                    f"This will import data from:\n{os.path.basename(file_path)}\n\n"
                    "WARNING: This may overwrite existing data.\n"
                    "Do you want to continue?"
                )
                
                if not confirm:
                    return
                
                # Find mysql executable
                mysql_path = find_mysql()
                if not mysql_path:
                    messagebox.showerror(
                        "MySQL Error",
                        "mysql client not found!\n\n"
                        "Please ensure MySQL is installed and add its bin folder to your system PATH."
                    )
                    return
                
                # Show progress
                progress_window = tk.Toplevel()
                progress_window.title("Import in Progress")
                progress_window.geometry("300x100")
                progress_window.resizable(False, False)
                progress_window.transient(self)
                progress_window.grab_set()
                
                progress_label = tk.Label(progress_window, text="Importing backup...\nPlease wait...")
                progress_label.pack(expand=True)
                progress_window.update()
                
                # Execute import
                with open(file_path, 'r', encoding='utf-8') as sql_file:
                    result = subprocess.run([
                        mysql_path,
                        "-u", DB_USER,
                        f"-p{DB_PASSWORD}",
                        DB_NAME
                    ], stdin=sql_file, stderr=subprocess.PIPE, text=True)
                
                progress_window.destroy()
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "Unknown error occurred"
                    messagebox.showerror("Import Failed", f"Database import failed!\n\nError: {error_msg}")
                    return
                
                # Log import to database
                try:
                    now = datetime.datetime.now()
                    connect = db()
                    cursor = connect.cursor()
                    
                    username = login_shared_states.get('logged_username', None)
                    cursor.execute("""
                        SELECT employee_id, full_name FROM users WHERE username = %s
                    """, (username,))
                    
                    result = cursor.fetchone()
                    if result:
                        employee_id_u, full_name = result
                        
                        cursor.execute("""
                            INSERT INTO backup_logs (
                                employee_id, backup_source, last_date, last_time
                            ) VALUES (%s, %s, %s, %s)
                        """, (
                            employee_id_u,
                            f"Import: {os.path.basename(file_path)}",
                            now.date(),
                            now.time()
                        ))
                        
                        connect.commit()
                    
                    cursor.close()
                    connect.close()
                    
                except Exception as db_error:
                    print(f"Failed to log import: {db_error}")
                
                # Show success message and offer refresh
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                
                # Ask user if they want to refresh the system
                refresh_choice = messagebox.askyesno(
                    "Import Successful - Refresh System?",
                    f"Database import completed successfully!\n\n"
                    f"File: {os.path.basename(file_path)}\n"
                    f"Size: {file_size:.2f} MB\n"
                    f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"Would you like to refresh all system data now?\n"
                    f"This will update all tables and views immediately."
                )
                
                if refresh_choice:
                    # Refresh all system components
                    self.refresh_entire_system()
                    messagebox.showinfo(
                        "System Refreshed",
                        "All system data has been refreshed successfully!\n"
                        "All pages now show the imported data."
                    )
                else:
                    messagebox.showinfo(
                        "Import Complete",
                        "Import successful! Please manually refresh pages or restart the application to see all imported data."
                    )
                
            except Exception as e:
                messagebox.showerror("Import Error", f"An unexpected error occurred:\n\n{str(e)}")

        try:
            LogsIcon_image = ctk.CTkImage(Image.open("assets/LogsIcon.png"), size=(20,20))
        except:
            LogsIcon_image = None
            
        ImportBackup_Button = ctk.CTkButton(option_frame,
                                            image=LogsIcon_image,
                                            compound="left",
                                            bg_color="transparent",
                                            fg_color="#1A374D",
                                            hover_color="#25475A",
                                            width=180,
                                            height=60,
                                            corner_radius=20,
                                            text="Import\nBackup",
                                            text_color="white",
                                            cursor="hand2",
                                            command=import_backup_action,
                                            font=button_font)
        ImportBackup_Button.place(x=550,y=80)

        # Schedule display frame
        Schedule_frame = ctk.CTkFrame(Maintenance_MainFrame,
                                    bg_color="transparent",
                                    fg_color="#FFFFFF", 
                                    width=800, 
                                    height=150, 
                                    corner_radius=20,
                                    border_width=1.5,
                                    border_color="#BBBBBB")
        Schedule_frame.place(x=100,y=300)

        schedule_label = ctk.CTkLabel(Schedule_frame,
                                     text="Schedule",
                                     text_color="black",
                                     bg_color="#FFFFFF",
                                     font=SubTitle_font)
        schedule_label.place(x=40,y=20)

        schedule_sublabel = ctk.CTkLabel(Schedule_frame,
                                       text="Date and Time.",
                                       text_color="black",
                                       bg_color="#FFFFFF",
                                       font=sublabel_font)
        schedule_sublabel.place(x=40,y=40)

        # Current date Frame
        current_date_frame = ctk.CTkFrame(Schedule_frame,
                                        bg_color="#FFFFFF",
                                        fg_color="#3B71AC", 
                                        width=200, 
                                        height=60, 
                                        corner_radius=10)
        current_date_frame.place(relx=.05,rely=.5)
        
        try:
            CurrenDate_image = ctk.CTkImage(Image.open("assets/TimeIcon.png"), size=(20,20))
            Current_image_label = ctk.CTkLabel(current_date_frame,image=CurrenDate_image,text="")
            Current_image_label.place(relx=.125,rely=.5,anchor="w")
        except:
            pass

        Current_date_label = ctk.CTkLabel(current_date_frame,
                                        bg_color="#3B71AC",
                                        text="Current Date :",
                                        text_color="#FFFFFF",
                                        font=time_label_font,
                                        height=10)
        Current_date_label.place(relx=.25,rely=.175)

        self.Current_date_output = ctk.CTkLabel(current_date_frame,
                                              bg_color="#3B71AC",
                                              text="06/01/25",
                                              text_color="#FFFFFF",
                                              font=time_output_font,
                                              height=10)
        self.Current_date_output.place(relx=.6,rely=.175)

        Current_time_label = ctk.CTkLabel(current_date_frame,
                                        bg_color="#3B71AC",
                                        text="Current time :",
                                        text_color="#FFFFFF",
                                        font=time_label_font,
                                        height=10)
        Current_time_label.place(relx=.25,rely=.5)

        self.Current_time_output = ctk.CTkLabel(current_date_frame,
                                              bg_color="#3B71AC",
                                              text="20 : 00",
                                              text_color="#FFFFFF",
                                              font=time_output_font,
                                              height=10)
        self.Current_time_output.place(relx=.6,rely=.5)

        # Last backup date Frame
        lastBackup_date_frame = ctk.CTkFrame(Schedule_frame,
                                           bg_color="#FFFFFF",
                                           fg_color="#00C88D", 
                                           width=200, 
                                           height=60, 
                                           corner_radius=10)
        lastBackup_date_frame.place(relx=.35,rely=.5)
        
        try:
            Lastbackup_image = ctk.CTkImage(Image.open("assets/TimeIcon.png"), size=(20,20))
            Lastbackup_image_label = ctk.CTkLabel(lastBackup_date_frame,image=Lastbackup_image,text="")
            Lastbackup_image_label.place(relx=.075,rely=.5,anchor="w")
        except:
            pass

        LastBackup_date_label = ctk.CTkLabel(lastBackup_date_frame,
                                           bg_color="#00C88D",
                                           text="Last Backup Date :",
                                           text_color="#FFFFFF",
                                           font=time_label_font,
                                           height=10)
        LastBackup_date_label.place(relx=.195,rely=.175)

        self.LastBackup_date_output = ctk.CTkLabel(lastBackup_date_frame,
                                                 bg_color="#00C88D",
                                                 text="No Backup",
                                                 text_color="#FFFFFF",
                                                 font=time_output_font,
                                                 height=10)
        self.LastBackup_date_output.place(relx=.675,rely=.175)

        LastBackup_time_label = ctk.CTkLabel(lastBackup_date_frame,
                                           bg_color="#00C88D",
                                           text="Last Backup Time :",
                                           text_color="#FFFFFF",
                                           font=time_label_font,
                                           height=10)
        LastBackup_time_label.place(relx=.195,rely=.5)

        self.LastBackup_time_output = ctk.CTkLabel(lastBackup_date_frame,
                                                 bg_color="#00C88D",
                                                 text="--:--",
                                                 text_color="#FFFFFF",
                                                 font=time_output_font,
                                                 height=10)
        self.LastBackup_time_output.place(relx=.675,rely=.5)

        # Next backup date Frame
        NextBackup_date_frame = ctk.CTkFrame(Schedule_frame,
                                           bg_color="#FFFFFF",
                                           fg_color="#FAAE61", 
                                           width=200, 
                                           height=60, 
                                           corner_radius=10)
        NextBackup_date_frame.place(relx=.65,rely=.5)
        
        try:
            Nextbackup_image = ctk.CTkImage(Image.open("assets/ScheduleBackup.png"), size=(20,20))
            Nextbackup_image_label = ctk.CTkLabel(NextBackup_date_frame,image=Nextbackup_image,text="")
            Nextbackup_image_label.place(relx=.075,rely=.5,anchor="w")
        except:
            pass

        NextBackup_date_label = ctk.CTkLabel(NextBackup_date_frame,
                                           bg_color="#FAAE61",
                                           text="Next Backup Date :",
                                           text_color="#FFFFFF",
                                           font=time_label_font,
                                           height=10)
        NextBackup_date_label.place(relx=.195,rely=.175)

        self.NextBackup_date_output = ctk.CTkLabel(NextBackup_date_frame,
                                                 bg_color="#FAAE61",
                                                 text="Not Scheduled",
                                                 text_color="#FFFFFF",
                                                 font=time_output_font,
                                                 height=10)
        self.NextBackup_date_output.place(relx=.675,rely=.175)

        NextBackup_time_label = ctk.CTkLabel(NextBackup_date_frame,
                                           bg_color="#FAAE61",
                                           text="Next Backup Time :",
                                           text_color="#FFFFFF",
                                           font=time_label_font,
                                           height=10)
        NextBackup_time_label.place(relx=.195,rely=.5)

        self.NextBackup_time_output = ctk.CTkLabel(NextBackup_date_frame,
                                                 bg_color="#FAAE61",
                                                 text="--:--",
                                                 text_color="#FFFFFF",
                                                 font=time_output_font,
                                                 height=10)
        self.NextBackup_time_output.place(relx=.675,rely=.5)

        # Latest Backup Logs Frame
        Maintenance_Logs_MainFrame = ctk.CTkFrame(self,
                                                bg_color="transparent", 
                                                fg_color='#FFFFFF',
                                                width=1000,
                                                height=350,
                                                corner_radius=20)
        Maintenance_Logs_MainFrame.place(x=100,y=630)

        leftbar_frame2 = ctk.CTkFrame(Maintenance_Logs_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#1A374D",
                                     width=25,
                                     height=350,
                                     corner_radius=20)
        leftbar_frame2.place(x=0)

        label_Title = ctk.CTkLabel(Maintenance_Logs_MainFrame, 
                                 bg_color="transparent",
                                 text="Latest Backup Logs",
                                 text_color="black",
                                 font=Title_font)
        label_Title.place(x=80,y=30)

        label_Subtitle = ctk.CTkLabel(Maintenance_Logs_MainFrame, 
                                    bg_color="transparent",
                                    text="Display the latest backup logs.",
                                    text_color="#104E44",
                                    font=sublabel_font)
        label_Subtitle.place(x=80,y=60)

        # Header frame for backup logs table
        backup_logs_header_frame = ctk.CTkFrame(Maintenance_Logs_MainFrame,
                                              width=900,
                                              height=30,
                                              corner_radius=10,
                                              fg_color="#1A374D")
        backup_logs_header_frame.place(x=50, y=90)
        
        # Header labels for backup logs
        ctk.CTkLabel(backup_logs_header_frame, text="Backup ID", 
                    font=("Merriweather Bold", 11), text_color="white").place(x=20, y=7)
        
        ctk.CTkLabel(backup_logs_header_frame, text="Employee Name", 
                    font=("Merriweather Bold", 11), text_color="white").place(x=230, y=7)
        
        ctk.CTkLabel(backup_logs_header_frame, text="Date", 
                    font=("Merriweather Bold", 11), text_color="white").place(x=505, y=7)
        
        ctk.CTkLabel(backup_logs_header_frame, text="Time", 
                    font=("Merriweather Bold", 11), text_color="white").place(x=705, y=7)
        
        # Scrollable frame for backup logs
        self.backup_logs_scrollable_frame = ctk.CTkScrollableFrame(Maintenance_Logs_MainFrame,
                                                                 width=900,
                                                                 height=220,
                                                                 corner_radius=0,
                                                                 fg_color="transparent")
        self.backup_logs_scrollable_frame.place(x=50, y=125)

        # Initialize backup data loading
        self.load_backup_data()
        self.load_backup_logs_table()
        self.update_time()

        #---------------------------------RIGHT SIDE-----------------------------------------

        # Storage Frame 
        Storage_Level_MainFrame = ctk.CTkFrame(self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=400,
                                            height=225,
                                            corner_radius=20)
        Storage_Level_MainFrame.place(x=1150,y=120)

        topbar_frame = ctk.CTkFrame(Storage_Level_MainFrame,
                                     bg_color="transparent",
                                     fg_color="#2B6B9C",
                                     width=400,
                                     height=10,
                                     corner_radius=20)
        topbar_frame.place(y=0)

        Storage_label = ctk.CTkLabel(Storage_Level_MainFrame, 
                                   bg_color="transparent",
                                   text="Storage Space",
                                   text_color="black",
                                   font=SubTitle_font)
        Storage_label.place(x=30,y=20)
        
        storage_sublabel = ctk.CTkLabel(Storage_Level_MainFrame, 
                                      bg_color="transparent",
                                      text="Current Storage Status of the System",
                                      text_color="#104E44",
                                      font=sublabel_font)
        storage_sublabel.place(x=30,y=50)

        current_path = os.getcwd()

        def get_disk_usage(path):
            usage = shutil.disk_usage(path)
            total = usage.total
            used = usage.used
            free = usage.free
            percent_used = used / total * 100
            return total, used, free, percent_used

        self.progress_bar = ctk.CTkProgressBar(Storage_Level_MainFrame, 
                                             width=300,
                                             height=30,
                                             fg_color="#D9D9D9")
        self.progress_bar.place(x=50, y=120)

        self.usage_label = ctk.CTkLabel(Storage_Level_MainFrame, 
                                      bg_color="transparent",
                                      text="", 
                                      text_color="black",
                                      font=time_output_font)
        self.usage_label.place(x=100, y=150)

        def update_disk_usage():
            total, used, free, percent_used = get_disk_usage(current_path)
            self.progress_bar.set(percent_used / 100)
            self.usage_label.configure(text=f"Used: {percent_used:.2f}%  |  Free: {free // (1024**3)} GB  |  Total: {total // (1024**3)} GB")
            self.after(5000, update_disk_usage)

        update_disk_usage()

        # Export Frame/Print Frame
        Print_MainFrame = ctk.CTkFrame(self,
                                     bg_color="transparent", 
                                     fg_color='#FFFFFF',
                                     width=400,
                                     height=225,
                                     corner_radius=20)
        Print_MainFrame.place(x=1150,y=390)

        Print_label = ctk.CTkLabel(Print_MainFrame, 
                                 bg_color="transparent",
                                 text="Data Export",
                                 text_color="black",
                                 font=SubTitle_font)
        Print_label.place(x=30,y=20)
        
        print_sublabel = ctk.CTkLabel(Print_MainFrame, 
                                    bg_color="transparent",
                                    text="Export the data available on report",
                                    text_color="#104E44",
                                    font=sublabel_font)
        print_sublabel.place(x=30,y=50)

        leftbar_frame_export = ctk.CTkFrame(Print_MainFrame,
                                          bg_color="transparent",
                                          fg_color="#972A2A",
                                          width=15,
                                          height=225,
                                          corner_radius=20)
        leftbar_frame_export.place(x=0)

        def export_pdf_action():
            """Export report data to PDF with shared state access"""
            try:
                # Get current period from shared state
                current_period = report_shared_states.get('current_period', 'Overall')
                
                print(f"📄 Generating PDF report for period: {current_period}")
                
                # Show progress message
                progress_window = tk.Toplevel()
                progress_window.title("Generating PDF Report")
                progress_window.geometry("350x120")
                progress_window.resizable(False, False)
                progress_window.transient(self)
                progress_window.grab_set()
                
                progress_label = tk.Label(progress_window, 
                                        text=f"Generating PDF report for {current_period}...\nPlease wait...",
                                        font=("Poppins", 11))
                progress_label.pack(expand=True)
                progress_window.update()
                
                # Create PDF generator and export
                pdf_generator = PDFReportGenerator(db)
                success = pdf_generator.export_report_to_pdf(current_period)
                
                progress_window.destroy()
                
                if success:
                    print("✅ PDF report exported successfully!")
                else:
                    print("❌ PDF report export failed!")
                    
            except Exception as e:
                if 'progress_window' in locals():
                    progress_window.destroy()
                print(f"❌ PDF export error: {str(e)}")
                messagebox.showerror("Export Error", f"Failed to export PDF:\n{str(e)}")

        try:
            exportpdf_image = ctk.CTkImage(Image.open("assets/ExportPDF.png"), size=(20,20))
        except:
            exportpdf_image = None
            
        ExportPDF_Button = ctk.CTkButton(Print_MainFrame,
                                       image=exportpdf_image,
                                       compound="left",
                                       bg_color="transparent",
                                       fg_color="#FF8181",
                                       hover_color="#D35858",
                                       width=200,
                                       height=40,
                                       corner_radius=20,
                                       text="Export PDF file",
                                       text_color="white",
                                       cursor="hand2",
                                       font=button_font)
        ExportPDF_Button.place(x=100,y=120)

        # Setup admin-only access for Export PDF button
        self.role_manager.setup_admin_only_button(
            button=ExportPDF_Button,
            parent_widget=self,
            command_callback=export_pdf_action,
            tooltip_text="Only Admin can export PDF files"
        )

        # Employee Backups Frame
        Employee_Backups_Frame = ctk.CTkFrame(self,
                                            bg_color="transparent", 
                                            fg_color='#FFFFFF',
                                            width=400,
                                            height=325,
                                            corner_radius=20)
        Employee_Backups_Frame.place(x=1150,y=650)

        Employeebackup_label = ctk.CTkLabel(Employee_Backups_Frame, 
                                          bg_color="transparent",
                                          text="Employee Backups",
                                          text_color="black",
                                          font=SubTitle_font)
        Employeebackup_label.place(x=30,y=20)
        
        employee_backup_sublabel = ctk.CTkLabel(Employee_Backups_Frame, 
                                              bg_color="transparent",
                                              text="Backups made per employee",
                                              text_color="#104E44",
                                              font=sublabel_font)
        employee_backup_sublabel.place(x=30,y=50)

        # Header frame for employee backups table
        employee_backup_header_frame = ctk.CTkFrame(Employee_Backups_Frame,
                                                  width=350,
                                                  height=30,
                                                  corner_radius=10,
                                                  fg_color="#1A374D")
        employee_backup_header_frame.place(x=25, y=80)
        
        # Header labels for employee backups
        ctk.CTkLabel(employee_backup_header_frame, text="Employee Name", 
                    font=("Merriweather Bold", 11), text_color="white").place(x=65, y=7)
        
        ctk.CTkLabel(employee_backup_header_frame, text="Backup Count", 
                    font=("Merriweather Bold", 11), text_color="white").place(x=245, y=7)
        
        # Scrollable frame for employee backup data
        self.employee_backup_scrollable_frame = ctk.CTkScrollableFrame(Employee_Backups_Frame,
                                                                      width=350,
                                                                      height=210,
                                                                      corner_radius=0,
                                                                      fg_color="transparent")
        self.employee_backup_scrollable_frame.place(x=25, y=115)

        # Load employee backup data
        self.load_employee_backup_table()

    def stop_scheduled_backup(self):
        """Stop the scheduled backup"""
        if self.backup_timer:
            self.after_cancel(self.backup_timer)
            self.backup_timer = None
            print("🛑 Scheduled backup stopped")
            messagebox.showinfo("Schedule Stopped", "Scheduled backup has been stopped.")
            
            # Clear next backup time
            self.NextBackup_date_output.configure(text="Not Scheduled")
            self.NextBackup_time_output.configure(text="--:--")
        else:
            messagebox.showinfo("No Schedule", "No backup schedule is currently running.")

    def update_time(self):
        """Update current date and time display"""
        now = datetime.datetime.now()  # USE datetime.datetime.now()
        self.Current_date_output.configure(text=now.strftime("%m - %d - %y"))
        self.Current_time_output.configure(text=now.strftime("%H : %M : %S"))
        self.after(1000, self.update_time)

    def update_last_backup_time(self):
        """Update last backup time from database"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            username = login_shared_states.get('logged_username', None)
            cursor.execute("""
                SELECT bl.last_date, bl.last_time 
                FROM backup_logs bl
                JOIN users u ON bl.employee_id = u.employee_id
                WHERE u.username = %s AND bl.last_date IS NOT NULL AND bl.last_time IS NOT NULL
                ORDER BY bl.last_date DESC, bl.last_time DESC
                LIMIT 1
            """, (username,))
            
            result = cursor.fetchone()
            if result:
                last_date, last_time = result
                self.LastBackup_date_output.configure(text=last_date.strftime("%m/%d/%y"))
                if isinstance(last_time, timedelta):
                    total_seconds = int(last_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_str = last_time.strftime("%H:%M")
                self.LastBackup_time_output.configure(text=time_str)
            else:
                self.LastBackup_date_output.configure(text="No Backup")
                self.LastBackup_time_output.configure(text="--:--")
                
            cursor.close()
            connect.close()
            
        except Exception as e:
            print(f"Error updating last backup time: {e}")

    def update_next_backup_time(self, scheduled_datetime=None):
        """Update next backup time display"""
        try:
            if scheduled_datetime:
                self.NextBackup_date_output.configure(text=scheduled_datetime.strftime("%m/%d/%y"))
                self.NextBackup_time_output.configure(text=scheduled_datetime.strftime("%H:%M"))
            else:
                self.NextBackup_date_output.configure(text="Not Scheduled")
                self.NextBackup_time_output.configure(text="--:--")
                
        except Exception as e:
            print(f"Error updating next backup time: {e}")

    def load_backup_logs_table(self):
        """Load latest backup logs and display in table"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Query to get latest backup logs with employee names
            cursor.execute("""
                SELECT 
                    bl.backup_id,
                    u.full_name as employee_name,
                    bl.last_date,
                    bl.last_time,
                    bl.backup_source
                FROM backup_logs bl
                JOIN users u ON bl.employee_id = u.employee_id
                WHERE bl.last_date IS NOT NULL AND bl.last_time IS NOT NULL
                ORDER BY bl.last_date DESC, bl.last_time DESC
                LIMIT 10
            """)
            
            backup_logs = cursor.fetchall()
            
            # Clear existing data
            for widget in self.backup_logs_scrollable_frame.winfo_children():
                widget.destroy()
            
            if not backup_logs:
                # Show "No data" message if no logs found
                no_data_frame = ctk.CTkFrame(self.backup_logs_scrollable_frame,
                                           width=880,
                                           height=60,
                                           corner_radius=5,
                                           fg_color="#F8F9FA")
                no_data_frame.pack(fill="x", pady=20, padx=5)
                no_data_frame.pack_propagate(False)
                
                ctk.CTkLabel(no_data_frame, 
                           text="No backup logs found",
                           font=("Poppins Regular", 12),
                           text_color="#666666").place(relx=0.5, rely=0.5, anchor="center")
                return
            
            # Add backup log rows
            for i, (backup_id, employee_name, last_date, last_time, backup_source) in enumerate(backup_logs):
                # Create row frame with alternating colors
                row_frame = ctk.CTkFrame(self.backup_logs_scrollable_frame,
                                       width=880,
                                       height=45,
                                       corner_radius=5,
                                       fg_color="#F8F9FA" if i % 2 == 0 else "#FFFFFF")
                row_frame.pack(fill="x", pady=1, padx=5)
                row_frame.pack_propagate(False)
                
                # Backup ID
                id_label = ctk.CTkLabel(row_frame, text=str(backup_id),
                                      font=("Poppins Regular", 10),
                                      text_color="#333333",
                                      width=60)
                id_label.place(x=10, y=12)
                
                # Employee Name
                name_label = ctk.CTkLabel(row_frame, text=str(employee_name) if employee_name else "Unknown",
                                        font=("Poppins Regular", 10),
                                        text_color="#333333",
                                        width=280)
                name_label.place(x=130, y=12)
                
                # Date
                if last_date:
                    if hasattr(last_date, 'strftime'):
                        date_str = last_date.strftime("%Y-%m-%d")
                    else:
                        date_str = str(last_date)
                else:
                    date_str = "N/A"
                    
                date_label = ctk.CTkLabel(row_frame, text=date_str,
                                        font=("Poppins Regular", 10),
                                        text_color="#333333",
                                        width=120)
                date_label.place(x=450, y=12)
                
                # Time
                if last_time:
                    if isinstance(last_time, timedelta):
                        total_seconds = int(last_time.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    elif hasattr(last_time, 'strftime'):
                        time_str = last_time.strftime("%H:%M:%S")
                    else:
                        time_str = str(last_time)
                else:
                    time_str = "N/A"
                    
                time_label = ctk.CTkLabel(row_frame, text=time_str,
                                        font=("Poppins Regular", 10),
                                        text_color="#333333",
                                        width=120)
                time_label.place(x=650, y=12)
                
        except Exception as e:
            print(f'Error loading backup logs: {e}')
            # Show error message
            error_frame = ctk.CTkFrame(self.backup_logs_scrollable_frame,
                                     width=880,
                                     height=60,
                                     corner_radius=5,
                                     fg_color="#FFE6E6")
            error_frame.pack(fill="x", pady=20, padx=5)
            error_frame.pack_propagate(False)
            
            error_label = ctk.CTkLabel(error_frame,
                                     text=f"Error loading backup logs: {str(e)}",
                                     font=("Poppins Regular", 10),
                                     text_color="red")
            error_label.place(relx=0.5, rely=0.5, anchor="center")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def load_employee_backup_table(self):
        """Load employee backup counts and display in table"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Query to get backup counts per employee
            cursor.execute("""
                SELECT 
                    u.full_name as employee_name,
                    COUNT(bl.backup_id) as backup_count
                FROM users u
                LEFT JOIN backup_logs bl ON u.employee_id = bl.employee_id 
                    AND bl.last_date IS NOT NULL AND bl.last_time IS NOT NULL
                GROUP BY u.employee_id, u.full_name
                HAVING backup_count > 0
                ORDER BY backup_count DESC, u.full_name ASC
            """)
            
            employee_backups = cursor.fetchall()
            
            # Clear existing data
            for widget in self.employee_backup_scrollable_frame.winfo_children():
                widget.destroy()
            
            if not employee_backups:
                # Show "No data" message if no backups found
                no_data_frame = ctk.CTkFrame(self.employee_backup_scrollable_frame,
                                           width=330,
                                           height=60,
                                           corner_radius=5,
                                           fg_color="#F8F9FA")
                no_data_frame.pack(fill="x", pady=20, padx=5)
                no_data_frame.pack_propagate(False)
                
                ctk.CTkLabel(no_data_frame, 
                           text="No employee backups found",
                           font=("Poppins Regular", 11),
                           text_color="#666666").place(relx=0.5, rely=0.5, anchor="center")
                return
            
            # Add employee backup rows
            for i, (employee_name, backup_count) in enumerate(employee_backups):
                # Create row frame with alternating colors
                row_frame = ctk.CTkFrame(self.employee_backup_scrollable_frame,
                                       width=330,
                                       height=40,
                                       corner_radius=5,
                                       fg_color="#F8F9FA" if i % 2 == 0 else "#FFFFFF")
                row_frame.pack(fill="x", pady=1, padx=5)
                row_frame.pack_propagate(False)
                
                # Employee Name
                name_label = ctk.CTkLabel(row_frame, text=str(employee_name) if employee_name else "Unknown",
                                        font=("Poppins Regular", 11),
                                        text_color="#333333",
                                        width=220)
                name_label.place(x=10, y=10)
                
                # Backup Count with badge-style background
                count_frame = ctk.CTkFrame(row_frame,
                                         width=50,
                                         height=25,
                                         corner_radius=12,
                                         fg_color="#68EDC6")
                count_frame.place(x=260, y=7)
                
                count_label = ctk.CTkLabel(count_frame, text=str(backup_count),
                                         font=("Poppins Bold", 11),
                                         text_color="white")
                count_label.place(relx=0.5, rely=0.5, anchor="center")
                
        except Exception as e:
            print(f'Error loading employee backup data: {e}')
            # Show error message
            error_frame = ctk.CTkFrame(self.employee_backup_scrollable_frame,
                                     width=330,
                                     height=60,
                                     corner_radius=5,
                                     fg_color="#FFE6E6")
            error_frame.pack(fill="x", pady=20, padx=5)
            error_frame.pack_propagate(False)
            
            error_label = ctk.CTkLabel(error_frame,
                                     text=f"Error loading employee data: {str(e)}",
                                     font=("Poppins Regular", 10),
                                     text_color="red")
            error_label.place(relx=0.5, rely=0.5, anchor="center")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def load_backup_data(self):
        """Load and display backup information"""
        self.update_last_backup_time()
        self.update_next_backup_time()

    def refresh_entire_system(self):
        """Refresh all system components after import"""
        try:
            print("🔄 Refreshing entire system after import...")
            
            # Get reference to main HomePage through widget hierarchy
            current_widget = self
            homepage = None
            
            # Traverse up to find HomePage
            while current_widget:
                if hasattr(current_widget, '__class__'):
                    class_name = current_widget.__class__.__name__
                    if class_name == 'HomePage':
                        homepage = current_widget
                        break
                current_widget = getattr(current_widget, 'master', None)
            
            if homepage and hasattr(homepage, 'pages'):
                print("✅ Found HomePage, refreshing all pages...")
                
                # 1. Refresh Home Page (pie chart, recent patients, graphs)
                if 'Home' in homepage.pages:
                    home_page = homepage.pages['Home']
                    if hasattr(home_page, 'refresh_patient_data_and_chart'):
                        home_page.refresh_patient_data_and_chart()
                    if hasattr(home_page, 'refresh_recent_patient'):
                        home_page.refresh_recent_patient()
                    if hasattr(home_page, 'show_overall_usage'):
                        home_page.show_overall_usage()
                    if hasattr(home_page, 'show_yesterday_usage'):
                        home_page.show_yesterday_usage()
                    print("✅ Home page refreshed")
                
                # 2. Refresh Patient Page (table data)
                if 'Patient' in homepage.pages:
                    patient_page = homepage.pages['Patient']
                    if hasattr(patient_page, 'refresh_table'):
                        patient_page.refresh_table()
                    print("✅ Patient page refreshed")
                
                # 3. Refresh Supply Page (table data)
                if 'Supply' in homepage.pages:
                    supply_page = homepage.pages['Supply']
                    if hasattr(supply_page, 'refresh_table'):
                        supply_page.refresh_table()
                    print("✅ Supply page refreshed")
                
                # 4. Refresh Report Page (data counts and graphs)
                if 'Report' in homepage.pages:
                    report_page = homepage.pages['Report']
                    if hasattr(report_page, 'refresh_data'):
                        report_page.refresh_data()
                    print("✅ Report page refreshed")
                
                # 5. Refresh Maintenance Page (backup logs AND tables)
                if 'Maintenance' in homepage.pages:
                    maintenance_page = homepage.pages['Maintenance']
                    if hasattr(maintenance_page, 'load_backup_data'):
                        maintenance_page.load_backup_data()
                    # Also refresh the backup logs tables
                    if hasattr(maintenance_page, 'load_backup_logs_table'):
                        maintenance_page.load_backup_logs_table()
                    if hasattr(maintenance_page, 'load_employee_backup_table'):
                        maintenance_page.load_employee_backup_table()
                    print("✅ Maintenance page refreshed")
                
                print("🎉 All system components refreshed successfully!")
                
            else:
                print("❌ Could not find HomePage for system refresh")
                
            try:
                self.load_backup_logs_table()
                self.load_employee_backup_table()
                self.load_backup_data()
                print("✅ Current maintenance page instance refreshed")
            except Exception as refresh_error:
                print(f"⚠️ Could not refresh current instance: {refresh_error}")
                
        except Exception as e:
            print(f"❌ Error during system refresh: {e}")
            messagebox.showwarning(
                "Refresh Warning", 
                f"Import was successful, but automatic refresh failed:\n{str(e)}\n\n"
                "Please manually refresh pages or restart the application."
            )

    def db_connection(self):
        """Database connection helper"""
        connect = db()
        cursor = connect.cursor()
        return connect, cursor

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, shared_state):
        super().__init__(parent, fg_color="#E8FBFC")
        self.shared_state = shared_state

        # RBAC
        self.role_manager = RoleAccessManager()

        Title_font = ("Merriweather Bold", 18)
        SubTitle_font = ("Merriweather Bold", 12)
        Ouput_font = ("Poppins Regular" ,18)
        SubOutput_font = ("Poppins Regular" ,13)
        SubLabel_font = ("Merriweather Sans Light" ,9)
        Button_font =("Merriweather Sans Light",14)
        DeveloperName_font = ("Merriweather Sans Bold",10)
        DeveloperContact_font = ("Merriweather Sans light",10)

        username = login_shared_states.get('logged_username', None)

        def retrieve_login_logs(access_type):
            try:
                connect = db()
                cursor = connect.cursor()

                if access_type.lower() == 'admin':
                    cursor.execute("""
                        SELECT u.full_name, sl.login_time, sl.logout_time FROM sessions_log sl
                        JOIN users u ON sl.employee_Id = u.employee_id
                    """)
                    admin_logs_result = cursor.fetchall()
                    print(admin_logs_result)
                    return admin_logs_result

                elif access_type.lower() == 'staff':
                    cursor.execute("""
                        SELECT sl.login_time, sl.logout_time FROM sessions_log sl
                        JOIN users u ON sl.employee_Id = u.employee_id
                        WHERE username = %s
                    """, (username,))
                    staff_logs_result = cursor.fetchall()
                    print(staff_logs_result)
                    return staff_logs_result

            except Exception as e:
                print('Error fetching retrieve login logs', e)
                return []

            finally:
                cursor.close()
                connect.close()

    #About Company Frame
        About_Frame = ctk.CTkFrame(self,height=340,width=870,fg_color="#FFFFFF",corner_radius=20,)
        About_Frame.place(x=130,y=100)

        leftbar_frame = ctk.CTkFrame(About_Frame,height=340,width=15,fg_color="#1A374D",corner_radius=20)
        leftbar_frame.place(x=0)

        About_Title=ctk.CTkLabel(About_Frame,text="About Us",text_color="#000000",font=Title_font,bg_color="#FFFFFF",height=18)
        About_Title.place(x=50,y=20)
        About_Sublabel = ctk.CTkLabel(About_Frame,text="Information about the company.",text_color="#104E44",font=SubLabel_font,bg_color="#FFFFFF",height=10)
        About_Sublabel.place(x=50,y=50)

        AboutCompany_frame=ctk.CTkFrame(About_Frame,height=215,width=345,fg_color="#FFFFFF",bg_color="#FFFFFF",corner_radius=20,border_width=1.5,border_color="#BBBBBB")
        AboutCompany_frame.place(relx=.08,rely=.25)
        AboutCompany_Title=ctk.CTkLabel(AboutCompany_frame,text="First Priority Dialysis Center",text_color="#000000",font=SubTitle_font,bg_color="#FFFFFF",height=18)
        AboutCompany_Title.place(x=30,y=30)

        ServicesOffer_frame=ctk.CTkFrame(About_Frame,height=215,width=345,fg_color="#FFFFFF",bg_color="#FFFFFF",corner_radius=20,border_width=1.5,border_color="#BBBBBB")
        ServicesOffer_frame.place(relx=.52,rely=.25)
        Services_Title=ctk.CTkLabel(ServicesOffer_frame,text="Services we Offer",text_color="#000000",font=SubTitle_font,bg_color="#FFFFFF",height=18)
        Services_Title.place(x=30,y=30)


    #Help/FAQS Frame
        Help_Mainframe = ctk.CTkFrame(self,height=480,width=870,fg_color="#FFFFFF",corner_radius=20)
        Help_Mainframe.place(x=130,y=495)

        leftbar_frame = ctk.CTkFrame(Help_Mainframe,height=480,width=15,fg_color="#1A374D",corner_radius=20)
        leftbar_frame.place(x=0)

        Help_Title=ctk.CTkLabel(Help_Mainframe,text="Help/FAQs",text_color="#000000",font=Title_font,bg_color="#FFFFFF",height=18)
        Help_Title.place(x=50,y=20)
        Help_Sublabel = ctk.CTkLabel(Help_Mainframe,text="Display the frequent ask questions.",text_color="#104E44",font=SubLabel_font,bg_color="#FFFFFF",height=10)
        Help_Sublabel.place(x=50,y=50)

        Help_Frame = ctk.CTkScrollableFrame(Help_Mainframe,height=350,width=790,fg_color="#FFFFFF",scrollbar_button_color="#FFFFFF",scrollbar_button_hover_color="#FFFFFF")
        Help_Frame.place(relx=.5125,rely=.575,anchor="center")

    #Question and Answer Maximum of 150 Characthers for Answer
    #Sample Data lang toh
        cards_data = [
            {"title": "What is this app for?", "body": "This app helps you manage your tasks efficiently."},
            {"title": "How to reset password?", "body": "Click on 'Forgot Password' at login screen and follow the instructions."},
            {"title": "Can I sync data?", "body": "Yes, sync across all devices using your account."},
            {"title": "Is my data private?", "body": "We use end-to-end encryption for all sensitive data."},
            {"title": "How to contact support?", "body": "You can reach out via the help section or email support@sample.com."},
            {"title": "Where is my backup?", "body": "Backups are stored securely and can be restored from settings."},
            {"title": "Where is my backup?", "body": "Backups are stored securely and can be restored from settings."},
            {"title": "Where is my backup?", "body": "Backups are stored securely and can be restored from settings."}
        ]

        Question_font = ("Merriweather bold", 11)
        Answer_font = ("Poppins",9)

        # Create cards using grid
        for i, data in enumerate(cards_data):
            row = i // 2
            col = i % 2

            card = ctk.CTkFrame(Help_Frame, width=370, height=100, corner_radius=15, fg_color="white",border_width=1.5,border_color="#BBBBBB")
            card.grid(row=row, column=col, padx=10, pady=10)

            # Icon
            Question_image = ctk.CTkImage(Image.open("assets/QuestionIcon.png"), size=(26,26))
            icon_label = ctk.CTkLabel(card, image=Question_image, text="")
            icon_label.place(relx=.1, rely=.5,anchor="center")

            # Title
            title_label = ctk.CTkLabel(card, text=data["title"], font=Question_font, text_color="#3B3939",height=11)
            title_label.place(x=60, y=15)

            # Body
            body_label = ctk.CTkLabel(
                card,
                text=data["body"],
                font=Answer_font,
                text_color="#104E44",
                wraplength=280,
                justify="left"
            )
            body_label.place(x=60, y=35)

        username = login_shared_states.get('logged_username', None)

        try:
            connect, cursor = self.db_connection()
        
            cursor.execute("""
                SELECT full_name, role, username FROM users
                WHERE username = %s
            """, (username,))

            fetched_result = cursor.fetchone()

        except Exception as e:
            print('Error fetching current user credentials', e)

        finally:
            cursor.close()
            connect.close()

    #Current User Frame
        User_frame = ctk.CTkFrame(self,height=95,width=230,fg_color="#fFFFFF",corner_radius=10)
        User_frame.place(x=1070,y=100)

        topbar_frame = ctk.CTkFrame(User_frame,height=7,width=230,fg_color="#63BCFF",corner_radius=20)
        topbar_frame.place(y=0)

        #Output
        User_Output=ctk.CTkLabel(User_frame,text=fetched_result[0],text_color="#000000",font=Ouput_font,height=18,bg_color="#FFFFFF")
        User_Output.place(relx=.125,rely=.25)

        #Output
        position_output = ctk.CTkLabel(User_frame,text=fetched_result[1],text_color="#104E44",font=SubOutput_font,height=13,bg_color="#FFFFFF")
        position_output.place(relx=.125,rely=.525)

        seperator = ctk.CTkLabel(User_frame,text=" | ",text_color="#104E44",font=SubOutput_font,height=13,bg_color="#FFFFFF")
        seperator.place(relx=.3125,rely=.525)

        #Output
        username_output = ctk.CTkLabel(User_frame,text=fetched_result[2],text_color="#104E44",font=SubOutput_font,height=13,bg_color="#FFFFFF")
        username_output.place(relx=.3625,rely=.525)

    #Date Time Frame
        DateTime_Frame = ctk.CTkFrame(self,height=95,width=145,fg_color="#FFFFFF",corner_radius=10)
        DateTime_Frame.place(x=1330,y=100)

        topbar_frame = ctk.CTkFrame(DateTime_Frame,height=7,width=145,fg_color="#88BD8E",corner_radius=20)
        topbar_frame.place(y=0)

        #Output
        CurrentTime_output=ctk.CTkLabel(DateTime_Frame,text="",text_color="#000000",font=Ouput_font,height=18,bg_color="#FFFFFF")
        CurrentTime_output.place(relx=.5,rely=.40,anchor="center")

        CurretDate_output = ctk.CTkLabel(DateTime_Frame,text="",text_color="#104E44",font=SubOutput_font,height=13,bg_color="#FFFFFF")
        CurretDate_output.place(relx=.5,rely=.65,anchor="center")

        def update_time():
            now = datetime.datetime.now()
            CurrentTime_output.configure(text=now.strftime("%H:%M"))
            CurretDate_output.configure(text=now.strftime("%m/%d/%y"))
            self.after(1000, update_time)

        update_time() 


    #Sign Out Frame
        SignOut_Frame =ctk.CTkFrame(self,height=155,width=400,fg_color="#FFFFFF",corner_radius=20)
        SignOut_Frame.place(x=1070,y=240)

        topbar_frame = ctk.CTkFrame(SignOut_Frame,height=15,width=400,fg_color="#AC1616",corner_radius=20)
        topbar_frame.place(y=0)

        Signout_Title=ctk.CTkLabel(SignOut_Frame,text="End Session",text_color="#000000",font=Title_font,height=18)
        Signout_Title.place(relx=.5,rely=.25,anchor="center")
        Signout_SubLabel = ctk.CTkLabel(SignOut_Frame,text="Log out from the system.",text_color="#104E44",font=SubLabel_font,height=10)
        Signout_SubLabel.place(relx=.5,rely=.4,anchor="center")

        Signout_image = ctk.CTkImage(Image.open("assets/ExitIcon.png"), size=(20,20))
        logout_button = ctk.CTkButton(SignOut_Frame, image=Signout_image,compound="left",text="Sign Out", width=260,height=37,text_color="#FFFFFF",fg_color="#AC1616",bg_color="#FFFFFF",font=Button_font,corner_radius=20, command=self.logout)
        logout_button.place(relx=.5,rely=.5,y=30,anchor="center")

    #Login Logs Frame
        LoginLogs_Frame = ctk.CTkFrame(self,height=320,width=400,fg_color="#FFFFFF",corner_radius=20)
        LoginLogs_Frame.place(x=1070,y=420)

        topbar_frame = ctk.CTkFrame(LoginLogs_Frame,height=15,width=400,fg_color="#1A374D",corner_radius=20)
        topbar_frame.place(y=0)

        LoginLogs_Title=ctk.CTkLabel(LoginLogs_Frame,text="Login Logs",text_color="#000000",font=Title_font,bg_color="#FFFFFF",height=18)
        LoginLogs_Title.place(x=30,y=30)
        LoginLogs_Sublabel = ctk.CTkLabel(LoginLogs_Frame,text="View your recent login activity.",text_color="#104E44",font=SubLabel_font,bg_color="#FFFFFF",height=10)
        LoginLogs_Sublabel.place(x=30,y=60)

        # Header frame for login logs table
        if self.role_manager.is_admin():
            # Admin view: User Full Name, Session, Date & Time
            login_logs_header_frame = ctk.CTkFrame(LoginLogs_Frame,
                                                  width=350,
                                                  height=25,
                                                  corner_radius=5,
                                                  fg_color="#1A374D")
            login_logs_header_frame.place(x=25, y=90)
            
            # Header labels for admin
            ctk.CTkLabel(login_logs_header_frame, text="User", 
                        font=("Merriweather Bold", 9), text_color="white").place(x=10, y=5)
            
            ctk.CTkLabel(login_logs_header_frame, text="Session", 
                        font=("Merriweather Bold", 9), text_color="white").place(x=120, y=5)
            
            ctk.CTkLabel(login_logs_header_frame, text="Date & Time", 
                        font=("Merriweather Bold", 9), text_color="white").place(x=220, y=5)
        else:
            # Staff view: Session, Date & Time only
            login_logs_header_frame = ctk.CTkFrame(LoginLogs_Frame,
                                                  width=350,
                                                  height=25,
                                                  corner_radius=5,
                                                  fg_color="#1A374D")
            login_logs_header_frame.place(x=25, y=90)
            
            # Header labels for staff
            ctk.CTkLabel(login_logs_header_frame, text="Session", 
                        font=("Merriweather Bold", 9), text_color="white").place(x=50, y=5)
            
            ctk.CTkLabel(login_logs_header_frame, text="Date & Time", 
                        font=("Merriweather Bold", 9), text_color="white").place(x=220, y=5)
        
        # Scrollable frame for login logs
        self.login_logs_scrollable_frame = ctk.CTkScrollableFrame(LoginLogs_Frame,
                                                                 width=350,
                                                                 height=200,
                                                                 corner_radius=0,
                                                                 fg_color="transparent")
        self.login_logs_scrollable_frame.place(x=25, y=120)

        # Load login logs table
        self.load_login_logs_table()

    #Developers Frame
        Developers_Frame=ctk.CTkFrame(self,height=200,width=400,fg_color="#FFFFFF",corner_radius=15)
        Developers_Frame.place(x=1070,y=775)

        leftbar_frame = ctk.CTkFrame(Developers_Frame,height=200,width=15,fg_color="#1A374D",corner_radius=20)
        leftbar_frame.place(x=0)

        LoginLogs_Title=ctk.CTkLabel(Developers_Frame,text="Contact Developers",text_color="#000000",font=SubTitle_font,bg_color="#FFFFFF",height=12)
        LoginLogs_Title.place(x=30,y=15)
        LoginLogs_Sublabel = ctk.CTkLabel(Developers_Frame,text="If you encounter any issues, feel free to contact the developers below.",text_color="#104E44",font=SubLabel_font,bg_color="#FFFFFF",height=10)
        LoginLogs_Sublabel.place(x=30,y=30)

        #Rhonnmark Heloerentino Information
        developer1 = ctk.CTkFrame(Developers_Frame,height=44,width=270,fg_color="#FFFFFF")
        developer1.place(relx=.1,rely=.25)

        developerIcon_image = ctk.CTkImage(Image.open("assets/DeveloperIcon.png"), size=(22,22))
        developerIcon=ctk.CTkLabel(developer1,image=developerIcon_image,text="")
        developerIcon.place(relx=.1,rely=.5,anchor="center")
        developer_name = ctk.CTkLabel(developer1,text="Rhonnmark L. Helorentino",text_color="#5B5B5B",font=DeveloperName_font,bg_color="#FFFFFF",height=10)
        developer_name.place(relx=.15,rely=.17)
        developer_name = ctk.CTkLabel(developer1,text="12121212121 | qrlhelorentino@tip.edu.ph",text_color="#000000",font=DeveloperContact_font,bg_color="#FFFFFF",height=10)
        developer_name.place(relx=.15,rely=.5)

        #Tristan Joe Lopez Information
        developer2 = ctk.CTkFrame(Developers_Frame,height=44,width=270,fg_color="#FFFFFF")
        developer2.place(relx=.1,rely=.50)

        developerIcon_image = ctk.CTkImage(Image.open("assets/DeveloperIcon.png"), size=(22,22))
        developerIcon=ctk.CTkLabel(developer2,image=developerIcon_image,text="")
        developerIcon.place(relx=.1,rely=.5,anchor="center")
        developer_name = ctk.CTkLabel(developer2,text="Tristan Joe A. Lopez",text_color="#5B5B5B",font=DeveloperName_font,bg_color="#FFFFFF",height=10)
        developer_name.place(relx=.15,rely=.17)
        developer_name = ctk.CTkLabel(developer2,text="12121212121 | tjalopez@tip.edu.ph",text_color="#000000",font=DeveloperContact_font,bg_color="#FFFFFF",height=10)
        developer_name.place(relx=.15,rely=.5)


        #Rod Vince Manzon
        developer3 = ctk.CTkFrame(Developers_Frame,height=44,width=270,fg_color="#FFFFFF")
        developer3.place(relx=.1,rely=.75)

        developerIcon_image = ctk.CTkImage(Image.open("assets/DeveloperIcon.png"), size=(22,22))
        developerIcon=ctk.CTkLabel(developer3,image=developerIcon_image,text="")
        developerIcon.place(relx=.1,rely=.5,anchor="center")
        developer_name = ctk.CTkLabel(developer3,text="Rod Vince B. Manzon",text_color="#5B5B5B",font=DeveloperName_font,bg_color="#FFFFFF",height=10)
        developer_name.place(relx=.15,rely=.17)
        developer_name = ctk.CTkLabel(developer3,text="09270542040 | qrvbmanzon@tip.edu.ph",text_color="#000000",font=DeveloperContact_font,bg_color="#FFFFFF",height=10)
        developer_name.place(relx=.15,rely=.5)

    def load_login_logs_table(self):
        """Load login logs and display in table based on user role"""
        try:
            # Clear existing data
            for widget in self.login_logs_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Get login logs based on role
            if self.role_manager.is_admin():
                login_logs = self.retrieve_login_logs('admin')
            else:
                login_logs = self.retrieve_login_logs('staff')
            
            if not login_logs:
                # Show "No data" message if no logs found
                no_data_frame = ctk.CTkFrame(self.login_logs_scrollable_frame,
                                           width=330,
                                           height=60,
                                           corner_radius=5,
                                           fg_color="#F8F9FA")
                no_data_frame.pack(fill="x", pady=20, padx=5)
                no_data_frame.pack_propagate(False)
                
                ctk.CTkLabel(no_data_frame, 
                           text="No login logs found",
                           font=("Poppins Regular", 10),
                           text_color="#666666").place(relx=0.5, rely=0.5, anchor="center")
                return
            
            # Display logs based on role
            for i, log_data in enumerate(login_logs[:10]):  # Show latest 10 logs
                # Create row frame with alternating colors
                row_frame = ctk.CTkFrame(self.login_logs_scrollable_frame,
                                       width=330,
                                       height=35,
                                       corner_radius=3,
                                       fg_color="#F8F9FA" if i % 2 == 0 else "#FFFFFF")
                row_frame.pack(fill="x", pady=1, padx=5)
                row_frame.pack_propagate(False)
                
                if self.role_manager.is_admin():
                    # Admin view: User Full Name, Session, Date & Time
                    full_name, login_time, logout_time = log_data
                    
                    # User name (shortened if too long)
                    user_name = str(full_name)[:12] + "..." if len(str(full_name)) > 12 else str(full_name)
                    name_label = ctk.CTkLabel(row_frame, text=user_name,
                                            font=("Poppins Regular", 8),
                                            text_color="#333333",
                                            width=100)
                    name_label.place(x=5, y=8)
                    
                    # Session status
                    if logout_time:
                        session_status = "Logged Out"
                        session_color = "#DC3545"  # Red
                    else:
                        session_status = "Logged In"
                        session_color = "#28A745"  # Green
                        
                    session_label = ctk.CTkLabel(row_frame, text=session_status,
                                                font=("Poppins Regular", 8),
                                                text_color=session_color,
                                                width=80)
                    session_label.place(x=110, y=8)
                    
                    # Date & Time (use login_time)
                    if login_time:
                        if hasattr(login_time, 'strftime'):
                            datetime_str = login_time.strftime("%m/%d %H:%M")
                        else:
                            datetime_str = str(login_time)[:11]  # Truncate if string
                    else:
                        datetime_str = "N/A"
                        
                    datetime_label = ctk.CTkLabel(row_frame, text=datetime_str,
                                                font=("Poppins Regular", 8),
                                                text_color="#333333",
                                                width=100)
                    datetime_label.place(x=200, y=8)
                    
                else:
                    # Staff view: Session, Date & Time only
                    login_time, logout_time = log_data
                    
                    # Session status
                    if logout_time:
                        session_status = "Logged Out"
                        session_color = "#DC3545"  # Red
                    else:
                        session_status = "Logged In"
                        session_color = "#28A745"  # Green
                        
                    session_label = ctk.CTkLabel(row_frame, text=session_status,
                                                font=("Poppins Regular", 9),
                                                text_color=session_color,
                                                width=120)
                    session_label.place(x=30, y=8)
                    
                    # Date & Time (use login_time)
                    if login_time:
                        if hasattr(login_time, 'strftime'):
                            datetime_str = login_time.strftime("%m/%d %H:%M")
                        else:
                            datetime_str = str(login_time)[:11]  # Truncate if string
                    else:
                        datetime_str = "N/A"
                        
                    datetime_label = ctk.CTkLabel(row_frame, text=datetime_str,
                                                font=("Poppins Regular", 9),
                                                text_color="#333333",
                                                width=120)
                    datetime_label.place(x=180, y=8)
                
        except Exception as e:
            print(f'Error loading login logs: {e}')
            # Show error message
            error_frame = ctk.CTkFrame(self.login_logs_scrollable_frame,
                                     width=330,
                                     height=60,
                                     corner_radius=5,
                                     fg_color="#FFE6E6")
            error_frame.pack(fill="x", pady=20, padx=5)
            error_frame.pack_propagate(False)
            
            error_label = ctk.CTkLabel(error_frame,
                                     text=f"Error loading login logs: {str(e)}",
                                     font=("Poppins Regular", 9),
                                     text_color="red")
            error_label.place(relx=0.5, rely=0.5, anchor="center")

    def retrieve_login_logs(self, access_type):
        """Modified version to return data instead of just printing"""
        try:
            connect = db()
            cursor = connect.cursor()
            username = login_shared_states.get('logged_username', None)

            if access_type.lower() == 'admin':
                cursor.execute("""
                    SELECT u.full_name, sl.login_time, sl.logout_time 
                    FROM sessions_log sl
                    JOIN users u ON sl.employee_Id = u.employee_id
                    ORDER BY sl.login_time DESC
                    LIMIT 15
                """)
                result = cursor.fetchall()
                print(f"Admin logs: {result}")
                return result

            elif access_type.lower() == 'staff':
                cursor.execute("""
                    SELECT sl.login_time, sl.logout_time 
                    FROM sessions_log sl
                    JOIN users u ON sl.employee_Id = u.employee_id
                    WHERE u.username = %s
                    ORDER BY sl.login_time DESC
                    LIMIT 15
                """, (username,))
                result = cursor.fetchall()
                print(f"Staff logs: {result}")
                return result

        except Exception as e:
            print('Error fetching retrieve login logs', e)
            return []

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

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

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=200, height=120, **kwargs)
        self.parent = parent
        self.visible = False
        self.place_forget()
        
        # Configure frame appearance
        self.configure(
            fg_color="white",
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0"
        )
        
        # Get user information
        self.user_info = self.get_user_info()
        
        # Setup UI
        self.setup_ui()
    
    def get_user_info(self):
        """Get current user information from database"""
        try:
            username = login_shared_states.get('logged_username', None)
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT full_name, role FROM users WHERE username = %s
            """, (username,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'full_name': result[0],
                    'role': result[1],
                    'username': username
                }
            else:
                return {
                    'full_name': 'Unknown User',
                    'role': 'Unknown',
                    'username': username or 'Unknown'
                }
                
        except Exception as e:
            print(f'Error fetching user info: {e}')
            return {
                'full_name': 'Error',
                'role': 'Error',
                'username': 'Error'
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()
    
    def setup_ui(self):
        """Setup the dropdown UI elements"""
        
        # User name label
        self.name_label = ctk.CTkLabel(
            self,
            text=self.user_info['full_name'],
            font=("Merriweather Bold", 14),
            text_color="#000000"
        )
        self.name_label.place(x=15, y=15)
        
        # Role label
        self.role_label = ctk.CTkLabel(
            self,
            text=self.user_info['role'],
            font=("Poppins Regular", 12),
            text_color="#666666"
        )
        self.role_label.place(x=15, y=40)
        
        # Separator line
        separator = ctk.CTkFrame(
            self,
            width=170,
            height=1,
            fg_color="#E0E0E0"
        )
        separator.place(x=15, y=65)
        
        # Logout button
        try:
            logout_img = ctk.CTkImage(
                light_image=Image.open("assets/ExitIcon.png"), 
                size=(16, 16)
            )
            self.logout_button = ctk.CTkButton(
                self,
                image=logout_img,
                text="Logout Account",
                compound="left",
                width=170,
                height=35,
                fg_color="#AC1616",
                hover_color="#8B0000",
                text_color="white",
                font=("Merriweather Sans", 12),
                corner_radius=8,
                command=self.logout
            )
        except:
            # Fallback if image fails to load
            self.logout_button = ctk.CTkButton(
                self,
                text="🚪 Logout Account",
                width=170,
                height=35,
                fg_color="#AC1616",
                hover_color="#8B0000",
                text_color="white",
                font=("Merriweather Sans", 12),
                corner_radius=8,
                command=self.logout
            )
        
        self.logout_button.place(x=15, y=75)
    
    def toggle(self):
        """Toggle settings frame visibility"""
        if self.visible:
            self.place_forget()
            self.visible = False
        else:
            # Position relative to the settings button (similar to notification frame)
            self.place(relx=0.85, rely=0.08)
            self.lift()
            self.visible = True
    
    def logout(self):
        """Handle logout functionality"""
        
        # Hide settings frame immediately
        self.place_forget()
        self.visible = False
        
        # Perform logout immediately without delay
        self.perform_logout()
    
    def perform_logout(self):
        """Perform the actual logout process"""
        connect = None
        cursor = None
        
        try:
            username = login_shared_states.get('logged_username', None)
            connect = db()
            cursor = connect.cursor()

            # Update logout time in sessions table
            cursor.execute("""
                UPDATE sessions
                SET logout_time = NOW()
                WHERE employee_id = (SELECT employee_id FROM users WHERE username = %s)
            """, (username,))
            connect.commit()

            # Get session data for logging
            cursor.execute("""
                SELECT s.employee_id, s.login_time, s.logout_time
                FROM sessions s
                JOIN users u ON s.employee_id = u.employee_id
                WHERE u.username = %s
            """, (username,))
            
            session_data = cursor.fetchone()
            
            # Consume any remaining results
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            
            if session_data:
                employee_id, login_time, logout_time = session_data
                print("✅ Successfully logged out")

                # Insert into sessions log
                cursor.execute("""
                    INSERT INTO sessions_log(employee_id, login_time, logout_time, login_duration)
                    VALUES(%s, %s, %s, TIMEDIFF(%s, %s))
                """, (employee_id, login_time, logout_time, logout_time, login_time))
                connect.commit()
                
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass

            # Delete from active sessions
            cursor.execute("""
                DELETE FROM sessions
                WHERE employee_id = (SELECT employee_id FROM users WHERE username = %s)
            """, (username,))
            connect.commit()
            
            try:
                while cursor.nextset():
                    pass
            except:
                pass

            # Clear login shared states
            login_shared_states.clear()
            
            print("🔄 Navigating to login page...")
            
            # Navigate back to login page
            self.navigate_to_login()
            
        except Exception as e:
            print(f"❌ Error with logout: {e}")
            import traceback
            traceback.print_exc()
            # Even if there's an error, still try to go to login
            self.navigate_to_login()
        finally:
            # Proper cleanup
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if connect:
                try:
                    connect.close()
                except:
                    pass
    
    def navigate_to_login(self):
        """Navigate back to login page smoothly"""
        try:
            # Method 1: Try to find navigation function in parent hierarchy
            current_widget = self.parent
            max_depth = 10  # Prevent infinite loop
            depth = 0
            
            while current_widget and depth < max_depth:
                # Check for shared_state with navigate function
                if hasattr(current_widget, 'shared_state'):
                    shared_state = current_widget.shared_state
                    if isinstance(shared_state, dict) and 'navigate' in shared_state:
                        print("✅ Found navigation function, going to LoginPage")
                        shared_state['navigate']('LoginPage')
                        return
                
                # Check for direct navigate method
                if hasattr(current_widget, 'navigate'):
                    print("✅ Found direct navigate method")
                    current_widget.navigate('LoginPage')
                    return
                
                # Move up the hierarchy
                current_widget = getattr(current_widget, 'parent', None) or getattr(current_widget, 'master', None)
                depth += 1
            
            # Method 2: Try to restart the application properly
            print("🔄 Attempting application restart...")
            import subprocess
            import sys
            import os
            
            # Get the root window
            root = self.winfo_toplevel()
            
            # Start new instance
            if hasattr(sys, 'argv') and sys.argv:
                # Get the main script path
                script_path = sys.argv[0]
                if script_path.endswith('.py'):
                    subprocess.Popen([sys.executable, script_path])
                else:
                    # If running from exe or other
                    subprocess.Popen([script_path])
            
            # Close current instance
            root.after(500, lambda: (root.quit(), root.destroy()))
            
        except Exception as e:
            print(f"❌ Error navigating to login: {e}")
            # Final fallback - just close gracefully
            try:
                root = self.winfo_toplevel()
                root.quit()
                root.destroy()
            except:
                import sys
                sys.exit()