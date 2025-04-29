import customtkinter as ctk
import tkinter as tk
from PIL import Image

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

class PatientPhoto(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=400, height=400, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.top_frame = ctk.CTkFrame(
            self,
            width=400,
            height=200,
            fg_color="#68EDC6",  
            corner_radius=0
        )
        self.top_frame.place(x=0, y=0)  

        self.patient_id_label = ctk.CTkLabel(
        self,text="Patient ID",font=("Merriweather", 14),text_color="black")
        self.patient_id_label.place(relx=0.5, rely=0.60, anchor="center")

        self.patient_id_value = ctk.CTkLabel(
        self,text="PID123456",font=("Merriweather", 14),text_color="black")
        self.patient_id_value.place(relx=0.5, rely=0.70, anchor="center")

class ContactOptionsPanel(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=400, height=400, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#1A374D",
            corner_radius=0
        )
        self.left_bar.pack(side="left", fill="y")

        self.patient_history_btn = ctk.CTkButton(
            self,
            text="Patient History",
            font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_patient_history
        )
        self.patient_history_btn.place(x=80, y=80)

        self.medication_btn = ctk.CTkButton(
            self,
            text="Medication",
            font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_medication
        )
        self.medication_btn.place(x=80, y=150)

        self.contact_btn = ctk.CTkButton(
            self,
            text="Contact",
            font=("Merriweather", 14),
            corner_radius=20,
            width=250,
            height=40,
            fg_color="#01516D",
            hover_color="#013B50",
            command=self.open_contact_info
        )
        self.contact_btn.place(x=80, y=220)

    def open_patient_history(self):
        self.patient_history_window = PatientHistory(self.master)
        self.patient_history_window.place(x=60, y=10)

    def open_medication(self):
        self.medication_window = Medication(self.master)
        self.medication_window.place(x=60, y=10)

    def open_contact_info(self):
        self.contact_info_window = ContactInfoRelativeInfo(self.master)
        self.contact_info_window.place(x=60, y=10)

class PatientInfo(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=950, height=500, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#68EDC6", 
            corner_radius=0
        )
        self.left_bar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self, text="Patient Info", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=50, y=20)

        self.lastname_label = ctk.CTkLabel(self, text="Last Name", font=("Merriweather", 14))
        self.lastname_label.place(x=50, y=70)
        self.lastname_labelv = ctk.CTkLabel(self, text="Lopez", font=("Merriweather", 14))
        self.lastname_labelv.place(x=50, y=100)

        self.firstname_label = ctk.CTkLabel(self, text="First Name", font=("Merriweather", 14))
        self.firstname_label.place(x=300, y=70)
        self.firstname_labelv = ctk.CTkLabel(self, text="Juan", font=("Merriweather", 14))
        self.firstname_labelv.place(x=300, y=100)

        self.middlename_label = ctk.CTkLabel(self, text="Middle Name", font=("Merriweather", 14))
        self.middlename_label.place(x=550, y=70)
        self.middlename_labelv = ctk.CTkLabel(self, text="Carlos", font=("Merriweather", 14))
        self.middlename_labelv.place(x=550, y=100)

        self.status_label = ctk.CTkLabel(self, text="Status", font=("Merriweather", 14))
        self.status_label.place(x=50, y=120)
        self.status_labelv = ctk.CTkLabel(self, text="Active", font=("Merriweather", 14))
        self.status_labelv.place(x=50, y=150)

        self.access_type_label = ctk.CTkLabel(self, text="Type of Access", font=("Merriweather", 14))
        self.access_type_label.place(x=250, y=120)
        self.access_type_labelv = ctk.CTkLabel(self, text="Admin", font=("Merriweather", 14))
        self.access_type_labelv.place(x=250, y=150)

        self.birthdate_label = ctk.CTkLabel(self, text="Birthdate", font=("Merriweather", 14))
        self.birthdate_label.place(x=500, y=120)
        self.birthdate_labelv = ctk.CTkLabel(self, text="01/01/1980", font=("Merriweather", 14))
        self.birthdate_labelv.place(x=500, y=150)

        self.age_label = ctk.CTkLabel(self, text="Age", font=("Merriweather", 14))
        self.age_label.place(x=750, y=120)
        self.age_labelv = ctk.CTkLabel(self, text="45", font=("Merriweather", 14))
        self.age_labelv.place(x=750, y=150)

        self.gender_label = ctk.CTkLabel(self, text="Gender", font=("Merriweather", 14))
        self.gender_label.place(x=50, y=170)
        self.gender_labelv = ctk.CTkLabel(self, text="Male", font=("Merriweather", 14))
        self.gender_labelv.place(x=50, y=200)

        self.height_label = ctk.CTkLabel(self, text="Height", font=("Merriweather", 14))
        self.height_label.place(x=250, y=170)
        self.height_labelv = ctk.CTkLabel(self, text="5'8\"", font=("Merriweather", 14))
        self.height_labelv.place(x=250, y=200)

        self.civil_status_label = ctk.CTkLabel(self, text="Civil Status", font=("Merriweather", 14))
        self.civil_status_label.place(x=450, y=170)
        self.civil_status_labelv = ctk.CTkLabel(self, text="Married", font=("Merriweather", 14))
        self.civil_status_labelv.place(x=450, y=200)

        self.religion_label = ctk.CTkLabel(self, text="Religion", font=("Merriweather", 14))
        self.religion_label.place(x=650, y=170)
        self.religion_labelv = ctk.CTkLabel(self, text="Christian", font=("Merriweather", 14))
        self.religion_labelv.place(x=650, y=200)

        self.address_label = ctk.CTkLabel(self, text="Complete Address", font=("Merriweather", 14))
        self.address_label.place(x=50, y=230)
        self.address_labelv = ctk.CTkLabel(self, text="1234 Elm St, Quezon City", font=("Merriweather", 14))
        self.address_labelv.place(x=50, y=260)

    def update_info(self, patient_data):
        self.age_labelv.configure(text=f"{patient_data[2]}")

