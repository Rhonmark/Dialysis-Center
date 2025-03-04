import tkinter as tk
from tkinter import ttk
from components.buttons import Button

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
        tk.Label(self, text="Patient Information", font=("Arial", 20, "bold"), bg="white").place(x=90, y=70)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name*", font=("Arial", 14, "bold"), bg="white").place(x=95, y=150)
        entry_lastname = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=100, y=180, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=100, y=210)

        tk.Label(self, text="First Name*", font=("Arial", 14, "bold"), bg="white").place(x=380, y=150)
        entry_firstname = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=385, y=180, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=385, y=210)

        tk.Label(self, text="Middle Name", font=("Arial", 14, "bold"), bg="white").place(x=680, y=150)
        entry_middlename = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=685, y=180, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=685, y=210)

        # Status, Type of Access, Birthdate, Age
        tk.Label(self, text="Status*", font=("Arial", 14, "bold"), bg="white").place(x=95, y=270)
        entry_status = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_status.place(x=100, y=300, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=100, y=330)

        tk.Label(self, text="Type of Access*", font=("Arial", 14, "bold"), bg="white").place(x=360, y=270)
        entry_access = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_access.place(x=360, y=300, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=360, y=330)

        tk.Label(self, text="Birthdate*", font=("Arial", 14, "bold"), bg="white").place(x=600, y=270)
        entry_birthdate = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_birthdate.place(x=600, y=300, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=600, y=330)

        tk.Label(self, text="Age*", font=("Arial", 14, "bold"), bg="white").place(x=850, y=270)
        entry_age = tk.Entry(self, width=10, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_age.place(x=850, y=300, height=30)
        tk.Frame(self, bg="black", height=2, width=100).place(x=850, y=330)

        # Gender, Height, Civil Status, Religion
        tk.Label(self, text="Gender*", font=("Arial", 14, "bold"), bg="white").place(x=95, y=390)
        entry_gender = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_gender.place(x=100, y=420, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=100, y=450)

        tk.Label(self, text="Height*", font=("Arial", 14, "bold"), bg="white").place(x=350, y=390)
        entry_height = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_height.place(x=350, y=420, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=350, y=450)

        tk.Label(self, text="Civil Status*", font=("Arial", 14, "bold"), bg="white").place(x=600, y=390)
        entry_civil_status = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_civil_status.place(x=600, y=420, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=600, y=450)

        tk.Label(self, text="Religion*", font=("Arial", 14, "bold"), bg="white").place(x=850, y=390)
        entry_religion = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_religion.place(x=850, y=420, height=30)
        tk.Frame(self, bg="black", height=2, width=150).place(x=850, y=450)

        # Complete Address 
        tk.Label(self, text="Complete Address*", font=("Arial", 14, "bold"), bg="white").place(x=95, y=510)
        entry_address = tk.Entry(self, width=80, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=100, y=540, height=30)
        tk.Frame(self, bg="black", height=2, width=800).place(x=100, y=570)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)

    def open_next(self):
        self.destroy()
        ContactPersonWindow(self.master)

class ContactPersonWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Contact Person Info")

        # Back Button
        self.btn_back = ttk.Button(self, text="Back", command=self.go_back)
        self.btn_back.place(x=40, y=20)
        # Title Label
        tk.Label(self, text="Contact Person Info", font=("Arial", 20, "bold"), bg="white").place(x=50, y=50)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=80)
        entry_lastname = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=50, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=140)

        tk.Label(self, text="First Name*", font=("Arial", 14, "bold"), bg="white").place(x=300, y=80)
        entry_firstname = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=300, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=300, y=140)

        tk.Label(self, text="Middle Name", font=("Arial", 14, "bold"), bg="white").place(x=550, y=80)
        entry_middlename = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=550, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=550, y=140)

        # Contact Number, Relationship to the Patient
        tk.Label(self, text="Contact Number*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=180)
        entry_contact = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_contact.place(x=50, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=240)

        tk.Label(self, text="Relationship to the Patient*", font=("Arial", 14, "bold"), bg="white").place(x=300, y=180)
        entry_relationship = tk.Entry(self, width=30, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_relationship.place(x=300, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=300).place(x=300, y=240)

        # Complete Address 
        tk.Label(self, text="Complete Address*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=280)
        entry_address = tk.Entry(self, width=80, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=50, y=310, height=30)
        tk.Frame(self, bg="black", height=2, width=800).place(x=50, y=340)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)

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
        self.btn_back = ttk.Button(self, text="Back", command=self.go_back)
        self.btn_back.place(x=40, y=20)
        # Title Label
        tk.Label(self, text="Relative Info", font=("Arial", 20, "bold"), bg="white").place(x=50, y=50)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=80)
        entry_lastname = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=50, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=140)

        tk.Label(self, text="First Name*", font=("Arial", 14, "bold"), bg="white").place(x=300, y=80)
        entry_firstname = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=300, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=300, y=140)

        tk.Label(self, text="Middle Name", font=("Arial", 14, "bold"), bg="white").place(x=550, y=80)
        entry_middlename = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=550, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=550, y=140)

        # Contact Number
        tk.Label(self, text="Contact Number*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=180)
        entry_contact = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_contact.place(x=50, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=240)

        # Complete Address
        tk.Label(self, text="Complete Address*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=280)
        entry_address = tk.Entry(self, width=80, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=50, y=310, height=30)
        tk.Frame(self, bg="black", height=2, width=800).place(x=50, y=340)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)

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
        self.btn_back = ttk.Button(self, text="Back", command=self.go_back)
        self.btn_back.place(x=40, y=20)
        # Title Label
        tk.Label(self, text="PhilHealth and Other Info", font=("Arial", 20, "bold"), bg="white").place(x=50, y=50)

        # PhilHealth Number & Membership
        tk.Label(self, text="PhilHealth Number*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=80)
        entry_philhealth = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_philhealth.place(x=50, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=140)

        tk.Label(self, text="Membership*", font=("Arial", 14, "bold"), bg="white").place(x=300, y=80)
        entry_membership = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_membership.place(x=300, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=300, y=140)

        # PWD & PWD ID Number
        tk.Label(self, text="PWD", font=("Arial", 14, "bold"), bg="white").place(x=50, y=180)
        entry_pwd = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_pwd.place(x=50, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=240)

        tk.Label(self, text="PWD ID Number", font=("Arial", 14, "bold"), bg="white").place(x=300, y=180)
        entry_pwd_id = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_pwd_id.place(x=300, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=300, y=240)

        # Senior & Senior ID Number
        tk.Label(self, text="Senior", font=("Arial", 14, "bold"), bg="white").place(x=50, y=280)
        entry_senior = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_senior.place(x=50, y=310, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=340)

        tk.Label(self, text="Senior ID Number", font=("Arial", 14, "bold"), bg="white").place(x=300, y=280)
        entry_senior_id = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_senior_id.place(x=300, y=310, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=300, y=340)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)

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
        self.btn_back = ttk.Button(self, text="Back", command=self.go_back)
        self.btn_back.place(x=40, y=20)
        tk.Label(self, text="Patient History Part 1", font=("Arial", 20, "bold"), bg="white").place(x=50, y=50)

        # Family History
        tk.Label(self, text="Family History*", font=("Arial", 16, "bold"), bg="white").place(x=50, y=60)

        self.family_hypertension = tk.BooleanVar()
        self.family_diabetes = tk.BooleanVar()
        self.family_malignancy = tk.BooleanVar()
        
        tk.Checkbutton(self, variable=self.family_hypertension, bg="white").place(x=50, y=100)
        tk.Label(self, text="Hypertension", font=("Arial", 14), bg="white").place(x=80, y=100)

        tk.Checkbutton(self, variable=self.family_diabetes, bg="white").place(x=300, y=100)
        tk.Label(self, text="Diabetes Mellitus", font=("Arial", 14), bg="white").place(x=330, y=100)

        tk.Checkbutton(self, variable=self.family_malignancy, bg="white").place(x=600, y=100)
        tk.Label(self, text="Malignancy", font=("Arial", 14), bg="white").place(x=630, y=100)

        # Other Family History
        tk.Label(self, text="Other:", font=("Arial", 14), bg="white").place(x=50, y=140)
        self.family_other = tk.Entry(self, width=50, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        self.family_other.place(x=120, y=140, height=30)
        tk.Frame(self, bg="black", height=2, width=400).place(x=120, y=170)

        # Medical History
        tk.Label(self, text="Medical History*", font=("Arial", 16, "bold"), bg="white").place(x=50, y=200)

        self.med_hypertension = tk.BooleanVar()
        self.med_urinary_stone = tk.BooleanVar()
        self.med_recurrent_uti = tk.BooleanVar()
        self.med_diabetes_type = tk.BooleanVar()
        
        tk.Checkbutton(self, variable=self.med_hypertension, bg="white").place(x=50, y=240)
        tk.Label(self, text="Hypertension", font=("Arial", 14), bg="white").place(x=80, y=240)

        tk.Checkbutton(self, variable=self.med_urinary_stone, bg="white").place(x=300, y=240)
        tk.Label(self, text="Urinary Stone", font=("Arial", 14), bg="white").place(x=330, y=240)

        tk.Checkbutton(self, variable=self.med_recurrent_uti, bg="white").place(x=600, y=240)
        tk.Label(self, text="Recurrent UTI", font=("Arial", 14), bg="white").place(x=630, y=240)

        tk.Checkbutton(self, variable=self.med_diabetes_type, bg="white").place(x=50, y=280)
        tk.Label(self, text="Diabetes Mellitus Type", font=("Arial", 14), bg="white").place(x=80, y=280)

        # Other Medical History
        tk.Label(self, text="Other:", font=("Arial", 14), bg="white").place(x=50, y=320)
        self.med_other1 = tk.Entry(self, width=30, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        self.med_other1.place(x=120, y=320, height=30)
        tk.Frame(self, bg="black", height=2, width=250).place(x=120, y=350)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)

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
        self.btn_back = ttk.Button(self, text="Back", command=self.go_back)
        self.btn_back.place(x=40, y=20)
        tk.Label(self, text="Patient History Part 2", font=("Arial", 20, "bold"), bg="white").place(x=50, y=50)

        # History of Present Illness
        tk.Label(self, text="History of Present Illness*", font=("Arial", 16, "bold"), bg="white").place(x=50, y=60)
        self.history_illness = tk.Text(self, width=80, height=5, font=("Arial", 12), bg="white", bd=1, relief="solid")
        self.history_illness.insert("1.0", "Type here")  # Placeholder text
        self.history_illness.place(x=50, y=100)

        # Pertinent Past Medical History
        tk.Label(self, text="Pertinent Past Medical History*", font=("Arial", 16, "bold"), bg="white").place(x=50, y=220)
        self.past_medical_history = tk.Text(self, width=80, height=5, font=("Arial", 12), bg="white", bd=1, relief="solid")
        self.past_medical_history.insert("1.0", "Type here")  # Placeholder text
        self.past_medical_history.place(x=50, y=260)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)

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
        self.btn_back = ttk.Button(self, text="Back", command=self.go_back)
        self.btn_back.place(x=40, y=20)

        tk.Label(self, text="Patient History Part 3", font=("Arial", 20, "bold"), bg="white").place(x=50, y=50)

        # Date of First Diagnosed having Kidney Disease 
        tk.Label(self, text="Date of First Diagnosed having Kidney Disease*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=80)
        entry_diagnosed = tk.Entry(self, width=30, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_diagnosed.place(x=50, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=300).place(x=50, y=140)

        tk.Label(self, text="Date of First Dialysis*", font=("Arial", 14, "bold"), bg="white").place(x=600, y=80)
        entry_dialysis = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_dialysis.place(x=600, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=600, y=140)

        # Mode & Access
        tk.Label(self, text="Mode", font=("Arial", 14, "bold"), bg="white").place(x=50, y=180)
        entry_mode = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_mode.place(x=50, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=240)

        tk.Label(self, text="Access", font=("Arial", 14, "bold"), bg="white").place(x=400, y=180)
        entry_access = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_access.place(x=400, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=400, y=240)

        # Chronic Hemodialysis & Clinical Impression
        tk.Label(self, text="Date of First Chronic Hemodialysis*", font=("Arial", 14, "bold"), bg="white").place(x=50, y=280)
        entry_chronic = tk.Entry(self, width=30, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_chronic.place(x=50, y=310, height=30)
        tk.Frame(self, bg="black", height=2, width=300).place(x=50, y=340)

        tk.Label(self, text="Clinical Impression*", font=("Arial", 14, "bold"), bg="white").place(x=400, y=280)
        entry_clinical = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_clinical.place(x=400, y=310, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=400, y=340)

        # Next Button
        self.btn_next = Button(self, text="Next", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)
        
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
        self.btn_back = ttk.Button(self, text="Back", command=self.go_back)
        self.btn_back.place(x=40, y=20)

        # Title Label
        tk.Label(self, text="Medication", font=("Arial", 20, "bold"), bg="white").place(x=50, y=50)

        # Medication 1, Medication 2, Medication 3
        tk.Label(self, text="Medication 1", font=("Arial", 14, "bold"), bg="white").place(x=50, y=80)
        entry_med1 = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_med1.place(x=50, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=140)

        tk.Label(self, text="Medication 2", font=("Arial", 14, "bold"), bg="white").place(x=300, y=80)
        entry_med2 = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_med2.place(x=300, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=300, y=140)

        tk.Label(self, text="Medication 3", font=("Arial", 14, "bold"), bg="white").place(x=550, y=80)
        entry_med3 = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_med3.place(x=550, y=110, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=550, y=140)

        # Medication 4, Medication 5, Medication 6
        tk.Label(self, text="Medication 4", font=("Arial", 14, "bold"), bg="white").place(x=50, y=180)
        entry_med4 = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_med4.place(x=50, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=240)

        tk.Label(self, text="Medication 5", font=("Arial", 14, "bold"), bg="white").place(x=300, y=180)
        entry_med5 = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_med5.place(x=300, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=300, y=240)

        tk.Label(self, text="Medication 6", font=("Arial", 14, "bold"), bg="white").place(x=550, y=180)
        entry_med6 = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_med6.place(x=550, y=210, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=550, y=240)

        # Medication 7 and "+ Another Slot"
        tk.Label(self, text="Medication 7", font=("Arial", 14, "bold"), bg="white").place(x=50, y=280)
        entry_med7 = tk.Entry(self, width=20, font=("Arial", 12), bg="white", bd=0, highlightthickness=0)
        entry_med7.place(x=50, y=310, height=30)
        tk.Frame(self, bg="black", height=2, width=200).place(x=50, y=340)

        tk.Label(self, text="+ Another Slot", font=("Arial", 14, "bold"), bg="#01516D", fg="white").place(x=300, y=310)

        # Next Button
        self.btn_next = Button(self, text="Save", command=self.open_next)
        self.btn_next.place(x=1070, y=600, width=150, height=50)

    def go_back(self):
        self.destroy()
        PatientHistory3Window(self.master)  

    def open_next(self):
        self.destroy()

    def open_next(self):
        self.destroy()
