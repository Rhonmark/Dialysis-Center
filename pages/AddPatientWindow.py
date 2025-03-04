import tkinter as tk
from tkinter import ttk

class AddPatientWindow(tk.Toplevel):
    def __init__(self, parent, add_callback):
        super().__init__(parent)
        self.title("Add Patient")
        self.geometry("400x400")
        self.add_callback = add_callback

        labels = ["Patient ID", "Patient Name", "Date Registered", "Condition", "Age", "Gender"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self, text=label, font=("Arial", 14)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(self, font=("Arial", 14))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label] = entry

        tk.Button(self, text="Add", font=("Arial", 14, "bold"), command=self.save_patient).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def save_patient(self):
        new_patient = tuple(entry.get() for entry in self.entries.values())
        self.add_callback(new_patient)
        self.destroy()