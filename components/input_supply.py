import customtkinter as ctk
from tkinter import Toplevel
from tkcalendar import Calendar
from PIL import Image
from backend.crud import supply_creation_id, get_existing_credentials
from backend.connector import db_connection as db

class CTkMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title, message, box_type="info"):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x160")
        self.configure(fg_color="white")
        self.resizable(False, False)
        self.grab_set()  
        self.transient(parent)  

        if box_type == "error":
            color = "#D9534F"  
            icon_text = "✖"
        elif box_type == "success":
            color = "#5CB85C" 
            icon_text = "✔"
        else:
            color = "#1A374D" 
            icon_text = "ℹ"

        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        icon_label = ctk.CTkLabel(container, text=icon_text, font=("Merriweather Sans", 40, "bold"), text_color=color, width=50)
        icon_label.grid(row=0, column=0, padx=(0,15), sticky="n")

        msg_label = ctk.CTkLabel(container, text=message, font=("Merriweather Sans", 14), text_color="#1A374D", wraplength=280, justify="left")
        msg_label.grid(row=0, column=1, sticky="w")

        btn_ok = ctk.CTkButton(self, text="OK", width=80, fg_color=color, hover_color="#16C79A", text_color="white", command=self.destroy)
        btn_ok.pack(pady=(0, 20))

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    @classmethod
    def show_error(cls, title, message, parent=None):
        parent = parent or ctk._default_root
        msgbox = cls(parent, title, message, box_type="error")
        parent.wait_window(msgbox)

    @classmethod
    def show_success(cls, title, message, parent=None):
        parent = parent or ctk._default_root
        msgbox = cls(parent, title, message, box_type="success")
        parent.wait_window(msgbox)

class SupplyBaseWindow(ctk.CTkToplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.geometry("1300x500")
        self.overrideredirect(True)
        self.center_window()

        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=25, bg_color="transparent")
        self.main_frame.pack(expand=True, fill="both", padx=0, pady=0)

        self.sidebar = ctk.CTkFrame(self.main_frame, width=30, fg_color="#1A374D", corner_radius=25, bg_color="transparent")
        self.sidebar.pack(side="left", fill="y", padx=7, pady=6)

        exit_image = ctk.CTkImage(light_image=Image.open("assets/exit.png"), size=(30, 30))
        self.exit_button = ctk.CTkButton(self, image=exit_image, text="", fg_color="transparent", bg_color="white", hover_color="white",
                                         width=40, height=40, command=self.destroy)
        self.exit_button.place(x=1200, y=15)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x500+{x}+{y}")


