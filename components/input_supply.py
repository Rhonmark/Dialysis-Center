import customtkinter as ctk
from tkcalendar import DateEntry
from tkcalendar import Calendar
from tkinter import Toplevel
from PIL import Image


class SupplyBaseWindow(ctk.CTkToplevel):  
    def __init__(self, parent,title):
        super().__init__(parent)
        self.geometry("1300x500")
        self.overrideredirect(True) 
        self.center_window()

        # Main Frame (Rounded Window)
        self.main_frame = ctk.CTkFrame(self,fg_color="white", corner_radius=25 ,bg_color="transparent")  
        self.main_frame.pack(expand=True, fill="both", padx=0, pady=0)

        # Sidebar 
        self.sidebar = ctk.CTkFrame(self.main_frame, width=30, fg_color="#1A374D", corner_radius=25,bg_color="transparent")  
        self.sidebar.pack(side="left", fill="y", padx=7,pady=6)  

        exit_image = ctk.CTkImage(light_image=Image.open("assets/exit.png"), size=(30, 30))  
        self.exit_button = ctk.CTkButton(self, image=exit_image, text="", fg_color="transparent", bg_color="white", hover_color="white",
            width=40, height=40, command=self.destroy
        )
        self.exit_button.place(x=1200, y=15) 

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x500+{x}+{y}")

class SupplyWindow(SupplyBaseWindow):
    def __init__(self, parent):
        super().__init__(parent,"Supply Information")

        ctk.CTkLabel(self, text="Supply Information" , font=("Merriweather bold" , 25), text_color="black",bg_color="white").place (x= 90, y=60)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

        def add_placeholder(entry, text):
            entry.insert(0, text)
            entry.configure(text_color="gray")
            entry.bind("<FocusIn>", lambda event: clear_placeholder(entry, text))
            entry.bind("<FocusOut>", lambda event: restore_placeholder(entry, text))

        def clear_placeholder(entry, text):
            if entry.get() == text:
                entry.delete(0, "end")
                entry.configure(text_color="black")

        def restore_placeholder(entry, text):
            if entry.get() == "":
                entry.insert(0, text)
                entry.configure(text_color="gray")
            
        #Fonts
        entry_font = ("Merriweather Sans", 13)
        label_font = ("Merriweather Sans bold", 15)
        button_font = ("Merriweather Bold",20)
        required_font = ("Merriweather Sans bold" , 10 )
        not_required_font = ("Merriweather Sans bold" , 10 )

        #Item Name
        ctk.CTkLabel(self, text="Item Name", font=label_font, fg_color="white", text_color="black").place(x=120, y=150)
        entry_itemname = ctk.CTkEntry(self, width=180, height=30, font=entry_font,  text_color="black",fg_color="white", border_width=0,bg_color="white")
        entry_itemname.place(x=120, y=200)

        #Required Text
        ctk.CTkLabel(self, text="*Required", font=not_required_font, text_color="#008400",bg_color="white").place(x=210, y=145)

        create_underline(120, 230, 180)
        add_placeholder(entry_itemname, "Type here")

        #Category
        ctk.CTkLabel(self, text="Category", font=label_font, fg_color="white", text_color="black").place(x=420, y=150)
        entry_category = ctk.CTkComboBox(self, width=180, height=30, font=entry_font, text_color="black",fg_color="white", border_width=0,bg_color="white",
                                         values=["Dispoable Material ",
                                                 "Medication",
                                                 "Cleaning Material",
                                                 "Other Material"],
                                         dropdown_fg_color="white",dropdown_hover_color="#68EDC6",dropdown_text_color="black",button_color="#1A374D",button_hover_color="#68EDC6")
        #Required Text
        ctk.CTkLabel(self, text="*Required", font=not_required_font, text_color="#008400",bg_color="white").place(x=495, y=145)

        entry_category.place(x=420, y=200)
        create_underline(420, 230, 140)

        #Last Restock Quantiity
        ctk.CTkLabel(self, text="Last Restock Quantity", font=label_font, fg_color="white", text_color="black").place(x=720, y=150)
        entry_maxquantity = ctk.CTkEntry(self, width=150, height=30, font=entry_font, text_color="black" ,fg_color="white", border_width=0,bg_color="white")
        entry_maxquantity.place(x=720, y=200)

        #Required Text
        ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red",bg_color="white").place(x=890, y=145)

        create_underline(720, 230, 180)
        add_placeholder(entry_maxquantity, "Type here")

        #Last Restock Date
        ctk.CTkLabel(self, text="Last Restock Date ", font=label_font, fg_color="white", text_color="black").place(x=1020, y=150)
        entry_date = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        entry_date.place(x=1020, y=200)

        #Required Text
        ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red",bg_color="white").place(x=1160, y=145 )

        create_underline(1020, 230, 140)
        add_placeholder(entry_date, "Select date")

        dropdown_btn = ctk.CTkButton(self, text="▼", width=30,font=entry_font,height=30, corner_radius=8, command=lambda: open_calendar(entry_date),bg_color="white", 
                                     fg_color="#1A374D", hover_color="#68EDC6", text_color="black")
        dropdown_btn.place(x=1170, y=200)

        def open_calendar(entry_widget):
            def on_date_select(event):
                selected_date = cal.get_date()
                entry_widget.delete(0, "end")
                entry_widget.insert(0, selected_date)
                entry_widget.configure(text_color="black")
                top.destroy()

            top = Toplevel(self)
            top.grab_set()
            top.overrideredirect(True) 
            top.geometry(f"+{self.winfo_rootx() + 1000}+{self.winfo_rooty() + 230}")
            cal = Calendar(top, date_pattern='MM-dd-yyyy')
            cal.pack(padx=10, pady=10)
            cal.bind("<<CalendarSelected>>", on_date_select)
        
        #Save Button
        self.btn_save = ctk.CTkButton(self, text="Save" , fg_color="#1A374D",hover_color="#16C79A", text_color="white",bg_color="white",corner_radius=20 ,font=button_font,width=200,height=50)
        self.btn_save.place(x=1020,y=400)

