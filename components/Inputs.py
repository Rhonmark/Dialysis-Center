import tkinter as tk
from tkinter import ttk, PhotoImage
from tkcalendar import DateEntry
from datetime import date, datetime
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from components.buttons import CTkButtonSelectable
from components.textfields_patients import TextField_Patients
from components.state import login_shared_states

from backend.connector import db_connection as db
from backend.crud import submit_form_creation, submit_form_subcreation, submit_form_extra, retrieve_form_data

class BaseWindow(ctk.CTkToplevel): 
    def __init__(self, parent, title, next_window=None, previous_window=None):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.geometry("1300x700")
        self.overrideredirect(True)
        self.center_window()
        self.next_window = next_window
        self.previous_window = previous_window

        self.main_frame = ctk.CTkFrame(self, fg_color="white",corner_radius=0)
        self.main_frame.pack(expand=True, fill="both", padx=0.5, pady=0.5)

        button_font = ("Merriweather Bold", 15)

        self.sidebar = ctk.CTkFrame(self.main_frame, width=30, fg_color="#1A374D", corner_radius=25, bg_color="transparent")
        self.sidebar.pack(side="left", fill="y")

        exit_img = Image.open("assets/exit.png")
        self.exit_icon = CTkImage(exit_img, size=(30, 30))

        self.btn_exit = ctk.CTkButton(self, height=25,width=25,image=self.exit_icon,text="",fg_color="#FFFFFF",hover_color="#FFFFFF",bg_color="#FFFFFF", border_width=0, command=self.destroy)
        self.btn_exit.place(x=1225, y=20)  

        if self.next_window:
            self.btn_next = ctk.CTkButton(
                self, 
                text="Next",
                text_color="#FFFFFF" ,
                font=button_font,
                command=self.open_next, 
                width=200, 
                height=50,
                corner_radius=20,
                fg_color="#00C88D", 
                hover_color="#1A374D",
                bg_color="#FFFFFF"
            )
            self.btn_next.place(x=1020, y=600)

        if not self.next_window: 
            # Check if we're in edit mode 
            if hasattr(self, 'edit_mode') and self.edit_mode:
                self.btn_update = ctk.CTkButton(
                    self, 
                    text="Update",  
                    text_color="#FFFFFF" ,
                    font=button_font,
                    command=self.update_form, 
                    width=200, 
                    height=50,
                    corner_radius=20,
                    fg_color="#00C88D", 
                    hover_color="#1A374D",
                    bg_color="#FFFFFF"
                )
                self.btn_update.place(x=1020, y=600)
            else:
                self.btn_submit = ctk.CTkButton(
                    self, 
                    text="Submit",  
                    text_color="#FFFFFF" ,
                    font=button_font,
                    command=self.submit_form, 
                    width=200, 
                    height=50,
                    corner_radius=20,
                    fg_color="#1A374D", 
                    hover_color="#00C88D",
                    bg_color="#FFFFFF"  
                )
                self.btn_submit.place(x=1020, y=600)

        if self.previous_window:
            self.back_icon = PhotoImage(file="assets/back.png" )
            self.btn_back = tk.Button(self, image=self.back_icon, bd=0, bg="white", activebackground="white", command=self.go_back)
            self.btn_back.place(x=50, y=25)

    def go_back(self):
        # Save current form data before going back
        if hasattr(self, 'save_current_data'):
            self.save_current_data()
        
        self.destroy()  
        if self.previous_window:
            self.previous_window(self.parent, self.data if hasattr(self, "data") else None)

    def open_next(self, data=None):
        if self.next_window:
            self.withdraw()  
            new_window = self.next_window(self.master, data)
            new_window.center_window()  
            new_window.grab_set()  
            new_window.focus_force()
            new_window.wait_window()  
            self.destroy()  

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x700+{x}+{y}")