class PhilHealthAndOtherInfo(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=950, height=300, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#68EDC6", 
            corner_radius=0
        )
        self.left_bar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self, text="Phil Health and Other Info", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=50, y=20)

        self.philhealth_number_label = ctk.CTkLabel(self, text="PhilHealth Number", font=("Merriweather", 14))
        self.philhealth_number_label.place(x=50, y=70)
        self.philhealth_number_labelv = ctk.CTkLabel(self, text="PH1234567890", font=("Merriweather", 14))
        self.philhealth_number_labelv.place(x=50, y=100)

        self.membership_label = ctk.CTkLabel(self, text="Membership", font=("Merriweather", 14))
        self.membership_label.place(x=350, y=70)
        self.membership_labelv = ctk.CTkLabel(self, text="Active", font=("Merriweather", 14))
        self.membership_labelv.place(x=350, y=100)

        self.pwd_label = ctk.CTkLabel(self, text="PWD", font=("Merriweather", 14))
        self.pwd_label.place(x=50, y=120)
        self.pwd_labelv = ctk.CTkLabel(self, text="Yes", font=("Merriweather", 14))
        self.pwd_labelv.place(x=50, y=150)

        self.pwd_id_label = ctk.CTkLabel(self, text="PWD ID Number", font=("Merriweather", 14))
        self.pwd_id_label.place(x=200, y=120)
        self.pwd_id_labelv = ctk.CTkLabel(self, text="PWD987654321", font=("Merriweather", 14))
        self.pwd_id_labelv.place(x=200, y=150)

        self.senior_label = ctk.CTkLabel(self, text="SENIOR", font=("Merriweather", 14))
        self.senior_label.place(x=450, y=120)
        self.senior_labelv = ctk.CTkLabel(self, text="No", font=("Merriweather", 14))
        self.senior_labelv.place(x=450, y=150)

        self.senior_id_label = ctk.CTkLabel(self, text="SENIOR ID Number", font=("Merriweather", 14))
        self.senior_id_label.place(x=600, y=120)
        self.senior_id_labelv = ctk.CTkLabel(self, text="None", font=("Merriweather", 14))
        self.senior_id_labelv.place(x=600, y=150)

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
        self.last_name_value.place(x=50, y=100)

        self.first_name_label = ctk.CTkLabel(self, text="First Name", font=("Merriweather", 14))
        self.first_name_label.place(x=250, y=70)

        self.first_name_value = ctk.CTkLabel(self, text="Juan", font=("Merriweather", 14))
        self.first_name_value.place(x=250, y=100)

        self.middle_name_label = ctk.CTkLabel(self, text="Middle Name", font=("Merriweather", 14))
        self.middle_name_label.place(x=450, y=70)

        self.middle_name_value = ctk.CTkLabel(self, text="Dela Cruz", font=("Merriweather", 14))
        self.middle_name_value.place(x=450, y=100)

        self.contact_number_label = ctk.CTkLabel(self, text="Contact Number", font=("Merriweather", 14))
        self.contact_number_label.place(x=50, y=120)

        self.contact_number_value = ctk.CTkLabel(self, text="09123456789", font=("Merriweather", 14))
        self.contact_number_value.place(x=50, y=150)

        self.relationship_label = ctk.CTkLabel(self, text="Relationship to the Patient", font=("Merriweather", 14))
        self.relationship_label.place(x=250, y=120)

        self.relationship_value = ctk.CTkLabel(self, text="Brother", font=("Merriweather", 14))
        self.relationship_value.place(x=250, y=150)

        self.complete_address_label = ctk.CTkLabel(self, text="Complete Address", font=("Merriweather", 14))
        self.complete_address_label.place(x=50, y=170)

        self.address_value = ctk.CTkLabel(self, text="123 Barangay St., Cityville", font=("Merriweather", 14))
        self.address_value.place(x=50, y=200)

        self.relative_info_label = ctk.CTkLabel(self, text="Relative Info", font=("Merriweather", 20, "bold"))
        self.relative_info_label.place(x=50, y=230)

        self.relative_last_name_label = ctk.CTkLabel(self, text="Last Name", font=("Merriweather", 14))
        self.relative_last_name_label.place(x=50, y=270)

        self.relative_last_name_value = ctk.CTkLabel(self, text="Garcia", font=("Merriweather", 14))
        self.relative_last_name_value.place(x=50, y=300)

        self.relative_first_name_label = ctk.CTkLabel(self, text="First Name", font=("Merriweather", 14))
        self.relative_first_name_label.place(x=250, y=270)

        self.relative_first_name_value = ctk.CTkLabel(self, text="Maria", font=("Merriweather", 14))
        self.relative_first_name_value.place(x=250, y=300)

        self.relative_middle_name_label = ctk.CTkLabel(self, text="Middle Name", font=("Merriweather", 14))
        self.relative_middle_name_label.place(x=450, y=270)

        self.relative_middle_name_value = ctk.CTkLabel(self, text="Santos", font=("Merriweather", 14))
        self.relative_middle_name_value.place(x=450, y=300)

        self.relative_contact_number_label = ctk.CTkLabel(self, text="Contact Number", font=("Merriweather", 14))
        self.relative_contact_number_label.place(x=50, y=320)

        self.relative_contact_number_value = ctk.CTkLabel(self, text="09234567890", font=("Merriweather", 14))
        self.relative_contact_number_value.place(x=50, y=350)

        self.relative_complete_address_label = ctk.CTkLabel(self, text="Complete Address", font=("Merriweather", 14))
        self.relative_complete_address_label.place(x=50, y=370)

        self.relative_address_value = ctk.CTkLabel(self, text="456 Calle Nueva, Townsville", font=("Merriweather", 14))
        self.relative_address_value.place(x=50, y=400)

        self.exit_button = create_exit_button(self, command=self.exit_panel)
        self.exit_button.place(x=900, y=15)

    def exit_panel(self):
        print("Contact and Relative Info closed")
        self.place_forget()

