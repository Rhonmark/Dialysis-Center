import tkinter as tk
from tkinter import PhotoImage
from components.buttons import Button
from components.textfields_patients import TextField_Patients
from backend.connector import db_connection as db

class BaseWindow(tk.Toplevel):
    def __init__(self, parent, title, next_window=None, previous_window=None):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.geometry("1300x700")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True) 
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
            self.previous_window(self.master)

    def open_next(self):
        if self.next_window:
            self.destroy()
            self.next_window(self.master)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x700+{x}+{y}")

class PatientInfoWindow(BaseWindow):
    def __init__(self, parent):

        super().__init__(parent, "Patient Information", next_window=ContactPersonWindow, previous_window=None)

        # Title Label
        tk.Label(self, text="Patient Information", font=("Merriweather bold", 25), bg="white").place(x=90, y=60)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=120, y=150)
        entry_lastname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=120, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=230)

        tk.Label(self, text="First Name *", font=("Merriweather Sans bold", 15 ), bg="white").place(x=420, y=150)
        entry_firstname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=420, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=230)

        tk.Label(self, text="Middle Name", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=150)
        entry_middlename = TextField_Patients(self, width=15, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=720, y=200, height=25)
        tk.Frame(self, bg="#979797", height=1, width=150).place(x=720, y=230)

        # Status, Type of Access, Birthdate, Age
        tk.Label(self, text="Status *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=270)
        entry_status = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_status.place(x=120, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=350)

        tk.Label(self, text="Type of Access *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=270)
        entry_access = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_access.place(x=420, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=350)

        tk.Label(self, text="Birthdate *", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=270)
        entry_birthdate = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_birthdate.place(x=720, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=350)

        tk.Label(self, text="Age *", font=("Merriweather Sans bold", 15), bg="white").place(x=1020, y=270)
        entry_age = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_age.place(x=1020, y=320, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=1020, y=350)

        # Gender, Height, Civil Status, Religion
        tk.Label(self, text="Gender *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=390)
        entry_gender = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_gender.place(x=120, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=470)

        tk.Label(self, text="Height *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=390)
        entry_height = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_height.place(x=420, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=470)

        tk.Label(self, text="Civil Status *", font=("Merriweather Sans bold",15), bg="white").place(x=720, y=390)
        entry_civil_status = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_civil_status.place(x=720, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=470)

        tk.Label(self, text="Religion *", font=("Merriweather Sans bold", 15), bg="white").place(x=1020, y=390)
        entry_religion = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_religion.place(x=1020, y=440, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=1020, y=470)

        # Complete Address 
        tk.Label(self, text="Complete Address *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=510)
        entry_address = TextField_Patients(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=120, y=560, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=590)

        try:
            connect = db()
            cursor = connect.cursor()

            access = entry_access.get().strip()
            address = entry_address.get().strip()
            last_name = entry_lastname.get().strip()
            print("Access:", access, "Address:", address, "Last Name:", last_name)

        except Exception as e:
            print("Error with step 1 input: ", e)

        finally:
            cursor.close()
            connect.close()

class ContactPersonWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Contact Person Info", next_window=RelativeInfoWindow, previous_window=PatientInfoWindow)

        # Title Label
        tk.Label(self, text="Contact Person Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        entry_lastname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="First Name *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        entry_firstname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Middle Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        entry_middlename = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=720, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=270)

        # Contact Number, Relationship to the Patient
        tk.Label(self, text="Contact Number *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_contact = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_contact.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="Relationship to the Patient *", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        entry_relationship = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_relationship.place(x=420, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Complete Address 
        tk.Label(self, text="Complete Address *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_address = TextField_Patients(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=510)

class RelativeInfoWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Relative Info", next_window=PhilHealthInfoWindow, previous_window=ContactPersonWindow)

        # Title Label
        tk.Label(self, text="Relative Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # Last Name, First Name, Middle Name
        tk.Label(self, text="Last Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        entry_lastname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_lastname.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="First Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=190)
        entry_firstname = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_firstname.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        tk.Label(self, text="Middle Name*", font=("Merriweather Sans bold", 15), bg="white").place(x=720, y=190)
        entry_middlename = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_middlename.place(x=720, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=720, y=270)

        # Contact Number
        tk.Label(self, text="Contact Number*", font=("Merriweather Sans bold",15), bg="white").place(x=120, y=310)
        entry_contact = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_contact.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        # Complete Address
        tk.Label(self, text="Complete Address*", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_address = TextField_Patients(self, width=50, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_address.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=500).place(x=120, y=510)

class PhilHealthInfoWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "PhilHealth and Other Info", next_window=PatientHistory1Window, previous_window=RelativeInfoWindow)

        # Title Label
        tk.Label(self, text="PhilHealth and Other Info", font=("Merriweather bold", 25), bg="white").place(x=90, y=100)

        # PhilHealth Number & Membership
        tk.Label(self, text="PhilHealth Number *", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=190)
        entry_philhealth = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_philhealth.place(x=120, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=270)

        tk.Label(self, text="Membership *", font=("Merriweather Sans bold",15), bg="white").place(x=420, y=190)
        entry_membership = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_membership.place(x=420, y=240, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=270)

        # PWD & PWD ID Number
        tk.Label(self, text="PWD", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=310)
        entry_pwd = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_pwd.place(x=120, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=390)

        tk.Label(self, text="PWD ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=310)
        entry_pwd_id = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_pwd_id.place(x=420, y=360, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=390)

        # Senior & Senior ID Number
        tk.Label(self, text="Senior", font=("Merriweather Sans bold", 15), bg="white").place(x=120, y=430)
        entry_senior = TextField_Patients(self, width=180, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_senior.place(x=120, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=120, y=510)

        tk.Label(self, text="Senior ID Number", font=("Merriweather Sans bold", 15), bg="white").place(x=420, y=430)
        entry_senior_id = TextField_Patients(self, width=18, font=("Merriweather light", 12), bg="white", bd=0, highlightthickness=0)
        entry_senior_id.place(x=420, y=480, height=25)
        tk.Frame(self, bg="#979797", height=1, width=180).place(x=420, y=510)

class PatientHistory1Window(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Patient History Part 1", next_window=PatientHistory2Window, previous_window=PhilHealthInfoWindow)

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

        
class PatientHistory2Window(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Patient History Part 2", next_window=PatientHistory3Window, previous_window=PatientHistory1Window)

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
    def __init__(self, parent):
        super().__init__(parent, "Patient History Part 3", next_window=MedicationWindow, previous_window=PatientHistory2Window)

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
    def __init__(self, parent):
        super().__init__(parent, "Medication", next_window=None, previous_window=PatientHistory3Window)

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