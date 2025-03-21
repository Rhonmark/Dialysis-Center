import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk
from components.buttons import Button
from components.textfields_patients import TextField_Patients
from backend.connector import db_connection as db
from backend.crud import submit_form_creation, submit_form_subcreation
import tkinter as tk
from tkcalendar import DateEntry

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
            self.btn_next = Button(self, text="Next", command=self.open_next)
            self.btn_next.place(x=1070, y=600, width=120, height=40)

        if not self.next_window: 
            self.btn_submit = Button(self, text="Submit", command=self.submit_form)
            self.btn_submit.place(x=1070, y=600, width=120, height=40)

        if self.previous_window:
            self.back_icon = PhotoImage(file="assets/back.png")
            self.btn_back = tk.Button(self, image=self.back_icon, bd=0, bg="white", activebackground="white", command=self.go_back)
            self.btn_back.place(x=50, y=25)

    def go_back(self):
        self.destroy()
        if self.previous_window:
            self.previous_window(self.parent, self.data if hasattr(self, "data") else None)

    def open_next(self, data=None):
        if self.next_window:
            self.destroy()
            self.next_window(self.master, data)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x700+{x}+{y}")

import tkinter as tk
from tkcalendar import DateEntry

class PatientInfoWindow(BaseWindow):
    def __init__(self, parent, data):
        super().__init__(parent, "Patient Information", next_window=ContactPersonWindow, previous_window=None)
        self.data = data

        # Title Label
        tk.Label(self, text="Patient Information", font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

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
        self.entry_birthdate = DateEntry(self, width=18, font=("Merriweather light", 12), bg="white", date_pattern="yyyy-MM-dd", state="readonly")
        self.entry_birthdate.place(x=720, y=320, height=25)

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

        tk.Label(self, text="Civil Status *", font=("Merriweather Sans bold",15), bg="white").place(x=720, y=390)
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
            
            super().open_next(self.data)

        except Exception as e:
            print("Error with step 1 input: ", e)

class ContactPersonWindow(BaseWindow):
    def __init__(self, parent, data=None):
        super().__init__(parent, "Contact Person Info", next_window=RelativeInfoWindow, previous_window=PatientInfoWindow)

        self.data = data

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

    def open_next(self, data=None):
        
        try:
            self.data["contact_last_name"] = self.entry_lastname.get().strip()
            self.data["contact_first_name"]= self.entry_firstname.get().strip()
            self.data["contact_middle_name"] = self.entry_middlename.get().strip()
            self.data["contact_contact_number"] = self.entry_contact.get().strip()
            self.data["contact_relationship"] = self.entry_relationship.get().strip()
            self.data["contact_address"] = self.entry_address.get().strip()

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 2 input: ", e)

class RelativeInfoWindow(BaseWindow):
    def __init__(self, parent, data=None):
        super().__init__(parent, "Relative Info", next_window=PhilHealthInfoWindow, previous_window=ContactPersonWindow)

        self.data = data
        # Title Label
        tk.Label(self, text="Relative Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

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

    def open_next(self, data=None):

        try:
            self.data["relative_last_name"] = self.entry_lastname.get().strip()
            self.data["relative_first_name"]= self.entry_firstname.get().strip()
            self.data["relative_middle_name"] = self.entry_middlename.get().strip()
            self.data["relative_contact_number"] = self.entry_contact.get().strip()
            self.data["relative_address"] = self.entry_address.get().strip()

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 3 input: ", e)

class PhilHealthInfoWindow(BaseWindow):
    def __init__(self, parent, data=None):
        super().__init__(parent, "PhilHealth and Other Info", next_window=PatientHistory1Window, previous_window=RelativeInfoWindow)
        self.data = data
        # Title Label
        tk.Label(self, text="PhilHealth and Other Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # PhilHealth Number & Membership
        tk.Label(self, text="PhilHealth Number *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        self.entry_philhealth = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_philhealth.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Membership *", font=("Merriweather Sans bold",15), bg="white").place(x=420, y=190)
        self.entry_membership = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_membership.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)
        

        # PWD & PWD ID Number
        tk.Label(self, text="PWD", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        self.pwd_var = tk.BooleanVar()
        tk.Checkbutton(self, variable=self.pwd_var, bg="white").place(x=120, y=350)
        tk.Label(self, text="Person with Disability", font=("Merriweather Sans bold", 12), bg="white").place(x=140, y=350)

        tk.Label(self, text="PWD ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        self.entry_pwd_id = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_pwd_id.place(x=420, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Senior & Senior ID Number
        tk.Label(self, text="Senior", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=440)
        self.senior_var = tk.BooleanVar()
        tk.Checkbutton(self, variable=self.senior_var, bg="white").place(x=120, y=480)
        tk.Label(self, text="Senior Citizen", font=("Merriweather Sans bold", 12), bg="white").place(x=140, y=480)

        tk.Label(self, text="Senior ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=430)
        self.entry_senior_id = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_senior_id.place(x=420, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=510)

    def open_next(self, data=None):
        try:

            is_pwd = 1 if self.pwd_var.get() else 0
            is_senior = 1 if self.senior_var.get() else 0

            self.data["philhealth_number"] = self.entry_philhealth.get().strip()
            self.data["membership_type"] = self.entry_membership.get().strip()
            self.data["is_pwd"] = is_pwd
            self.data["is_senior"] = is_senior
            self.data["pwd_id"] = self.entry_pwd_id.get().strip()
            self.data["senior_id"] = self.entry_senior_id.get().strip()

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 4 input: ", e)

class PatientHistory1Window(BaseWindow):
    def __init__(self, parent, data=None):
        super().__init__(parent, "Patient History Part 1", next_window=PatientHistory2Window, previous_window=PhilHealthInfoWindow)
        self.data = data
        tk.Label(self, text="Patient History Part 1 ", font=("Merriweather bold", 25, ), bg="white").place(x=90, y=100)

        # Family History
        tk.Label(self, text="Family History*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)

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
            self.data["med_other"] = self.med_other1.get().strip()

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 5 input: ", e)
        
class PatientHistory2Window(BaseWindow):
    def __init__(self, parent, data=None):
        super().__init__(parent, "Patient History Part 2", next_window=PatientHistory3Window, previous_window=PatientHistory1Window)
        self.data = data
        tk.Label(self, text="Patient History Part 2", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

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
            self.data["illness_history"] = self.history_illness.get("1.0", "end-1c").strip()
            self.data["medical_history"] = self.past_medical_history.get("1.0", "end-1c").strip()

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 6 input: ", e)

class PatientHistory3Window(BaseWindow):
    def __init__(self, parent, data):
        super().__init__(parent, "Patient History Part 3", next_window=MedicationWindow, previous_window=PatientHistory2Window)
        self.data = data
        tk.Label(self, text="Patient History Part 3", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

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
    
    def open_next(self, data=None):
        try:    
            self.data["history_3_diagnosed"] = self.entry_diagnosed.get_date().strftime("%Y-%m-%d")
            self.data["history_3_dialysis"] = self.entry_dialysis.get_date().strftime("%Y-%m-%d")
            self.data["history_3_mode"] = self.entry_mode.get().strip()
            self.data["history_3_access"] = self.entry_access.get().strip()
            self.data["history_3_chronic"] = self.entry_chronic.get_date().strftime("%Y-%m-%d")
            self.data["history_3_clinical"] = self.entry_clinical.get().strip()

            super().open_next(self.data)

        except Exception as e:
            print("Error with step 7 input: ", e)


class MedicationWindow(BaseWindow):
    medication_slots = [] #storage for medication slots

    def __init__(self, parent, data):
        self.data = data
        super().__init__(parent, "Medication", next_window=None, previous_window=PatientHistory3Window)
        self.medication_entries = []
        self.max_columns = 3 

        # Title Label
        tk.Label(self.main_frame, text="Medication", font=("Merriweather bold", 25), bg="white").pack(pady=20)

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

    def add_medication_slot(self, slot_number, value=""):
        frame = tk.Frame(self.grid_frame, bg="white", bd=1)
        frame.grid(row=len(self.medication_entries) // self.max_columns, column=len(self.medication_entries) % self.max_columns, padx=10, pady=10)

        tk.Label(frame, text=f"Medication {slot_number}", font=("Merriweather Sans bold", 12), bg="white").pack(anchor="w")
        entry = TextField_Patients(frame, width=15, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry.pack(anchor="w", pady=5)
        tk.Frame(frame, bg="black", height=1, width=150).pack(anchor="w", pady=5)

        entry.insert(0, value)  # Restore saved value
        self.medication_entries.append(entry)

    def add_new_slot(self):
        new_slot_number = len(self.medication_entries) + 1
        MedicationWindow.medication_slots.append("")  #extend storage
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

    def submit_form(self):
        
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
                "contact_number": self.data.get("contact_contact_number"),
                "relationship": self.data.get("contact_relationship"),
                "address": self.data.get("contact_address")
            }

            patient_contact_information_column = ', '.join(patient_contact_information.keys())
            patient_contact_information_row = [f"{entries}" for entries in patient_contact_information.values()]

            patient_relative_information = {
                "last_name": self.data.get("relative_last_name"),
                "first_name": self.data.get("relative_first_name"),
                "middle_name": self.data.get("relative_middle_name"), 
                "contact_number": self.data.get("relative_contact_number"),
                "address": self.data.get("relative_access")
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
                "other_medical_history": self.data.get("med_other")
            }

            patient_history_2 = {
                "present_illness_history": self.data.get("illness_history"), 
                "past_illness_history": self.data.get("medical_history"),
            }

            patient_history_3 = {
                "first_diagnosis": self.data.get("history_3_diagnosed"),
                "first_dialysis": self.data.get("history_3_dialysis"),
                "mode": self.data.get("history_3_mode"),
                "access_type": self.data.get("history_3_access"),
                "first_hemodialysis": self.data.get("history_3_chronic"),
                "clinical_impression": self.data.get("history_3_clinical"),
            }

            medication_entries_row = [entries.get().strip() for entries in self.medication_entries]
            medication_entries_data = ', '.join(medication_entries_row)

            print(medication_entries_row)
            print(medication_entries_data)

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
            
            #this creates the main table
            pk_patient_id = submit_form_creation(patient_information_column, patient_information_row, table_name='patient_info')

            if pk_patient_id:
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
            
            # medications_column = "drugs_taken"

            # create_patient_medications = submit_form_subcreation(
            #     medications_column,
            #     medication_entries_data,
            #     pk_patient_id,
            #     table_name='patient_medications'
            # )

            # if create_patient_medications:
            #    print("Step 6 input successfully created")
            # else:
            #     print("Error with step 6 input creation")
            #     return

            self.destroy()

        except Exception as e:
            print("Error with submitting the form: ", e)
        
        finally:
            cursor.close()
            connect.close()