class PatientHistory(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1443, height=1100, fg_color="white", corner_radius=20, **kwargs)
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

        self.title_label = ctk.CTkLabel(self.scrollable_frame, text="Family History", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=30, y=20)

        self.disease_label = ctk.CTkLabel(self.scrollable_frame, text="Disease History", font=("Merriweather", 14))
        self.disease_label.place(x=30, y=70)

        self.father_history = ctk.CTkLabel(self.scrollable_frame, text="Father: Hypertension", font=("Merriweather", 14), text_color="black")
        self.father_history.place(x=30, y=110)

        self.mother_history = ctk.CTkLabel(self.scrollable_frame, text="Mother: Diabetes", font=("Merriweather", 14), text_color="black")
        self.mother_history.place(x=30, y=150)

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

        self.title_label = ctk.CTkLabel(self.scrollable_frame, text="Medical History", font=("Merriweather", 20, "bold"))
        self.title_label.grid(row=0, column=0, pady=10, padx=30, sticky="w")

        start_y = 1

        self.surgery_label = ctk.CTkLabel(self.scrollable_frame, text="Previous Surgeries", font=("Merriweather", 14))
        self.surgery_label.grid(row=start_y, column=0, sticky="w", padx=30)

        start_y += 1  

        self.appendectomy_surgery = ctk.CTkLabel(self.scrollable_frame, text="Appendectomy - 2018", font=("Merriweather", 14), text_color="black")
        self.appendectomy_surgery.grid(row=start_y, column=0, sticky="w", padx=30)

        start_y += 1

        self.gallbladder_removal_surgery = ctk.CTkLabel(self.scrollable_frame, text="Gallbladder Removal - 2020", font=("Merriweather", 14), text_color="black")
        self.gallbladder_removal_surgery.grid(row=start_y, column=0, sticky="w", padx=30)