class PatientInfoWindow(BaseWindow): 
    def __init__(self, parent, data):
    

        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None
        
        super().__init__(parent, "Patient Information", next_window=ContactPersonWindow, previous_window=None)
        self.data = data if data else {}

        label_font = ("Merriweather Sans Bold",15)
        entry_font = ("Merriweather Sans", 12)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

        

        title_text = "Edit Patient Information" if self.edit_mode else "Patient Information"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), text_color="black", bg_color="white").place(x=90, y=60)

        
       # Last Name Field
        ctk.CTkLabel(self, text="Last Name", font=label_font, fg_color="white", text_color="black").place(x=120, y=150)
        self.entry_lastname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_lastname.place(x=120, y=200)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=205, y=150)  
        create_underline(120, 230, 180)

        # First Name Field
        ctk.CTkLabel(self, text="First Name", font=label_font, fg_color="white", text_color="black").place(x=420, y=150)
        self.entry_firstname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_firstname.place(x=420, y=200)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=510, y=150)  
        create_underline(420, 230, 180)

        # Middle Name Field (No required - no change needed)
        ctk.CTkLabel(self, text="Middle Name", font=label_font, fg_color="white", text_color="black").place(x=720, y=150)
        self.entry_middlename = ctk.CTkEntry(self, width=150, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_middlename.place(x=720, y=200)
        create_underline(720, 230, 150)

        # Status Field
        ctk.CTkLabel(self, text="Status", font=label_font, fg_color="white", text_color="black").place(x=120, y=270)
        self.status_var = tk.StringVar(value="active")
        ctk.CTkRadioButton(self, text="Active", variable=self.status_var, value="active", font=entry_font, fg_color="#00C88D", text_color="black", bg_color="white", radiobutton_width=20, radiobutton_height=20).place(x=120, y=320)
        ctk.CTkRadioButton(self, text="Inactive", variable=self.status_var, value="inactive", font=entry_font, fg_color="#00C88D", text_color="black", bg_color="white", radiobutton_width=20, radiobutton_height=20).place(x=200, y=320)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=175, y=270)  
        create_underline(120, 350, 160)

        # Type of Access Field
        ctk.CTkLabel(self, text="Type of Access", font=label_font, fg_color="white", text_color="black").place(x=420, y=270)
        self.access_options = ["L AVF", "R AVF", "L AVG", "R AVG", "L CVC", "R CVC", "L PDC", "R PDC"]
        self.entry_access = ctk.CTkComboBox(self, values=self.access_options, width=180, height=30, button_color="#00C88D",font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", state="readonly")
        self.entry_access.place(x=420, y=320)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=540, y=270)  
        create_underline(420, 350, 180)

        # Birthdate Field
        ctk.CTkLabel(self, text="Birthdate", font=label_font, fg_color="white", text_color="black").place(x=720, y=270)
        self.entry_birthdate = DateEntry(self, width=12, font=entry_font, bg="white", date_pattern="yyyy-MM-dd", state="normal")
        self.entry_birthdate.place(x=720, y=320, height=25)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=795, y=270)  
        create_underline(720, 345, 180)

        # Age Field
        ctk.CTkLabel(self, text="Age", font=label_font, fg_color="white", text_color="black").place(x=1020, y=270)
        self.entry_age = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_age.place(x=1020, y=320)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=1055, y=270)  
        create_underline(1020, 350, 180)

        # Gender Field
        ctk.CTkLabel(self, text="Gender", font=label_font, fg_color="white", text_color="black").place(x=120, y=390)
        self.entry_gender = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_gender.place(x=120, y=440)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=185, y=390)  
        create_underline(120, 470, 180)

        # Height Field
        ctk.CTkLabel(self, text="Height", font=label_font, fg_color="white", text_color="black").place(x=420, y=390)
        self.entry_height = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_height.place(x=420, y=440)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=485, y=390)  
        create_underline(420, 470, 180)

        # Civil Status Field
        ctk.CTkLabel(self, text="Civil Status", font=label_font, fg_color="white", text_color="black").place(x=720, y=390)
        self.entry_civil_status = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_civil_status.place(x=720, y=440)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=815, y=390)  
        create_underline(720, 470, 180)

        # Religion Field
        ctk.CTkLabel(self, text="Religion", font=label_font, fg_color="white", text_color="black").place(x=1020, y=390)
        self.entry_religion = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_religion.place(x=1020, y=440)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=1095, y=390)  
        create_underline(1020, 470, 180)

        # Complete Address Field
        ctk.CTkLabel(self, text="Complete Address", font=label_font, fg_color="white", text_color="black").place(x=120, y=510)
        self.entry_address = ctk.CTkEntry(self, width=500, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_address.place(x=120, y=560)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=265, y=510)  
        create_underline(120, 590, 500)
            
        
        self.entry_birthdate.bind("<<DateEntrySelected>>", self.update_age)

        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        try:
            if self.data.get("patient_last_name"):
                self.entry_lastname.delete(0, "end")
                self.entry_lastname.insert(0, self.data.get("patient_last_name"))
                
            if self.data.get("patient_first_name"):
                self.entry_firstname.delete(0, "end")
                self.entry_firstname.insert(0, self.data.get("patient_first_name"))
                
            if self.data.get("patient_middle_name"):
                self.entry_middlename.delete(0, "end")
                self.entry_middlename.insert(0, self.data.get("patient_middle_name"))
                
            if self.data.get("patient_status"):
                self.status_var.set(self.data.get("patient_status"))
                
            if self.data.get("patient_access"):
                self.entry_access.set(self.data.get("patient_access"))
                
            if self.data.get("patient_birthdate"):
                from datetime import datetime
                birthdate = datetime.strptime(self.data.get("patient_birthdate"), "%Y-%m-%d").date()
                self.entry_birthdate.set_date(birthdate)
                
            if self.data.get("patient_age"):
                self.entry_age.delete(0, "end")
                self.entry_age.insert(0, self.data.get("patient_age"))
                
            if self.data.get("patient_gender"):
                self.entry_gender.delete(0, "end")
                self.entry_gender.insert(0, self.data.get("patient_gender"))
                
            if self.data.get("patient_height"):
                self.entry_height.delete(0, "end")
                self.entry_height.insert(0, self.data.get("patient_height"))
                
            if self.data.get("patient_civil_status"):
                self.entry_civil_status.delete(0, "end")
                self.entry_civil_status.insert(0, self.data.get("patient_civil_status"))
                
            if self.data.get("patient_religion"):
                self.entry_religion.delete(0, "end")
                self.entry_religion.insert(0, self.data.get("patient_religion"))
                
            if self.data.get("patient_address"):
                self.entry_address.delete(0, "end")
                self.entry_address.insert(0, self.data.get("patient_address"))
        
        except Exception as e:
            print(f"❌ Error restoring form data: {e}")

    def save_current_data(self):
        try:
            self.data["patient_last_name"] = self.entry_lastname.get()
            self.data["patient_first_name"] = self.entry_firstname.get()
            self.data["patient_middle_name"] = self.entry_middlename.get()
            self.data["patient_status"] = self.status_var.get()
            self.data["patient_access"] = self.entry_access.get()
            self.data["patient_birthdate"] = self.entry_birthdate.get_date().strftime("%Y-%m-%d")
            self.data["patient_age"] = self.entry_age.get()
            self.data["patient_gender"] = self.entry_gender.get()
            self.data["patient_height"] = self.entry_height.get()
            self.data["patient_civil_status"] = self.entry_civil_status.get()
            self.data["patient_religion"] = self.entry_religion.get()
            self.data["patient_address"] = self.entry_address.get()
            
        except Exception as e:
            print(f"❌ Error saving current data: {e}")

    def populate_fields(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()
                
                cursor.execute("""
                    SELECT pi.last_name, pi.first_name, pi.middle_name, pi.status, 
                        pi.access_type, pi.birthdate, pi.age, pi.gender, pi.height, 
                        pi.civil_status, pi.religion, pi.address
                    FROM patient_info pi
                    WHERE pi.patient_id = %s
                """, (self.patient_id,))
                
                patient_data = cursor.fetchone()
                
                if patient_data:
                    if patient_data[0]:
                        self.entry_lastname.delete(0, "end")
                        self.entry_lastname.insert(0, patient_data[0])
                    
                    if patient_data[1]:
                        self.entry_firstname.delete(0, "end")
                        self.entry_firstname.insert(0, patient_data[1])
                    
                    if patient_data[2]:
                        self.entry_middlename.delete(0, "end")
                        self.entry_middlename.insert(0, patient_data[2])
                    
                    if patient_data[3]:
                        self.status_var.set(patient_data[3])
                    
                    if patient_data[4]:
                        self.entry_access.set(patient_data[4])
                    
                    if patient_data[5]:
                        self.entry_birthdate.set_date(patient_data[5])
                    
                    if patient_data[6]:
                        self.entry_age.delete(0, "end")
                        self.entry_age.insert(0, str(patient_data[6]))
                    
                    if patient_data[7]:
                        self.entry_gender.delete(0, "end")
                        self.entry_gender.insert(0, patient_data[7])
                    
                    if patient_data[8]:
                        self.entry_height.delete(0, "end")
                        self.entry_height.insert(0, patient_data[8])
                    
                    if patient_data[9]:
                        self.entry_civil_status.delete(0, "end")
                        self.entry_civil_status.insert(0, patient_data[9])
                    
                    if patient_data[10]:
                        self.entry_religion.delete(0, "end")
                        self.entry_religion.insert(0, patient_data[10])
                    
                    if patient_data[11]:
                        self.entry_address.delete(0, "end")
                        self.entry_address.insert(0, patient_data[11])
                
                cursor.close()
                connect.close()
                
            except Exception as e:
                print(f"Error populating fields: {e}")

    def update_age(self, event):
        try:
            birthdate = self.entry_birthdate.get_date()
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            self.entry_age.set_real_value(str(age))
        except Exception as e:
            print(f"Error calculating age: {e}")
    
    def open_next(self, data=None):
        try:
            self.data["patient_last_name"] = self.entry_lastname.get().lower().capitalize()
            self.data["patient_first_name"] = self.entry_firstname.get().lower().capitalize()
            self.data["patient_middle_name"] = self.entry_middlename.get().lower().capitalize()
            self.data["patient_status"] = self.status_var.get().capitalize()
            self.data["patient_access"] = self.entry_access.get()
            self.data["patient_birthdate"] = self.entry_birthdate.get_date().strftime("%Y-%m-%d")  
            self.data["patient_age"] = self.entry_age.get()
            self.data["patient_gender"] = self.entry_gender.get().lower().capitalize()
            self.data["patient_height"] = self.entry_height.get()
            self.data["patient_civil_status"] = self.entry_civil_status.get().lower().capitalize()
            self.data["patient_religion"] = self.entry_religion.get().lower().capitalize()
            self.data["patient_address"] = self.entry_address.get().lower().capitalize()
            
            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 1 input: ", e)

class ContactPersonWindow(BaseWindow):
    def __init__(self, parent, data=None):
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Contact Information", next_window=RelativeInfoWindow, previous_window=PatientInfoWindow)
        self.data = data if data else {}

        Title_font = ("Merriweather bold", 25)
        label_font = ("Merriweather Sans Bold",15)
        entry_font = ("Merriweather Sans", 13)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

       

        title_text = "Edit Contact Information" if self.edit_mode else "Contact Information"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), text_color="black", bg_color="white").place(x=90, y=100)


        # Last Name Field
        ctk.CTkLabel(self, text="Last Name", font=label_font, fg_color="white", text_color="black").place(x=120, y=190)
        self.entry_lastname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_lastname.place(x=120, y=240)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=205, y=190)  
        create_underline(120, 270, 180)

        # First Name Field
        ctk.CTkLabel(self, text="First Name", font=label_font, fg_color="white", text_color="black").place(x=420, y=190)
        self.entry_firstname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_firstname.place(x=420, y=240)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=510, y=190)  
        create_underline(420, 270, 180)

        # Middle Name Field
        ctk.CTkLabel(self, text="Middle Name", font=label_font, fg_color="white", text_color="black").place(x=720, y=190)
        self.entry_middlename = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_middlename.place(x=720, y=240)
        create_underline(720, 270, 180)

        # Contact Number Field
        ctk.CTkLabel(self, text="Contact Number", font=label_font, fg_color="white", text_color="black").place(x=120, y=310)
        self.entry_contact = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_contact.place(x=120, y=360)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=250, y=310)  
        create_underline(120, 390, 180)

        # Relationship to the Patient Field
        ctk.CTkLabel(self, text="Relationship to the Patient", font=label_font, fg_color="white", text_color="black").place(x=420, y=310)
        self.entry_relationship = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_relationship.place(x=420, y=360)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=635, y=310)  
        create_underline(420, 390, 180)

        # Complete Address Field
        ctk.CTkLabel(self, text="Complete Address", font=label_font, fg_color="white", text_color="black").place(x=120, y=430)
        self.entry_address = ctk.CTkEntry(self, width=500, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_address.place(x=120, y=480)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=265, y=430)  
        create_underline(120, 510, 500)


        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        try:
            if self.data.get("contact_last_name"):
                self.entry_lastname.set_real_value(self.data.get("contact_last_name"))
                
            if self.data.get("contact_first_name"):
                self.entry_firstname.set_real_value(self.data.get("contact_first_name"))
                
            if self.data.get("contact_middle_name"):
                self.entry_middlename.set_real_value(self.data.get("contact_middle_name"))
                
            if self.data.get("contact_number"):
                self.entry_contact.set_real_value(self.data.get("contact_number"))
                
            if self.data.get("relationship_to_patient"):
                self.entry_relationship.set_real_value(self.data.get("relationship_to_patient"))
                
            if self.data.get("contact_address"):
                self.entry_address.set_real_value(self.data.get("contact_address"))
            
        except Exception as e:
            print(f"❌ Error restoring contact form data: {e}")

    def save_current_data(self):
        try:
            self.data["contact_last_name"] = self.entry_lastname.get().lower().capitalize()
            self.data["contact_first_name"] = self.entry_firstname.get().lower().capitalize()
            self.data["contact_middle_name"] = self.entry_middlename.get().lower().capitalize()
            self.data["contact_number"] = self.entry_contact.get()
            self.data["relationship_to_patient"] = self.entry_relationship.get().lower().capitalize()
            self.data["contact_address"] = self.entry_address.get().lower().capitalize()
            
        except Exception as e:
            print(f"❌ Error saving current contact data: {e}")
    
    def populate_fields(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()
                
                cursor.execute("""
                    SELECT cp.last_name, cp.first_name, cp.middle_name, 
                        cp.contact_number, cp.relationship, cp.address
                    FROM patient_contact cp
                    WHERE cp.patient_id = %s
                """, (self.patient_id,))
                
                contact_data = cursor.fetchone()
                
                if contact_data:
                    self.entry_lastname.set_real_value(contact_data[0])
                    self.entry_firstname.set_real_value(contact_data[1])
                    self.entry_middlename.set_real_value(contact_data[2])
                    self.entry_contact.set_real_value(contact_data[3])
                    self.entry_relationship.set_real_value(contact_data[4])
                    self.entry_address.set_real_value(contact_data[5])
                
                cursor.close()
                connect.close()
                
            except Exception as e:
                print(f"Error populating fields: {e}")

    def open_next(self, data=None):
        try:
            self.data["contact_last_name"] = self.entry_lastname.get().lower().capitalize()
            self.data["contact_first_name"] = self.entry_firstname.get().lower().capitalize()
            self.data["contact_middle_name"] = self.entry_middlename.get().lower().capitalize()
            self.data["contact_number"] = self.entry_contact.get()
            self.data["relationship_to_patient"] = self.entry_relationship.get().lower().capitalize()
            self.data["contact_address"] = self.entry_address.get().lower().capitalize()

            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 2 input: ", e)
        
class RelativeInfoWindow(BaseWindow):
    def __init__(self, parent, data=None):
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Relative Information", next_window=PhilHealthInfoWindow, previous_window=ContactPersonWindow)
        self.data = data if data else {}


        label_font = ("Merriweather Sans Bold",15)
        entry_font = ("Merriweather Sans", 13)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)


        title_text = "Edit Relative Information" if self.edit_mode else "Relative Information"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), text_color="black", bg_color="white").place(x=90, y=100)

        # Last Name
        ctk.CTkLabel(self, text="Last Name", font=label_font, fg_color="white", text_color="black").place(x=120, y=190)
        self.entry_lastname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_lastname.place(x=120, y=240)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=205, y=190)  
        create_underline(120, 270, 180)

        # First Name Field
        ctk.CTkLabel(self, text="First Name", font=label_font, fg_color="white", text_color="black").place(x=420, y=190)
        self.entry_firstname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_firstname.place(x=420, y=240)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=510, y=190)  
        create_underline(420, 270, 180)

        # Middle Name Field
        ctk.CTkLabel(self, text="Middle Name", font=label_font, fg_color="white", text_color="black").place(x=720, y=190)
        self.entry_middlename = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_middlename.place(x=720, y=240)
        create_underline(720, 270, 180)

        # Contact Number Field
        ctk.CTkLabel(self, text="Contact Number", font=label_font, fg_color="white", text_color="black").place(x=120, y=310)
        self.entry_contact = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_contact.place(x=120, y=360)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=250, y=310)  
        create_underline(120, 390, 180)

        # Complete Address Field
        ctk.CTkLabel(self, text="Complete Address", font=label_font, fg_color="white", text_color="black").place(x=120, y=430)
        self.entry_address = ctk.CTkEntry(self, width=500, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_address.place(x=120, y=480)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=265, y=430)  
        create_underline(120, 510, 500)


        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        try:
            if self.data.get("relative_last_name"):
                self.entry_lastname.insert(0, self.data.get("relative_last_name"))
                
            if self.data.get("relative_first_name"):
                self.entry_firstname.insert(0, self.data.get("relative_first_name"))
                
            if self.data.get("relative_middle_name"):
                self.entry_middlename.insert(0, self.data.get("relative_middle_name"))
                
            if self.data.get("relative_contact_number"):
                self.entry_contact.insert(0, self.data.get("relative_contact_number"))
                
            if self.data.get("relative_address"):
                self.entry_address.insert(0, self.data.get("relative_address"))
            
        except Exception as e:
            print(f"❌ Error restoring relative form data: {e}")

    def save_current_data(self):
        try:
            self.data["relative_last_name"] = self.entry_lastname.get().lower().capitalize()
            self.data["relative_first_name"] = self.entry_firstname.get().lower().capitalize()
            self.data["relative_middle_name"] = self.entry_middlename.get().lower().capitalize()
            self.data["relative_contact_number"] = self.entry_contact.get()
            self.data["relative_address"] = self.entry_address.get().lower().capitalize()
            
        except Exception as e:
            print(f"❌ Error saving current relative data: {e}")

    def populate_fields(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT r.last_name, r.first_name, r.middle_name, 
                        r.contact_number, r.address
                    FROM patient_relative r
                    WHERE r.patient_id = %s
                """, (self.patient_id,))

                relative_data = cursor.fetchone()

                if relative_data:
                    self.entry_lastname.insert(0, relative_data[0])
                    self.entry_firstname.insert(0, relative_data[1])
                    self.entry_middlename.insert(0, relative_data[2])
                    self.entry_contact.insert(0, relative_data[3])
                    self.entry_address.insert(0, relative_data[4])

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")

    def open_next(self, data=None):
        try:
            self.data["relative_last_name"] = self.entry_lastname.get().lower().capitalize()
            self.data["relative_first_name"] = self.entry_firstname.get().lower().capitalize()
            self.data["relative_middle_name"] = self.entry_middlename.get().lower().capitalize()
            self.data["relative_contact_number"] = self.entry_contact.get()
            self.data["relative_address"] = self.entry_address.get().lower().capitalize()

            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 3 input: ", e)

class PhilHealthInfoWindow(BaseWindow):
    def __init__(self, parent, data=None):
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "PhilHealth and Other Info", next_window=PatientHistory1Window, previous_window=RelativeInfoWindow)
        self.data = data if data else {}

        label_font = ("Merriweather Sans Bold",15)
        entry_font = ("Merriweather Sans", 13)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

        title_text = "Edit PhilHealth and Other Info" if self.edit_mode else "PhilHealth and Other Info"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), text_color="black", bg_color="white").place(x=90, y=100)

        # PhilHealth Number Field
        ctk.CTkLabel(self, text="PhilHealth Number", font=label_font, fg_color="white", text_color="black").place(x=120, y=190)
        self.entry_philhealth = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_philhealth.place(x=120, y=240)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=275, y=190)
        create_underline(120, 270, 180)

        # Membership Field
        ctk.CTkLabel(self, text="Membership", font=label_font, fg_color="white", text_color="black").place(x=420, y=190)
        self.entry_membership = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_membership.place(x=420, y=240)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=525, y=190)
        create_underline(420, 270, 180)

        # PWD Radio Buttons
        ctk.CTkLabel(self, text="PWD", font=label_font, fg_color="white", text_color="black").place(x=120, y=310)
        self.pwd_var = ctk.IntVar()
        ctk.CTkRadioButton(self, text="Yes", variable=self.pwd_var, value=1, font=entry_font, text_color="black", fg_color="#00C88D", bg_color="white").place(x=120, y=350)
        ctk.CTkRadioButton(self, text="No", variable=self.pwd_var, value=0, font=entry_font, text_color="black", fg_color="#00C88D", bg_color="white").place(x=180, y=350)

        # PWD ID Number Field
        ctk.CTkLabel(self, text="PWD ID Number", font=label_font, fg_color="white", text_color="black").place(x=420, y=310)
        self.entry_pwd_id = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_pwd_id.place(x=420, y=360)
        create_underline(420, 390, 180)

        # Senior Radio Buttons
        ctk.CTkLabel(self, text="Senior", font=label_font, fg_color="white", text_color="black").place(x=120, y=440)
        self.senior_var = ctk.IntVar()
        ctk.CTkRadioButton(self, text="Yes", variable=self.senior_var, value=1, font=entry_font, text_color="black", fg_color="#00C88D", bg_color="white").place(x=120, y=480)
        ctk.CTkRadioButton(self, text="No", variable=self.senior_var, value=0, font=entry_font, text_color="black", fg_color="#00C88D", bg_color="white").place(x=180, y=480)

        # Senior ID Number Field
        ctk.CTkLabel(self, text="Senior ID Number", font=label_font, fg_color="white", text_color="black").place(x=420, y=430)
        self.entry_senior_id = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white",placeholder_text="Type here")
        self.entry_senior_id.place(x=420, y=480)
        create_underline(420, 510, 180)
        
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        try:
            if self.data.get("philhealth_number"):
                self.entry_philhealth.insert(0, self.data.get("philhealth_number"))
                
            if self.data.get("membership_type"):
                self.entry_membership.insert(0, self.data.get("membership_type"))
                
            if "is_pwd" in self.data:
                self.pwd_var.set(self.data.get("is_pwd"))
                
            if "is_senior" in self.data:
                self.senior_var.set(self.data.get("is_senior"))
                
            if self.data.get("pwd_id"):
                self.entry_pwd_id.insert(0, self.data.get("pwd_id"))
                
            if self.data.get("senior_id"):
                self.entry_senior_id.insert(0, self.data.get("senior_id"))
            
        except Exception as e:
            print(f"❌ Error restoring PhilHealth form data: {e}")

    def save_current_data(self):
        try:
            self.data["philhealth_number"] = self.entry_philhealth.get()
            self.data["membership_type"] = self.entry_membership.get().lower().capitalize()
            self.data["is_pwd"] = self.pwd_var.get()
            self.data["is_senior"] = self.senior_var.get()
            self.data["pwd_id"] = self.entry_pwd_id.get()
            self.data["senior_id"] = self.entry_senior_id.get()
            
        except Exception as e:
            print(f"❌ Error saving current PhilHealth data: {e}")

    def populate_fields(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT pb.philhealth_number, pb.membership_type, pb.is_pwd, 
                        pb.pwd_id, pb.is_senior, pb.senior_id
                    FROM patient_benefits pb
                    WHERE pb.patient_id = %s
                """, (self.patient_id,))

                philhealth_data = cursor.fetchone()

                if philhealth_data:
                    self.entry_philhealth.insert(0, philhealth_data[0] if philhealth_data[0] else "")
                    self.entry_membership.insert(0, philhealth_data[1] if philhealth_data[1] else "")
                    
                    self.pwd_var.set(1 if philhealth_data[2] else 0)
                    self.entry_pwd_id.insert(0, str(philhealth_data[3]) if philhealth_data[3] else "")
                    
                    self.senior_var.set(1 if philhealth_data[4] else 0)
                    self.entry_senior_id.insert(0, str(philhealth_data[5]) if philhealth_data[5] else "")

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")

    def open_next(self, data=None):
        try:
            self.data["philhealth_number"] = self.entry_philhealth.get()
            self.data["membership_type"] = self.entry_membership.get()
            self.data["is_pwd"] = self.pwd_var.get()
            self.data["is_senior"] = self.senior_var.get()
            self.data["pwd_id"] = self.entry_pwd_id.get()
            self.data["senior_id"] = self.entry_senior_id.get()

            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 4 input: ", e)