class SupplyWindow(SupplyBaseWindow):
    def __init__(self, parent, edit_data=None):
        super().__init__(parent, "Supply Information")
        
        self.edit_data = edit_data
        self.is_editing = edit_data is not None

        title_text = "Edit Supply Information" if self.is_editing else "Supply Information"
        ctk.CTkLabel(self, text=title_text, font=("Merriweather bold", 25), text_color="black", bg_color="white").place(x=90, y=60)

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

        def add_placeholder(entry, text):
            entry.insert(0, text)
            entry.configure(text_color="gray")
            entry.bind("<FocusIn>", lambda event: clear_placeholder(entry, text))
            entry.bind("<FocusOut>", lambda event: restore_placeholder(entry, text))
            entry.bind("<Button-1>", lambda event: force_clear(entry))

        def clear_placeholder(entry, text):
            if entry.get() == text:
                entry.delete(0, "end")
                entry.configure(text_color="black")

        def restore_placeholder(entry, text):
            if entry.get() == "":
                entry.insert(0, text)
                entry.configure(text_color="gray")

        def force_clear(entry):
            entry.delete(0, "end")
            entry.configure(text_color="black")

        entry_font = ("Merriweather Sans", 13)
        label_font = ("Merriweather Sans bold", 15)
        button_font = ("Merriweather Bold", 20)
        required_font = ("Merriweather Sans bold", 10)
        not_required_font = ("Merriweather Sans bold", 10)

        # Item Name
        ctk.CTkLabel(self, text="Item Name", font=label_font, fg_color="white", text_color="black").place(x=120, y=150)
        self.entry_itemname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                      bg_color="white")
        self.entry_itemname.place(x=120, y=200)
        ctk.CTkLabel(self, text="*Required", font=not_required_font, text_color="#008400", bg_color="white").place(x=210, y=145)
        create_underline(120, 230, 180)

        if not self.is_editing:
            add_placeholder(self.entry_itemname, "Type here")

        # Category
        ctk.CTkLabel(self, text="Category", font=label_font, fg_color="white", text_color="black").place(x=420, y=150)
        self.entry_category = ctk.CTkComboBox(
            self, width=180, height=30, font=entry_font, text_color="black",
            fg_color="white", border_width=0, bg_color="white",
            values=["Disposable Material", "Medication", "Cleaning Material", "Other Material"],
            dropdown_fg_color="white", dropdown_hover_color="#68EDC6",
            dropdown_text_color="black", button_color="#1A374D", button_hover_color="#68EDC6"
        )
        self.entry_category.configure(state="readonly")
        self.entry_category.place(x=420, y=200)
        ctk.CTkLabel(self, text="*Required", font=not_required_font, text_color="#008400", bg_color="white").place(x=495, y=145)
        create_underline(420, 230, 140)

        # Restock Quantity
        ctk.CTkLabel(self, text="Last Restock Quantity", font=label_font, fg_color="white", text_color="black").place(x=720, y=150)
        self.entry_restock_quantity = ctk.CTkEntry(self, width=150, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        self.entry_restock_quantity.place(x=720, y=200)
        ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red", bg_color="white").place(x=890, y=145)
        create_underline(720, 230, 180)

        if not self.is_editing:
            add_placeholder(self.entry_restock_quantity, "Type here")

        # Restock Date
        ctk.CTkLabel(self, text="Last Restock Date", font=label_font, fg_color="white", text_color="black").place(x=1020, y=150)
        self.entry_restock_date = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                 bg_color="white")
        self.entry_restock_date.place(x=1020, y=200)
        ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red", bg_color="white").place(x=1160, y=145)
        create_underline(1020, 230, 140)

        if not self.is_editing:
            add_placeholder(self.entry_restock_date, "Select date")

        dropdown_btn = ctk.CTkButton(self, text="▼", width=30, font=entry_font, height=30, corner_radius=8,
                                     command=lambda: open_calendar(self.entry_restock_date), bg_color="white",
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
            cal = Calendar(top, date_pattern='yyyy-mm-dd')
            cal.pack(padx=10, pady=10)
            cal.bind("<<CalendarSelected>>", on_date_select)

        # Second Row - Average Weekly Usage
        ctk.CTkLabel(self, text="Average Weekly Usage", font=label_font, fg_color="white", text_color="black").place(x=120, y=300)
        self.entry_averageuse = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                      bg_color="white")
        self.entry_averageuse.place(x=120, y=350)
        ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red", bg_color="white").place(x=300, y=295)
        create_underline(120, 380, 180)
        if not self.is_editing:
            add_placeholder(self.entry_averageuse, "Type here")

        # Delivery Date
        ctk.CTkLabel(self, text="Delivery Time in Days", font=label_font, fg_color="white", text_color="black").place(x=420, y=300)
        self.entry_delivery_date = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                 bg_color="white")
        self.entry_delivery_date.place(x=420, y=350)
        ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red", bg_color="white").place(x=580, y=295)
        create_underline(420, 380, 140)
        if not self.is_editing:
            add_placeholder(self.entry_delivery_date, "Select date")

        # Populate fields if editing
        if self.is_editing:
            self.populate_fields()

        def on_save_click():
            item_name = self.entry_itemname.get()
            category = self.entry_category.get()
            restock_quantity_str = self.entry_restock_quantity.get()
            restock_date = self.entry_restock_date.get()
            avg_weekly_usage = self.entry_averageuse.get()
            delivery_time = int(self.entry_delivery_date.get())

            if item_name == "" or item_name == "Type here":
                CTkMessageBox.show_error("Input Error", "Item Name is required.", parent=self)
                return
            if category == "":
                CTkMessageBox.show_error("Input Error", "Category is required.", parent=self)
                return

            # Handle restock quantity
            try:
                restock_quantity = int(restock_quantity_str) if restock_quantity_str and restock_quantity_str != "Type here" else 0
            except ValueError:
                CTkMessageBox.show_error("Input Error", "Restock quantity must be a valid number.", parent=self)
                return

            try:
                connect = db()
                cursor = connect.cursor()

                if self.is_editing:
                    # Update existing record
                    cursor.execute("""
                        UPDATE supply 
                        SET item_name = %s, category = %s, restock_quantity = %s, 
                        restock_date = %s, average_weekly_usage = %s, delivery_time_days = %s 
                        WHERE item_id = %s 
                    """, (item_name, category, restock_quantity, restock_date, avg_weekly_usage, delivery_time, self.edit_data['item_id']))

                    print(f"Updated supply item with ID: {self.edit_data['item_id']}")
                    CTkMessageBox.show_success("Success", "Supply information updated successfully!", parent=self)
                
                else:
                    # Create new record
                    supply_information = {
                        'item_name': item_name,
                        'category': category,
                        'restock_quantity': restock_quantity,
                        'restock_date': restock_date,
                        'average_weekly_usage': avg_weekly_usage,
                        'delivery_time_days': delivery_time
                    }

                    supply_column = ', '.join(supply_information.keys())
                    supply_row = [f"{entries}" for entries in supply_information.values()]

                    check_uniqueness = get_existing_credentials(item_name, 'item_name', table_name='supply')

                    if check_uniqueness:
                        CTkMessageBox.show_error("Error", 'Items already exists ', parent=self)
                        return

                    item_id = supply_creation_id(supply_column, supply_row, table_name='supply')

                    if item_id: 
                        print('Item ID: ', item_id)
                        CTkMessageBox.show_success("Success", "Supply information saved successfully!", parent=self)
                    else:
                        print('Item ID creation error')
                        return

                connect.commit()

            except Exception as e:
                print(f"Error saving supply: {e}")
                CTkMessageBox.show_error("Error", 'Something went wrong! ', parent=self)
                return

            finally:
                cursor.close()
                connect.close() 
                self.destroy()

        # Save button
        button_text = "Update" if self.is_editing else "Save"
        self.btn_save = ctk.CTkButton(self, text=button_text, fg_color="#1A374D", hover_color="#16C79A", text_color="white",
                                      bg_color="white", corner_radius=20, font=button_font, width=200, height=50,
                                      command=on_save_click)
        self.btn_save.place(x=1020, y=420)

    def populate_fields(self):
        """Populate fields with edit data"""
        if not self.edit_data:
            return
        
        # Clear and set item name
        self.entry_itemname.delete(0, "end")
        self.entry_itemname.insert(0, self.edit_data['item_name'])
        self.entry_itemname.configure(text_color="black")
        
        # Set category
        self.entry_category.set(self.edit_data['category'])
        
        # Clear and set restock quantity
        self.entry_restock_quantity.delete(0, "end")
        self.entry_restock_quantity.insert(0, str(self.edit_data['restock_quantity']))
        self.entry_restock_quantity.configure(text_color="black")
        
        # Clear and set restock date
        self.entry_restock_date.delete(0, "end")
        self.entry_restock_date.insert(0, self.edit_data['restock_date'])
        self.entry_restock_date.configure(text_color="black")