class OtherHistory(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1255, height=474, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(
            self,
            width=20,
            fg_color="#68EDC6",
            corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        self.canvas, self.scrollbar, self.scrollable_frame = add_scrollable_frame(self)

        self.title_label = ctk.CTkLabel(self.scrollable_frame, text="Other History", font=("Merriweather", 20, "bold"))
        self.title_label.grid(row=0, column=0, pady=20, padx=30)

        start_y = 1

        self.hpi_label = ctk.CTkLabel(self.scrollable_frame, text="History of Present Illness", font=("Merriweather", 14))
        self.hpi_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.hpi_info = ctk.CTkLabel(self.scrollable_frame, text="Patient experienced persistent fatigue and swelling.", font=("Merriweather", 14), text_color="black")
        self.hpi_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.pmh_label = ctk.CTkLabel(self.scrollable_frame, text="Pertinent Past Medical History", font=("Merriweather", 14))
        self.pmh_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.pmh_info = ctk.CTkLabel(self.scrollable_frame, text="History of hypertension and Type 2 diabetes.", font=("Merriweather", 14), text_color="black")
        self.pmh_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.kidney_disease_date_label = ctk.CTkLabel(self.scrollable_frame, text="Date of first diagnosed having kidney disease", font=("Merriweather", 14))
        self.kidney_disease_date_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.kidney_disease_date_info = ctk.CTkLabel(self.scrollable_frame, text="March 2015", font=("Merriweather", 14), text_color="black")
        self.kidney_disease_date_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.dialysis_date_label = ctk.CTkLabel(self.scrollable_frame, text="Date of first Dialysis", font=("Merriweather", 14))
        self.dialysis_date_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.dialysis_date_info = ctk.CTkLabel(self.scrollable_frame, text="January 2020", font=("Merriweather", 14), text_color="black")
        self.dialysis_date_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        self.mode_label = ctk.CTkLabel(self.scrollable_frame, text="Mode", font=("Merriweather", 14))
        self.mode_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.mode_info = ctk.CTkLabel(self.scrollable_frame, text="Hemodialysis", font=("Merriweather", 14), text_color="black")
        self.mode_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.access_label = ctk.CTkLabel(self.scrollable_frame, text="Access", font=("Merriweather", 14))
        self.access_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.access_info = ctk.CTkLabel(self.scrollable_frame, text="Arteriovenous fistula (AVF)", font=("Merriweather", 14), text_color="black")
        self.access_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.chronic_hemo_date_label = ctk.CTkLabel(self.scrollable_frame, text="Date of first Chronic Hemodialysis (* Leave NA if not)", font=("Merriweather", 14))
        self.chronic_hemo_date_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.chronic_hemo_date_info = ctk.CTkLabel(self.scrollable_frame, text="April 2021", font=("Merriweather", 14), text_color="black")
        self.chronic_hemo_date_info.grid(row=start_y+1, column=0, sticky="w", padx=30)

        start_y += 2

        self.clinical_impression_label = ctk.CTkLabel(self.scrollable_frame, text="Clinical Impression", font=("Merriweather", 14))
        self.clinical_impression_label.grid(row=start_y, column=0, sticky="w", padx=30)
        self.clinical_impression_info = ctk.CTkLabel(self.scrollable_frame, text="End-stage renal disease secondary to diabetes.", font=("Merriweather", 14), text_color="black")
        self.clinical_impression_info.grid(row=start_y+1, column=0, sticky="w", padx=30)


class Medication(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=1400, height=650, fg_color="white", corner_radius=20, **kwargs)
        self.pack_propagate(False)

        self.left_bar = ctk.CTkFrame(self, width=20, fg_color="#1A374D", corner_radius=0)
        self.left_bar.pack(side="left", fill="y")

        self.canvas, self.scrollbar, self.scrollable_frame = add_scrollable_frame(self)

        self.title_label = ctk.CTkLabel(self, text="Medication", font=("Merriweather", 20, "bold"))
        self.title_label.place(x=50, y=20)

        self.exit_button = create_exit_button(self, command=self.exit_medication)
        self.exit_button.place(x=1330, y=15)

        self.medication_label = ctk.CTkLabel(self.scrollable_frame, text="Drugs Taken", font=("Merriweather", 16))
        self.medication_label.place(x=30, y=35)

        meds = [
            "Amlodipine 10mg",
            "Metformin 500mg",
            "Erythropoietin Injection",
            "Sevelamer 800mg",
            "Calcium Carbonate 500mg"
        ]

        y_position = 60
        for med in meds:
            med_label = ctk.CTkLabel(self.scrollable_frame, text=med, font=("Merriweather", 13), text_color="black")
            med_label.place(x=30, y=y_position)
            y_position += 30

    def exit_medication(self):
        print("Medication closed")
        self.place_forget()