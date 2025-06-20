import customtkinter as ctk
from tkinter import Toplevel, ttk
from tkcalendar import Calendar
from PIL import Image
from backend.crud import supply_creation_id, get_existing_credentials
from backend.connector import db_connection as db
from components.state import login_shared_states
import math
from datetime import date, datetime

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
        self.geometry("1300x700") 
        self.overrideredirect(True)
        self.center_window()

        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=25, bg_color="transparent")
        self.main_frame.pack(expand=True, fill="both", padx=0, pady=0)

        self.sidebar = ctk.CTkFrame(self.main_frame, width=30, fg_color="#1A374D", corner_radius=25, bg_color="transparent")
        self.sidebar.pack(side="left", fill="y", padx=7, pady=6)

        exit_image = ctk.CTkImage(light_image=Image.open("assets/exit.png"), size=(30, 30))
        self.exit_button = ctk.CTkButton(self, image=exit_image, text="", fg_color="transparent", bg_color="white", hover_color="white",
                                         width=40, height=40, command=self.close_window)
        self.exit_button.place(x=1200, y=15)

    def close_window(self):
        """Properly close the window and release grab"""
        self.grab_release() 
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x700+{x}+{y}")


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

        # FIRST ROW - Item Name, Category, Current Stock/Restock Quantity
        # Item Name
        ctk.CTkLabel(self, text="Item Name", font=label_font, fg_color="white", text_color="black").place(x=120, y=150)
        self.entry_itemname = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                      bg_color="white")
        self.entry_itemname.place(x=120, y=200)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=210, y=145)
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
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=495, y=145)
        create_underline(420, 230, 140)

        # Current Stock 
        if not self.is_editing:
            # Add mode: Show Current Stock field
            ctk.CTkLabel(self, text="Current Stock", font=label_font, fg_color="white", text_color="black").place(x=720, y=150)
            self.entry_current_stock = ctk.CTkEntry(self, width=150, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
            self.entry_current_stock.place(x=720, y=200)
            ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=890, y=145)
            create_underline(720, 230, 180)
            add_placeholder(self.entry_current_stock, "Type here")

        # SECOND ROW - Average Weekly Usage, Delivery Time, Supplier Name
        # Average Weekly Usage
        ctk.CTkLabel(self, text="Average Weekly Usage", font=label_font, fg_color="white", text_color="black").place(x=120, y=300)
        self.entry_averageuse = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                      bg_color="white")
        self.entry_averageuse.place(x=120, y=350)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=300, y=295)
        create_underline(120, 380, 180)
        if not self.is_editing:
            add_placeholder(self.entry_averageuse, "Type here")

        # Delivery Time in Days
        ctk.CTkLabel(self, text="Delivery Time in Days", font=label_font, fg_color="white", text_color="black").place(x=420, y=300)
        self.entry_delivery_date = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                 bg_color="white")
        self.entry_delivery_date.place(x=420, y=350)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=580, y=295)
        create_underline(420, 380, 140)
        if not self.is_editing:
            add_placeholder(self.entry_delivery_date, "Type here")

        # Supplier Name 
        ctk.CTkLabel(self, text="Supplier Name", font=label_font, fg_color="white", text_color="black").place(x=720, y=300)
        self.entry_supplier_name = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                 bg_color="white")
        self.entry_supplier_name.place(x=720, y=350)
        ctk.CTkLabel(self, text="*Not Required", font=required_font, text_color="red", bg_color="white").place(x=880, y=295)
        create_underline(720, 380, 180)
        if not self.is_editing:
            add_placeholder(self.entry_supplier_name, "Supplier ABC")

        # THIRD ROW - Expiration Date 
        if not self.is_editing:
            ctk.CTkLabel(self, text="Expiration Date", font=label_font, fg_color="white", text_color="black").place(x=120, y=450)
            self.entry_expiration_date = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                     bg_color="white")
            self.entry_expiration_date.place(x=120, y=500)
            ctk.CTkLabel(self, text="*Not Required", font=required_font, text_color="red", bg_color="white").place(x=300, y=445)
            ctk.CTkLabel(self, text="(YYYY-MM-DD)", font=("Merriweather Sans", 10), text_color="#666666", bg_color="white").place(x=120, y=535)
            create_underline(120, 530, 180)
            add_placeholder(self.entry_expiration_date, "2024-12-31")

        # Populate fields if editing
        if self.is_editing:
            self.populate_fields()

        def retrieve_supply_data(cursor, column, unique_id):
            try:
                query = f"SELECT {column} FROM supply WHERE item_id = %s"
                
                cursor.execute(query, [unique_id])
                result = cursor.fetchone()[0]
                return result
            
            except Exception as e:
                print('error retrieving supply data (retrieve_supply_data)', e)

        def set_supply_data(cursor, column, row, unique_id):
            try:
                query = f"""
                UPDATE supply
                SET {column} = %s 
                WHERE item_id = %s
                """
                
                cursor.execute(query, [row, unique_id])

            except Exception as e:
                print('error setting supply data (set_supply_data)', e)

        def set_stock_levels(avg_weekly_usage, delivery_time, current_stock_val):

            #daily usage for standard dev
            avg_daily_usage = avg_weekly_usage / 7 
                
            #standard 20% 
            daily_standard_dev_estimate = avg_daily_usage * 0.2
            safety_stock = 2.33 * daily_standard_dev_estimate * math.sqrt(delivery_time)
            reorder_point = (avg_daily_usage * delivery_time) + safety_stock

            #stock level
            low_stock_level = reorder_point
            critical_stock_level = 0.50 * reorder_point
            good_level = reorder_point * 1.7

            if current_stock_val <= critical_stock_level:
                status = 'Critical Stock Level'

            elif current_stock_val <= low_stock_level:
                status = 'Low Stock Level'

            elif current_stock_val <= good_level:
                status = 'Good Stock Level'
            
            elif current_stock_val > good_level:
                status = 'Excellent Stock Level'         

            return status
        
        def update_notif_restock(cursor, user_fn, item_name, res_quan, curr_stock, status, notif_type):
            try:
                cursor.execute("""
                    INSERT INTO notification_logs(user_fullname, item_name, restock_quantity, current_stock, stock_status, notification_type, notification_timestamp) 
                    VALUES(%s, %s, %s, %s, %s, %s, NOW())
                """, (user_fn, item_name, res_quan, curr_stock, status, notif_type))

                unique_id = cursor.lastrowid
                return unique_id

            except Exception as e:
                print(f'Error inserting ({notif_type}):', e)

        def validate_date_format(date_string):
            """Validate date format YYYY-MM-DD"""
            try:
                datetime.strptime(date_string, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        def on_save_click():
            item_name_val = self.entry_itemname.get().strip()
            category = self.entry_category.get().strip()
            avg_weekly_usage_str = self.entry_averageuse.get().strip()      
            delivery_time_str = self.entry_delivery_date.get().strip()
            supplier_name_str = self.entry_supplier_name.get().strip()
            
            # Only get expiration date in add mode
            if not self.is_editing:
                expiration_date_str = self.entry_expiration_date.get().strip()
            else:
                expiration_date_str = ""
            item_name = ' '.join(item.capitalize() for item in item_name_val.split())

            item_id_store = []

            # Validation for required field
            if not item_name or item_name == "Type here":
                CTkMessageBox.show_error("Input Error", "Item Name is required.", parent=self)
                return
            if not category:
                CTkMessageBox.show_error("Input Error", "Category is required.", parent=self)
                return
            
            # Validate Average Weekly Usage
            if not avg_weekly_usage_str or avg_weekly_usage_str == "Type here":
                CTkMessageBox.show_error("Input Error", "Average Weekly Usage is required.", parent=self)
                return
            try:
                avg_weekly_usage = float(avg_weekly_usage_str)
                if avg_weekly_usage <= 0:
                    CTkMessageBox.show_error("Input Error", "Average weekly usage must be greater than 0.", parent=self)
                    return
            except ValueError:
                CTkMessageBox.show_error("Input Error", "Average weekly usage must be a valid number.", parent=self)
                return

            # Validate Delivery Time
            if not delivery_time_str or delivery_time_str == "Type here":
                CTkMessageBox.show_error("Input Error", "Delivery Time in Days is required.", parent=self)
                return
            try:
                delivery_time = int(delivery_time_str)
                if delivery_time <= 0:
                    CTkMessageBox.show_error("Input Error", "Delivery time must be greater than 0.", parent=self)
                    return
            except ValueError:
                CTkMessageBox.show_error("Input Error", "Delivery time must be a valid number.", parent=self)
                return

            # Validate Supplier Name
            
            # Validate Expiration Date 
            if not self.is_editing and expiration_date_str and expiration_date_str != "2024-12-31":
                if not validate_date_format(expiration_date_str):
                    CTkMessageBox.show_error("Input Error", "Expiration Date must be in YYYY-MM-DD format.", parent=self)
                    return
            
            if self.is_editing:
                current_stock = None 
                restock_quantity = 0
            else:
                current_stock_str = self.entry_current_stock.get().strip()
                if not current_stock_str or current_stock_str == "Type here":
                    CTkMessageBox.show_error("Input Error", "Current Stock is required.", parent=self)
                    return
                
                try:
                    current_stock = int(current_stock_str)
                    if current_stock < 0:
                        CTkMessageBox.show_error("Input Error", "Current stock cannot be negative.", parent=self)
                        return
                except ValueError:
                    CTkMessageBox.show_error("Input Error", "Current stock must be a valid number.", parent=self)
                    return
                restock_quantity = 0 

            supply_information = {
                'item_name': item_name,
                'category': category,
                'current_stock': current_stock,
                'restock_quantity': restock_quantity,
                'average_weekly_usage': avg_weekly_usage,
                'delivery_time_days': delivery_time
            }

            supply_column = ', '.join(supply_information.keys())
            supply_row = [f"{entries}" for entries in supply_information.values()]

            username = login_shared_states.get('logged_username', None)

            try:
                connect = db()
                cursor = connect.cursor()

                cursor.execute("""
                    SELECT full_name FROM users
                    WHERE username = %s
                """, (username,))

                user_fn = cursor.fetchone()[0]

                if self.is_editing:
                    cursor.execute("""
                        SELECT item_name FROM supply
                        WHERE item_id = %s
                    """, (self.edit_data['item_id'],))

                    item_fn = cursor.fetchone()[0]

            except Exception as e:
                print('error retrieving user_fullname ', e)
            finally:
                cursor.close()
                connect.close()

            try:
                connect = db()
                cursor = connect.cursor()

                now = datetime.now()
                right_now = now.strftime('%Y-%m-%d %H:%M:%S')

                if self.is_editing:
                    current_stock_before = retrieve_supply_data(cursor, 'current_stock', self.edit_data['item_id'])

                    # Update the supply record
                    cursor.execute("""  
                        UPDATE supply 
                        SET item_name = %s, category = %s, average_weekly_usage = %s, delivery_time_days = %s
                        WHERE item_id = %s 
                    """, (item_name, category, avg_weekly_usage, delivery_time, self.edit_data['item_id']))

                    # Current stock remains the same in edit mode
                    new_current_stock = current_stock_before
                    print(f"Updated supply item with ID: {self.edit_data['item_id']} without changing stock")

                    # Update stock level status with required values
                    status = set_stock_levels(avg_weekly_usage, delivery_time, new_current_stock)
                    set_status = set_supply_data(cursor, 'stock_level_status', status, self.edit_data['item_id']) 

                    connect.commit()
                    CTkMessageBox.show_success("Success", "Supply information updated successfully!", parent=self)

                else:
                    # Add mode logic remains the same
                    check_uniqueness = get_existing_credentials(item_name, 'item_name', table_name='supply')

                    if check_uniqueness:
                        CTkMessageBox.show_error("Error", 'Item already exists', parent=self)
                        return

                    item_id = supply_creation_id(supply_column, supply_row, table_name='supply')

                    if item_id: 
                        item_id_store.append(item_id)
                        
                        # Set max_supply to current_stock for new items
                        set_supply_data(cursor, 'max_supply', current_stock, item_id)

                        print('Item ID: ', item_id)
                        CTkMessageBox.show_success("Success", "Supply information saved successfully!", parent=self)
                    else:
                        print('Item ID creation error')
                        return
                    
                    current_stock_val = retrieve_supply_data(cursor, 'current_stock', item_id)

                    # Set stock level status with all required values
                    status = set_stock_levels(avg_weekly_usage, delivery_time, current_stock_val)
                    set_supply_data(cursor, 'stock_level_status', status, item_id)

                    cursor.execute("""
                        INSERT INTO notification_logs(user_fullname, item_name, notification_type, notification_timestamp) 
                        VALUES(%s, %s, %s, %s)
                    """, (user_fn, item_name, 'New Item Added', right_now))
                    connect.commit()

                    notification_id = cursor.lastrowid

                    print(f"""
                        New Item Added

                        {item_name} was added to the system by {user_fn}.  
                        
                        {right_now} 
                    """)

                connect.commit()

            except Exception as e:
                print(f"Error saving supply: {e}")
                CTkMessageBox.show_error("Error", f'Database error: {str(e)}', parent=self)
                return

            finally:
                cursor.close()
                connect.close() 
                self.close_window()

        # Save button
        button_text = "Update" if self.is_editing else "Save"
        self.btn_save = ctk.CTkButton(self, text=button_text, fg_color="#1A374D", hover_color="#16C79A", text_color="white",
                                      bg_color="white", corner_radius=20, font=button_font, width=200, height=50,
                                      command=on_save_click)
        
        # Position based on edit mode
        save_button_y = 420 if self.is_editing else 570
        self.btn_save.place(x=1020, y=save_button_y)

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

        # Clear and set average weekly usage
        self.entry_averageuse.delete(0, "end")
        avg_usage = self.edit_data.get('average_weekly_usage')
        if avg_usage is None or avg_usage == 0:
            self.entry_averageuse.insert(0, "0")
        else:
            self.entry_averageuse.insert(0, str(avg_usage))
        self.entry_averageuse.configure(text_color="black")
        
        # Clear and set delivery time
        self.entry_delivery_date.delete(0, "end")
        delivery_time = self.edit_data.get('delivery_time_days')
        if delivery_time is None or delivery_time == 0:
            self.entry_delivery_date.insert(0, "0")
        else:
            self.entry_delivery_date.insert(0, str(delivery_time))
        self.entry_delivery_date.configure(text_color="black")

        # Clear and set supplier name
        self.entry_supplier_name.delete(0, "end")
        # Show default supplier name since it's static
        self.entry_supplier_name.insert(0, "Default Supplier")
        self.entry_supplier_name.configure(text_color="black")
        
        # Clear and set expiration date 
        if not self.is_editing:
            self.entry_expiration_date.delete(0, "end")
            self.entry_expiration_date.insert(0, "2025-12-31")
            self.entry_expiration_date.configure(text_color="black")

def show_detailed_info(self, supply_data):
    self.table_frame.place_forget()
    self.button_frame.place_forget()
    
    # Update supply ID display
    self.supply_id_value.configure(text=supply_data[0])
    
    # Update supply info
    self.Supply_Name_Output.configure(text=supply_data[1])
    self.Category_Output.configure(text=supply_data[2])
    
    current_stock = supply_data[6]
    date_registered = supply_data[5] if len(supply_data) > 5 else "N/A"
    average_weekly_usage = supply_data[8] if len(supply_data) > 6 else "N/A"
    delivery_time_days = supply_data [10] if len(supply_data) > 7 else "N/A"

    # Display current stock as remaining stock
    self.currentstock_Output.configure(text=str(current_stock))
    self.Registered_Date_Output.configure(text=date_registered)
    self.Average_Weekly_Usage_Output.configure(text=str(average_weekly_usage))
    self.Delivery_Time_Output.configure(text=str(delivery_time_days))
    
    # Use current_stock for calculations
    current_stock_value = int(current_stock) if current_stock else 0
    max_stock = supply_data[12]  # max stock value

class EditStockWindow(SupplyBaseWindow):
    def __init__(self, parent, item_id=None):
        super().__init__(parent, "Edit Stock")

        # Store the item_id
        self.item_id = item_id

        print("edit stock - item_id:", self.item_id)

        # Title
        ctk.CTkLabel(
            self, 
            text="Edit Stock", 
            font=("Merriweather bold", 25), 
            text_color="black", 
            bg_color="white"
        ).place(x=90, y=60)

        # for placeholders
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

        def create_underline(x, y, width):
            ctk.CTkFrame(self, height=1, width=width, fg_color="black").place(x=x, y=y)

        # Font styles
        entry_font = ("Merriweather Sans", 13)
        label_font = ("Merriweather Sans bold", 15)
        required_font = ("Merriweather Sans bold", 10)

        # Patient ID Input
        ctk.CTkLabel(self, text="Patient ID", font=label_font, fg_color="white", text_color="black").place(x=120, y=150)
        self.entry_patient_id = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        self.entry_patient_id.place(x=120, y=200)
        create_underline(120, 230, 180)
        add_placeholder(self.entry_patient_id, "Type here")

        # Quantity Used Input
        ctk.CTkLabel(self, text="Quantity Used", font=label_font, fg_color="white", text_color="black").place(x=420, y=150)
        self.entry_quantity_used = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        self.entry_quantity_used.place(x=420, y=200)
        create_underline(420, 230, 180)
        add_placeholder(self.entry_quantity_used, "Type here")

        def retrieve_supply_data(cursor, column, unique_id):
            try:
                query = f"SELECT {column} FROM supply WHERE item_id = %s"
                
                cursor.execute(query, [unique_id])
                result = cursor.fetchone()[0]
                return result
            
            except Exception as e:
                print('error retrieving supply data (retrieve_supply_data)', e)

        def set_supply_data(cursor, column, row, unique_id):
            try:
                query = f"""
                UPDATE supply
                SET {column} = %s 
                WHERE item_id = %s
                """
                
                cursor.execute(query, [row, unique_id])

            except Exception as e:
                print('error setting supply data (set_supply_data)', e)

        def set_stock_levels(avg_weekly_usage, delivery_time, current_stock_val):

            #daily usage for standard dev
            avg_daily_usage = avg_weekly_usage / 7 

            #standard 20% 
            daily_standard_dev_estimate = avg_daily_usage * 0.2
            safety_stock = 2.33 * daily_standard_dev_estimate * math.sqrt(delivery_time)
            reorder_point = (avg_daily_usage * delivery_time) + safety_stock

            #stock level
            low_stock_level = reorder_point
            critical_stock_level = 0.50 * reorder_point
            good_level = reorder_point * 1.7

            if current_stock_val <= critical_stock_level:
                status = 'Critical Stock Level'

            elif current_stock_val <= low_stock_level:
                status = 'Low Stock Level'

            elif current_stock_val <= good_level:
                status = 'Good Stock Level'

            elif current_stock_val > good_level:   
                status = 'Excellent Stock Level' 

            return status

        def update_notif_status(cursor, user_fn, item_name, curr_stock, status, notif_type):
            try:
                cursor.execute("""
                    INSERT INTO notification_logs(user_fullname, item_name, current_stock, stock_status, notification_type, notification_timestamp) 
                    VALUES(%s, %s, %s, %s, %s, NOW())
                """, (user_fn, item_name, curr_stock, status, notif_type))

                unique_id = cursor.lastrowid  
                return unique_id

            except Exception as e:
                print(f'Error inserting ({notif_type}):', e)

        def on_submit_click():
            quantity_used = self.entry_quantity_used.get().strip()
            patient_id = self.entry_patient_id.get().strip()

            # Validation for quantity_used 
            if not quantity_used or quantity_used.lower() == 'type here':
                print("Quantity used is required.")
                return

            try:
                quantity_used = int(quantity_used)
                if quantity_used <= 0:
                    print("Quantity used must be greater than 0.")
                    return
            except ValueError:
                print("Quantity used must be a valid integer.")
                return

            # Validation for patient_id 
            if not patient_id or patient_id.lower() == 'type here':
                print("Patient ID is required.")
                return
            try:
                patient_id = int(patient_id)
            except ValueError:
                print("Patient ID must be a valid integer.")
                return

            # Get current timestamp for usage
            from datetime import datetime
            current_timestamp = datetime.now()
            usage_date = current_timestamp.date()  # Date only
            usage_time = current_timestamp.time()  # Time only
            usage_datetime = current_timestamp     # Full datetime

            usage_information = {
                'item_id': self.item_id,
                'patient_id': patient_id,
                'quantity_used': quantity_used,
                'usage_date': usage_date,
                'usage_time': usage_time,
                'usage_timestamp': usage_datetime  # Full timestamp with date and time
            }

            username = login_shared_states.get('logged_username', None)

            try:
                connect = db()
                cursor = connect.cursor()

                # Add safety checks for user lookup
                if username:
                    cursor.execute("""
                        SELECT full_name FROM users
                        WHERE username = %s
                    """, (username,))
                    
                    user_result = cursor.fetchone()
                    if user_result:
                        user_fn = user_result[0]
                    else:
                        print(f"WARNING: No user found with username '{username}', using default")
                        user_fn = "Unknown User"
                else:
                    print("WARNING: No username in shared state, using default")
                    user_fn = "Unknown User"

                # Add safety check for item lookup
                cursor.execute("""
                    SELECT item_name FROM supply
                    WHERE item_id = %s
                """, (self.item_id,))

                item_result = cursor.fetchone()
                if item_result:
                    notif_item_name = item_result[0]
                else:
                    print(f"ERROR: No item found with item_id '{self.item_id}'")
                    return

                # Check if there's enough stock
                current_stock = retrieve_supply_data(cursor, 'current_stock', self.item_id)
                if current_stock is None:
                    print(f"ERROR: Could not retrieve current stock for item_id '{self.item_id}'")
                    return
                    
                if current_stock < quantity_used:
                    print(f"Insufficient stock. Available: {current_stock}, Requested: {quantity_used}")
                    return

                # Insert usage record with full timestamp information
                try:
                    cursor.execute("""
                        INSERT INTO item_usage (item_id, patient_id, quantity_used, usage_date, usage_time, usage_timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (self.item_id, patient_id, quantity_used, usage_date, usage_time, usage_datetime))
                    
                    usage_id = cursor.lastrowid
                    print(f'Usage record created successfully with ID: {usage_id}')
                    print(f'Timestamp recorded: {usage_datetime}')
                    
                except Exception as e:
                    # If the table doesn't have separate time columns, try with just timestamp
                    print(f"Error with full timestamp insert, trying alternative: {e}")
                    cursor.execute("""
                        INSERT INTO item_usage (item_id, patient_id, quantity_used, usage_date)
                        VALUES (%s, %s, %s, %s)
                    """, (self.item_id, patient_id, quantity_used, usage_datetime))
                    
                    usage_id = cursor.lastrowid
                    print(f'Usage record created with basic timestamp: {usage_id}')

                if usage_id:
                    print(f'Usage ID creation successful: {usage_id}')
                    print(f'Stock usage recorded at: {current_timestamp.strftime("%Y-%m-%d %H:%M:%S")}')

                    # IMPORTANT: Only update current_stock, DO NOT change max_supply
                    total_stock = current_stock - quantity_used
                    set_supply_data(cursor, 'current_stock', total_stock, self.item_id)
                    print(f'Item ID {self.item_id}: Previous stock was {current_stock} now updated to {total_stock}')
                    print(f'IMPORTANT: max_supply remains unchanged when using quantity')

                    # Update stock level status
                    current_stock_val = retrieve_supply_data(cursor, 'current_stock', self.item_id)
                    avg_weekly_usage_result = retrieve_supply_data(cursor, 'average_weekly_usage', self.item_id)
                    delivery_time_result = retrieve_supply_data(cursor, 'delivery_time_days', self.item_id)

                    right_now = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')

                    if avg_weekly_usage_result and avg_weekly_usage_result > 0 and delivery_time_result and delivery_time_result > 0:
                        status = set_stock_levels(avg_weekly_usage_result, delivery_time_result, current_stock_val)
                        set_supply_data(cursor, 'stock_level_status', status, self.item_id)
                        if status:
                            notification_id = update_notif_status(cursor, user_fn, notif_item_name, total_stock, status, 'Item Stock Status Alert')

                            print(f"""
                                Item Stock Status Alert

                                {notif_item_name} is at {status} and only has {total_stock} quantities left, please inform the admin.

                                {right_now}
                            """)

                    connect.commit()
                    
                    print(f"Stock updated successfully! New stock: {total_stock}")
                    print(f"Usage timestamp: {right_now}")
                    
                    # Refresh 
                    if hasattr(self.master, 'selected_supply_id') and self.master.selected_supply_id == self.item_id:
                        self.master.refresh_detailed_view()
                        print("Detailed view refreshed with new stock levels")
                    
                    # Also refresh the table view
                    if hasattr(self.master, 'refresh_table'):
                        self.master.refresh_table()
                        print("Table view refreshed")
                    
                    self.close_window()
                else:
                    print("ERROR: Failed to create usage record")
                    return

            except Exception as e:
                print('Error with editing supply stocks', e)
                # Add more detailed error information
                import traceback
                print("Full traceback:")
                traceback.print_exc()
            finally:
                cursor.close()
                connect.close()

        # Submit button
        button_font = ("Merriweather Bold", 20)
        self.btn_submit = ctk.CTkButton(self, text="Submit", fg_color="#1A374D", hover_color="#16C79A", text_color="white",
                                      bg_color="white", corner_radius=20, font=button_font, width=200, height=50,
                                      command=on_submit_click)
        self.btn_submit.place(x=720, y=300)

        exit_image = ctk.CTkImage(light_image=Image.open("assets/exit.png"), size=(30, 30))
        self.exit_button = ctk.CTkButton(self, image=exit_image, text="", fg_color="transparent", bg_color="white", hover_color="white",
                                         width=40, height=40, command=self.close_window)
        self.exit_button.place(x=1200, y=15)

class QuantityUsedLogsWindow(SupplyBaseWindow):
    def __init__(self, parent, item_id=None):
        super().__init__(parent, "Quantity Used Logs")  
        self.geometry("1300x700")
        self.center_window()

        # Store the item_id
        self.item_id = item_id
        print("quantity used log - item_id:", self.item_id)

        # Get item name first to use in title and labels
        self.item_name = self.get_item_name()
        
        # Update window title with actual item name
        if self.item_name:
            self.title(f"Quantity Used Logs - {self.item_name}")

        # Main content area 
        self.logs_frame = ctk.CTkFrame(self,
                                      width=1180,
                                      height=580,
                                      corner_radius=20,
                                      fg_color="#FFFFFF",
                                      bg_color="transparent")
        self.logs_frame.place(x=60, y=80)
        
        # Header frame with colored background (similar to patient/backup tables)
        header_frame = ctk.CTkFrame(self.logs_frame,
                                   width=1160,
                                   height=40,
                                   corner_radius=10,
                                   fg_color="#1A374D")  # Using your app's primary color
        header_frame.place(x=10, y=10)
        
        # Header labels with proper spacing
        ctk.CTkLabel(header_frame, text="Patient ID", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=40, y=10)
        
        ctk.CTkLabel(header_frame, text="Patient Details", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=330, y=10)
        
        ctk.CTkLabel(header_frame, text="Quantity", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=670, y=10)
        
        ctk.CTkLabel(header_frame, text="Timestamp", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=885, y=10)
        
        # Scrollable frame for usage data (matching ReportPage style)
        self.usage_scrollable_frame = ctk.CTkScrollableFrame(self.logs_frame,
                                                           width=1160,
                                                           height=510,
                                                           corner_radius=0,
                                                           fg_color="transparent")
        self.usage_scrollable_frame.place(x=10, y=55)
        
        # Title above the table with actual item name
        title_text = f"Quantity Used Logs - {self.item_name}" if self.item_name else "Quantity Used Logs"
        title_label = ctk.CTkLabel(
            self, 
            text=title_text, 
            font=("Merriweather Bold", 22), 
            text_color="#1A374D",
            bg_color="white"
        )
        title_label.place(x=90, y=30)
        
        # Subtitle with item name context
        subtitle_text = f"Every usage of {self.item_name} will appear here" if self.item_name else "Every item usage will appear here"
        subtitle_label = ctk.CTkLabel(
            self, 
            text=subtitle_text, 
            font=("Merriweather Sans", 12), 
            text_color="#666666",
            bg_color="white"
        )
        subtitle_label.place(x=90, y=55)

        # Load the usage data
        self.load_usage_data()

    def get_item_name(self):
        """Get the item name from the database using item_id"""
        if not self.item_id:
            return None
            
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT item_name FROM supply 
                WHERE item_id = %s
            """, (self.item_id,))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                print(f"No item found with item_id: {self.item_id}")
                return None
                
        except Exception as e:
            print(f'Error getting item name: {e}')
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def load_usage_data(self):
        """Load usage data from database and display in table with full timestamp"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Query to get usage logs for this specific item with full timestamp
            cursor.execute("""
                SELECT 
                    iu.patient_id,
                    CONCAT(pi.first_name, 
                        CASE WHEN pi.middle_name IS NOT NULL AND pi.middle_name != '' 
                                THEN CONCAT(' ', pi.middle_name, ' ') 
                                ELSE ' ' END, 
                        pi.last_name) as patient_name,
                    COALESCE(pi.age, 'N/A') as age,
                    COALESCE(pi.gender, 'N/A') as gender,
                    COALESCE(pi.access_type, 'N/A') as access_type,
                    iu.quantity_used,
                    COALESCE(iu.usage_timestamp, iu.usage_date) as usage_datetime,
                    iu.usage_time
                FROM item_usage iu
                JOIN patient_info pi ON iu.patient_id = pi.patient_id
                JOIN supply s ON iu.item_id = s.item_id
                WHERE iu.item_id = %s
                ORDER BY COALESCE(iu.usage_timestamp, iu.usage_date) DESC, 
                        COALESCE(iu.usage_time, '00:00:00') DESC
            """, (self.item_id,))
            
            usage_logs = cursor.fetchall()
            
            # Clear existing data
            for widget in self.usage_scrollable_frame.winfo_children():
                widget.destroy()
            
            if not usage_logs:
                # Show "No data" message if no logs found
                no_data_frame = ctk.CTkFrame(self.usage_scrollable_frame,
                                        width=1140,
                                        height=100,
                                        corner_radius=5,
                                        fg_color="#F8F9FA")
                no_data_frame.pack(fill="x", pady=20, padx=5)
                no_data_frame.pack_propagate(False)
                
                no_data_text = f"No usage logs found for {self.item_name}" if self.item_name else "No usage logs found for this item"
                ctk.CTkLabel(no_data_frame, 
                        text=no_data_text,
                        font=("Poppins Regular", 14),
                        text_color="#666666").place(relx=0.5, rely=0.5, anchor="center")
                return
            
            # Add usage log rows with full timestamp display
            for i, (patient_id, patient_name, age, gender, access_type, quantity_used, usage_datetime, usage_time) in enumerate(usage_logs):
                # Create row frame with alternating colors - taller for two-line content
                row_frame = ctk.CTkFrame(self.usage_scrollable_frame,
                                    width=1140,
                                    height=60,  # Increased height for two-line content
                                    corner_radius=5,
                                    fg_color="#F8F9FA" if i % 2 == 0 else "#FFFFFF")
                row_frame.pack(fill="x", pady=2, padx=5)
                row_frame.pack_propagate(False)
                
                # Patient ID - centered vertically
                id_label = ctk.CTkLabel(row_frame, text=str(patient_id),
                                    font=("Poppins Regular", 11),
                                    text_color="#333333",
                                    width=80)
                id_label.place(x=10, y=20)
                
                # Patient Details 
                # Patient Name
                name_label = ctk.CTkLabel(row_frame, text=patient_name,
                                        font=("Poppins Bold", 14),  # Bold and larger
                                        text_color="#333333",
                                        width=400)
                name_label.place(x=170, y=8)
                
                # Patient additional details (age, gender, access_type) - Clean any placeholder text
                # Handle potential None or placeholder values
                age_clean = str(age) if age and str(age) not in ['None', 'Type here', ''] else 'N/A'
                gender_clean = str(gender) if gender and str(gender) not in ['None', 'Type here', ''] else 'N/A'
                access_type_clean = str(access_type) if access_type and str(access_type) not in ['None', 'Type here', ''] else 'N/A'
                
                details_text = f"{age_clean}, {gender_clean}, {access_type_clean}"
                details_label = ctk.CTkLabel(row_frame, text=details_text,
                                        font=("Poppins Regular", 10), 
                                        text_color="#666666",  
                                        width=400)
                details_label.place(x=170, y=32)
                
                # Quantity Used - centered vertically
                quantity_label = ctk.CTkLabel(row_frame, text=f"{quantity_used} pc(s)",
                                            font=("Poppins Regular", 11),
                                            text_color="#333333",
                                            width=100)
                quantity_label.place(x=640, y=20)
                
                # Timestamp - Handle different timestamp formats
                if usage_datetime:
                    try:
                        # Try to parse as datetime first
                        if hasattr(usage_datetime, 'strftime'):
                            # It's already a datetime object
                            date_part = usage_datetime.strftime("%Y-%m-%d")
                            time_part = usage_datetime.strftime("%H:%M:%S")
                        else:
                            # It might be a string, try to parse it
                            from datetime import datetime
                            if isinstance(usage_datetime, str):
                                # Try parsing different formats
                                try:
                                    dt = datetime.strptime(usage_datetime, "%Y-%m-%d %H:%M:%S")
                                    date_part = dt.strftime("%Y-%m-%d")
                                    time_part = dt.strftime("%H:%M:%S")
                                except ValueError:
                                    try:
                                        dt = datetime.strptime(usage_datetime, "%Y-%m-%d")
                                        date_part = dt.strftime("%Y-%m-%d")
                                        # Use separate time column if available
                                        if usage_time and hasattr(usage_time, 'strftime'):
                                            time_part = usage_time.strftime("%H:%M:%S")
                                        elif usage_time:
                                            time_part = str(usage_time)
                                        else:
                                            time_part = "N/A"
                                    except ValueError:
                                        date_part = str(usage_datetime)
                                        time_part = str(usage_time) if usage_time else "N/A"
                            else:
                                date_part = str(usage_datetime)
                                time_part = str(usage_time) if usage_time else "N/A"
                        
                        # Date (larger)
                        date_label = ctk.CTkLabel(row_frame, text=date_part,
                                                font=("Poppins Regular", 11),
                                                text_color="#333333",
                                                width=150)
                        date_label.place(x=840, y=8)
                        
                        # Time (smaller)
                        time_label = ctk.CTkLabel(row_frame, text=time_part,
                                                font=("Poppins Regular", 10),
                                                text_color="#666666",
                                                width=150)
                        time_label.place(x=840, y=32)
                        
                    except Exception as e:
                        print(f"Error parsing timestamp: {e}")
                        # Fallback to string representation
                        timestamp_label = ctk.CTkLabel(row_frame, text=str(usage_datetime),
                                                    font=("Poppins Regular", 11),
                                                    text_color="#333333",
                                                    width=150)
                        timestamp_label.place(x=840, y=20)
                else:
                    # Single "N/A" label if no date
                    timestamp_label = ctk.CTkLabel(row_frame, text="N/A",
                                                font=("Poppins Regular", 11),
                                                text_color="#333333",
                                                width=150)
                    timestamp_label.place(x=840, y=20)
                
        except Exception as e:
            print(f'Error loading usage data: {e}')
            # Show error message
            error_frame = ctk.CTkFrame(self.usage_scrollable_frame,
                                    width=1140,
                                    height=100,
                                    corner_radius=5,
                                    fg_color="#FFE6E6")
            error_frame.pack(fill="x", pady=20, padx=5)
            error_frame.pack_propagate(False)
            
            error_label = ctk.CTkLabel(error_frame,
                                    text=f"Error loading data: {str(e)}",
                                    font=("Poppins Regular", 12),
                                    text_color="red")
            error_label.place(relx=0.5, rely=0.5, anchor="center")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x700+{x}+{y}")

    def close_window(self):
        """Properly close the window and release grab"""
        self.grab_release() 
        self.destroy()

class PatientQuantityUsedLogsWindow(SupplyBaseWindow):
    def __init__(self, parent, patient_id=None):
        super().__init__(parent, "Patient Quantity Used Logs")  # Initial title without patient name
        self.geometry("1300x700")
        self.center_window()

        # Store the patient_id
        self.patient_id = patient_id
        print("patient quantity used log - patient_id:", self.patient_id)

        # Get patient name first to use in title and labels
        self.patient_name = self.get_patient_name()
        
        # Update window title with actual patient name
        if self.patient_name:
            self.title(f"Quantity Used Logs - {self.patient_name}")

        # Main content area
        self.logs_frame = ctk.CTkFrame(self,
                                      width=1180,
                                      height=580,
                                      corner_radius=20,
                                      fg_color="#FFFFFF",
                                      bg_color="transparent")
        self.logs_frame.place(x=60, y=80)
        
        # Header frame with colored background
        header_frame = ctk.CTkFrame(self.logs_frame,
                                   width=1160,
                                   height=40,
                                   corner_radius=10,
                                   fg_color="#1A374D")  # Using your app's primary color
        header_frame.place(x=10, y=10)
        
        # Header labels with proper spacing for patient usage logs
        ctk.CTkLabel(header_frame, text="Item ID", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=40, y=10)
        
        ctk.CTkLabel(header_frame, text="Item Details", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=330, y=10)
        
        ctk.CTkLabel(header_frame, text="Quantity Used", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=650, y=10)
        
        ctk.CTkLabel(header_frame, text="Timestamp", 
                    font=("Merriweather Bold", 12), text_color="white").place(x=885, y=10)
        
        # Scrollable frame for usage data (matching ReportPage style)
        self.usage_scrollable_frame = ctk.CTkScrollableFrame(self.logs_frame,
                                                           width=1160,
                                                           height=510,
                                                           corner_radius=0,
                                                           fg_color="transparent")
        self.usage_scrollable_frame.place(x=10, y=55)
        
        # Title above the table with actual patient name
        title_text = f"Quantity Used Logs - {self.patient_name}" if self.patient_name else "Patient Quantity Used Logs"
        title_label = ctk.CTkLabel(
            self, 
            text=title_text, 
            font=("Merriweather Bold", 22), 
            text_color="#1A374D",
            bg_color="white"
        )
        title_label.place(x=90, y=30)
        
        # Subtitle with patient name context
        subtitle_text = f"All items used by {self.patient_name} will appear here" if self.patient_name else "All items used by this patient will appear here"
        subtitle_label = ctk.CTkLabel(
            self, 
            text=subtitle_text, 
            font=("Merriweather Sans", 12), 
            text_color="#666666",
            bg_color="white"
        )
        subtitle_label.place(x=90, y=55)

        # Load the usage data
        self.load_usage_data()

    def get_patient_name(self):
        """Get the patient name from the database using patient_id"""
        if not self.patient_id:
            return None
            
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("""
                SELECT patient_name FROM patient_list 
                WHERE patient_id = %s
            """, (self.patient_id,))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                print(f"No patient found with patient_id: {self.patient_id}")
                return None
                
        except Exception as e:
            print(f'Error getting patient name: {e}')
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def load_usage_data(self):
        """Load usage data from database and display in table (quantity_used_patient logic)"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            # Query to get usage logs for this specific patient (based on your quantity_used_patient function)
            cursor.execute("""
                SELECT 
                    iu.item_id, 
                    s.item_name, 
                    s.category, 
                    iu.quantity_used, 
                    COALESCE(iu.usage_timestamp, iu.usage_date) as usage_datetime,
                    iu.usage_time
                FROM item_usage iu 
                JOIN supply s ON iu.item_id = s.item_id
                WHERE iu.patient_id = %s
                ORDER BY COALESCE(iu.usage_timestamp, iu.usage_date) DESC, 
                         COALESCE(iu.usage_time, '00:00:00') DESC
            """, (self.patient_id,))
            
            usage_logs = cursor.fetchall()
            
            # Clear existing data
            for widget in self.usage_scrollable_frame.winfo_children():
                widget.destroy()
            
            if not usage_logs:
                # Show "No data" message if no logs found
                no_data_frame = ctk.CTkFrame(self.usage_scrollable_frame,
                                           width=1140,
                                           height=100,
                                           corner_radius=5,
                                           fg_color="#F8F9FA")
                no_data_frame.pack(fill="x", pady=20, padx=5)
                no_data_frame.pack_propagate(False)
                
                no_data_text = f"No usage logs found for {self.patient_name}" if self.patient_name else "No usage logs found for this patient"
                ctk.CTkLabel(no_data_frame, 
                           text=no_data_text,
                           font=("Poppins Regular", 14),
                           text_color="#666666").place(relx=0.5, rely=0.5, anchor="center")
                return
            
            # Add usage log rows for patient (showing items used)
            for i, (item_id, item_name, category, quantity_used, usage_datetime, usage_time) in enumerate(usage_logs):
                # Create row frame with alternating colors - taller for two-line content
                row_frame = ctk.CTkFrame(self.usage_scrollable_frame,
                                       width=1140,
                                       height=60,  # Increased height for two-line content
                                       corner_radius=5,
                                       fg_color="#F8F9FA" if i % 2 == 0 else "#FFFFFF")
                row_frame.pack(fill="x", pady=2, padx=5)
                row_frame.pack_propagate(False)
                
                # Item ID - centered vertically
                id_label = ctk.CTkLabel(row_frame, text=str(item_id),
                                      font=("Poppins Regular", 11),
                                      text_color="#333333",
                                      width=80)
                id_label.place(x=10, y=20)
                
                # Item Details - Two lines: Item Name (bold, larger) and Category
                # Item Name (bold and larger)
                name_label = ctk.CTkLabel(row_frame, text=item_name,
                                        font=("Poppins Bold", 14),  # Bold and larger
                                        text_color="#333333",
                                        width=400)
                name_label.place(x=170, y=8)
                
                # Category (smaller, lighter)
                category_clean = str(category) if category and str(category) not in ['None', 'Type here', ''] else 'N/A'
                category_label = ctk.CTkLabel(row_frame, text=f"Category: {category_clean}",
                                           font=("Poppins Regular", 10),  # Smaller font
                                           text_color="#666666",  # Lighter color
                                           width=400)
                category_label.place(x=170, y=32)
                
                # Quantity Used - centered vertically
                quantity_label = ctk.CTkLabel(row_frame, text=f"{quantity_used} pc(s)",
                                            font=("Poppins Regular", 11),
                                            text_color="#333333",
                                            width=100)
                quantity_label.place(x=640, y=20)
                
                # Timestamp - Handle different timestamp formats (same as supply logs)
                if usage_datetime:
                    try:
                        # Try to parse as datetime first
                        if hasattr(usage_datetime, 'strftime'):
                            # It's already a datetime object
                            date_part = usage_datetime.strftime("%Y-%m-%d")
                            time_part = usage_datetime.strftime("%H:%M:%S")
                        else:
                            # It might be a string, try to parse it
                            from datetime import datetime
                            if isinstance(usage_datetime, str):
                                # Try parsing different formats
                                try:
                                    dt = datetime.strptime(usage_datetime, "%Y-%m-%d %H:%M:%S")
                                    date_part = dt.strftime("%Y-%m-%d")
                                    time_part = dt.strftime("%H:%M:%S")
                                except ValueError:
                                    try:
                                        dt = datetime.strptime(usage_datetime, "%Y-%m-%d")
                                        date_part = dt.strftime("%Y-%m-%d")
                                        # Use separate time column if available
                                        if usage_time and hasattr(usage_time, 'strftime'):
                                            time_part = usage_time.strftime("%H:%M:%S")
                                        elif usage_time:
                                            time_part = str(usage_time)
                                        else:
                                            time_part = "N/A"
                                    except ValueError:
                                        date_part = str(usage_datetime)
                                        time_part = str(usage_time) if usage_time else "N/A"
                            else:
                                date_part = str(usage_datetime)
                                time_part = str(usage_time) if usage_time else "N/A"
                        
                        # Date (larger)
                        date_label = ctk.CTkLabel(row_frame, text=date_part,
                                                font=("Poppins Regular", 11),
                                                text_color="#333333",
                                                width=150)
                        date_label.place(x=840, y=8)
                        
                        # Time (smaller)
                        time_label = ctk.CTkLabel(row_frame, text=time_part,
                                                font=("Poppins Regular", 10),
                                                text_color="#666666",
                                                width=150)
                        time_label.place(x=840, y=32)
                        
                    except Exception as e:
                        print(f"Error parsing timestamp: {e}")
                        # Fallback to string representation
                        timestamp_label = ctk.CTkLabel(row_frame, text=str(usage_datetime),
                                                     font=("Poppins Regular", 11),
                                                     text_color="#333333",
                                                     width=150)
                        timestamp_label.place(x=840, y=20)
                else:
                    # Single "N/A" label if no date
                    timestamp_label = ctk.CTkLabel(row_frame, text="N/A",
                                                 font=("Poppins Regular", 11),
                                                 text_color="#333333",
                                                 width=150)
                    timestamp_label.place(x=840, y=20)
                
        except Exception as e:
            print(f'Error loading patient usage data: {e}')
            # Show error message
            error_frame = ctk.CTkFrame(self.usage_scrollable_frame,
                                     width=1140,
                                     height=100,
                                     corner_radius=5,
                                     fg_color="#FFE6E6")
            error_frame.pack(fill="x", pady=20, padx=5)
            error_frame.pack_propagate(False)
            
            error_label = ctk.CTkLabel(error_frame,
                                     text=f"Error loading data: {str(e)}",
                                     font=("Poppins Regular", 12),
                                     text_color="red")
            error_label.place(relx=0.5, rely=0.5, anchor="center")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + int(3 * 50)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"1300x700+{x}+{y}")

    def close_window(self):
        """Properly close the window and release grab"""
        self.grab_release() 
        self.destroy()