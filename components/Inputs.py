import tkinter as tk
from tkinter import ttk
from components.buttons import Button
from components.buttons import BackButton


class BaseWindow(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry("1300x700")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True) 
        self.center_window()

        self.border_frame = tk.Frame(self, bg="black", bd=0.5) 
        self.border_frame.pack(expand=True, fill="both", padx=0, pady=0)

        self.main_frame = tk.Frame(self.border_frame, bg="white")
        self.main_frame.pack(expand=True, fill="both", padx=0.5, pady=0.5)

        self.sidebar = tk.Frame(self.main_frame, width=30, bg="#1A374D")
        self.sidebar.pack(side="left", fill="y")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x700+{x}+{y}")

class PatientInfoWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Patient Information")

        # Title Label
        tk.Label(self, text="Patient Information", font=("Merriweather bold", 25 ), bg="white").place(x=90, y=60)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=120, y=150)
        entry_lastname = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=120, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=230)

        tk.Label(self, text="First Name *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=420, y=150)
        entry_firstname = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=420, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=230)

        tk.Label(self, text="Middle Name", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=150)
        entry_middlename = tk.Entry(self, width=15, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=720, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=150).place(x=720, y=230)

        # Status, Type of Access, Birthdate, Age
        tk.Label(self, text="Status *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=270)
        entry_status = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_status.place(x=120, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=350)

        tk.Label(self, text="Type of Access *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=270)
        entry_access = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_access.place(x=420, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=350)

        tk.Label(self, text="Birthdate *", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=270)
        entry_birthdate = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_birthdate.place(x=720, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=350)

        tk.Label(self, text="Age *", font=("Merriweather Sans bold", 15), bg="white").place(x=1020, y=270)
        entry_age = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_age.place(x=1020, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=1020, y=350)

        # Gender, Height, Civil Status, Religion
        tk.Label(self, text="Gender *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=390)
        entry_gender = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_gender.place(x=120, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=470)

        tk.Label(self, text="Height *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=390)
        entry_height = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_height.place(x=420, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=470)

        tk.Label(self, text="Civil Status *", font=("Merriweather Sans bold",15), bg="white").place(x=720, y=390)
        entry_civil_status = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_civil_status.place(x=720, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=470)

        tk.Label(self, text="Religion *", font=("Merriweather Sans bold", 15), bg="white").place(x=1020, y=390)
        entry_religion = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_religion.place(x=1020, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=1020, y=470)

        # Complete Address 
        tk.Label(self, text="Complete Address *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=510)
        entry_address = tk.Entry(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=120, y=560, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=590)

        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)

    def open_next(self):
        self.destroy()
        ContactPersonWindow(self.master)

class ContactPersonWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Contact Person Info")

        # Back Button
        self.btn_back = BackButton(self, text="Back", command=self.go_back)
        self.btn_back.place(x=90, y=30, width=120, height=40)

        # Title Label
        tk.Label(self, text="Contact Person Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        entry_lastname = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="First Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        entry_firstname = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Middle Name", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        entry_middlename = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=720, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=270)

        # Contact Number, Relationship to the Patient
        tk.Label(self, text="Contact Number *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_contact = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_contact.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Relationship to the Patient *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        entry_relationship = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_relationship.place(x=420, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Complete Address 
        tk.Label(self, text="Complete Address *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_address = tk.Entry(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=510)

        
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)

    def go_back(self):
        self.destroy()
        PatientInfoWindow(self.master) 

    def open_next(self):
        self.destroy()
        RelativeInfoWindow(self.master)

class RelativeInfoWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Relative Info")

        # Back Button
        self.btn_back = BackButton(self, text="Back", command=self.go_back)
        self.btn_back.place(x=90, y=30, width=120, height=40)
        # Title Label
        tk.Label(self, text="Relative Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        entry_lastname = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="First Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        entry_firstname = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Middle Name", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        entry_middlename = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=720, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=270)

        # Contact Number
        tk.Label(self, text="Contact Number*", font=("Merriweather Sans bold",15), bg="white").place(x=120, y=310)
        entry_contact = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_contact.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        # Complete Address
        tk.Label(self, text="Complete Address*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_address = tk.Entry(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=510)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)

    def go_back(self):
        self.destroy()
        ContactPersonWindow(self.master) 

    def open_next(self):
        self.destroy()
        PhilHealthInfoWindow(self.master)

class PhilHealthInfoWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "PhilHealth and Other Info")

        # Back Button
        self.btn_back = BackButton(self, text="Back", command=self.go_back)
        self.btn_back.place(x=90, y=30, width=120, height=40)
        # Title Label
        tk.Label(self, text="PhilHealth and Other Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # PhilHealth Number & Membership
        tk.Label(self, text="PhilHealth Number *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        entry_philhealth = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_philhealth.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Membership *", font=("Merriweather Sans bold",15), bg="white").place(x=420, y=190)
        entry_membership = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_membership.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        # PWD & PWD ID Number
        tk.Label(self, text="PWD", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_pwd = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_pwd.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="PWD ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        entry_pwd_id = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_pwd_id.place(x=420, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Senior & Senior ID Number
        tk.Label(self, text="Senior", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_senior = tk.Entry(self, width=180, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_senior.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=510)

        tk.Label(self, text="Senior ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=430)
        entry_senior_id = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_senior_id.place(x=420, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=510)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)

    def go_back(self):
        self.destroy()
        RelativeInfoWindow(self.master) 

    def open_next(self):
        self.destroy()
        PatientHistory1Window(self.master)

class PatientHistory1Window(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Patient History Part 1")

        # Back Button
        self.btn_back = BackButton(self, text="Back", command=self.go_back)
        self.btn_back.place(x=90, y=30, width=120, height=40)
        tk.Label(self, text="Patient History Part 1 ", font=("Merriweather bold", 25, ), bg="white").place(x=90, y=100)

        # Family History
        tk.Label(self, text="Family History *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)

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
        self.family_other = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.family_other.place(x=140 , y=340, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=140, y=370)

        # Medical History
        tk.Label(self, text="Medical History *", font=("Merriweather sans bold", 15), bg="white").place(x=120, y=400)

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
        self.med_other1 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        self.med_other1.place(x=140, y=550, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=140, y=580)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)

    def go_back(self):
        self.destroy()
        PhilHealthInfoWindow(self.master) 

    def open_next(self):
        self.destroy()
        PatientHistory2Window(self.master)

class PatientHistory2Window(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Patient History Part 2")

        # Back Button
        self.btn_back = BackButton(self, text="Back", command=self.go_back)
        self.btn_back.place(x=90, y=30, width=120, height=40)
        tk.Label(self, text="Patient History Part 2", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # History of Present Illness
        tk.Label(self, text="History of Present Illness *", font=("Merriweather Sans bold", 15,), bg="white").place(x=120, y=190)
        self.history_illness = tk.Text(self, width=80, height=5, font=("Merriweather light", 12,), bg="white", bd=1, relief="solid")
        self.history_illness.insert("1.0", "Type here")  # Placeholder text
        self.history_illness.place(x=120, y=240)

        # Pertinent Past Medical History
        tk.Label(self, text="Pertinent Past Medical History *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=120, y=400)
        self.past_medical_history = tk.Text(self, width=80, height=5, font=("Merriweather light", 12,), bg="white", bd=1, relief="solid")
        self.past_medical_history.insert("1.0", "Type here")  # Placeholder text
        self.past_medical_history.place(x=120, y=450)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)

    def go_back(self):
        self.destroy()
        PatientHistory1Window(self.master) 

    def open_next(self):
        self.destroy()
        PatientHistory3Window(self.master)

class PatientHistory3Window(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Patient History Part 3")

        # Back Button
        self.btn_back = BackButton(self, text="Back", command=self.go_back)
        self.btn_back.place(x=90, y=30, width=120, height=40)

        tk.Label(self, text="Patient History Part 3", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Date of First Diagnosed having Kidney Disease 
        tk.Label(self, text="Date of First Diagnosed having Kidney Disease *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=120, y=190)
        entry_diagnosed = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_diagnosed.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Date of First Dialysis", font=("Merriweather Sans bold", 15), bg="white").place(x=750, y=190)
        entry_dialysis = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_dialysis.place(x=750, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=750, y=270)

        # Mode & Access
        tk.Label(self, text="Mode *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_mode = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_mode.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Access *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        entry_access = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_access.place(x=420, y=360, height=30)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Chronic Hemodialysis & Clinical Impression
        tk.Label(self, text="Date of First Chronic Hemodialysis ", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_chronic = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_chronic.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=510)

        tk.Label(self, text="Clinical Impression *", font=("Merriweather Sans bold", 15), bg="white").place(x=550, y=430)
        entry_clinical = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_clinical.place(x=550, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=550, y=510)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)
        
    def go_back(self):
        self.destroy()
        PatientHistory2Window(self.master) 

    def open_next(self):
        self.destroy()
        MedicationWindow(self.master)

class MedicationWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Medication")

        # Back Button
        self.btn_back = BackButton(self, text="Back", command=self.go_back)
        self.btn_back.place(x=90, y=30, width=120, height=40)

        # Title Label
        tk.Label(self, text="Medication", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Medication 1, Medication 2, Medication 3
        tk.Label(self, text="Medication 1", font=("Merriweather Sans bold", 14, "bold"), bg="white").place(x=120, y=190)
        entry_med1 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med1.place(x=120, y=240, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Medication 2", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        entry_med2 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med2.place(x=420, y=240, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Medication 3", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        entry_med3 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med3.place(x=720, y=240, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=720, y=270)

        # Medication 4, Medication 5, Medication 6
        tk.Label(self, text="Medication 4", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_med4 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med4.place(x=120, y=360, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Medication 5", font=("Merriweather Sans bold", 15 ), bg="white").place(x=420, y=310)
        entry_med5 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med5.place(x=420, y=360, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=420, y=390)

        tk.Label(self, text="Medication 6", font=("Merriweather Sans bold", 15 ), bg="white").place(x=720, y=310)
        entry_med6 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med6.place(x=720, y=360, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=720, y=390)

        # Medication 7 and "+ Another Slot"
        tk.Label(self, text="Medication 7", font=("Merriweather Sans bold", 15, ), bg="white").place(x=120, y=430)
        entry_med7 = tk.Entry(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_med7.place(x=120, y=480, height=25)
        tk.Frame(self, bg="black", height=1, width=180).place(x=120, y=510)

        tk.Label(self, text="+ Another Slot", font=("Merriweather Sans bold", 15), fg="blue",bg="white").place(x=420, y=430)

        # Next Button
        self.btn_next = Button(self, text="Save", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=120, height=40)

    def go_back(self):
        self.destroy()
        PatientHistory3Window(self.master)  

    def open_next(self):
        self.destroy()

    def open_next(self):
        self.destroy()
