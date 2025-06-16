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
from components.input_supply import CTkMessageBox, EditStockWindow, QuantityUsedLogsWindow, SupplyWindow
from components.state import login_shared_states
from backend.crud import retrieve_form_data, db_connection
from datetime import datetime
from customtkinter import CTkInputDialog
import datetime
import shutil
import os
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import font_manager as fm


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

        # Initialize graph canvases
        self.most_used_canvas = None
        self.yesterday_canvas = None
        self.pie_chart_canvas = None  

        # Initialize patient count variables
        self.total_patients = 0
        self.active_patients = 0
        self.inactive_patients = 0

        def get_name():
            # Commented out backend database call
            # username = login_shared_states.get('logged_username', None)

            # try:
            #     connect = db()
            #     cursor = connect.cursor()

            #     cursor.execute("""
            #         SELECT full_name FROM users WHERE username = %s
            #     """, (username,))

            #     full_name = cursor.fetchone()[0]

            #     first_name = full_name.split()[0]

            #     return first_name, full_name

            # except Exception as e:
            #     print('Error retrieving user full name ', e)
            # finally:
            #     cursor.close()
            #     connect.close()

            # Static values for testing
            full_name = "User"
            first_name = "User"

            return first_name, full_name

        first_name, full_name = get_name()

        # Setup UI
        self.setup_ui(first_name, full_name)
        
        # Load initial graphs and patient data
        self.show_overall_usage()
        self.show_yesterday_usage()
        self.load_patient_data_and_pie_chart()
        
    try:
        connect = db()
        cursor = connect.cursor()

        name = 'toni'

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
        """, (f'%{name}%',))

        search_result = cursor.fetchall()
        
        for search in search_result:
            if search[5] == 'patient':
                print(f'{search [0]} is a patient!')
            elif search[5] == 'supply':
                print(f'{search[0]} is a supply!')

    except Exception as e:
        print('Error searching', e)

    finally:
        cursor.close()
        connect.close()

    def load_patient_data_and_pie_chart(self):
        """Load patient data and create pie chart"""
        try:
            connect = db()
            cursor = connect.cursor()

            # Update inactive patients based on usage
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

                print('active:', self.active_patients)
                print('inactive:', self.inactive_patients)
                print('total patient:', self.total_patients)

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
        """Show yesterday's usage chart in container"""
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

            # Clear existing canvas if it exists
            if self.yesterday_canvas:
                self.yesterday_canvas.get_tk_widget().destroy()

            # Create new figure
            fig = Figure(figsize=(5.5, 3.5), dpi=100)
            ax = fig.add_subplot(111)
            
            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            # Create bar chart
            if not df_yesterday.empty:
                    ax.bar(df_yesterday['item_name'], df_yesterday['total_used'], color='#C0DABE')
                    ax.tick_params(axis='x', pad=10)
                    ax.margins(y=0.15)    
                    for label in ax.get_xticklabels() + ax.get_yticklabels():
                        label.set_fontproperties(tick_font)
                        label.set_fontsize(11)
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
            self.yesterday_canvas.get_tk_widget().place(x=20, y=100, width=560, height=320)

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

    def setup_ui(self, first_name, full_name):
        """Setup all the UI elements"""
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

        self.name_label = ctk.CTkLabel(self.navbar, text=f"{first_name}!", text_color="black", font=("Arial", 30, "bold"))
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

        self.namev2_label = ctk.CTkLabel(self.navbar, text=full_name, text_color="black", font=("Arial", 30, "bold"))
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
            most_used_icon_btn = ctk.CTkButton(
                self.most_used_frame,
                image=most_used_icon,
                text="",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.show_overall_usage
            )
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

        # Backup Information Frame
        self.backup_frame = ctk.CTkFrame(
            self,
            width=410,
            height=200,
            fg_color="white",
            corner_radius=20
        )
        self.backup_frame.place(x=710, y=610)

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

        # Recent Patient Frame
        self.fourth_frame = ctk.CTkFrame(
            self,
            width=410,
            height=200,
            fg_color="white",
            corner_radius=20
        )
        self.fourth_frame.place(x=710, y=845)

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
        # Clean up matplotlib canvases
        if self.most_used_canvas:
            self.most_used_canvas.get_tk_widget().destroy()
        if self.yesterday_canvas:
            self.yesterday_canvas.get_tk_widget().destroy()
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

        # Sort By 
        self.sort_label = ctk.CTkLabel(
            self.button_frame,
            text="SORT BY:",
            font=ctk.CTkFont("Arial", 14, "bold")
        )
        self.sort_label.pack(side="left", padx=(10, 5))

        self.sort_dropdown = ctk.CTkComboBox(
            self.button_frame,
            values=["Patient ID", "Patient Name", "Age", "Gender", "Type of Access", 'Date Registered'],
            font=ctk.CTkFont("Arial", 14),
            width=150,
            height=35,
            bg_color="white"
        )
        self.sort_dropdown.pack(side="left", padx=(0, 10))

        def sort_by_func(sort_type):
            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT * FROM patient_list
                    ORDER BY %s
                """, (sort_type,))

                sorting_result = cursor.fetchall()
                return sorting_result

            except Exception as e:
                print(f'Error sorting by {sort_type}', e)
            finally:
                cursor.close()
                connect.close()
        
        patient_id_sort = sort_by_func('patient_id')
        patient_name_sort = sort_by_func ('patient_name')
        age_sort = sort_by_func('age')
        gender_sort = sort_by_func('gender')
        access_sort = sort_by_func('access_type')
        date_sort = sort_by_func('date_registered')
 
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
        self.quantity_used_window = QuantityUsedLogsWindow(self.master)

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

    def refresh_after_update(self):
        """Called after a patient is updated to refresh the table and view"""
        print("🔄 Refreshing patient data after update...")
        
        # Store current patient_id if we were viewing details
        current_patient_id = self.patient_id_value.cget("text") if hasattr(self, 'patient_id_value') else None
        
        # Refresh the table
        self.refresh_table()
        
        # FIXED: Trigger automatic refresh of home page pie chart
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
            # FIXED: Automatically refresh after any patient input operation
            self.refresh_after_update()

        input_window.protocol("WM_DELETE_WINDOW", on_close)
        self.wait_window(input_window)
        self.refresh_table()
        self.enable_buttons()
        
        # FIXED: Additional refresh after input window closes
        self.refresh_after_update()

    def refresh_table(self):
        self.detailed_info_frame.place_forget() 
        self.button_frame.place(x=20, y=50, anchor="nw") 
        self.navbar.pack(fill="x", side="top")
        self.table_frame.place(x=20, y=150, relwidth=0.95, relheight=0.8) 
        """Refresh the patient table with latest data"""
        try:
            # Make sure we're in table view
            self.show_table_view()
            
            # Clear existing table data
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Fetch fresh data and populate table
            fresh_data = self.fetch_patient_data()
            self.populate_table(fresh_data)
            
            print("✅ Patient table refreshed with latest data")
            
        except Exception as e:
            print(f"❌ Error refreshing table: {e}")                

    def enable_buttons(self):
        self.add_button.configure(state="normal")
        self.edit_button_detailed.configure(state="normal")

    def disable_buttons(self):
        self.add_button.configure(state="disabled")
        self.edit_button_detailed.configure(state="disabled")

    def open_add_window(self, data=None):
        self.disable_buttons()
        self.open_input_window(PatientInfoWindow, data)

    def refresh_after_update(self):
        """Called after a patient is updated to refresh the table and view"""
        print("🔄 Refreshing patient data after update...")
        
        # Store current patient_id if we were viewing details
        current_patient_id = self.patient_id_value.cget("text") if hasattr(self, 'patient_id_value') else None
        
        # Refresh the table
        self.refresh_table()
        
        # If we were viewing a patient's details, refresh that view too
        if current_patient_id:
            self.show_detailed_info(current_patient_id)
        
        print("✅ Patient data refreshed successfully!")

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

        # Sort By 
        self.sort_label = ctk.CTkLabel(
            self.button_frame,
            text="SORT BY:",
            font=ctk.CTkFont("Arial", 14, "bold")
        )
        self.sort_label.pack(side="left", padx=(10, 5))

        self.sort_dropdown = ctk.CTkComboBox(
            self.button_frame,
            values=["Item ID", 'Item Name', 'Category', 'Remaining Stock', 'Restock Date', 'Date Registered'],
            font=ctk.CTkFont("Arial", 14),
            width=150,
            height=35,
            bg_color="white"
        )
        self.sort_dropdown.pack(side="left", padx=(0, 10))

        def sort_by_func(sort_type):
            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT * FROM supply
                    ORDER BY %s
                """, (sort_type,))

                sorting_result = cursor.fetchall()
                return sorting_result

            except Exception as e:
                print(f'Error sorting by {sort_type}', e)
            finally:
                cursor.close()
                connect.close()
        
        item_id_sort = sort_by_func('item_id')
        item_name_sort = sort_by_func('item_name')
        category = sort_by_func('category')
        current_stock_sort = sort_by_func('current_stock')
        restock_date_sort = sort_by_func('restock_date')
        register_date_sort = sort_by_func('date_registered')

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

        # Table Frame
        self.table_frame = ctk.CTkFrame(self, fg_color="#1A374D", border_width=2, border_color="black")

        tree_container = ctk.CTkFrame(self.table_frame, fg_color="black")
        tree_container.pack(fill="both", expand=True, padx=1, pady=1)

        # Updated columns - removed restock_date
        columns = ("item_id", "item_name", "category", "current_stock", "date_registered")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        self.tree.pack(side="left", fill="both", expand=True)

        # Updated headers - removed restock date
        headers = [
            ("ITEM ID", 120),
            ("ITEM NAME", 180),
            ("CATEGORY", 140),
            ("REMAINING STOCK", 150),
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

        # Remaining Stock Label and Output
        self.currentstock_Label = ctk.CTkLabel(supply_info_frame, text="Remaining Stock", font=label_font)
        self.currentstock_Label.place(x=520,y=100)
        self.currentstock_Output = ctk.CTkLabel(supply_info_frame, text="", font=output_font)
        self.currentstock_Output.place(x=520,y=130)

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

        self.Capacity_Output = ctk.CTkLabel(storage_meter_frame, text="", font=label_font)
        self.Capacity_Output.place(x=850,y=180)

        # Edit Stock Frame
        self.Edit_Stock_Frame = ctk.CTkFrame(self.Main_Supply_Frame,
                width=400,
                height=200,
                fg_color="white",
                corner_radius=20)
        self.Edit_Stock_Frame.place(x=50, y=600)

        self.Top_bar = ctk.CTkFrame(self.Edit_Stock_Frame,
                width=400,
                height=20,
                fg_color="#68EDC6")
        self.Top_bar.place(y=0)

        # Edit Stock Button
        self.Edit_Stock_Button = ctk.CTkButton(
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
        self.Edit_Stock_Button.place(x=130, y=50)

        # Quantity Used Button
        self.Quantity_Used_Button = ctk.CTkButton(
            self.Edit_Stock_Frame,
            text="Quantity Used",
            width=150,
            height=50,
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
        self.Reminder_Frame.place(x=50, y=820)

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
                width=950,
                height=380,
                fg_color="white",
                corner_radius=20)
        self.Restock_Logs_Frame.place(x=600, y=690)

        # Top bar for restock logs frame
        self.Restock_Logs_Top_bar = ctk.CTkFrame(self.Restock_Logs_Frame,
                width=950,
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
                SELECT item_id, item_name, category, current_stock, 
                    date_registered, restock_quantity, average_daily_usage, average_weekly_usage, 
                    average_monthly_usage, delivery_time_days, stock_level_status, max_supply
                FROM supply
            """)
            return cursor.fetchall()
        except Exception as e:
            print("Error fetching supply data:", e)
            return []

    def populate_table(self, data):
        """Populate the table with supply data (excluding restock_date)"""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insert new data - only include relevant columns for display
        for row in data:
            # Only show: item_id, item_name, category, current_stock, date_registered
            display_row = (row[0], row[1], row[2], row[3], row[4])
            self.tree.insert("", "end", values=display_row)

    def on_row_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            supply_data = self.tree.item(item, 'values')
            
            # Get full data from database using item_id
            try:
                connect = db()
                cursor = connect.cursor()
                cursor.execute("""
                    SELECT item_id, item_name, category, current_stock, 
                        date_registered, restock_quantity, average_daily_usage, average_weekly_usage, 
                        average_monthly_usage, delivery_time_days, stock_level_status, max_supply
                    FROM supply WHERE item_id = %s
                """, (supply_data[0],))
                
                full_data = cursor.fetchone()
                if full_data:
                    self.selected_supply_data = {
                        'item_id': full_data[0],
                        'item_name': full_data[1],
                        'category': full_data[2],
                        'current_stock': full_data[3],
                        'date_registered': full_data[4],
                        'restock_quantity': full_data[5],
                        'average_daily_usage': full_data[6] if full_data[6] else 0,
                        'average_weekly_usage': full_data[7] if full_data[7] else 0,
                        'average_monthly_usage': full_data[8] if full_data[8] else 0,
                        'delivery_time_days': full_data[9] if full_data[9] else 0,
                        'stock_level_status': full_data[10],
                        'max_supply': full_data[11] if full_data[11] else 0
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
        """Handle row click to show detailed info"""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            supply_data = self.tree.item(item_id, 'values')
            supply_id = supply_data[0]
            print("Supply ID:", supply_id)
            
            self.selected_supply_id = supply_id
            
            # Get full data including max_supply for detailed view
            try:
                connect = db()
                cursor = connect.cursor()
                cursor.execute("""
                    SELECT item_id, item_name, category, current_stock, 
                        date_registered, restock_quantity, average_daily_usage, average_weekly_usage, 
                        average_monthly_usage, delivery_time_days, stock_level_status, max_supply
                    FROM supply WHERE item_id = %s
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
        
        # Get data safely
        current_stock = supply_data[3] if len(supply_data) > 3 else 0
        date_registered = supply_data[4] if len(supply_data) > 4 and supply_data[4] else "N/A"
        average_weekly_usage = supply_data[7] if len(supply_data) > 7 and supply_data[7] else "N/A"
        delivery_time_days = supply_data[9] if len(supply_data) > 9 and supply_data[9] else "N/A"
        max_supply = supply_data[11] if len(supply_data) > 11 and supply_data[11] else 0
        
        # Display current stock as remaining stock
        self.currentstock_Output.configure(text=str(current_stock))
        self.Registered_Date_Output.configure(text=date_registered)
        self.Average_Weekly_Usage_Output.configure(text=str(average_weekly_usage))
        self.Delivery_Time_Output.configure(text=str(delivery_time_days))
        
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

        # Calculate stock percentage for status based on max_supply
        stock_percentage = current_stock_val / max_supply_val if max_supply_val > 0 else 0

        # Updated color scheme: Critical=Red, Low=Orange, Good=Green, Excellent=Light Blue
        if stock_percentage == 0:
            status_text = "Out of Stock"
            status_color = "#8B0000"  # Dark Red
            progress_color = "#8B0000"
            remaining_color = "#8B0000"
        elif stock_percentage <= 0.25:  # 25% or less of max capacity - CRITICAL
            status_text = "Critical Stock Level"
            status_color = "#FF0000"  # Red
            progress_color = "#FF0000"
            remaining_color = "#FF0000"
        elif stock_percentage <= 0.50:  # 26-50% of max capacity - LOW
            status_text = "Low Stock Level"
            status_color = "#FF8C00"  # Orange
            progress_color = "#FF8C00"
            remaining_color = "#FF8C00"
        elif stock_percentage <= 0.80:  # 51-80% of max capacity - GOOD
            status_text = "Good Stock Level"
            status_color = "#28A745"  # Green
            progress_color = "#28A745"
            remaining_color = "#28A745"
        else:  # Above 80% of max capacity - EXCELLENT
            status_text = "Excellent Stock Level"
            status_color = "#17A2B8"  # Light Blue/Cyan
            progress_color = "#17A2B8"
            remaining_color = "#17A2B8"

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
                SELECT item_id, item_name, category, current_stock, 
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
                    'date_registered': updated_data[4],
                    'restock_quantity': updated_data[5],
                    'average_daily_usage': updated_data[6] if updated_data[6] else 0,
                    'average_weekly_usage': updated_data[7] if updated_data[7] else 0,
                    'average_monthly_usage': updated_data[8] if updated_data[8] else 0,
                    'delivery_time_days': updated_data[9] if updated_data[9] else 0,
                    'stock_level_status': updated_data[10],
                    'max_supply': updated_data[11]
                }
                
                # Refresh the detailed view display
                self.show_detailed_info(updated_data)
                
            cursor.close()
            connect.close()
            
        except Exception as e:
            print("Error refreshing detailed view:", e)

class ReportPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#EFEFEF")

        label_font = ("Merriweather Sans Bold", 9)
        Title_font = ("Merriweather Bold", 13)
        NumberOuput_font = ("Poppins Regular" ,19)
        DateOutput_font = ("Poppins Regular" ,15)
        SubLabel_font = ("Merriweather Sans Light" ,9)
        SubSubLabel_font = ("Poppins Regular" ,9)

        # Initialize graph canvases
        self.low_stock_canvas = None
        self.critical_stock_canvas = None

    #Patient Report
        PatientReport_frame = ctk.CTkFrame(self,
                                        width=245,
                                        height=335,
                                        corner_radius=20,
                                        fg_color="#FFFFFF",
                                        bg_color="transparent")
        PatientReport_frame.place(x=120,y=75)
        left_bar = ctk.CTkFrame(PatientReport_frame,width=20,height=335,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        PateintReport_title = ctk.CTkLabel(PatientReport_frame,font=Title_font,text="Patient Report")
        PateintReport_title.place(x=43,y=17)

        #Active
        Activepatient_BG = ctk.CTkFrame(PatientReport_frame,width=145,height=62.5,corner_radius=10,fg_color="#88BD8E",bg_color="transparent")
        Activepatient_BG.place(x=55,y=65)

         #Output for Active User
        PatientIcon_image = ctk.CTkImage(Image.open("assets/PatientIcon.png"), size=(15,15))
        ActivePatientCount = ctk.CTkLabel(Activepatient_BG,font=NumberOuput_font,text="58",text_color="#fFFFFF",fg_color="transparent",image=PatientIcon_image,compound='right')
        ActivePatientCount.place(relx=.5,rely=.45,anchor="center")
        PatientCount_SubLabel = ctk.CTkLabel(Activepatient_BG,font=SubLabel_font,text="Patient",text_color="#FfFFFF",fg_color="transparent",height=10)
        PatientCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        ActiveLabel_bg = ctk.CTkFrame(PatientReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB")
        ActiveLabel_bg.place(x=58,y=140)
        ActiveLabel = ctk.CTkLabel(ActiveLabel_bg,font=label_font,text="Active",text_color="#104E44",bg_color="transparent",height=10)
        ActiveLabel.place(relx=.5,rely=.5,anchor="center")

        #InActive
        Inactivepatient_BG = ctk.CTkFrame(PatientReport_frame,width=145,height=62.5,corner_radius=10,fg_color="#F25B5B",bg_color="transparent")
        Inactivepatient_BG.place(x=55,y=197)

        #Output for Inactive User
        PatientIcon_image = ctk.CTkImage(Image.open("assets/PatientIcon.png"), size=(15,15))
        InactivePatientCount = ctk.CTkLabel(Inactivepatient_BG,font=NumberOuput_font,text="58",text_color="#fFFFFF",fg_color="transparent",image=PatientIcon_image,compound='right')
        InactivePatientCount.place(relx=.5,rely=.45,anchor="center")
        PatientCount_SubLabel = ctk.CTkLabel(Inactivepatient_BG,font=SubLabel_font,text="Patient",text_color="#FfFFFF",fg_color="transparent",height=10)
        PatientCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        InactiveLabel_bg = ctk.CTkFrame(PatientReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB")
        InactiveLabel_bg.place(x=58,y=270)
        InactiveLabel = ctk.CTkLabel(InactiveLabel_bg,font=label_font,text="Inactive",text_color="#104E44",bg_color="transparent",height=10)
        InactiveLabel.place(relx=.5,rely=.4,anchor="center")

#------------------------------------------------------------------------------------------------------------------------------------------
    #Active Patient Table
        Activepatient_frame = ctk.CTkFrame(self,
                                           width=515,
                                           height=335,
                                           corner_radius=20,
                                           fg_color="#FFFFFF",
                                           bg_color="transparent")
        Activepatient_frame.place(x=400,y=75)
       


    #Inactive Patient Table
        Inactivepatient_frame = ctk.CTkFrame(self,
                                             width=515,
                                             height=335,
                                             corner_radius=20,
                                             fg_color="#FFFFFF",
                                             bg_color="transparent")
        Inactivepatient_frame.place(x=965,y=75)
        


#------------------------------------------------------------------------------------------------------------------------------------------

    #Supply Report
        SupplyReport_frame = ctk.CTkFrame(self,
                                          width=675,
                                          height=165,
                                          corner_radius=20,
                                          fg_color="#FFFFFF",
                                          bg_color="transparent")
        SupplyReport_frame.place(x=120,y=445)
        left_bar = ctk.CTkFrame(SupplyReport_frame,width=20,height=165,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        SupplyReport_title = ctk.CTkLabel(SupplyReport_frame,font=Title_font,text="Supply Report")
        SupplyReport_title.place(x=43,y=17)

        SupplyCount_BG = ctk.CTkFrame(SupplyReport_frame,width=155,height=55,corner_radius=10,fg_color="#818C7D",bg_color="transparent")
        SupplyCount_BG.place(x=70,y=65)

        #Output Supply Count
        SupplyCountIcon_image = ctk.CTkImage(Image.open("assets/SupplyCountIcon.png"), size=(15,15))
        SupplyCount = ctk.CTkLabel(SupplyCount_BG,font=NumberOuput_font,text="68",text_color="#fFFFFF",fg_color="transparent",image=SupplyCountIcon_image,compound='right')
        SupplyCount.place(relx=.5,rely=.45,anchor="center")
        SupplyCount_SubLabel = ctk.CTkLabel(SupplyCount_BG,font=SubLabel_font,text="Items",text_color="#FfFFFF",fg_color="transparent",height=10)
        SupplyCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        SupplyCountLabel_bg = ctk.CTkFrame(SupplyReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        SupplyCountLabel_bg.place(x=77,y=125)
        SupplyCountLabel = ctk.CTkLabel(SupplyCountLabel_bg,font=label_font,text="Supply Count",text_color="#104E44",bg_color="transparent",height=10)
        SupplyCountLabel.place(relx=.5,rely=.4,anchor="center")

        Lowstock_BG = ctk.CTkFrame(SupplyReport_frame,width=155,height=55,corner_radius=10,fg_color="#D08B40",bg_color="transparent")
        Lowstock_BG.place(x=270,y=65)

        #Output Low Stock
        LowStockIcon_image = ctk.CTkImage(Image.open("assets/LowStockIcon.png"), size=(15,15))
        LowStockCount = ctk.CTkLabel(Lowstock_BG,font=NumberOuput_font,text="68",text_color="#fFFFFF",fg_color="transparent",image=LowStockIcon_image,compound='right')
        LowStockCount.place(relx=.5,rely=.45,anchor="center")
        LowStockCount_SubLabel = ctk.CTkLabel(Lowstock_BG,font=SubLabel_font,text="Items",text_color="#FfFFFF",fg_color="transparent",height=10)
        LowStockCount_SubLabel.place(relx=.5,rely=.7,anchor="center")


        LowStockLabel_bg = ctk.CTkFrame(SupplyReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        LowStockLabel_bg.place(x=277,y=125)
        LowStockLabel = ctk.CTkLabel(LowStockLabel_bg,font=label_font,text="Low Stock",text_color="#104E44",bg_color="transparent",height=10)
        LowStockLabel.place(relx=.5,rely=.4,anchor="center")


        CriticalStock_BG = ctk.CTkFrame(SupplyReport_frame,width=155,height=55,corner_radius=10,fg_color="#AC1616",bg_color="transparent")
        CriticalStock_BG.place(x=470,y=65)

        #Output Critical Stock
        CriticalStockIcon_image = ctk.CTkImage(Image.open("assets/CriticalStockIcon.png"), size=(15,15))
        CriticalStockCount = ctk.CTkLabel(CriticalStock_BG,font=NumberOuput_font,text="68",text_color="#fFFFFF",fg_color="transparent",image=CriticalStockIcon_image,compound='right')
        CriticalStockCount.place(relx=.5,rely=.45,anchor="center")
        CriticalStockCount_SubLabel = ctk.CTkLabel(CriticalStock_BG,font=SubLabel_font,text="Items",text_color="#FfFFFF",fg_color="transparent",height=10)
        CriticalStockCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        CriticalStockLabel_bg = ctk.CTkFrame(SupplyReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        CriticalStockLabel_bg.place(x=477,y=125)
        CriticalStockLabel = ctk.CTkLabel(CriticalStockLabel_bg,font=label_font,text="Critical Stock",text_color="#104E44",bg_color="transparent",height=10)
        CriticalStockLabel.place(relx=.5,rely=.4,anchor="center")

#------------------------------------------------------------------------------------------------------------------------------------------

    #Backup Report

        BackupReport_frame = ctk.CTkFrame(self,
                                        width=485,
                                        height=165,
                                        corner_radius=20,
                                        fg_color="#FFFFFF",
                                        bg_color="transparent")
        BackupReport_frame.place(x=825,y=445)
        left_bar = ctk.CTkFrame(BackupReport_frame,width=20,height=165,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        BackupReport_title = ctk.CTkLabel(BackupReport_frame,font=Title_font,text="Backup Report")
        BackupReport_title.place(x=43,y=17)

        BackupCount_BG = ctk.CTkFrame(BackupReport_frame,width=155,height=55,corner_radius=10,fg_color="#818C7D",bg_color="transparent")
        BackupCount_BG.place(x=70,y=65)

        #Output Backup Count
        BackupIcon_image = ctk.CTkImage(Image.open("assets/BackupIcon.png"), size=(15,15))
        BackupCount = ctk.CTkLabel(BackupCount_BG,font=NumberOuput_font,text="68",text_color="#fFFFFF",fg_color="transparent",image=BackupIcon_image,compound='right')
        BackupCount.place(relx=.5,rely=.45,anchor="center")
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
        RecentBackupDate = ctk.CTkLabel(MostRecentBackup_BG,font=DateOutput_font,text="2025-06-13",text_color="#FFFFFF",fg_color="transparent",image=CalendarIcon_image,compound='right')
        RecentBackupDate.place(relx=.5,rely=.45,anchor="center")
        RecentBackup_SubLabel = ctk.CTkLabel(MostRecentBackup_BG,font=SubLabel_font,text="yyyy - mm - dd",text_color="#FFFFFF",fg_color="transparent",height=10)
        RecentBackup_SubLabel.place(relx=.5,rely=.7,anchor="center")

        MostRecentlabel_bg = ctk.CTkFrame(BackupReport_frame,width=185,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        MostRecentlabel_bg.place(x=270,y=125)
        MostRecentLabel = ctk.CTkLabel(MostRecentlabel_bg,font=label_font,text="Most Recent Backup",text_color="#104E44",bg_color="transparent",height=0)
        MostRecentLabel.place(relx=.5,rely=.4,anchor="center")

#------------------------------------------------------------------------------------------------------------------------------------------

    #Discrepancies
        Discrepancies_frame = ctk.CTkFrame(self,
                                           width=145,
                                           height=165,
                                           corner_radius=20,
                                           fg_color="#FFFFFF",
                                           bg_color="transparent")
        Discrepancies_frame.place(x=1340,y=445)

    #Low Stock Level items
        self.LowOnStock_frame = ctk.CTkFrame(self,
                                        width=525,
                                        height=390,
                                        corner_radius=20,
                                        fg_color="#FFFFFF",
                                        bg_color="transparent")
        self.LowOnStock_frame.place(x=120,y=645)

        # Top bar for Low Stock Frame
        low_stock_top_bar = ctk.CTkFrame(
            self.LowOnStock_frame,
            width=525,
            height=20,
            fg_color="#D08B40",
            corner_radius=0
        )
        low_stock_top_bar.place(x=0, y=0)

        LowonStock_title = ctk.CTkLabel(self.LowOnStock_frame,font=Title_font,text="Low Stock Level Items")
        LowonStock_title.place(x=20,y=40)

        # Refresh icon for Low Stock
        try:
            low_stock_refresh_icon = ctk.CTkImage(light_image=Image.open("assets/refresh.png"), size=(20, 20))
            low_stock_refresh_btn = ctk.CTkButton(
                self.LowOnStock_frame,
                image=low_stock_refresh_icon,
                text="",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.low_stock_graph
            )
            low_stock_refresh_btn.place(x=220, y=40)
        except:
            low_stock_refresh_btn = ctk.CTkButton(
                self.LowOnStock_frame,
                text="🔄",
                font=("Arial", 14),
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.low_stock_graph
            )
            low_stock_refresh_btn.place(x=220, y=40)

        LowonStock_sublabel = ctk.CTkLabel(self.LowOnStock_frame,font=SubSubLabel_font,text="Current Data")
        LowonStock_sublabel.place(x=20,y=65)

    #Critical Stock Level Items
        self.CriticalStock_frame = ctk.CTkFrame(self,
                                           width=525,
                                           height=390,
                                           corner_radius=20,
                                           fg_color="#FFFFFF",
                                           bg_color="transparent")
        self.CriticalStock_frame.place(x=680,y=645)

        # Top bar for Critical Stock Frame
        critical_stock_top_bar = ctk.CTkFrame(
            self.CriticalStock_frame,
            width=525,
            height=20,
            fg_color="#AC1616",
            corner_radius=0
        )
        critical_stock_top_bar.place(x=0, y=0)

        CriticalStock_title = ctk.CTkLabel(self.CriticalStock_frame,font=Title_font,text="Critical Stock Level Items")
        CriticalStock_title.place(x=20,y=40)

        # Refresh icon for Critical Stock
        try:
            critical_stock_refresh_icon = ctk.CTkImage(light_image=Image.open("assets/refresh.png"), size=(20, 20))
            critical_stock_refresh_btn = ctk.CTkButton(
                self.CriticalStock_frame,
                image=critical_stock_refresh_icon,
                text="",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.critical_stock_graph
            )
            critical_stock_refresh_btn.place(x=250, y=40)
        except:
            critical_stock_refresh_btn = ctk.CTkButton(
                self.CriticalStock_frame,
                text="🔄",
                font=("Arial", 14),
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="#f0f0f0",
                command=self.critical_stock_graph
            )
            critical_stock_refresh_btn.place(x=250, y=40)

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
        NotificationReport_frame.place(x=1240,y=645)
        left_bar = ctk.CTkFrame(NotificationReport_frame,width=20,height=390,fg_color="#1A374D",bg_color="transparent")
        left_bar.place(x=0)

        NotificationReport_title = ctk.CTkLabel(NotificationReport_frame,font=Title_font,text="Notification Report")
        NotificationReport_title.place(x=43,y=17)

        Stocklevels_BG = ctk.CTkFrame(NotificationReport_frame,width=155,height=55,corner_radius=10,fg_color="#538A8C",bg_color="transparent")
        Stocklevels_BG.place(x=55,y=65)

         #Output for Stock Levels
        StockLevelIcon_image = ctk.CTkImage(Image.open("assets/LowStockIcon.png"), size=(15,15))
        StockLevelCount = ctk.CTkLabel(Stocklevels_BG,font=NumberOuput_font,text="68",text_color="#fFFFFF",fg_color="transparent",image=StockLevelIcon_image,compound='right')
        StockLevelCount.place(relx=.5,rely=.45,anchor="center")
        StockCount_SubLabel = ctk.CTkLabel(Stocklevels_BG,font=SubLabel_font,text="Notifications",text_color="#FfFFFF",fg_color="transparent",height=10)
        StockCount_SubLabel.place(relx=.5,rely=.7,anchor="center")

        StocklevelsLabel_bg = ctk.CTkFrame(NotificationReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        StocklevelsLabel_bg.place(x=62,y=125)
        StockLevelsLabel = ctk.CTkLabel(StocklevelsLabel_bg,font=label_font,text="Stock Levels",text_color="#104E44",bg_color="transparent",height=11)
        StockLevelsLabel.place(relx=.5,rely=.4,anchor="center")


        PatientInformation_BG = ctk.CTkFrame(NotificationReport_frame,width=155,height=55,corner_radius=10,fg_color="#57CFBB",bg_color="transparent")
        PatientInformation_BG.place(x=55,y=175)

         #Output for Patient Information
        PatientNotificationIcon_image = ctk.CTkImage(Image.open("assets/PatientNotificationIcon.png"), size=(15,15))
        PatientNotificationCount = ctk.CTkLabel(PatientInformation_BG,font=NumberOuput_font,text="68",text_color="#fFFFFF",bg_color="#57CFBB",image=PatientNotificationIcon_image,compound='right')
        PatientNotificationCount.place(relx=.5,rely=.45,anchor="center")
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
        RecentNotificationCount = ctk.CTkLabel(RecentBackup_BG,font=NumberOuput_font,text="68",text_color="#fFFFFF",bg_color="#AB8C6F",image=BackupNotificationIcon_image,compound='right')
        RecentNotificationCount.place(relx=.5,rely=.45,anchor="center")
        BackupNotification_SubLabel = ctk.CTkLabel(RecentBackup_BG,font=SubLabel_font,text="Notifications",text_color="#FfFFFF",fg_color="transparent",height=10)
        BackupNotification_SubLabel.place(relx=.5,rely=.7,anchor="center")


        RecentBackuplabel_bg = ctk.CTkFrame(NotificationReport_frame,width=140,height=25,corner_radius=10,fg_color="#FFFFFF",bg_color="transparent",border_width=1.5,border_color="#BBBBBB",)
        RecentBackuplabel_bg.place(x=62,y=340)
        RecentBackuplabel = ctk.CTkLabel(RecentBackuplabel_bg,font=label_font,text="Back Up",text_color="#104E44",bg_color="transparent",height=11)
        RecentBackuplabel.place(relx=.5,rely=.4,anchor="center")

        # Load initial graphs
        self.low_stock_graph()
        self.critical_stock_graph()

    def low_stock_graph(self):
        """Show low stock items chart in LowOnStock_frame"""
        try:
            connect = db()
            query = """
                SELECT item_name, current_stock FROM supply
                WHERE stock_level_status = 'Low Stock Level'
                ORDER BY current_stock ASC
            """

            df = pd.read_sql(query, connect)

            # Clear existing canvas if it exists
            if self.low_stock_canvas:
                self.low_stock_canvas.get_tk_widget().destroy()

            # Create new figure
            fig = Figure(figsize=(5.2, 3.0), dpi=100)
            ax = fig.add_subplot(111)
            
            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            if not df.empty:
                # Create bar chart
                bars = ax.bar(df['item_name'], df['current_stock'], color='#D08B40')
                ax.tick_params(axis='x', pad=10)
                ax.margins(y=0.15)
                
                # Set font for labels
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontproperties(tick_font)
                    label.set_fontsize(9)
                
                # Rotate x-axis labels if too many items
                if len(df) > 5:
                    ax.tick_params(axis='x', rotation=45)
                    
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
            self.low_stock_canvas.get_tk_widget().place(x=20, y=95, width=485, height=280)

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

    def critical_stock_graph(self):
        """Show critical stock items chart in CriticalStock_frame"""
        try:
            connect = db()
            query = """
                SELECT item_name, current_stock FROM supply
                WHERE stock_level_status = 'Critical Stock Level'
                ORDER BY current_stock ASC
            """

            df = pd.read_sql(query, connect)

            # Clear existing canvas if it exists
            if self.critical_stock_canvas:
                self.critical_stock_canvas.get_tk_widget().destroy()

            # Create new figure
            fig = Figure(figsize=(5.2, 3.0), dpi=100)
            ax = fig.add_subplot(111)

            tick_font = fm.FontProperties(fname='font/Inter_18pt-Italic.ttf')

            if not df.empty:
                # Create bar chart with red color for critical items
                bars = ax.bar(df['item_name'], df['current_stock'], color='#AC1616')
                ax.tick_params(axis='x', pad=10)
                ax.margins(y=0.15)
                
                # Set font for labels
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontproperties(tick_font)
                    label.set_fontsize(9)
                
                # Rotate x-axis labels if too many items
                if len(df) > 5:
                    ax.tick_params(axis='x', rotation=45)
                    
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
            self.critical_stock_canvas.get_tk_widget().place(x=20, y=95, width=485, height=280)

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

        # Choose Destination Button Function
        def choose_destination_action():
            print("Clicked Choose destination")

        # Choose Destination Button 
        ChooseDestination_Button = ctk.CTkButton(Maintenance_MainFrame,
                                                bg_color="transparent",
                                                fg_color="#6C757D",
                                                hover_color="#5A6268",
                                                width=150,
                                                height=35,
                                                corner_radius=15,
                                                text="Choose Destination",
                                                text_color="white",
                                                cursor="hand2",
                                                command=choose_destination_action,
                                                font=("Merriweather Bold", 12))
        ChooseDestination_Button.place(x=800, y=50)

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

        #last/next backup date/time
        def retrieve_backup_logs(cursor, column):
            try:
                #pag isipan ko pa
                # cursor.execute("""
                #     SELECT %s FROM backup_logs
                #     wWHERE employee_id = %s                
                # """, (column, identifier))
                cursor.execute("""
                    SELECT %s FROM backup_logs                
                """, (column,))

                col_list = column.split(',')
                col_length = len(col_list)

                if col_length <=2:
                    log_result = cursor.fetchone()
                    return log_result

                else:
                    logs_result = cursor.fetchall()
                    return logs_result

            except Exception as e:
                print('Error retrieveng backup logs', e)

        def set_backup_schedule(cursor, date, time):
            try:
                cursor.execute("""
                    UPDATE backup_logs
                    SET next_date = %s, next_time = %s        
                """, {date, time})
            except Exception as e:
                print('Error appointing backup schedule', e)

        def manual_backup_action():
            update_last_backup_time
            print("Clicked Manual Backup")

        # Schedule Backup Frame Function
        def schedule_backup_action():
            # Create Schedule Backup Frame
            global schedule_backup_frame
            schedule_backup_frame = ctk.CTkFrame(self,
                                               bg_color="transparent",
                                               fg_color="#FFFFFF",
                                               width=1000,
                                               height=450,
                                               corner_radius=20)
            schedule_backup_frame.place(x=100, y=180)
            
            # Left bar for Schedule Frame
            leftbar_frame = ctk.CTkFrame(schedule_backup_frame,
                                       bg_color="transparent",
                                       fg_color="#1A374D",
                                       width=25,
                                       height=450,
                                       corner_radius=20)
            leftbar_frame.place(x=0)
            
            # Title
            title_label = ctk.CTkLabel(schedule_backup_frame,
                                     bg_color="transparent",
                                     text="Date and Time",
                                     text_color="black",
                                     font=Title_font)
            title_label.place(x=100, y=50)
            
            # Subtitle
            subtitle_label = ctk.CTkLabel(schedule_backup_frame,
                                        bg_color="transparent",
                                        text="Select the schedule for the next backup.",
                                        text_color="black",
                                        font=SubTitle_font)
            subtitle_label.place(x=100, y=100)
            
            # Date Label
            date_label = ctk.CTkLabel(schedule_backup_frame,
                                    bg_color="transparent",
                                    text="Date",
                                    text_color="black",
                                    font=("Merriweather Sans bold", 15))
            date_label.place(x=100, y=180)
            
            # Date Entry Field 
            from tkcalendar import DateEntry
            self.entry_date = DateEntry(schedule_backup_frame, 
                                      width=18, 
                                      font=("Merriweather light", 12), 
                                      bg="white", 
                                      date_pattern="yyyy-MM-dd", 
                                      state="normal")
            self.entry_date.place(x=100, y=220, height=25)
            
            # Time Label
            time_label = ctk.CTkLabel(schedule_backup_frame,
                                    bg_color="transparent",
                                    text="Time",
                                    text_color="black",
                                    font=("Merriweather Sans bold", 15))
            time_label.place(x=100, y=280)
            
            # Time Entry Fields 
            # Hour Entry
            self.entry_hour = ctk.CTkEntry(schedule_backup_frame,
                                         width=50,
                                         height=25,
                                         placeholder_text="HH",
                                         font=("Merriweather light", 12))
            self.entry_hour.place(x=100, y=320)
            
            # Colon Label
            colon_label = ctk.CTkLabel(schedule_backup_frame,
                                     bg_color="transparent",
                                     text=":",
                                     text_color="black",
                                     font=("Merriweather Sans bold", 15))
            colon_label.place(x=160, y=320)
            
            # Minute Entry
            self.entry_minute = ctk.CTkEntry(schedule_backup_frame,
                                           width=50,
                                           height=25,
                                           placeholder_text="MM",
                                           font=("Merriweather light", 12))
            self.entry_minute.place(x=180, y=320)
            
            # Back Button 
            def back_to_maintenance():
                schedule_backup_frame.place_forget()
            
            # Back Button
            back_button = ctk.CTkButton(schedule_backup_frame,
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
            back_button.place(x=100, y=380)
            
            # Select Button Function
            def select_schedule():
                print(f"Selected schedule")
            
            # Select Button 
            select_button = ctk.CTkButton(schedule_backup_frame,
                                        bg_color="transparent",
                                        fg_color="#00C88D",
                                        hover_color="#00B07B",
                                        width=120,
                                        height=40,
                                        corner_radius=15,
                                        text="Select",
                                        text_color="white",
                                        cursor="hand2",
                                        command=select_schedule,
                                        font=("Merriweather Bold", 14))
            select_button.place(x=850, y=380)

        
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
                                            command=schedule_backup_action,
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