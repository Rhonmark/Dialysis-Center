import tkinter as tk
from tkinter import PhotoImage
from components.buttons import Button
from components.textfields_patients import TextField_Patients
from backend.connector import db_connection as db
from backend.crud import create_patient_info, create_contact_person, create_relative_info

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
        self.btn_exit.place(x=1250, y=10)  

        if self.next_window:
            self.btn_next = Button(self, text="Next", command=self.open_next)
            self.btn_next.place(x=1070, y=600, width=120, height=40)

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

class PatientInfoWindow(BaseWindow):
    def __init__(self, parent, data):

        super().__init__(parent, "Patient Information", next_window=ContactPersonWindow, previous_window=None)

        self.data = data

        # Title Label
        tk.Label(self, text="Patient Information", font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=120, y=150)
        self.entry_lastname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_lastname.place(x=120, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=230)

        tk.Label(self, text="First Name *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=420, y=150)
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
        self.entry_birthdate = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.entry_birthdate.place(x=720, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=350)

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
            last_name = self.entry_lastname.get().strip()
            first_name = self.entry_firstname.get().strip()
            middle_name = self.entry_middlename.get().strip()
            status = self.entry_status.get().strip()
            access_type = self.entry_access.get().strip()
            birthdate = self.entry_birthdate.get().strip()
            age = self.entry_age.get().strip()
            gender = self.entry_gender.get().strip()
            height = self.entry_height.get().strip()
            civil_status = self.entry_civil_status.get().strip()
            religion = self.entry_religion.get().strip()
            address = self.entry_address.get().strip()

            super().open_next({
                "last_name": last_name,
                "first_name": first_name,
                "middle_name": middle_name,
                "status": status,
                "access": access_type,
                "birthdate": birthdate,
                "age": age,
                "gender": gender,
                "height": height,
                "civil_status": civil_status,
                "religion": religion,
                "address": address})
            
            create_info = create_patient_info(last_name, first_name, middle_name, status, access_type, birthdate,
                              age, gender, height, civil_status, religion, address)

            if create_info:
                print("Successful with step 1 input!")

        except Exception as e:
            print("Error with step 1 input: ", e)

class ContactPersonWindow(BaseWindow):
    def __init__(self, parent, data):
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
            last_name = self.entry_lastname.get().strip()
            first_name = self.entry_firstname.get().strip()
            middle_name = self.entry_middlename.get().strip()
            contact_number = self.entry_contact.get().strip()
            relationship = self.entry_relationship.get().strip()
            address = self.entry_address.get().strip()

            super().open_next({
                "last_name": last_name,
                "first_name": first_name,
                "middle_name": middle_name,
                "contact_number": contact_number,
                "relationship": relationship,
                "address": address})
            
            create_contact = create_contact_person(last_name, first_name, middle_name, contact_number, relationship, address)

            if create_contact:
                print("Successful with step 2 input!")

        except Exception as e:
            print("Error with step 2 input: ", e)

        # print(last_name, first_name, middle_name, contact_number, relationship, address)

class RelativeInfoWindow(BaseWindow):
    def __init__(self, parent, data):
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
            last_name = self.entry_lastname.get().strip()
            first_name = self.entry_firstname.get().strip()
            middle_name = self.entry_middlename.get().strip()
            contact_number = self.entry_contact.get().strip()
            address = self.entry_address.get().strip()

            super().open_next({
                    "last_name": last_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "contact_number": contact_number,
                    "address": address})

            relative_info = create_relative_info(last_name, first_name, middle_name, contact_number, address)

            if relative_info:
                print("Successful with step 3 input!")

        except Exception as e:
            print("Error with step 3 input: ", e)

class PhilHealthInfoWindow(BaseWindow):
    def __init__(self, parent, data):
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
        philhealth_number = self.entry_philhealth.get().strip() 
        membership_type = self.entry_membership.get().strip()
        is_pwd = self.pwd_var.get() #bool
        is_senior = self.senior_var.get()
        pwd_id = self.entry_pwd_id.get().strip()
        senior_id = self.entry_senior_id.get().strip()  
        super().open_next({
            "philhealth_number": philhealth_number,
            "membership_type": membership_type, 
            "is_pwd": is_pwd,
            "is_senior": is_senior,
            "pwd_id": pwd_id,
            "senior_id": senior_id
        })

class PatientHistory1Window(BaseWindow):
    def __init__(self, parent, data):
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

        self.med_hypertension = tk.BooleanVar()
        self.med_urinary_stone = tk.BooleanVar()
        self.med_recurrent_uti = tk.BooleanVar()
        self.med_diabetes_type = tk.BooleanVar()
        
        tk.Checkbutton(self, variable=self.med_hypertension, bg="white").place(x=120, y=450)
        tk.Label(self, text="Hypertension", font=("Merriweather Sans bold", 12), bg="white").place(x=140, y=450)

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
            family_hypertension = self.family_hypertension.get()
            family_diabetes = self.family_diabetes.get()
            family_malignancy = self.family_malignancy.get()

            med_hypertension = self.med_hypertension.get()
            med_urinary_stone = self.med_urinary_stone.get()
            med_recurrent_uti = self.med_recurrent_uti.get()
            med_diabetes_type = self.med_diabetes_type.get()

            super().open_next({
                "family_hypertension": family_hypertension,
                "family_diabetes": family_diabetes,
                "family_malignancy": family_malignancy,
                " med_hypertension":  med_hypertension,
                "med_urinary_stone": med_urinary_stone,
                "med_recurrent_uti": med_recurrent_uti,
                "med_diabetes_type": med_diabetes_type
            })

            print(family_hypertension, family_diabetes, family_malignancy)
            print(med_hypertension, med_urinary_stone, med_recurrent_uti, med_diabetes_type)

        except Exception as e:
            print("Error with patient history 1: ", e)

        
class PatientHistory2Window(BaseWindow):
    def __init__(self, parent, data):
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


class PatientHistory3Window(BaseWindow):
    def __init__(self, parent, data):
        super().__init__(parent, "Patient History Part 3", next_window=MedicationWindow, previous_window=PatientHistory2Window)
        self.data = data
        tk.Label(self, text="Patient History Part 3", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Date of First Diagnosed having Kidney Disease 
        tk.Label(self, text="Date of First Diagnosed having Kidney Disease*", font=("Merriweather Sans bold", 15 ), bg="white").place(x=120, y=190)
        entry_diagnosed = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_diagnosed.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Date of First Dialysis", font=("Merriweather Sans bold", 15), bg="white").place(x=750, y=190)
        entry_dialysis = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_dialysis.place(x=750, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=750, y=270)

        # Mode & Access
        tk.Label(self, text="Mode *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_mode = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_mode.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Access *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        entry_access = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_access.place(x=420, y=360, height=30)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Chronic Hemodialysis & Clinical Impression
        tk.Label(self, text="Date of First Chronic Hemodialysis ", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_chronic = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_chronic.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=510)

        tk.Label(self, text="Clinical Impression*", font=("Merriweather Sans bold", 15), bg="white").place(x=550, y=430)
        entry_clinical = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_clinical.place(x=550, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=550, y=510)

class MedicationWindow(BaseWindow):
    def __init__(self, parent, data):
        super().__init__(parent, "Medication", next_window=None, previous_window=PatientHistory3Window)
        self.data = data
        # Title Label
        tk.Label(self, text="Medication", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Medication 1, Medication 2, Medication 3
        tk.Label(self, text="Medication 1", font=("Merriweather Sans bold", 14, "bold"), bg="white").place(x=120, y=190)
        entry_med1 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med1.place(x=120, y=240, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Medication 2", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        entry_med2 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med2.place(x=420, y=240, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Medication 3", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        entry_med3 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med3.place(x=720, y=240, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=720, y=270)

        # Medication 4, Medication 5, Medication 6
        tk.Label(self, text="Medication 4", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_med4 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med4.place(x=120, y=360, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Medication 5", font=("Merriweather Sans bold", 15 ), bg="white").place(x=420, y=310)
        entry_med5 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med5.place(x=420, y=360, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=420, y=390)

        tk.Label(self, text="Medication 6", font=("Merriweather Sans bold", 15 ), bg="white").place(x=720, y=310)
        entry_med6 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med6.place(x=720, y=360, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=720, y=390)

        # Medication 7 and "+ Another Slot"
        tk.Label(self, text="Medication 7", font=("Merriweather Sans bold", 15, ), bg="white").place(x=120, y=430)
        entry_med7 = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med7.place(x=120, y=480, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=120, y=510)

        tk.Label(self, text="+ Another Slot", font=("Merriweather Sans bold", 15), fg="blue",bg="white").place(x=420, y=430)

        self.btn_submit = Button(self, text="Submit", command=self.submit_data)
        self.btn_submit.place(x=1070, y=600, width=120, height=40)

    def submit_data(self):
        print("Submit button clicked!") 
        self.destroy()