class PatientHistory1Window(BaseWindow):
    def __init__(self, parent, data=None):
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None
        
        super().__init__(parent, "Patient History Part 1", next_window=PatientHistory2Window, previous_window=PhilHealthInfoWindow)
        self.data = data if data else {}

        label_font = ("Merriweather Sans Bold",15)
        entry_font = ("Merriweather Sans", 13)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

        # Title
        title_text = "Edit Patient History Part 1" if self.edit_mode else "Patient History Part 1"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), text_color="black", bg_color="white").place(x=90, y=100)

        # Family History Boolean Variables
        self.family_hypertension = ctk.BooleanVar()
        self.family_diabetes = ctk.BooleanVar()
        self.family_malignancy = ctk.BooleanVar()

        ctk.CTkLabel(self, text="Family History", font=label_font, fg_color="white", text_color="black").place(x=120, y=190)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=235, y=190) 
        

        # Family History Checkboxes
        ctk.CTkCheckBox(self, variable=self.family_hypertension, text="Hypertension", 
                        font=entry_font, text_color="black", fg_color="#008400", 
                        bg_color="white", checkbox_width=20, checkbox_height=20).place(x=120, y=240)

        ctk.CTkCheckBox(self, variable=self.family_diabetes, text="Diabetes Mellitus", 
                        font=entry_font, text_color="black", fg_color="#008400", 
                        bg_color="white", checkbox_width=20, checkbox_height=20).place(x=370, y=240)

        ctk.CTkCheckBox(self, variable=self.family_malignancy, text="Malignancy", 
                        font=entry_font, text_color="black", fg_color="#008400", 
                        bg_color="white", checkbox_width=20, checkbox_height=20).place(x=620, y=240)

        # Family History Other Field
        ctk.CTkLabel(self, text="Other:", font=entry_font, fg_color="white", text_color="black").place(x=140, y=300)
        self.family_other = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        self.family_other.place(x=140, y=340)
        create_underline(140, 370, 180)

        # Medical History Label
        ctk.CTkLabel(self, text="Medical History", font=label_font, fg_color="white", text_color="black").place(x=120, y=400)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=250, y=400) 

        # Medical History Boolean Variables
        self.med_kidney_disease = ctk.BooleanVar()
        self.med_urinary_stone = ctk.BooleanVar()
        self.med_recurrent_uti = ctk.BooleanVar()
        self.med_diabetes_type = ctk.BooleanVar()

        ctk.CTkCheckBox(self, variable=self.med_kidney_disease, text="Hypertension prior to kidney disease", 
                        font=entry_font, text_color="black", fg_color="#008400", 
                        bg_color="white", checkbox_width=20, checkbox_height=20).place(x=120, y=450)

        ctk.CTkCheckBox(self, variable=self.med_urinary_stone, text="Urinary Stone", 
                        font=entry_font, text_color="black", fg_color="#008400", 
                        bg_color="white", checkbox_width=20, checkbox_height=20).place(x=400, y=450)

        ctk.CTkCheckBox(self, variable=self.med_recurrent_uti, text="Recurrent UTI", 
                        font=entry_font, text_color="black", fg_color="#008400", 
                        bg_color="white", checkbox_width=20, checkbox_height=20).place(x=650, y=450)

        ctk.CTkCheckBox(self, variable=self.med_diabetes_type, text="Diabetes Mellitus Type", 
                        font=entry_font, text_color="black", fg_color="#008400", 
                        bg_color="white", checkbox_width=20, checkbox_height=20).place(x=900, y=450)

        # Medical History Other Field
        ctk.CTkLabel(self, text="Other:", font=entry_font, fg_color="white", text_color="black").place(x=140, y=510)
        self.med_other1 = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        self.med_other1.place(x=140, y=550)
        create_underline(140, 580, 180)


        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        try:
            if "family_hypertension" in self.data:
                self.family_hypertension.set(self.data.get("family_hypertension"))
            if "family_diabetes" in self.data:
                self.family_diabetes.set(self.data.get("family_diabetes"))
            if "family_malignancy" in self.data:
                self.family_malignancy.set(self.data.get("family_malignancy"))
            if "med_kidney_disease" in self.data:
                self.med_kidney_disease.set(self.data.get("med_kidney_disease"))
            if "med_urinary_stone" in self.data:
                self.med_urinary_stone.set(self.data.get("med_urinary_stone"))
            if "med_recurrent_uti" in self.data:
                self.med_recurrent_uti.set(self.data.get("med_recurrent_uti"))
            if "med_diabetes_type" in self.data:
                self.med_diabetes_type.set(self.data.get("med_diabetes_type"))
                
            if self.data.get("family_other"):
                self.family_other.set_real_value(self.data.get("family_other"))
                
            if self.data.get("med_other1"):
                self.med_other1.set_real_value(self.data.get("med_other1"))
            
        except Exception as e:
            print(f"❌ Error restoring Patient History 1 form data: {e}")

    def save_current_data(self):
        try:
            self.data["family_hypertension"] = self.family_hypertension.get()
            self.data["family_diabetes"] = self.family_diabetes.get()
            self.data["family_malignancy"] = self.family_malignancy.get()
            self.data["family_other"] = self.family_other.get().lower().capitalize()
            self.data["med_kidney_disease"] = self.med_kidney_disease.get()
            self.data["med_urinary_stone"] = self.med_urinary_stone.get()
            self.data["med_recurrent_uti"] = self.med_recurrent_uti.get()
            self.data["med_diabetes_type"] = self.med_diabetes_type.get()
            self.data["med_other1"] = self.med_other1.get().lower().capitalize()
            
        except Exception as e:
            print(f"❌ Error saving current Patient History 1 data: {e}")

    def populate_fields(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()
                cursor.execute("""
                    SELECT ph.has_hypertension, ph.has_diabetes, ph.has_malignancy, 
                        ph.other_family_history, ph.has_kidney_disease, ph.has_urinary_stone, 
                        ph.has_recurrent_uti, ph.diabetes_type, ph.other_medical_history
                    FROM patient_history ph
                    WHERE ph.patient_id = %s
                """, (self.patient_id,))

                history_data = cursor.fetchone()

                if history_data:
                    self.family_hypertension.set(bool(history_data[0]))
                    self.family_diabetes.set(bool(history_data[1]))
                    self.family_malignancy.set(bool(history_data[2]))
                    self.family_other.insert(0, history_data[3] if history_data[3] else '')

                    self.med_kidney_disease.set(bool(history_data[4]))
                    self.med_urinary_stone.set(bool(history_data[5]))
                    self.med_recurrent_uti.set(bool(history_data[6]))
                    self.med_diabetes_type.set(bool(history_data[7]))
                    self.med_other1.insert(0, history_data[8] if history_data[8] else '')

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")

    def open_next(self, data=None):
        try:
            self.data["family_hypertension"] = self.family_hypertension.get()
            self.data["family_diabetes"] = self.family_diabetes.get()
            self.data["family_malignancy"] = self.family_malignancy.get()
            self.data["family_other"] = self.family_other.get().lower().capitalize()
            self.data["med_kidney_disease"] = self.med_kidney_disease.get()
            self.data["med_urinary_stone"] = self.med_urinary_stone.get()
            self.data["med_recurrent_uti"] = self.med_recurrent_uti.get()
            self.data["med_diabetes_type"] = self.med_diabetes_type.get()
            self.data["med_other1"] = self.med_other1.get().lower().capitalize()

            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 5 input: ", e)

class PatientHistory2Window(BaseWindow):
    def __init__(self, parent, data=None):
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Patient History Part 2", next_window=PatientHistory3Window, previous_window=PatientHistory1Window)
        self.data = data if data else {}

        label_font = ("Merriweather Sans Bold",15)
        entry_font = ("Merriweather Sans", 13)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)

        

        title_text = "Edit Patient History Part 2" if self.edit_mode else "Patient History Part 2"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), text_color="black", bg_color="white").place(x=90, y=100)

        # History of Present Illness Field
        ctk.CTkLabel(self, text="History of Present Illness", font=label_font, fg_color="white", text_color="black").place(x=120, y=190)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=325, y=190)
        self.history_illness = ctk.CTkTextbox(self, width=700, height=150, font=entry_font, text_color="black", fg_color="white", border_width=1.5, bg_color="white",corner_radius=20)
        self.history_illness.place(x=170, y=240)
        

        # Pertinent Past Medical History Field
        ctk.CTkLabel(self, text="Pertinent Past Medical History", font=label_font, fg_color="white", text_color="black").place(x=120, y=400)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=360, y=400)
        self.past_medical_history = ctk.CTkTextbox(self, width=700 ,height=150, font=entry_font, text_color="black", fg_color="white", border_width=1.5, bg_color="white",corner_radius=20)
        self.past_medical_history.place(x=170, y=450)
        

        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        try:
            if self.data.get("history_illness"):
                self.set_text_value(self.history_illness, self.data.get("history_illness"))
                
            if self.data.get("past_medical_history"):
                self.set_text_value(self.past_medical_history, self.data.get("past_medical_history"))
            
        except Exception as e:
            print(f"❌ Error restoring Patient History 2 form data: {e}")

    def save_current_data(self):
        try:
            self.data["history_illness"] = self.get_text_value(self.history_illness)
            self.data["past_medical_history"] = self.get_text_value(self.past_medical_history)
            
        except Exception as e:
            print(f"❌ Error saving current Patient History 2 data: {e}")
        
    def populate_fields(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()
                cursor.execute("""
                    SELECT ph.present_illness_history, ph.past_illness_history
                    FROM patient_history ph
                    WHERE ph.patient_id = %s
                """, (self.patient_id,))

                history_data = cursor.fetchone()

                if history_data:
                    illness_text = history_data[0] if history_data[0] else ''
                    past_medical_text = history_data[1] if history_data[1] else ''

                    self.set_text_value(self.history_illness, illness_text)
                    self.set_text_value(self.past_medical_history, past_medical_text)

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")

    def set_text_value(self, text_widget, value):
        """Set real value in Text widget, handling placeholder"""
        text_widget.delete("1.0", "end")
        if value and value.strip() and value != "Type here":
            text_widget.insert("1.0", value)
            text_widget.config(fg="black")
        else:
            text_widget.insert("1.0", "Type here")
            text_widget.config(fg="gray")

    def get_text_value(self, text_widget):
        """Get real value from Text widget, excluding placeholder"""
        content = text_widget.get("1.0", "end-1c").strip()
        if content == "Type here":
            return ""
        return content

    def add_placeholder(self, text_widget, placeholder):
        def on_focus_in(event):
            if text_widget.get("1.0", "end-1c") == placeholder:
                text_widget.delete("1.0", "end")
                text_widget.config(fg="black")

        def on_focus_out(event):
            if not text_widget.get("1.0", "end-1c").strip():
                text_widget.insert("1.0", placeholder)
                text_widget.config(fg="gray")

        text_widget.insert("1.0", placeholder)
        text_widget.config(fg="gray")
        text_widget.bind("<FocusIn>", on_focus_in)
        text_widget.bind("<FocusOut>", on_focus_out)

    def open_next(self, data=None):
        try:
            self.data["history_illness"] = self.get_text_value(self.history_illness)
            self.data["past_medical_history"] = self.get_text_value(self.past_medical_history)

            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 6 input: ", e)

class PatientHistory3Window(BaseWindow):
    def __init__(self, parent, data):
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Patient History Part 3", next_window=MedicationWindow, previous_window=PatientHistory2Window)
        self.data = data if data else {}

        label_font = ("Merriweather Sans Bold",15)
        entry_font = ("Merriweather Sans", 13)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

        title_text = "Edit Patient History Part 3" if self.edit_mode else "Patient History Part 3"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), bg_color="white").place(x=90, y=100)

        # Date of First Diagnosed having Kidney Disease
        ctk.CTkLabel(self, text="Date of First Diagnosed having Kidney Disease", font=label_font, fg_color="white", text_color="black").place(x=120, y=190)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=480, y=190)
        self.entry_diagnosed = DateEntry(self, width=12, font=entry_font, bg="white", date_pattern="yyyy-MM-dd", state="readonly")
        self.entry_diagnosed.place(x=120, y=240, height=25)

        # Date of First Dialysis  
        ctk.CTkLabel(self, text="Date of First Dialysis", font=label_font, fg_color="white", text_color="black").place(x=750, y=190)
        self.entry_dialysis = DateEntry(self, width=12, font=entry_font, bg="white", date_pattern="yyyy-MM-dd", state="readonly")
        self.entry_dialysis.place(x=750, y=240, height=25)

        # Mode Section
        ctk.CTkLabel(self, text="Mode", font=label_font, fg_color="white", text_color="black").place(x=120, y=310)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=170, y=310)
        self.mode_var = ctk.StringVar(value="hemodialysis")
        ctk.CTkRadioButton(self, text="Peritoneal", variable=self.mode_var, value="peritoneal", font=entry_font, text_color="black", fg_color="#008400", bg_color="white", radiobutton_width=20, radiobutton_height=20).place(x=120, y=360)
        ctk.CTkRadioButton(self, text="Hemodialysis", variable=self.mode_var, value="hemodialysis", font=entry_font, text_color="black", fg_color="#008400", bg_color="white", radiobutton_width=20, radiobutton_height=20).place(x=220, y=360)

        # Type of Access Section
        ctk.CTkLabel(self, text="Type of Access", font=label_font, fg_color="white", text_color="black").place(x=420, y=310)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=540, y=310)
        self.access_options = ["L AVF", "R AVF", "L AVG", "R AVG", "L CVC", "R CVC", "L PDC", "R PDC"]
        self.entry_access = ctk.CTkComboBox(self, values=self.access_options, width=180, height=25, font=entry_font, text_color="black", fg_color="white",button_color="#00C88D" ,border_width=1.5, bg_color="white", state="readonly")
        self.entry_access.place(x=420, y=360)

        # Date of First Chronic Hemodialysis
        ctk.CTkLabel(self, text="Date of First Chronic Hemodialysis", font=label_font, fg_color="white", text_color="black").place(x=120, y=430)
        self.entry_chronic = DateEntry(self, width=12,font=entry_font, bg="white", date_pattern="yyyy-MM-dd", state="readonly")
        self.entry_chronic.place(x=120, y=480,height=25)

        # Clinical Impression Section
        ctk.CTkLabel(self, text="Clinical Impression", font=label_font, fg_color="white", text_color="black").place(x=550, y=430)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=710, y=430)
        self.entry_clinical = ctk.CTkEntry(self, width=180, height=25, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white", placeholder_text="Type here")
        self.entry_clinical.place(x=550, y=480)
        create_underline(550, 510, 180)

        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        try:
            if self.data.get("date_diagnosed"):
                from datetime import datetime
                date_diagnosed = datetime.strptime(self.data.get("date_diagnosed"), "%Y-%m-%d").date()
                self.entry_diagnosed.set_date(date_diagnosed)
                
            if self.data.get("date_dialysis"):
                date_dialysis = datetime.strptime(self.data.get("date_dialysis"), "%Y-%m-%d").date()
                self.entry_dialysis.set_date(date_dialysis)
                
            if self.data.get("mode"):
                self.mode_var.set(self.data.get("mode"))
                
            if self.data.get("access"):
                self.entry_access.set(self.data.get("access"))
                
            if self.data.get("date_chronic"):
                date_chronic = datetime.strptime(self.data.get("date_chronic"), "%Y-%m-%d").date()
                self.entry_chronic.set_date(date_chronic)
                
            if self.data.get("clinical_impression"):
                self.entry_clinical.set_real_value(self.data.get("clinical_impression"))
            
        except Exception as e:
            print(f"❌ Error restoring Patient History 3 form data: {e}")

    def save_current_data(self):
        try:
            self.data["date_diagnosed"] = self.entry_diagnosed.get_date().strftime("%Y-%m-%d")
            self.data["date_dialysis"] = self.entry_dialysis.get_date().strftime("%Y-%m-%d")
            self.data["mode"] = self.mode_var.get()
            self.data["access"] = self.entry_access.get()
            self.data["date_chronic"] = self.entry_chronic.get_date().strftime("%Y-%m-%d")
            self.data["clinical_impression"] = self.entry_clinical.get()
            
        except Exception as e:
            print(f"❌ Error saving current Patient History 3 data: {e}")

    def populate_fields(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()
                cursor.execute("""
                    SELECT ph.first_diagnosis, ph.first_dialysis, ph.mode, 
                        ph.access_type, ph.first_hemodialysis, ph.clinical_impression
                    FROM patient_history ph
                    WHERE ph.patient_id = %s
                """, (self.patient_id,))

                history_data = cursor.fetchone()

                if history_data:
                    if history_data[0]:
                        self.entry_diagnosed.set_date(history_data[0])
                    if history_data[1]:
                        self.entry_dialysis.set_date(history_data[1])
                    if history_data[2]:
                        self.mode_var.set(history_data[2])
                    if history_data[3]:
                        self.entry_access.set(history_data[3])
                    if history_data[4]:
                        self.entry_chronic.set_date(history_data[4])
                    
                    # Changed from set_real_value() to insert() for CTkEntry
                    clinical_value = history_data[5] if history_data[5] else ""
                    self.entry_clinical.delete(0, "end")  # Clear existing content
                    self.entry_clinical.insert(0, clinical_value)

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")
    
    def open_next(self, data=None):
        try:
            self.data["date_diagnosed"] = self.entry_diagnosed.get_date().strftime("%Y-%m-%d")
            self.data["date_dialysis"] = self.entry_dialysis.get_date().strftime("%Y-%m-%d")
            self.data["mode"] = self.mode_var.get()
            self.data["access"] = self.entry_access.get()
            self.data["date_chronic"] = self.entry_chronic.get_date().strftime("%Y-%m-%d")
            self.data["clinical_impression"] = self.entry_clinical.get()

            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 7 input: ", e)

class MedicationWindow(BaseWindow):
    medication_slots = []

    def __init__(self, parent, data):
        self.data = data
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None
        
        super().__init__(parent, "Medication", next_window=None, previous_window=PatientHistory3Window)
        self.medication_entries = []
        self.max_columns = 3 

        title_text = "Edit Medications" if self.edit_mode else "Medication"
        ctk.CTkLabel(self.main_frame, text=title_text, font=("Merriweather bold", 25), text_color="#000000",bg_color="white").pack(pady=20)

        container = tk.Frame(self.main_frame, bg="white")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="white")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.grid_frame = tk.Frame(self.scroll_frame, bg="white")
        self.grid_frame.pack(pady=10, padx=20, fill="x")

        if self.edit_mode and self.patient_id:
            self.load_existing_medications()
        else:
            if not MedicationWindow.medication_slots:
                for i in range(9):
                    MedicationWindow.medication_slots.append("")
        
        for i, value in enumerate(MedicationWindow.medication_slots):
            self.add_medication_slot(i + 1, value)

        self.add_slot_button = tk.Button(
            self.grid_frame, text="+ Another Slot", font=("Merriweather Sans bold", 14),
            fg="blue", bg="white", bd=0, cursor="hand2", command=self.add_new_slot
        )
        self.add_slot_button.grid(row=len(self.medication_entries) // self.max_columns, column=len(self.medication_entries) % self.max_columns, padx=10, pady=10)

        self.right_panel = tk.Frame(self.main_frame, bg="white", width=200)
        self.right_panel.pack(side="right", fill="y", padx=20, pady=10)

        self.bind_scroll_events()

    def save_current_data(self):
        try:
            for i, entry in enumerate(self.medication_entries):
                if i < len(MedicationWindow.medication_slots):
                    MedicationWindow.medication_slots[i] = entry.get_real_value()
                else:
                    MedicationWindow.medication_slots.append(entry.get_real_value())
        except Exception as e:
            print(f"❌ Error saving current medication data: {e}")

    def load_existing_medications(self):
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()
                
                cursor.execute("""
                    SELECT m.medication_name 
                    FROM patient_medications pm 
                    JOIN medicines m ON m.medication_id = pm.medication_id
                    WHERE pm.patient_id = %s
                """, (self.patient_id,))
                
                medications = cursor.fetchall()
                
                MedicationWindow.medication_slots.clear()
                
                for med in medications:
                    med_name = med[0] if med[0] else ""
                    if med_name and med_name.strip() and med_name.strip() not in ['Type Here', 'Type here', 'Type here', '']:
                        MedicationWindow.medication_slots.append(med_name.strip())
                
                while len(MedicationWindow.medication_slots) < 9:
                    MedicationWindow.medication_slots.append("")
                
                cursor.close()
                connect.close()
                
            except Exception as e:
                print(f"Error loading medications: {e}")
                MedicationWindow.medication_slots = [""] * 9

    def add_medication_slot(self, slot_number, value=""):
        frame = tk.Frame(self.grid_frame, bg="white", bd=1)
        frame.grid(row=len(self.medication_entries) // self.max_columns, column=len(self.medication_entries) % self.max_columns, padx=10, pady=10)

        tk.Label(frame, text=f"Medication {slot_number}", font=("Merriweather Sans bold", 12), bg="white").pack(anchor="w")
        entry = TextField_Patients(frame, width=15, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry.pack(anchor="w", pady=5)
        tk.Frame(frame, bg="black", height=1, width=150).pack(anchor="w", pady=20)

        entry.set_real_value(value)
        
        self.medication_entries.append(entry)

    def add_new_slot(self):
        new_slot_number = len(self.medication_entries) + 1
        MedicationWindow.medication_slots.append("")
        self.add_medication_slot(new_slot_number)

        row = len(self.medication_entries) // self.max_columns
        col = len(self.medication_entries) % self.max_columns
        self.add_slot_button.grid(row=row, column=col, padx=10, pady=10)

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)

    def save_slots(self):
        for i, entry in enumerate(self.medication_entries):
            MedicationWindow.medication_slots[i] = entry.get_real_value()
        print("Saved Medications:", MedicationWindow.medication_slots)
    
    def bind_scroll_events(self):
        def on_mousewheel(event):
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)  
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def refresh_homepage_recent_patient(self):
        try:
            current_window = self.master
            while current_window and not hasattr(current_window, 'pages'):
                current_window = current_window.master
            
            if current_window and hasattr(current_window, 'pages'):
                if 'Home' in current_window.pages:
                    home_page = current_window.pages['Home']
                    if hasattr(home_page, 'refresh_recent_patient'):
                        home_page.refresh_recent_patient()
                        print("✅ Homepage recent patient refreshed successfully!")
                
                if 'Patient' in current_window.pages:
                    patient_page = current_window.pages['Patient']
                    if hasattr(patient_page, 'refresh_table'):
                        patient_page.refresh_table()
                        print("✅ Patient page table refreshed successfully!")
                        
        except Exception as e:
            print(f"❌ Error refreshing homepage: {e}")

    def update_notif_status(self, edited_by, patient_id, patient_fn, status, notif_type):
        try:
            connect = db()
            cursor = connect.cursor()

            cursor.execute("""
                INSERT INTO notification_logs(user_fullname, patient_id, patient_name, patient_status, notification_type, notification_timestamp)
                VALUES(%s, %s, %s, %s, %s, NOW())
            """, (edited_by, patient_id, patient_fn, status, notif_type))
            connect.commit()

            unique_id = cursor.lastrowid
            return unique_id

        except Exception as e:
            print(f'Failed updating status notif logs ({notif_type})!', e)
        
        finally: 
            cursor.close()
            connect.close()

    def update_form(self):
        if not self.edit_mode or not self.patient_id:
            print("Not in edit mode or no patient ID")
            return
        
        username = login_shared_states.get('logged_username', None)

        try:
            connect = db()
            cursor = connect.cursor()

            cursor.execute("""
                SELECT full_name FROM users
                WHERE username = %s
            """, (username,))
            
            user_fn = cursor.fetchone()[0]

            cursor.execute("""
                SELECT pl.patient_name, pi.status 
                FROM patient_info pi JOIN patient_list pl ON pi.patient_id = pl.patient_id
                WHERE pi.patient_id = %s
            """, (self.patient_id,))
            
            reactive_status = cursor.fetchone()
            stat_patient_name = reactive_status[0]
            stat_status = reactive_status[1]

        except Exception as e:
            print('Error fetching user_fullname', e)
        
        finally:
            cursor.close()
            connect.close()
            
        try:
            print(f"🔄 Updating patient {self.patient_id} with new data...")
            
            from backend.crud import (
                update_patient_info, update_patient_contact, update_patient_relative,
                update_patient_benefits, update_patient_history, update_patient_medications,
                update_patient_list
            )
            
            patient_information = {
                "last_name": self.data.get("patient_last_name").lower().capitalize(),
                "first_name": self.data.get("patient_first_name").lower().capitalize(),
                "middle_name": self.data.get("patient_middle_name").lower().capitalize(), 
                "status": self.data.get("patient_status").capitalize(),
                "access_type": self.data.get("patient_access"),
                "birthdate": self.data.get("patient_birthdate"),
                "age": self.data.get("patient_age"),
                "gender": self.data.get("patient_gender").capitalize(),
                "height": self.data.get("patient_height"),
                "civil_status": self.data.get("patient_civil_status").capitalize(),
                "religion": self.data.get("patient_religion").capitalize(),
                "address": self.data.get("patient_address").capitalize()
            }

            now = datetime.now()
            right_now = now.strftime('%Y-%m-%d %H:%M:%S')

            if stat_status.lower() ==  'inactive' and patient_information['status'].lower() == 'active':
                self.update_notif_status(user_fn, self.patient_id, stat_patient_name, 'Reactivated', 'Patient Status')

                print(f"""
                    Patient Status

                    {stat_patient_name} is now an active patient again. Reactivated by: {user_fn}.

                    {right_now}
                """)

            if stat_status.lower() ==  'active' and patient_information['status'].lower() == 'inactive':
                self.update_notif_status(user_fn, self.patient_id, stat_patient_name, 'Deactivated', 'Patient Status')

                print(f"""
                    Patient Status

                    {stat_patient_name} is now inactive, go to the patient information to reactivate.

                    {right_now}
                """)

            if update_patient_info(self.patient_id, patient_information):
                print("Patient info updated successfully")
                self.refresh_homepage_recent_patient()
            else:
                print("Error updating patient info")
                return

            patient_contact_information = {
                "last_name": self.data.get("contact_last_name").lower().capitalize(),
                "first_name": self.data.get("contact_first_name").lower().capitalize(),
                "middle_name": self.data.get("contact_middle_name").lower().capitalize(), 
                "contact_number": self.data.get("contact_number"),
                "relationship": self.data.get("relationship_to_patient").capitalize(),
                "address": self.data.get("contact_address")
            }
            
            if update_patient_contact(self.patient_id, patient_contact_information):
                print("Contact info updated successfully")
            else:
                print("Error updating contact info")
                return

            patient_relative_information = {
                "last_name": self.data.get("relative_last_name").lower().capitalize(),
                "first_name": self.data.get("relative_first_name").lower().capitalize(),
                "middle_name": self.data.get("relative_middle_name").lower().capitalize(), 
                "contact_number": self.data.get("relative_contact_number"),
                "address": self.data.get("relative_address")
            }
            
            if update_patient_relative(self.patient_id, patient_relative_information):
                print("Relative info updated successfully")
            else:
                print("Error updating relative info")
                return

            patient_benefits = {
                "is_senior": self.data.get("is_senior"),
                "is_pwd": self.data.get("is_pwd"),
                "philhealth_number": self.data.get("philhealth_number"),
                "membership_type": self.data.get("membership_type").capitalize(),
                "pwd_id": self.data.get("pwd_id"), 
                "senior_id": self.data.get("senior_id")
            }
            
            if update_patient_benefits(self.patient_id, patient_benefits):
                print("Benefits info updated successfully")
            else:
                print("Error updating benefits info")
                return

            patient_history_1 = {
                "has_hypertension": self.data.get("family_hypertension"),
                "has_diabetes": self.data.get("family_diabetes"),
                "has_malignancy": self.data.get("family_malignancy"), 
                "other_family_history": self.data.get("family_other").capitalize(),
                "has_kidney_disease": self.data.get("med_kidney_disease"),
                "has_urinary_stone": self.data.get("med_urinary_stone"),
                "has_recurrent_uti": self.data.get("med_recurrent_uti"), 
                "diabetes_type": self.data.get("med_diabetes_type"),
                "other_medical_history": self.data.get("med_other1").capitalize()
            }

            patient_history_2 = {
                "present_illness_history": self.data.get("history_illness").capitalize(), 
                "past_illness_history": self.data.get("past_medical_history").capitalize(),
            }

            patient_history_3 = {
                "first_diagnosis": self.data.get("date_diagnosed"),
                "first_dialysis": self.data.get("date_dialysis"),
                "mode": self.data.get("mode"),
                "access_type": self.data.get("access"),
                "first_hemodialysis": self.data.get("date_chronic"),
                "clinical_impression": self.data.get("clinical_impression").capitalize(),
            }

            patient_history_combined = {**patient_history_1, **patient_history_2, **patient_history_3}
            
            if update_patient_history(self.patient_id, patient_history_combined):
                print("Patient history updated successfully")
            else:
                print("Error updating patient history")
                return

            medication_entries_row = [
                entry.get_real_value().capitalize() 
                for entry in self.medication_entries 
                if entry.get_real_value()
            ]
            
            if update_patient_medications(self.patient_id, medication_entries_row):
                print("Medications updated successfully")
            else:
                print("Error updating medications")
                return

            first_name = self.data.get("patient_first_name")
            middle_name = self.data.get("patient_middle_name")
            last_name = self.data.get("patient_last_name")
            
            null_values = ["Type Here", None, "", " "]
            name_validation = [name for name in [first_name, middle_name, last_name] if name not in null_values]
            patient_full_name = ' '.join(name_validation)

            patient_list_data = {
                'patient_name': patient_full_name,   
                'age': self.data.get("patient_age"),
                'gender': self.data.get("patient_gender"),
                'access_type': self.data.get("patient_access")
            }
            
            if update_patient_list(self.patient_id, patient_list_data):
                print("Patient list updated successfully")
                self.refresh_homepage_recent_patient()
            else:
                print("Error updating patient list")
                return
            
            self.destroy()
            
            print("Update completed and window closed!")
            
        except Exception as e:
            print(f"❌ Error updating patient: {e}")
            import traceback
            traceback.print_exc()

    def submit_form(self):
        if self.edit_mode:
            print("In edit mode - use Update button instead")
            return
        try:
            connect = db()
            cursor = connect.cursor()

            patient_information = {
                "last_name": self.data.get("patient_last_name"),
                "first_name": self.data.get("patient_first_name"),
                "middle_name": self.data.get("patient_middle_name"), 
                "status": self.data.get("patient_status"),
                "access_type": self.data.get("patient_access"),
                "birthdate": self.data.get("patient_birthdate"),
                "age": self.data.get("patient_age"),
                "gender": self.data.get("patient_gender"),
                "height": self.data.get("patient_height"),
                "civil_status": self.data.get("patient_civil_status"),
                "religion": self.data.get("patient_religion"),
                "address": self.data.get("patient_address")
            }

            keys_needed = ['first_name', 'middle_name', 'last_name']
            joined_fn = ' '.join(patient_information[keys].capitalize() for keys in keys_needed)

            patient_information_column = ', '.join(patient_information.keys())
            patient_information_row = [
                entries.capitalize() if isinstance(entries, str) else  entries 
                for entries in patient_information.values()]

            patient_contact_information = {
                "last_name": self.data.get("contact_last_name"),
                "first_name": self.data.get("contact_first_name"),
                "middle_name": self.data.get("contact_middle_name"), 
                "contact_number": self.data.get("contact_number"),
                "relationship": self.data.get("relationship_to_patient"),
                "address": self.data.get("contact_address")
            }

            patient_contact_information_column = ', '.join(patient_contact_information.keys())
            patient_contact_information_row = [
                entries.capitalize() if isinstance(entries, str) else entries
                for entries in patient_contact_information.values()]

            patient_relative_information = {
                "last_name": self.data.get("relative_last_name"),
                "first_name": self.data.get("relative_first_name"),
                "middle_name": self.data.get("relative_middle_name"), 
                "contact_number": self.data.get("relative_contact_number"),
                "address": self.data.get("relative_address")
            }

            patient_relative_information_column = ', '.join(patient_relative_information.keys())
            patient_relative_information_row = [
                entries.capitalize() if isinstance(entries, str) else entries
                for entries in patient_relative_information.values()]

            patient_benefits = {
                "is_senior": self.data.get("is_senior"),
                "is_pwd": self.data.get("is_pwd"),
                "philhealth_number": self.data.get("philhealth_number"),
                "membership_type": self.data.get("membership_type"),
                "pwd_id": self.data.get("pwd_id"), 
                "senior_id": self.data.get("senior_id")
            }

            patient_benefits_column = ', '.join(patient_benefits.keys())
            patient_benefits_row = [
                entries.capitalize() if isinstance(entries, str) else entries                    
                for entries in patient_benefits.values()]

            patient_history_1 = {
                "has_hypertension": self.data.get("family_hypertension"),
                "has_diabetes": self.data.get("family_diabetes"),
                "has_malignancy": self.data.get("family_malignancy"), 
                "other_family_history": self.data.get("family_other"),
                "has_kidney_disease": self.data.get("med_kidney_disease"),
                "has_urinary_stone": self.data.get("med_urinary_stone"),
                "has_recurrent_uti": self.data.get("med_recurrent_uti"), 
                "diabetes_type": self.data.get("med_diabetes_type"),
                "other_medical_history": self.data.get("med_other1")  
            }

            patient_history_2 = {
                "present_illness_history": self.data.get("history_illness"), 
                "past_illness_history": self.data.get("past_medical_history"),  
            }

            patient_history_3 = {
                "first_diagnosis": self.data.get("date_diagnosed"),     
                "first_dialysis": self.data.get("date_dialysis"),    
                "mode": self.data.get("mode"),                           
                "access_type": self.data.get("access"),                   
                "first_hemodialysis": self.data.get("date_chronic"),       
                "clinical_impression": self.data.get("clinical_impression"), 
            }

            medication_entries_row = [
                entry.get_real_value().capitalize() 
                for entry in self.medication_entries 
                if entry.get_real_value()
            ]
            medication_entries_data = ', '.join(medication_entries_row)

            patient_history_column = ', '.join(
                list(patient_history_1.keys()) +
                list(patient_history_2.keys()) +
                list(patient_history_3.keys()))
            
            patient_history_row = [
                value if isinstance(value, (bool)) else str(value)    
                for value in (
                list(patient_history_1.values()) +  
                list(patient_history_2.values()) +
                list(patient_history_3.values())
                )]
            
            first_name = self.data.get("patient_first_name")
            middle_name = self.data.get("patient_middle_name")
            last_name = self.data.get("patient_last_name")

            null_values = ["Type Here", None, "", " "]

            name_validation = [name for name in [first_name, middle_name, last_name] if name not in null_values]

            patient_full_name = ' '.join(name.capitalize() for name in name_validation)

            patient_list = {
                'patient_name': patient_full_name,   
                'age': self.data.get("patient_age"),
                'gender': self.data.get("patient_gender"),
                'access_type': self.data.get("patient_access"), 
                'date_registered': date.today()
            }       

            patient_list_column = ', '.join(patient_list.keys())
            patient_list_row = [entries.strip() if isinstance(entries, str) else entries for entries in patient_list.values()]

            print(patient_list_column)
            print(patient_list_row)

            pk_patient_id = submit_form_creation(patient_list_column, patient_list_row, table_name='patient_list')

            if pk_patient_id:
                print("Successfully inserted on the list")
            else:
                print("Error with list insertion")
                return
            
            create_patient_info = submit_form_subcreation(
                patient_information_column, 
                patient_information_row, 
                pk_patient_id,  
                table_name='patient_info')

            if create_patient_info:
                print("Step 1 input successfully created")
            else:
                print("Error with step 1 input creation")
                return

            create_patient_contact = submit_form_subcreation(
                patient_contact_information_column, 
                patient_contact_information_row,
                pk_patient_id,
                table_name='patient_contact')

            if create_patient_contact:
                print("Step 2 input successfully created")
            else:
                print("Error with step 2 input creation")
                return
            
            create_patient_relative_information = submit_form_subcreation(
                patient_relative_information_column,
                patient_relative_information_row,
                pk_patient_id,
                table_name='patient_relative'
            )

            if create_patient_relative_information:
                print("Step 3 input successfully created")
            else:
                print("Error with step 3 input creation")
                return
            
            create_patient_benefits = submit_form_subcreation(
                patient_benefits_column,
                patient_benefits_row,
                pk_patient_id,
                table_name='patient_benefits'
            )

            if create_patient_benefits:
                print("Step 4 input successfully created")
            else:
                print("Error with step 4 input creation")
                return
            
            create_patient_history = submit_form_subcreation(
                patient_history_column,
                patient_history_row,
                pk_patient_id,
                table_name='patient_history'
            )

            if create_patient_history:
                print("Step 5 input successfully created")
            else:
                print("Error with step 5 input creation")
                return

            create_patient_medications = submit_form_extra(
                pk_patient_id,
                medication_entries_row
            )

            if create_patient_medications:
                print("Step 6 input successfully created")
                self.refresh_homepage_recent_patient()  
            else:
                print("Error with step 6 input creation")
                return

            self.destroy()

            print('fullllllllllllllllllll nameeeeeeeeeeeeeeeeeeeeee', joined_fn)

            try:
                username = login_shared_states.get('logged_username', None)

                cursor.execute("""
                    SELECT full_name FROM users
                    WHERE username = %s
                """, (username,))

                user_fn = cursor.fetchone()[0]

            except Exception as e:
                print('Error retrieving user_fullname', e)

            now = datetime.now()
            right_now = now.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("""
                INSERT INTO notification_logs(user_fullname, patient_id, patient_name, notification_type, notification_timestamp) 
                VALUES(%s, %s, %s, %s, %s)
            """, (user_fn, pk_patient_id, joined_fn, 'New Patient Added', right_now))
            connect.commit()

            notification_id = cursor.lastrowid

            print(f"""
                New Patient Added

                {joined_fn} was added to the system by {user_fn}.  
                  
                {right_now} 
            """)

        except Exception as e:
            print("Error with submitting the form: ", e)
        
        finally:
            cursor.close()
            connect.close()