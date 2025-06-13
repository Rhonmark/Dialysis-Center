import tkinter as tk
from tkinter import ttk, PhotoImage
from tkcalendar import DateEntry
from datetime import date, datetime

from components.buttons import CTkButtonSelectable
from components.textfields_patients import TextField_Patients

from backend.connector import db_connection as db
from backend.crud import submit_form_creation, submit_form_subcreation, submit_form_extra, retrieve_form_data

class BaseWindow(tk.Toplevel):
    def __init__(self, parent, title, next_window=None, previous_window=None):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.geometry("1300x700")
        self.overrideredirect(True)
        self.center_window()
        self.next_window = next_window
        self.previous_window = previous_window

        self.border_frame = tk.Frame(self, bg="black", bd=0.5) 
        self.border_frame.pack(expand=True, fill="both", padx=0, pady=0)

        self.main_frame = tk.Frame(self.border_frame, bg="white")
        self.main_frame.pack(expand=True, fill="both", padx=0.5, pady=0.5)

        self.sidebar = tk.Frame(self.main_frame, width=30, bg="#1A374D")
        self.sidebar.pack(side="left", fill="y")

        self.exit_icon = PhotoImage(file="assets/exit.png")
        self.btn_exit = tk.Button(self, image=self.exit_icon, bd=0, bg="white", activebackground="white", command=self.destroy)
        self.btn_exit.place(x=1200, y=10)  

        if self.next_window:
            self.btn_next = CTkButtonSelectable(
                self, 
                text="Next", 
                command=self.open_next, 
                width=120, 
                height=40  
            )
            self.btn_next.place(x=1070, y=600)

        if not self.next_window: 
            # Check if we're in edit mode 
            if hasattr(self, 'edit_mode') and self.edit_mode:
                self.btn_update = CTkButtonSelectable(
                    self, 
                    text="Update", 
                    command=self.update_form, 
                    width=120, 
                    height=40  
                )
                self.btn_update.place(x=1070, y=600)
            else:
                self.btn_submit = CTkButtonSelectable(
                    self, 
                    text="Submit", 
                    command=self.submit_form, 
                    width=120, 
                    height=40  
                )
                self.btn_submit.place(x=1070, y=600)

        if self.previous_window:
            self.back_icon = PhotoImage(file="assets/back.png")
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
        # Check if we're in edit mode
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None
        
        super().__init__(parent, "Patient Information", next_window=ContactPersonWindow, previous_window=None)
        self.data = data if data else {}

        # Title Label - change based on mode
        title_text = "Edit Patient Information" if self.edit_mode else "Patient Information"
        tk.Label(self, text=title_text, font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=150)
        self.entry_lastname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_lastname.place(x=120, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=230)

        tk.Label(self, text="First Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=150)
        self.entry_firstname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_firstname.place(x=420, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=230)

        tk.Label(self, text="Middle Name", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=150)
        self.entry_middlename = TextField_Patients(self, width=15, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_middlename.place(x=720, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=150).place(x=720, y=230)

        # Status, Type of Access, Birthdate, Age
        tk.Label(self, text="Status *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=270)
        self.entry_status = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_status.place(x=120, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=350)

        tk.Label(self, text="Type of Access *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=270)
        self.entry_access = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_access.place(x=420, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=350)

        tk.Label(self, text="Birthdate *", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=270)
        self.entry_birthdate = DateEntry(self, width=18, font=("Merriweather light", 12), bg="white", date_pattern="yyyy-MM-dd", state="normal")
        self.entry_birthdate.place(x=720, y=320, height=25)
        
        # Age field
        tk.Label(self, text="Age *", font=("Merriweather Sans bold", 15), bg="white").place(x=1020, y=270)
        self.entry_age = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_age.place(x=1020, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=1020, y=350)

        # Gender, Height, Civil Status, Religion
        tk.Label(self, text="Gender *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=390)
        self.entry_gender = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_gender.place(x=120, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=470)

        tk.Label(self, text="Height *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=390)
        self.entry_height = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_height.place(x=420, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=470)

        tk.Label(self, text="Civil Status *", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=390)
        self.entry_civil_status = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_civil_status.place(x=720, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=470)

        tk.Label(self, text="Religion *", font=("Merriweather Sans bold", 15), bg="white").place(x=1020, y=390)
        self.entry_religion = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_religion.place(x=1020, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=1020, y=470)

        # Complete Address 
        tk.Label(self, text="Complete Address *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=510)
        self.entry_address = TextField_Patients(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_address.place(x=120, y=560, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=590)

        self.entry_birthdate.bind("<<DateEntrySelected>>", self.update_age)

        # Load data for both edit mode AND add mode
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            # Restore form data when coming back from next window
            self.restore_form_data()

    def restore_form_data(self):
        """Restore form data when navigating back in add mode"""
        try:
            # Clear placeholder text and populate with saved data
            if self.data.get("patient_last_name"):
                self.entry_lastname.delete(0, tk.END)
                self.entry_lastname.insert(0, self.data.get("patient_last_name"))
                
            if self.data.get("patient_first_name"):
                self.entry_firstname.delete(0, tk.END)
                self.entry_firstname.insert(0, self.data.get("patient_first_name"))
                
            if self.data.get("patient_middle_name"):
                self.entry_middlename.delete(0, tk.END)
                self.entry_middlename.insert(0, self.data.get("patient_middle_name"))
                
            if self.data.get("patient_status"):
                self.entry_status.delete(0, tk.END)
                self.entry_status.insert(0, self.data.get("patient_status"))
                
            if self.data.get("patient_access"):
                self.entry_access.delete(0, tk.END)
                self.entry_access.insert(0, self.data.get("patient_access"))
                
            if self.data.get("patient_birthdate"):
                from datetime import datetime
                birthdate = datetime.strptime(self.data.get("patient_birthdate"), "%Y-%m-%d").date()
                self.entry_birthdate.set_date(birthdate)
                
            if self.data.get("patient_age"):
                self.entry_age.delete(0, tk.END)
                self.entry_age.insert(0, self.data.get("patient_age"))
                
            if self.data.get("patient_gender"):
                self.entry_gender.delete(0, tk.END)
                self.entry_gender.insert(0, self.data.get("patient_gender"))
                
            if self.data.get("patient_height"):
                self.entry_height.delete(0, tk.END)
                self.entry_height.insert(0, self.data.get("patient_height"))
                
            if self.data.get("patient_civil_status"):
                self.entry_civil_status.delete(0, tk.END)
                self.entry_civil_status.insert(0, self.data.get("patient_civil_status"))
                
            if self.data.get("patient_religion"):
                self.entry_religion.delete(0, tk.END)
                self.entry_religion.insert(0, self.data.get("patient_religion"))
                
            if self.data.get("patient_address"):
                self.entry_address.delete(0, tk.END)
                self.entry_address.insert(0, self.data.get("patient_address"))
            
        except Exception as e:
            print(f"❌ Error restoring form data: {e}")

    def save_current_data(self):
        """Save current form data before navigating away"""
        try:
            self.data["patient_last_name"] = self.entry_lastname.get().strip()
            self.data["patient_first_name"] = self.entry_firstname.get().strip()
            self.data["patient_middle_name"] = self.entry_middlename.get().strip()
            self.data["patient_status"] = self.entry_status.get().strip()
            self.data["patient_access"] = self.entry_access.get().strip()
            self.data["patient_birthdate"] = self.entry_birthdate.get_date().strftime("%Y-%m-%d")
            self.data["patient_age"] = self.entry_age.get().strip()
            self.data["patient_gender"] = self.entry_gender.get().strip()
            self.data["patient_height"] = self.entry_height.get().strip()
            self.data["patient_civil_status"] = self.entry_civil_status.get().strip()
            self.data["patient_religion"] = self.entry_religion.get().strip()
            self.data["patient_address"] = self.entry_address.get().strip()
            
        except Exception as e:
            print(f"❌ Error saving current data: {e}")

    def populate_fields(self):
        """Populate fields with existing patient data for editing"""
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
                    # Clear and populate fields only if value is not 'Type Here' or None
                    if patient_data[0] and patient_data[0] != 'Type Here':
                        self.entry_lastname.delete(0, tk.END)
                        self.entry_lastname.insert(0, patient_data[0])
                    
                    if patient_data[1] and patient_data[1] != 'Type Here':
                        self.entry_firstname.delete(0, tk.END)
                        self.entry_firstname.insert(0, patient_data[1])
                    
                    if patient_data[2] and patient_data[2] != 'Type Here':
                        self.entry_middlename.delete(0, tk.END)
                        self.entry_middlename.insert(0, patient_data[2])
                    
                    if patient_data[3] and patient_data[3] != 'Type Here':
                        self.entry_status.delete(0, tk.END)
                        self.entry_status.insert(0, patient_data[3])
                    
                    if patient_data[4] and patient_data[4] != 'Type Here':
                        self.entry_access.delete(0, tk.END)
                        self.entry_access.insert(0, patient_data[4])
                    
                    # Handle birthdate
                    if patient_data[5]:
                        self.entry_birthdate.set_date(patient_data[5])
                    
                    if patient_data[6]:
                        self.entry_age.delete(0, tk.END)
                        self.entry_age.insert(0, str(patient_data[6]))
                    
                    if patient_data[7] and patient_data[7] != 'Type Here':
                        self.entry_gender.delete(0, tk.END)
                        self.entry_gender.insert(0, patient_data[7])
                    
                    if patient_data[8] and patient_data[8] != 'Type Here':
                        self.entry_height.delete(0, tk.END)
                        self.entry_height.insert(0, patient_data[8])
                    
                    if patient_data[9] and patient_data[9] != 'Type Here':
                        self.entry_civil_status.delete(0, tk.END)
                        self.entry_civil_status.insert(0, patient_data[9])
                    
                    if patient_data[10] and patient_data[10] != 'Type Here':
                        self.entry_religion.delete(0, tk.END)
                        self.entry_religion.insert(0, patient_data[10])
                    
                    if patient_data[11] and patient_data[11] != 'Type Here':
                        self.entry_address.delete(0, tk.END)
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
            self.entry_age.delete(0, tk.END)
            self.entry_age.insert(0, str(age))  
        except Exception as e:
            print(f"Error calculating age: {e}")
    
    def open_next(self, data=None):
        try:
            self.data["patient_last_name"] = self.entry_lastname.get().strip()
            self.data["patient_first_name"] = self.entry_firstname.get().strip()
            self.data["patient_middle_name"] = self.entry_middlename.get().strip()
            self.data["patient_status"] = self.entry_status.get().strip()
            self.data["patient_access"] = self.entry_access.get().strip()
            self.data["patient_birthdate"] = self.entry_birthdate.get_date().strftime("%Y-%m-%d")  
            self.data["patient_age"] = self.entry_age.get().strip()
            self.data["patient_gender"] = self.entry_gender.get().strip()
            self.data["patient_height"] = self.entry_height.get().strip()
            self.data["patient_civil_status"] = self.entry_civil_status.get().strip()
            self.data["patient_religion"] = self.entry_religion.get().strip()
            self.data["patient_address"] = self.entry_address.get().strip()
            
            # Pass edit mode and patient_id forward
            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 1 input: ", e)

class ContactPersonWindow(BaseWindow):
    def __init__(self, parent, data=None):
        # Check if we're in edit mode
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Contact Information", next_window=RelativeInfoWindow, previous_window=PatientInfoWindow)
        self.data = data if data else {}

        # Title Label - change based on mode
        title_text = "Edit Contact Information" if self.edit_mode else "Contact Information"
        tk.Label(self, text=title_text, font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # Title Label
        tk.Label(self, text="Contact Person Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        self.entry_lastname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_lastname.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)
    
        tk.Label(self, text="First Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        self.entry_firstname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_firstname.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Middle Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        self.entry_middlename = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_middlename.place(x=720, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=270)

        # Contact Number, Relationship to the Patient
        tk.Label(self, text="Contact Number *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        self.entry_contact = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_contact.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Relationship to the Patient *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        self.entry_relationship = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_relationship.place(x=420, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Complete Address 
        tk.Label(self, text="Complete Address *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        self.entry_address = TextField_Patients(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_address.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=510)

        #Load data for both edit mode AND add mode
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            # Restore form data when coming back from next window
            self.restore_form_data()

    def restore_form_data(self):
        """Restore form data when navigating back in add mode"""
        try:
            if self.data.get("contact_last_name"):
                self.entry_lastname.delete(0, tk.END)
                self.entry_lastname.insert(0, self.data.get("contact_last_name"))
                
            if self.data.get("contact_first_name"):
                self.entry_firstname.delete(0, tk.END)
                self.entry_firstname.insert(0, self.data.get("contact_first_name"))
                
            if self.data.get("contact_middle_name"):
                self.entry_middlename.delete(0, tk.END)
                self.entry_middlename.insert(0, self.data.get("contact_middle_name"))
                
            if self.data.get("contact_number"):
                self.entry_contact.delete(0, tk.END)
                self.entry_contact.insert(0, self.data.get("contact_number"))
                
            if self.data.get("relationship_to_patient"):
                self.entry_relationship.delete(0, tk.END)
                self.entry_relationship.insert(0, self.data.get("relationship_to_patient"))
                
            if self.data.get("contact_address"):
                self.entry_address.delete(0, tk.END)
                self.entry_address.insert(0, self.data.get("contact_address"))
            
        except Exception as e:
            print(f"❌ Error restoring contact form data: {e}")

    def save_current_data(self):
        """Save current form data before navigating away"""
        try:
            self.data["contact_last_name"] = self.entry_lastname.get().strip()
            self.data["contact_first_name"] = self.entry_firstname.get().strip()
            self.data["contact_middle_name"] = self.entry_middlename.get().strip()
            self.data["contact_number"] = self.entry_contact.get().strip()
            self.data["relationship_to_patient"] = self.entry_relationship.get().strip()
            self.data["contact_address"] = self.entry_address.get().strip()
            
        except Exception as e:
            print(f"❌ Error saving current contact data: {e}")
    
    def populate_fields(self):
        """Populate fields with existing contact person data for editing"""
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()
                
                cursor.execute("""
                    SELECT cp.last_name, cp.first_name, cp.middle_name, 
                        cp.contact_number, cp.relationship, cp.address
                    FROM patient_contact cp  -- Changed from 'contact_person'
                    WHERE cp.patient_id = %s
                """, (self.patient_id,))
                
                contact_data = cursor.fetchone()
                
                if contact_data:
                    # Clear and populate fields only if value is not 'Type Here' or None
                    if contact_data[0] and contact_data[0] != 'Type Here':
                        self.entry_lastname.delete(0, tk.END)
                        self.entry_lastname.insert(0, contact_data[0])
                    
                    if contact_data[1] and contact_data[1] != 'Type Here':
                        self.entry_firstname.delete(0, tk.END)
                        self.entry_firstname.insert(0, contact_data[1])
                    
                    if contact_data[2] and contact_data[2] != 'Type Here':
                        self.entry_middlename.delete(0, tk.END)
                        self.entry_middlename.insert(0, contact_data[2])
                    
                    if contact_data[3] and contact_data[3] != 'Type Here':
                        self.entry_contact.delete(0, tk.END)
                        self.entry_contact.insert(0, contact_data[3])
                    
                    if contact_data[4] and contact_data[4] != 'Type Here':
                        self.entry_relationship.delete(0, tk.END)
                        self.entry_relationship.insert(0, contact_data[4])
                    
                    if contact_data[5] and contact_data[5] != 'Type Here':
                        self.entry_address.delete(0, tk.END)
                        self.entry_address.insert(0, contact_data[5])
                
                cursor.close()
                connect.close()
                
            except Exception as e:
                print(f"Error populating fields: {e}")

    def open_next(self, data=None):
        try:
            self.data["contact_last_name"] = self.entry_lastname.get().strip()
            self.data["contact_first_name"] = self.entry_firstname.get().strip()
            self.data["contact_middle_name"] = self.entry_middlename.get().strip()
            self.data["contact_number"] = self.entry_contact.get().strip()
            self.data["relationship_to_patient"] = self.entry_relationship.get().strip()
            self.data["contact_address"] = self.entry_address.get().strip()

            # Pass edit mode and patient_id forward
            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 2 input: ", e)
        
class RelativeInfoWindow(BaseWindow):
    def __init__(self, parent, data=None):
        # Check if we're in edit mode
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Relative Information", next_window=PhilHealthInfoWindow, previous_window=ContactPersonWindow)
        self.data = data if data else {}

        # Title Label - change based on mode
        title_text = "Edit Relative Information" if self.edit_mode else "Relative Information"
        tk.Label(self, text=title_text, font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        self.entry_lastname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_lastname.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="First Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        self.entry_firstname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_firstname.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Middle Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        self.entry_middlename = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_middlename.place(x=720, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=270)

        # Contact Number
        tk.Label(self, text="Contact Number*", font=("Merriweather Sans bold",15), bg="white").place(x=120, y=310)
        self.entry_contact = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_contact.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        # Complete Address
        tk.Label(self, text="Complete Address*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        self.entry_address = TextField_Patients(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_address.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=510)

        #Load data for both edit mode AND add mode
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        """Restore form data when navigating back in add mode"""
        try:
            if self.data.get("relative_last_name"):
                self.entry_lastname.delete(0, tk.END)
                self.entry_lastname.insert(0, self.data.get("relative_last_name"))
                
            if self.data.get("relative_first_name"):
                self.entry_firstname.delete(0, tk.END)
                self.entry_firstname.insert(0, self.data.get("relative_first_name"))
                
            if self.data.get("relative_middle_name"):
                self.entry_middlename.delete(0, tk.END)
                self.entry_middlename.insert(0, self.data.get("relative_middle_name"))
                
            if self.data.get("relative_contact_number"):
                self.entry_contact.delete(0, tk.END)
                self.entry_contact.insert(0, self.data.get("relative_contact_number"))
                
            if self.data.get("relative_address"):
                self.entry_address.delete(0, tk.END)
                self.entry_address.insert(0, self.data.get("relative_address"))
            
        except Exception as e:
            print(f"❌ Error restoring relative form data: {e}")

    def save_current_data(self):
        """Save current form data before navigating away"""
        try:
            self.data["relative_last_name"] = self.entry_lastname.get().strip()
            self.data["relative_first_name"] = self.entry_firstname.get().strip()
            self.data["relative_middle_name"] = self.entry_middlename.get().strip()
            self.data["relative_contact_number"] = self.entry_contact.get().strip()
            self.data["relative_address"] = self.entry_address.get().strip()
            
        except Exception as e:
            print(f"❌ Error saving current relative data: {e}")


    def populate_fields(self):
        """Populate fields with existing relative data for editing"""
        if self.patient_id:
            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT r.last_name, r.first_name, r.middle_name, 
                        r.contact_number, r.address
                    FROM patient_relative r  -- Changed from 'relatives'
                    WHERE r.patient_id = %s
                """, (self.patient_id,))

                relative_data = cursor.fetchone()

                if relative_data:
                    # Clear and populate fields only if value is not 'Type Here' or None
                    if relative_data[0] and relative_data[0] != 'Type Here':
                        self.entry_lastname.delete(0, tk.END)
                        self.entry_lastname.insert(0, relative_data[0])

                    if relative_data[1] and relative_data[1] != 'Type Here':
                        self.entry_firstname.delete(0, tk.END)
                        self.entry_firstname.insert(0, relative_data[1])

                    if relative_data[2] and relative_data[2] != 'Type Here':
                        self.entry_middlename.delete(0, tk.END)
                        self.entry_middlename.insert(0, relative_data[2])

                    if relative_data[3] and relative_data[3] != 'Type Here':
                        self.entry_contact.delete(0, tk.END)
                        self.entry_contact.insert(0, relative_data[3])

                    if relative_data[4] and relative_data[4] != 'Type Here':
                        self.entry_address.delete(0, tk.END)
                        self.entry_address.insert(0, relative_data[4])

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")

    def open_next(self, data=None):
        try:
            self.data["relative_last_name"] = self.entry_lastname.get().strip()
            self.data["relative_first_name"] = self.entry_firstname.get().strip()
            self.data["relative_middle_name"] = self.entry_middlename.get().strip()
            self.data["relative_contact_number"] = self.entry_contact.get().strip()
            self.data["relative_address"] = self.entry_address.get().strip()

            # Pass edit mode and patient_id forward
            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 3 input: ", e)

class PhilHealthInfoWindow(BaseWindow):
    def __init__(self, parent, data=None):
        # Check if we're in edit mode
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "PhilHealth and Other Info", next_window=PatientHistory1Window, previous_window=RelativeInfoWindow)
        self.data = data if data else {}

        # Title Label - change based on mode
        title_text = "Edit PhilHealth and Other Info" if self.edit_mode else "PhilHealth and Other Info"
        tk.Label(self, text=title_text, font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # PhilHealth Number & Membership
        tk.Label(self, text="PhilHealth Number *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        self.entry_philhealth = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_philhealth.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Membership *", font=("Merriweather Sans bold",15), bg="white").place(x=420, y=190)
        self.entry_membership = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_membership.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        #  FIXED: PWD Radio Buttons 
        tk.Label(self, text="PWD", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        self.pwd_var = tk.IntVar() 

        tk.Radiobutton(self, text="Yes", variable=self.pwd_var, value=1, bg="white", font=("Merriweather Sans", 12)).place(x=120, y=350)
        tk.Radiobutton(self, text="No", variable=self.pwd_var, value=0, bg="white", font=("Merriweather Sans", 12)).place(x=180, y=350)

        # PWD ID Number
        tk.Label(self, text="PWD ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        self.entry_pwd_id = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_pwd_id.place(x=420, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        #  FIXED: Senior Radio Buttons 
        tk.Label(self, text="Senior", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=440)
        self.senior_var = tk.IntVar() 
        tk.Radiobutton(self, text="Yes", variable=self.senior_var, value=1, bg="white", font=("Merriweather Sans", 12)).place(x=120, y=480)
        tk.Radiobutton(self, text="No", variable=self.senior_var, value=0, bg="white", font=("Merriweather Sans", 12)).place(x=180, y=480)

        # Senior ID Number
        tk.Label(self, text="Senior ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=430)
        self.entry_senior_id = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_senior_id.place(x=420, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=510)
        
        # Load data for both edit mode AND add mode
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        """Restore form data when navigating back in add mode"""
        try:
            if self.data.get("philhealth_number"):
                self.entry_philhealth.delete(0, tk.END)
                self.entry_philhealth.insert(0, self.data.get("philhealth_number"))
                
            if self.data.get("membership_type"):
                self.entry_membership.delete(0, tk.END)
                self.entry_membership.insert(0, self.data.get("membership_type"))
                
            # Restore radio button values
            if "is_pwd" in self.data:
                self.pwd_var.set(self.data.get("is_pwd"))
                
            if "is_senior" in self.data:
                self.senior_var.set(self.data.get("is_senior"))
                
            if self.data.get("pwd_id"):
                self.entry_pwd_id.delete(0, tk.END)
                self.entry_pwd_id.insert(0, self.data.get("pwd_id"))
                
            if self.data.get("senior_id"):
                self.entry_senior_id.delete(0, tk.END)
                self.entry_senior_id.insert(0, self.data.get("senior_id"))
            
        except Exception as e:
            print(f"❌ Error restoring PhilHealth form data: {e}")

    def save_current_data(self):
        """Save current form data before navigating away"""
        try:
            self.data["philhealth_number"] = self.entry_philhealth.get().strip()
            self.data["membership_type"] = self.entry_membership.get().strip()
            self.data["is_pwd"] = self.pwd_var.get()
            self.data["is_senior"] = self.senior_var.get()
            self.data["pwd_id"] = self.entry_pwd_id.get().strip()
            self.data["senior_id"] = self.entry_senior_id.get().strip()
            
        except Exception as e:
            print(f"❌ Error saving current PhilHealth data: {e}")

    def populate_fields(self):
        """Populate fields with existing PhilHealth data for editing"""
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
                    # Clear and populate fields only if value is not 'Type Here' or None
                    if philhealth_data[0] and philhealth_data[0] != 'Type Here':
                        self.entry_philhealth.delete(0, tk.END)
                        self.entry_philhealth.insert(0, philhealth_data[0])

                    if philhealth_data[1] and philhealth_data[1] != 'Type Here':
                        self.entry_membership.delete(0, tk.END)
                        self.entry_membership.insert(0, philhealth_data[1])

                    self.pwd_var.set(1 if philhealth_data[2] else 0)
                    
                    # PWD ID field
                    self.entry_pwd_id.delete(0, tk.END)
                    if philhealth_data[3] and str(philhealth_data[3]).strip() and philhealth_data[3] != 'Type Here':
                        self.entry_pwd_id.insert(0, str(philhealth_data[3]))

                    # Senior radio button
                    self.senior_var.set(1 if philhealth_data[4] else 0)
                    
                    # Senior ID field
                    self.entry_senior_id.delete(0, tk.END)
                    if philhealth_data[5] and str(philhealth_data[5]).strip() and philhealth_data[5] != 'Type Here':
                        self.entry_senior_id.insert(0, str(philhealth_data[5]))

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")

    def open_next(self, data=None):
        try:
            self.data["philhealth_number"] = self.entry_philhealth.get().strip()
            self.data["membership_type"] = self.entry_membership.get().strip()

            # Get radio button values
            self.data["is_pwd"] = self.pwd_var.get()
            self.data["is_senior"] = self.senior_var.get()

            self.data["pwd_id"] = self.entry_pwd_id.get().strip()
            self.data["senior_id"] = self.entry_senior_id.get().strip()

            # Pass edit mode and patient_id forward
            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 4 input: ", e)

class PatientHistory1Window(BaseWindow):
    def __init__(self, parent, data=None):
        # Check if we're in edit mode
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None
        
        super().__init__(parent, "Patient History Part 1", next_window=PatientHistory2Window, previous_window=PhilHealthInfoWindow)
        self.data = data if data else {}

        # Title Label - change based on mode
        title_text = "Edit Patient History Part 1" if self.edit_mode else "Patient History Part 1"
        tk.Label(self, text=title_text, font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        self.family_hypertension = tk.BooleanVar()
        self.family_diabetes = tk.BooleanVar()
        self.family_malignancy = tk.BooleanVar()
        
        tk.Checkbutton(self, variable=self.family_hypertension, bg="white").place(x=120, y=240)
        tk.Label(self, text="Hypertension", font=("Merriweather Sans bold", 12), bg="white").place(x=140, y=240)

        tk.Checkbutton(self, variable=self.family_diabetes, bg="white").place(x=320, y=240)
        tk.Label(self, text="Diabetes Mellitus", font=("Merriweather Sans bold", 12), bg="white").place(x=340, y=240)

        tk.Checkbutton(self, variable=self.family_malignancy, bg="white").place(x=520, y=240)
        tk.Label(self, text="Malignancy", font=("Merriweather Sans bold", 12), bg="white").place(x=540, y=240)

        # Other Family History
        tk.Label(self, text="Other:", font=("Merriweather Sans bold", 12), bg="white").place(x=140, y=300)
        self.family_other = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.family_other.place(x=140 , y=340, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=140, y=370)

        # Medical History
        tk.Label(self, text="Medical History*", font=("Merriweather sans bold", 15), bg="white").place(x=120, y=400)

        self.med_kidney_disease = tk.BooleanVar()
        self.med_urinary_stone = tk.BooleanVar()
        self.med_recurrent_uti = tk.BooleanVar()
        self.med_diabetes_type = tk.BooleanVar()
        
        tk.Checkbutton(self, variable=self.med_kidney_disease, bg="white").place(x=120, y=450)
        tk.Label(self, text="Hypertension prior to kidney disease", font=("Merriweather Sans bold", 12), bg="white").place(x=140, y=450)

        tk.Checkbutton(self, variable=self.med_urinary_stone, bg="white").place(x=320, y=450)
        tk.Label(self, text="Urinary Stone", font=("Merriweather Sans bold", 12), bg="white").place(x=340, y=450)

        tk.Checkbutton(self, variable=self.med_recurrent_uti, bg="white").place(x=520, y=450)
        tk.Label(self, text="Recurrent UTI", font=("Merriweather Sans bold", 12), bg="white").place(x=540, y=450)

        tk.Checkbutton(self, variable=self.med_diabetes_type, bg="white").place(x=720, y=450)
        tk.Label(self, text="Diabetes Mellitus Type", font=("Merriweather Sans bold", 12), bg="white").place(x=740, y=450)

        # Other Medical History
        tk.Label(self, text="Other:", font=("Merriweather Sans bold", 12), bg="white").place(x=140, y=510)
        self.med_other1 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.med_other1.place(x=140, y=550, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=140, y=580)

        # Load data for both edit mode AND add mode
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        """Restore form data when navigating back in add mode"""
        try:
            # Restore checkbox values
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
                
            # Restore text fields
            if self.data.get("family_other"):
                self.family_other.delete(0, tk.END)
                self.family_other.insert(0, self.data.get("family_other"))
                
            if self.data.get("med_other1"):
                self.med_other1.delete(0, tk.END)
                self.med_other1.insert(0, self.data.get("med_other1"))
            
        except Exception as e:
            print(f"❌ Error restoring Patient History 1 form data: {e}")

    def save_current_data(self):
        """Save current form data before navigating away"""
        try:
            self.data["family_hypertension"] = self.family_hypertension.get()
            self.data["family_diabetes"] = self.family_diabetes.get()
            self.data["family_malignancy"] = self.family_malignancy.get()
            self.data["family_other"] = self.family_other.get().strip()
            self.data["med_kidney_disease"] = self.med_kidney_disease.get()
            self.data["med_urinary_stone"] = self.med_urinary_stone.get()
            self.data["med_recurrent_uti"] = self.med_recurrent_uti.get()
            self.data["med_diabetes_type"] = self.med_diabetes_type.get()
            self.data["med_other1"] = self.med_other1.get().strip()
            
        except Exception as e:
            print(f"❌ Error saving current Patient History 1 data: {e}")

    def populate_fields(self):
        """Populate fields with existing patient history data for editing"""
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
                    self.family_other.delete(0, tk.END)
                    self.family_other.insert(0, history_data[3] if history_data[3] else '')

                    self.med_kidney_disease.set(bool(history_data[4]))
                    self.med_urinary_stone.set(bool(history_data[5]))
                    self.med_recurrent_uti.set(bool(history_data[6]))
                    self.med_diabetes_type.set(bool(history_data[7]))
                    self.med_other1.delete(0, tk.END)
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
            self.data["family_other"] = self.family_other.get().strip()
            self.data["med_kidney_disease"] = self.med_kidney_disease.get()
            self.data["med_urinary_stone"] = self.med_urinary_stone.get()
            self.data["med_recurrent_uti"] = self.med_recurrent_uti.get()
            self.data["med_diabetes_type"] = self.med_diabetes_type.get()
            self.data["med_other1"] = self.med_other1.get().strip()

            # Pass edit mode and patient_id forward
            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 5 input: ", e)
        
class PatientHistory2Window(BaseWindow):
    def __init__(self, parent, data=None):
        # Check if we're in edit mode
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Patient History Part 2", next_window=PatientHistory3Window, previous_window=PatientHistory1Window)
        self.data = data if data else {}

        # Title Label - change based on mode
        title_text = "Edit Patient History Part 2" if self.edit_mode else "Patient History Part 2"
        tk.Label(self, text=title_text, font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # History of Present Illness
        tk.Label(self, text="History of Present Illness*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        self.history_illness = tk.Text(self, width=80, height=5, font=("Merriweather light", 12), bg="white", bd=1, relief="solid")
        self.history_illness.place(x=120, y=240)
        self.add_placeholder(self.history_illness, "Type here")

        # Pertinent Past Medical History
        tk.Label(self, text="Pertinent Past Medical History *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=400)
        self.past_medical_history = tk.Text(self, width=80, height=5, font=("Merriweather light", 12), bg="white", bd=1, relief="solid")
        self.past_medical_history.place(x=120, y=450)
        self.add_placeholder(self.past_medical_history, "Type here")

        # Load data for both edit mode AND add mode
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        """Restore form data when navigating back in add mode"""
        try:
            if self.data.get("history_illness"):
                self.history_illness.delete("1.0", "end")
                self.history_illness.insert("1.0", self.data.get("history_illness"))
                self.history_illness.config(fg="black")
                
            if self.data.get("past_medical_history"):
                self.past_medical_history.delete("1.0", "end")
                self.past_medical_history.insert("1.0", self.data.get("past_medical_history"))
                self.past_medical_history.config(fg="black")
            
        except Exception as e:
            print(f"❌ Error restoring Patient History 2 form data: {e}")

    def save_current_data(self):
        """Save current form data before navigating away"""
        try:
            self.data["history_illness"] = self.history_illness.get("1.0", "end-1c").strip()
            self.data["past_medical_history"] = self.past_medical_history.get("1.0", "end-1c").strip()
            
        except Exception as e:
            print(f"❌ Error saving current Patient History 2 data: {e}")
        
    def populate_fields(self):
        """Populate fields with existing patient history data for editing"""
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
                    # Clear and populate fields only if value is not 'Type Here' or None
                    illness_text = history_data[0] if history_data[0] else ''
                    past_medical_text = history_data[1] if history_data[1] else ''

                    self.history_illness.delete("1.0", "end")
                    self.history_illness.insert("1.0", illness_text)
                    self.history_illness.config(fg="black" if illness_text else "gray")

                    self.past_medical_history.delete("1.0", "end")
                    self.past_medical_history.insert("1.0", past_medical_text)
                    self.past_medical_history.config(fg="black" if past_medical_text else "gray")

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")

    def add_placeholder(self, text_widget, placeholder):
        """Adds a placeholder to a Text widget and handles focus events."""
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
            self.data["history_illness"] = self.history_illness.get("1.0", "end-1c").strip()
            self.data["past_medical_history"] = self.past_medical_history.get("1.0", "end-1c").strip()

            # Pass edit mode and patient_id forward
            self.data["edit_mode"] = self.edit_mode
            self.data["patient_id"] = self.patient_id
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 6 input: ", e)

class PatientHistory3Window(BaseWindow):
    def __init__(self, parent, data):
        # Check if we're in edit mode
        self.edit_mode = data.get('edit_mode', False) if data else False
        self.patient_id = data.get('patient_id') if data else None

        super().__init__(parent, "Patient History Part 3", next_window=MedicationWindow, previous_window=PatientHistory2Window)
        self.data = data if data else {}

        # Title Label - change based on mode
        title_text = "Edit Patient History Part 3" if self.edit_mode else "Patient History Part 3"
        tk.Label(self, text=title_text, font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # Date of First Diagnosed having Kidney Disease 
        tk.Label(self, text="Date of First Diagnosed having Kidney Disease*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        self.entry_diagnosed = DateEntry(self, width=18, font=("Merriweather light", 12), bg="white", date_pattern="yyyy-MM-dd", state="readonly")
        self.entry_diagnosed.place(x=120, y=240, height=25)

        tk.Label(self, text="Date of First Dialysis", font=("Merriweather Sans bold", 15), bg="white").place(x=750, y=190)
        self.entry_dialysis = DateEntry(self, width=18, font=("Merriweather light", 12), bg="white", date_pattern="yyyy-MM-dd", state="readonly")
        self.entry_dialysis.place(x=750, y=240, height=25)

        # Mode & Access
        tk.Label(self, text="Mode *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        self.entry_mode = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_mode.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Access *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        self.entry_access = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_access.place(x=420, y=360, height=30)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Chronic Hemodialysis & Clinical Impression
        tk.Label(self, text="Date of First Chronic Hemodialysis", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        self.entry_chronic = DateEntry(self, width=18, font=("Merriweather light", 12), bg="white", date_pattern="yyyy-MM-dd", state="readonly")
        self.entry_chronic.place(x=120, y=480, height=25)

        tk.Label(self, text="Clinical Impression*", font=("Merriweather Sans bold", 15), bg="white").place(x=550, y=430)
        self.entry_clinical = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_clinical.place(x=550, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=550, y=510)

        # Load data for both edit mode AND add mode
        if self.edit_mode and self.patient_id:
            self.populate_fields()
        elif not self.edit_mode and self.data:
            self.restore_form_data()

    def restore_form_data(self):
        """Restore form data when navigating back in add mode"""
        try:
            if self.data.get("date_diagnosed"):
                from datetime import datetime
                date_diagnosed = datetime.strptime(self.data.get("date_diagnosed"), "%Y-%m-%d").date()
                self.entry_diagnosed.set_date(date_diagnosed)
                
            if self.data.get("date_dialysis"):
                date_dialysis = datetime.strptime(self.data.get("date_dialysis"), "%Y-%m-%d").date()
                self.entry_dialysis.set_date(date_dialysis)
                
            if self.data.get("mode"):
                self.entry_mode.delete(0, tk.END)
                self.entry_mode.insert(0, self.data.get("mode"))
                
            if self.data.get("access"):
                self.entry_access.delete(0, tk.END)
                self.entry_access.insert(0, self.data.get("access"))
                
            if self.data.get("date_chronic"):
                date_chronic = datetime.strptime(self.data.get("date_chronic"), "%Y-%m-%d").date()
                self.entry_chronic.set_date(date_chronic)
                
            if self.data.get("clinical_impression"):
                self.entry_clinical.delete(0, tk.END)
                self.entry_clinical.insert(0, self.data.get("clinical_impression"))
            
        except Exception as e:
            print(f"❌ Error restoring Patient History 3 form data: {e}")

    def save_current_data(self):
        """Save current form data before navigating away"""
        try:
            self.data["date_diagnosed"] = self.entry_diagnosed.get_date().strftime("%Y-%m-%d")
            self.data["date_dialysis"] = self.entry_dialysis.get_date().strftime("%Y-%m-%d")
            self.data["mode"] = self.entry_mode.get().strip()
            self.data["access"] = self.entry_access.get().strip()
            self.data["date_chronic"] = self.entry_chronic.get_date().strftime("%Y-%m-%d")
            self.data["clinical_impression"] = self.entry_clinical.get().strip()
            
        except Exception as e:
            print(f"❌ Error saving current Patient History 3 data: {e}")

    def populate_fields(self):
        """Populate fields with existing patient history data for editing"""
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
                    # Clear and populate fields only if value is not 'Type Here' or None
                    if history_data[0]:
                        self.entry_diagnosed.set_date(history_data[0])
                    if history_data[1]:
                        self.entry_dialysis.set_date(history_data[1])
                    if history_data[2] and history_data[2] != 'Type Here':
                        self.entry_mode.delete(0, tk.END)
                        self.entry_mode.insert(0, history_data[2])
                    if history_data[3] and history_data[3] != 'Type Here':
                        self.entry_access.delete(0, tk.END)
                        self.entry_access.insert(0, history_data[3])
                    if history_data[4]:
                        self.entry_chronic.set_date(history_data[4])
                    if history_data[5] and history_data[5] != 'Type Here':
                        self.entry_clinical.delete(0, tk.END)
                        self.entry_clinical.insert(0, history_data[5])

                cursor.close()
                connect.close()

            except Exception as e:
                print(f"Error populating fields: {e}")
    
    def open_next(self, data=None):
        try:
            self.data["date_diagnosed"] = self.entry_diagnosed.get_date().strftime("%Y-%m-%d")
            self.data["date_dialysis"] = self.entry_dialysis.get_date().strftime("%Y-%m-%d")
            self.data["mode"] = self.entry_mode.get().strip()
            self.data["access"] = self.entry_access.get().strip()
            self.data["date_chronic"] = self.entry_chronic.get_date().strftime("%Y-%m-%d")
            self.data["clinical_impression"] = self.entry_clinical.get().strip()

            # Pass edit mode and patient_id forward
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

        # Title Label - change based on mode
        title_text = "Edit Medications" if self.edit_mode else "Medication"
        tk.Label(self.main_frame, text=title_text, font=("Merriweather bold", 25), bg="white").pack(pady=20)

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

        # Load medications if in edit mode
        if self.edit_mode and self.patient_id:
            self.load_existing_medications()
        else:
            # Restore Previous Slots or Initialize New Slots
            if not MedicationWindow.medication_slots:
                for i in range(9):  # Default 9 slots
                    MedicationWindow.medication_slots.append("")
        
        for i, value in enumerate(MedicationWindow.medication_slots):
            self.add_medication_slot(i + 1, value)

        #+ Another Slot Button
        self.add_slot_button = tk.Button(
            self.grid_frame, text="+ Another Slot", font=("Merriweather Sans bold", 14),
            fg="blue", bg="white", bd=0, cursor="hand2", command=self.add_new_slot
        )
        self.add_slot_button.grid(row=len(self.medication_entries) // self.max_columns, column=len(self.medication_entries) % self.max_columns, padx=10, pady=10)

        self.right_panel = tk.Frame(self.main_frame, bg="white", width=200)
        self.right_panel.pack(side="right", fill="y", padx=20, pady=10)

        # Mouse Scroll
        self.bind_scroll_events()

    def save_current_data(self):
        """ NEW: Save current medication data"""
        try:
            # Update the class-level medication slots with current values
            for i, entry in enumerate(self.medication_entries):
                if i < len(MedicationWindow.medication_slots):
                    MedicationWindow.medication_slots[i] = entry.get().strip()
                else:
                    MedicationWindow.medication_slots.append(entry.get().strip())
            
        except Exception as e:
            print(f"❌ Error saving current medication data: {e}")

    def load_existing_medications(self):
        """Load existing medications for editing"""
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
                
                # Clear existing slots
                MedicationWindow.medication_slots.clear()
                
                # Add medications to slots
                for med in medications:
                    if med[0] and med[0] != 'Type Here':
                        MedicationWindow.medication_slots.append(med[0])
                
                # Ensure at least 9 slots
                while len(MedicationWindow.medication_slots) < 9:
                    MedicationWindow.medication_slots.append("")
                
                cursor.close()
                connect.close()
                
            except Exception as e:
                print(f"Error loading medications: {e}")

    def add_medication_slot(self, slot_number, value=""):
        frame = tk.Frame(self.grid_frame, bg="white", bd=1)
        frame.grid(row=len(self.medication_entries) // self.max_columns, column=len(self.medication_entries) % self.max_columns, padx=10, pady=10)

        tk.Label(frame, text=f"Medication {slot_number}", font=("Merriweather Sans bold", 12), bg="white").pack(anchor="w")
        entry = TextField_Patients(frame, width=15, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry.pack(anchor="w", pady=5)
        tk.Frame(frame, bg="black", height=1, width=150).pack(anchor="w", pady=5)

        # Clear placeholder when populating with real data
        if value and value != 'Type Here' and value.strip():
            current_text = entry.get()
            if current_text == "Type Here":
                entry.delete(0, tk.END)
            
            # Insert the real medication value
            entry.insert(0, value)
            
            entry.config(fg="black")
        else:
            pass
            
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
        """Save slots"""
        for i, entry in enumerate(self.medication_entries):
            MedicationWindow.medication_slots[i] = entry.get().strip()
        print("Saved Medications:", MedicationWindow.medication_slots)
    
    def bind_scroll_events(self):
        """Enable mouse."""
        def on_mousewheel(event):
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)  
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def refresh_homepage_recent_patient(self):
        """Refresh the homepage recent patient display after adding/updating a patient"""
        try:
            # Find the main application window (HomePage)
            current_window = self.master
            while current_window and not hasattr(current_window, 'pages'):
                current_window = current_window.master
            
            # If we found the HomePage and it has a Home page
            if current_window and hasattr(current_window, 'pages') and 'Home' in current_window.pages:
                home_page = current_window.pages['Home']
                if hasattr(home_page, 'refresh_recent_patient'):
                    home_page.refresh_recent_patient()
                    print("✅ Homepage recent patient refreshed successfully!")
        except Exception as e:
            print(f"❌ Error refreshing homepage: {e}")

    def update_form(self):
        """ COMPLETE UPDATE FUNCTIONALITY"""
        if not self.edit_mode or not self.patient_id:
            print("Not in edit mode or no patient ID")
            return
            
        try:
            print(f"🔄 Updating patient {self.patient_id} with new data...")
            
            # Import the update functions
            from backend.crud import (
                update_patient_info, update_patient_contact, update_patient_relative,
                update_patient_benefits, update_patient_history, update_patient_medications,
                update_patient_list
            )
            
            # 1. Update Patient Information
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
            
            if update_patient_info(self.patient_id, patient_information):
                print("✅ Patient info updated successfully")
                self.refresh_homepage_recent_patient()
            else:
                print("❌ Error updating patient info")
                return

            # 2. Update Contact Information
            patient_contact_information = {
                "last_name": self.data.get("contact_last_name"),
                "first_name": self.data.get("contact_first_name"),
                "middle_name": self.data.get("contact_middle_name"), 
                "contact_number": self.data.get("contact_number"),
                "relationship": self.data.get("relationship_to_patient"),
                "address": self.data.get("contact_address")
            }
            
            if update_patient_contact(self.patient_id, patient_contact_information):
                print("✅ Contact info updated successfully")
            else:
                print("❌ Error updating contact info")
                return

            # 3. Update Relative Information
            patient_relative_information = {
                "last_name": self.data.get("relative_last_name"),
                "first_name": self.data.get("relative_first_name"),
                "middle_name": self.data.get("relative_middle_name"), 
                "contact_number": self.data.get("relative_contact_number"),
                "address": self.data.get("relative_address")
            }
            
            if update_patient_relative(self.patient_id, patient_relative_information):
                print("✅ Relative info updated successfully")
            else:
                print("❌ Error updating relative info")
                return

            # 4. Update Benefits Information
            patient_benefits = {
                "is_senior": self.data.get("is_senior"),
                "is_pwd": self.data.get("is_pwd"),
                "philhealth_number": self.data.get("philhealth_number"),
                "membership_type": self.data.get("membership_type"),
                "pwd_id": self.data.get("pwd_id"), 
                "senior_id": self.data.get("senior_id")
            }
            
            if update_patient_benefits(self.patient_id, patient_benefits):
                print("✅ Benefits info updated successfully")
            else:
                print("❌ Error updating benefits info")
                return

            # 5. Update Patient History
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

            # Combine all history data
            patient_history_combined = {**patient_history_1, **patient_history_2, **patient_history_3}
            
            if update_patient_history(self.patient_id, patient_history_combined):
                print("✅ Patient history updated successfully")
            else:
                print("❌ Error updating patient history")
                return

            # 6. Update Medications
            medication_entries_row = [entry.get().strip() for entry in self.medication_entries if entry.get().strip() and entry.get().strip() != "Type Here"]
            
            if update_patient_medications(self.patient_id, medication_entries_row):
                print("✅ Medications updated successfully")
            else:
                print("❌ Error updating medications")
                return

            # 7. Update Patient List (main table)
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
                print("✅ Patient list updated successfully")
                self.refresh_homepage_recent_patient()
            else:
                print("❌ Error updating patient list")
                return
            
            self.destroy()
            
            print("✅ Update completed and window closed!")
            
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

            patient_information_column = ', '.join(patient_information.keys())
            patient_information_row = [f"{entries}" for entries in patient_information.values()]

            patient_contact_information = {
                "last_name": self.data.get("contact_last_name"),
                "first_name": self.data.get("contact_first_name"),
                "middle_name": self.data.get("contact_middle_name"), 
                "contact_number": self.data.get("contact_number"),
                "relationship": self.data.get("relationship_to_patient"),
                "address": self.data.get("contact_address")
            }

            patient_contact_information_column = ', '.join(patient_contact_information.keys())
            patient_contact_information_row = [f"{entries}" for entries in patient_contact_information.values()]

            patient_relative_information = {
                "last_name": self.data.get("relative_last_name"),
                "first_name": self.data.get("relative_first_name"),
                "middle_name": self.data.get("relative_middle_name"), 
                "contact_number": self.data.get("relative_contact_number"),
                "address": self.data.get("relative_address")
            }

            patient_relative_information_column = ', '.join(patient_relative_information.keys())
            patient_relative_information_row = [f"{entries}" for entries in patient_relative_information.values()]

            patient_benefits = {
                "is_senior": self.data.get("is_senior"),
                "is_pwd": self.data.get("is_pwd"),
                "philhealth_number": self.data.get("philhealth_number"),
                "membership_type": self.data.get("membership_type"),
                "pwd_id": self.data.get("pwd_id"), 
                "senior_id": self.data.get("senior_id")
            }

            patient_benefits_column = ', '.join(patient_benefits.keys())
            patient_benefits_row = [f"{entries}" for entries in patient_benefits.values()]

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

            medication_entries_row = [entries.get().strip() for entries in self.medication_entries]
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

            patient_full_name = ' '.join(name_validation)

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

            #this creates the main table which includes the patient id
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

            #retrieve all the data from patient list table
            cursor.execute("SELECT * FROM patient_list")
            list_result = cursor.fetchall()

            for i in list_result:
                print(i)

            #retrieve all the data from patient info table
            retrieve_patient_info = retrieve_form_data(pk_patient_id, patient_information_column, table_name='patient_info')
            print(retrieve_patient_info)
            
            #retrieve all the data from patient contact table
            retrieve_patient_contact = retrieve_form_data(pk_patient_id, patient_contact_information_column, table_name='patient_contact')
            print(retrieve_patient_contact)

            #retrieve all the data from patient relative table
            retrieve_patient_relative = retrieve_form_data(pk_patient_id, patient_relative_information_column, table_name='patient_relative')
            print(retrieve_patient_relative)

            #retrieve all the data from patient benefits table
            retrieve_patient_benefits = retrieve_form_data(pk_patient_id, patient_benefits_column, table_name='patient_benefits')
            print(retrieve_patient_benefits)

            #retrieve all the data from patient history table
            retrieve_patient_history = retrieve_form_data(pk_patient_id, patient_history_column, table_name='patient_history')
            print(retrieve_patient_history)

            #retrieve all the data from patient medications table
            cursor.execute(f"""
                SELECT m.medication_name FROM patient_medications pm 
                JOIN medicines m ON m.medication_id = pm.medication_id
                JOIN patient_info pi ON pm.patient_id = pi.patient_id 
                WHERE pi.patient_id = {pk_patient_id}
            """)          

            medication_result = cursor.fetchall()

            print(medication_result)
        
        except Exception as e:
            print("Error with submitting the form: ", e)
        
        finally:
            cursor.close()
            connect.close()