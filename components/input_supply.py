import customtkinter as ctk
from tkinter import Toplevel, ttk
from tkcalendar import Calendar, DateEntry
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

        # Supplier Name - NOW REQUIRED
        ctk.CTkLabel(self, text="Supplier Name", font=label_font, fg_color="white", text_color="black").place(x=720, y=300)
        self.entry_supplier_name = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                 bg_color="white")
        self.entry_supplier_name.place(x=720, y=350)
        ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=810, y=295)
        create_underline(720, 380, 180)
        if not self.is_editing:
            add_placeholder(self.entry_supplier_name, "Supplier ABC")

        # THIRD ROW - Expiration Date - NOW REQUIRED
        if not self.is_editing:
            ctk.CTkLabel(self, text="Expiration Date", font=label_font, fg_color="white", text_color="black").place(x=120, y=450)
            self.entry_expiration_date = DateEntry(self, width=18, font=("Merriweather Sans", 12), bg="white", 
                                                  date_pattern="yyyy-MM-dd", state="normal")
            self.entry_expiration_date.place(x=120, y=500, height=30)
            ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=210, y=445)
            ctk.CTkLabel(self, text="(YYYY-MM-DD)", font=("Merriweather Sans", 10), text_color="#666666", bg_color="white").place(x=120, y=535)
            
            # Set default expiration date to today's date + 1 year
            today = date.today()
            default_expiry = date(today.year + 1, today.month, today.day)
            self.entry_expiration_date.set_date(default_expiry)

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
                print(f'error retrieving supply data (retrieve_supply_data) in column {column}', e)

        def set_supply_data(cursor, column, row, unique_id):
            try:
                query = f"""
                UPDATE supply
                SET {column} = %s 
                WHERE item_id = %s
                """
                
                cursor.execute(query, [row, unique_id])

            except Exception as e:
                print(f'error setting supply data (set_supply_data) in column {column}', e)

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
            """Validate date format YYYY-MM-DD and ensure it's a valid date"""
            try:
                parsed_date = datetime.strptime(date_string, '%Y-%m-%d').date()
                return True
            except ValueError:
                return False

        def on_save_click():
            item_name_val = self.entry_itemname.get().strip()
            category = self.entry_category.get().strip()
            avg_weekly_usage_str = self.entry_averageuse.get().strip()      
            delivery_time_str = self.entry_delivery_date.get().strip()
            supplier_name_str = self.entry_supplier_name.get().strip()

            today_now = datetime.now().date()
            
            # Only get expiration date in add mode
            if not self.is_editing:
                expiry_date = self.entry_expiration_date.get_date()
                expiration_date_str = expiry_date.strftime("%Y-%m-%d")
            else:
                expiration_date_str = ""
            item_name = ' '.join(item.capitalize() for item in item_name_val.split())

            item_id_store = []

            # Validation for required fields
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
            if not supplier_name_str or supplier_name_str == "Supplier ABC":
                CTkMessageBox.show_error("Input Error", "Supplier Name is required.", parent=self)
                return
            
            # Validate Expiration Date 
            if not self.is_editing:
                # Get the date from DateEntry widget
                expiry_date = self.entry_expiration_date.get_date()
                expiration_date_str = expiry_date.strftime("%Y-%m-%d")
                
                # Check if expiration date is in the future
                if expiry_date <= today_now:
                    CTkMessageBox.show_error("Input Error", "Expiration Date must be in the future.", parent=self)
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
                'delivery_time_days': delivery_time,
                'new_expiry_date': expiration_date_str,
                'supplier_name': supplier_name_str,
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
                today = datetime.now().date()

                if self.is_editing:
                    current_stock_before = retrieve_supply_data(cursor, 'current_stock', self.edit_data['item_id'])

                    # Update the supply record
                    cursor.execute("""  
                        UPDATE supply 
                        SET item_name = %s, category = %s, average_weekly_usage = %s, delivery_time_days = %s, supplier_name = %s
                        WHERE item_id = %s 
                    """, (item_name, category, avg_weekly_usage, delivery_time, supplier_name_str, self.edit_data['item_id']))
                    connect.commit()

                    # cursor.execute("""
                    #     SELECT new_expiry_date FROM supply
                    #     WHERE item_id = %s
                    # """, (self.edit_data['item_id']),)
                    # new_expiry_date = cursor.fetchone()[0]

                    # cursor.execute("UPDATE supply SET previous_")

                    # Current stock remains the same in edit mode
                    new_current_stock = current_stock_before
                    print(f"Updated supply item with ID: {self.edit_data['item_id']} without changing stock")

                    # Update stock level status with required values
                    status = set_stock_levels(avg_weekly_usage, delivery_time, new_current_stock)
                    set_supply_data(cursor, 'stock_level_status', status, self.edit_data['item_id']) 
                    set_supply_data(cursor, 'status_update', today, self.edit_data['item_id'])

                    
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
                    set_supply_data(cursor, 'status_update', today, item_id)

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
        supplier_name = self.edit_data.get('supplier_name')
        if supplier_name and supplier_name != 'None' and str(supplier_name).strip():
            self.entry_supplier_name.insert(0, str(supplier_name))
        else:
            self.entry_supplier_name.insert(0, "Default Supplier")  
        self.entry_supplier_name.configure(text_color="black")

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
    average_weekly_usage = supply_data[8] if len(supply_data) > 8 else "N/A"
    delivery_time_days = supply_data [10] if len(supply_data) > 10 else "N/A"
    current_restock_expiry = supply_data[13] if len(supply_data) > 13 else "N/A"
    previous_restock_expiry = supply_data[14] if len(supply_data) > 14 else "N/A"
    supplier_name_output = supply_data[15] if len(supply_data) > 15 else "N/A"

    # Display current stock as remaining stock
    self.currentstock_Output.configure(text=str(current_stock))
    self.Registered_Date_Output.configure(text=date_registered)
    self.Average_Weekly_Usage_Output.configure(text=str(average_weekly_usage))
    self.Delivery_Time_Output.configure(text=str(delivery_time_days))

    self.Current_Restock_Expiry_Output.configure(text=str(current_restock_expiry))
    self.Previous_Restock_Expiry_Output.configure(text=str(previous_restock_expiry))
    self.Supplier_Name_Output.configure(text=str(supplier_name_output))
    
    # Use current_stock for calculations
    current_stock_value = int(current_stock) if current_stock else 0
    max_stock = supply_data[12]  # max stock value

class EditStockWindow(SupplyBaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Edit Stock")
        
        # Store parent reference for later use
        self.parent = parent
        
        self.sidebar.destroy()

        header_bar = ctk.CTkFrame(self.main_frame, 
                                 height=40, 
                                 fg_color="#1A374D",
                                 corner_radius=0)
        header_bar.pack(fill="x", side="top")
        header_bar.pack_propagate(False)

        # Main content frame
        content_frame = ctk.CTkFrame(self.main_frame, 
                                   fg_color="white",
                                   corner_radius=0)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title and subtitle in content area 
        title_label = ctk.CTkLabel(content_frame, 
                                  text="Edit Stock", 
                                  font=("Merriweather Bold", 20), 
                                  text_color="#1A374D")
        title_label.pack(anchor="w", pady=(0, 3))

        subtitle_label = ctk.CTkLabel(content_frame, 
                                     text="Item restock will be processed here", 
                                     font=("Merriweather Sans", 11), 
                                     text_color="#666666")
        subtitle_label.pack(anchor="w", pady=(0, 20))

        # Scrollable frame for multiple rows 
        self.scrollable_frame = ctk.CTkScrollableFrame(content_frame,
                                                      height=320,
                                                      fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Store row widgets
        self.stock_rows = []
        
        # Create first row with database items
        self.add_stock_row()

        # Bottom frame for buttons
        bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom")

        # Add more rows button
        self.add_row_button = ctk.CTkButton(bottom_frame,
                                           text="+ Add more rows",
                                           font=("Merriweather Sans", 11),
                                           fg_color="transparent",
                                           text_color="#1A374D",
                                           hover_color="#F0F0F0",
                                           width=120,
                                           height=25,
                                           command=self.add_stock_row)
        self.add_row_button.pack(side="left", pady=(5, 0))

        # Submit button
        submit_button = ctk.CTkButton(bottom_frame,
                                     text="Submit",
                                     font=("Merriweather Bold", 14),
                                     fg_color="#1A374D",
                                     hover_color="#16C79A",
                                     text_color="white",
                                     width=100,
                                     height=35,
                                     corner_radius=8,
                                     command=self.submit_changes)
        submit_button.pack(side="right", pady=(5, 0))

    def get_database_items(self):
        """Get item names from database for dropdown initialization"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("SELECT item_name FROM supply ORDER BY item_name")
            result = cursor.fetchall()
            
            cursor.close()
            connect.close()
            
            return ["Click to choose"] + [row[0] for row in result]
            
        except Exception as e:
            print(f"Error fetching item names from database: {e}")
            return ["Click to choose"]

    def delete_stock_row(self, row_data):
        """Delete a specific stock row"""
        print(f"Delete button clicked. Current rows: {len(self.stock_rows)}")
        
        # Don't allow deletion if this is the last row
        if len(self.stock_rows) <= 1:
            print("Cannot delete - at least one row must remain.")
            return
        
        # Remove the row from the list
        if row_data in self.stock_rows:
            self.stock_rows.remove(row_data)
            # Destroy the frame widget
            row_data['frame'].destroy()
            print(f"Successfully deleted row. Remaining rows: {len(self.stock_rows)}")
        else:
            print("Error: Row data not found in stock_rows list")

    def add_stock_row(self):
        """Add a new stock row"""
        row_index = len(self.stock_rows)

        # Create row frame
        row_frame = ctk.CTkFrame(self.scrollable_frame, 
                                fg_color="transparent",
                                height=130)
        row_frame.pack(fill="x", pady=(0, 20), padx=5)
        row_frame.pack_propagate(False)

        # Configure grid 
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1) 
        row_frame.grid_columnconfigure(2, weight=1)
        row_frame.grid_columnconfigure(3, weight=0)  

        # Item Name section
        item_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        item_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        item_label = ctk.CTkLabel(item_frame, 
                                 text="Item Name", 
                                 font=("Merriweather Sans bold", 14), 
                                 text_color="#333333")
        item_label.pack(anchor="w", pady=(0, 8))

        # Get actual items from database instead of hardcoded values
        database_items = self.get_database_items()
        
        item_var = ctk.StringVar(value="Click to choose")
        item_dropdown = ctk.CTkComboBox(item_frame,
                                       variable=item_var,
                                       values=database_items,
                                       state="readonly",
                                       width=200,
                                       height=35,
                                       font=("Merriweather Sans", 12),
                                       fg_color="#e8e8e8",
                                       border_width=1,
                                       border_color="black",
                                       button_color="#1A374D",
                                       button_hover_color="#68EDC6",
                                       dropdown_fg_color="white",
                                       dropdown_hover_color="#68EDC6",
                                       text_color="black",
                                       dropdown_text_color="black")
        item_dropdown.pack(fill="x")

        # Quantity Used section
        qty_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        qty_frame.grid(row=0, column=1, sticky="ew", padx=5)

        qty_label = ctk.CTkLabel(qty_frame, 
                                text="Quantity to Add", 
                                font=("Merriweather Sans bold", 14), 
                                text_color="#333333")
        qty_label.pack(anchor="w", pady=(0, 8))

        qty_var = ctk.StringVar()
        qty_entry = ctk.CTkEntry(qty_frame,
                                textvariable=qty_var,
                                width=200,
                                height=35,
                                font=("Merriweather Sans", 12),
                                fg_color="#e8e8e8",
                                border_width=1,
                                border_color="black",
                                text_color="black")
        qty_entry.pack(fill="x")

        # Add placeholder behavior
        qty_entry.insert(0, "Enter Quantity")
        qty_entry.configure(text_color="gray")

        def on_qty_focus_in(event):
            if qty_entry.get() == "Enter Quantity":
                qty_entry.delete(0, "end")
                qty_entry.configure(text_color="black")

        def on_qty_focus_out(event):
            if qty_entry.get() == "":
                qty_entry.insert(0, "Enter Quantity")
                qty_entry.configure(text_color="gray")

        qty_entry.bind('<FocusIn>', on_qty_focus_in)
        qty_entry.bind('<FocusOut>', on_qty_focus_out)

        # Expiry Date section  
        date_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        date_frame.grid(row=0, column=2, sticky="ew", padx=(5, 10))

        date_label = ctk.CTkLabel(date_frame, 
                                 text="Expiry Date", 
                                 font=("Merriweather Sans bold", 14), 
                                 text_color="#333333")
        date_label.pack(anchor="w", pady=(0, 8))

        # Use DateEntry instead of regular entry
        from tkcalendar import DateEntry
        date_entry = DateEntry(date_frame, 
                              width=16, 
                              font=("Merriweather Sans", 12), 
                              bg="#e8e8e8", 
                              date_pattern="yyyy-MM-dd", 
                              state="normal")
        date_entry.pack(fill="x", pady=(0, 0))

        # Store row data first (needed for delete function)
        row_data = {
            'frame': row_frame,
            'item_var': item_var,
            'item_dropdown': item_dropdown,
            'qty_var': qty_var,
            'qty_entry': qty_entry,
            'date_entry': date_entry
        }
        
        # Delete button section
        delete_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        delete_frame.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        spacer = ctk.CTkLabel(delete_frame, text="", height=20)
        spacer.pack()

        delete_button = ctk.CTkButton(delete_frame,
                                     text="🗑",
                                     font=("Arial", 14),
                                     fg_color="#dc3545",
                                     hover_color="#c82333",
                                     text_color="white",
                                     width=35,
                                     height=35,
                                     corner_radius=5,
                                     command=lambda: self.delete_stock_row(row_data))
        delete_button.pack()
        
        # Add delete button to row data
        row_data['delete_button'] = delete_button
        
        self.stock_rows.append(row_data)

    def set_stock_levels(self, avg_weekly_usage, delivery_time, current_stock_val):
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

    def set_supply_data(self, cursor, column, row, unique_id):
        try:
            query = f"""
            UPDATE supply
            SET {column} = %s 
            WHERE item_id = %s
            """
            
            cursor.execute(query, [row, unique_id])

        except Exception as e:
            print(f'error setting supply data (set_supply_data) in column {column}', e)

    # Submit changes
    def submit_changes(self):
        """Process and submit stock changes to database"""
        print("Submit button clicked!")
        
        from datetime import datetime

        # Collect data from all rows
        stock_changes = []
        today_date = datetime.now().date() 
        
        for i, row in enumerate(self.stock_rows):
            item_name = row['item_var'].get()
            quantity_str = row['qty_var'].get().strip()
            expiry_date = row['date_entry'].get() 
            
            # Skip empty rows
            if (item_name == "Click to choose" and 
                (not quantity_str or quantity_str == "Enter Quantity") and 
                not expiry_date):
                continue
            
        # Basic validation
        if item_name == "Click to choose":
            print(f"ERROR: Please select an item for row {i+1}.")
            return
        
        if not quantity_str or quantity_str == "Enter Quantity":
            print(f"ERROR: Please enter quantity for row {i+1}.")
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                print(f"ERROR: Quantity must be greater than 0 for row {i+1}.")
                return
        except ValueError:
            print(f"ERROR: Please enter a valid number for quantity in row {i+1}.")
            return
        
        if not expiry_date:
            print(f"ERROR: Please select an expiry date for row {i+1}.")
            return
            
        stock_changes.append({
            'item_name': item_name,
            'quantity': quantity,
            'expiry_date': expiry_date
        })
        
        if not stock_changes:
            print("ERROR: Please fill at least one row with complete information.")
            return
        
        # Database operations
        try:
            connect = db()
            cursor = connect.cursor()
            
            # First, verify all items exist in the database
            item_names = [item['item_name'] for item in stock_changes]
            placeholders = ', '.join(['%s'] * len(item_names))
            
            cursor.execute(f"""
                SELECT item_name FROM supply 
                WHERE item_name IN ({placeholders})
            """, item_names)
            
            existing_items = [row[0] for row in cursor.fetchall()]
            
            # Check for non-existent items
            missing_items = [item for item in item_names if item not in existing_items]
            if missing_items:
                print(f"ERROR: The following items don't exist in the database: {', '.join(missing_items)}")
                return
            
            # Use a simpler two-step approach for expiry dates
            names = ', '.join(['%s'] * len(stock_changes))
            
            # Step 1: Move current expiry to previous expiry (only if current expiry exists)
            cursor.execute(f"""
                UPDATE supply
                SET previous_expiry_date = CASE 
                    WHEN new_expiry_date IS NOT NULL THEN new_expiry_date 
                    ELSE previous_expiry_date 
                END
                WHERE item_name IN ({names});
            """, [item['item_name'] for item in stock_changes])
            
            # Step 2: Update stock and set new expiry date
            stock = ' '.join(f"WHEN %s THEN current_stock + %s" for _ in stock_changes)
            expiry = ' '.join(f"WHEN %s THEN %s" for _ in stock_changes)
            
            # Build the parameters list for step 2
            store = []
            
            # Add item names and quantities for stock update
            for item in stock_changes:
                store.extend([item['item_name'], item['quantity']])
            
            # Add item names and expiry dates for expiry update  
            for item in stock_changes:
                store.extend([item['item_name'], item['expiry_date']])
            
            # Add item names for WHERE clause
            store.extend([item['item_name'] for item in stock_changes])
            
            # Execute the main update query
            query = f"""
                UPDATE supply
                SET 
                    current_stock = CASE item_name
                        {stock}
                    END,
                    new_expiry_date = CASE item_name
                        {expiry}
                    END
                WHERE item_name IN ({names});
            """
            
            print("Executing query:", query)
            print("Parameters:", store)
            
            cursor.execute(query, store)
            
            # Insert restock logs for tracking
            for item in stock_changes:
                cursor.execute("""
                    INSERT INTO restock_logs (item_id, restock_quantity, restock_date)
                    SELECT item_id, %s, CURDATE()
                    FROM supply 
                    WHERE item_name = %s
                """, (item['quantity'], item['item_name']))

            for item in stock_changes:
                cursor.execute("""
                    SELECT item_id, average_weekly_usage, delivery_time_days, current_stock
                    FROM supply 
                    WHERE item_name = %s
                """, (item['item_name'],))
                
                result = cursor.fetchone()
                if result:
                    item_id, avg_weekly_usage, delivery_time, current_stock_val = result
                    
                    if avg_weekly_usage and delivery_time and current_stock_val is not None:
                        stock_status = self.set_stock_levels(avg_weekly_usage, delivery_time, current_stock_val)

                        self.set_supply_data(cursor, 'stock_level_status', stock_status, item_id)
                        if stock_status == 'Critical Stock Level' or stock_status == 'Low Stock Level':
                            self.set_supply_data(cursor, 'status_update', today_date, item_id)
                        
                        print(f"Updated stock status for {item['item_name']}: {stock_status}")
                    else:
                        print(f"Skipping stock level calculation for {item['item_name']} - missing required data")
            
            connect.commit()

            # Show success message
            message = "Stock successfully updated:\n\n"
            for change in stock_changes:
                message += f"• {change['item_name']}: +{change['quantity']} (Expiry: {change['expiry_date']})\n"
            
            print("SUCCESS:", message)
            
            # Clear the form
            self.clear_all_rows()
            
            # Refresh parent table if it exists
            if hasattr(self, 'parent') and hasattr(self.parent, 'refresh_table'):
                self.parent.refresh_table()
                print("Parent table refreshed successfully")
                
            # Also refresh the detailed view if an item is selected
            if hasattr(self.parent, 'selected_supply_id') and self.parent.selected_supply_id:
                self.parent.refresh_detailed_view()
                print("Parent detailed view refreshed successfully")
            
            print("Stock changes successfully committed to database")
            
        except Exception as e:
            connect.rollback()
            error_msg = f"Database error occurred: {str(e)}"
            print("ERROR:", error_msg)
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def clear_all_rows(self):
        """Clear all rows and reset to single empty row"""
        # Remove all existing rows
        for row in self.stock_rows:
            row['frame'].destroy()
        
        self.stock_rows.clear()
        
        # Add one fresh row
        self.add_stock_row()

    def populate_item_dropdown(self):
        """Populate dropdown with actual items from database"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("SELECT item_name FROM supply ORDER BY item_name")
            result = cursor.fetchall()
            
            item_names = ["Click to choose"] + [row[0] for row in result]
            
            # Update all existing dropdowns
            for row in self.stock_rows:
                row['item_dropdown'].configure(values=item_names)
            
            cursor.close()
            connect.close()
            
            return item_names
            
        except Exception as e:
            print(f"Error fetching item names: {e}")
            return ["Click to choose"] 

    def refresh_dropdowns(self):
        """Refresh all dropdowns with latest database items"""
        self.populate_item_dropdown()

class EditUsageWindow(SupplyBaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Edit Usage")

        self.sidebar.destroy()
        
        header_bar = ctk.CTkFrame(self.main_frame, 
                                 height=40, 
                                 fg_color="#1A374D",
                                 corner_radius=0)
        header_bar.pack(fill="x", side="top")
        header_bar.pack_propagate(False)

        # Main content frame
        content_frame = ctk.CTkFrame(self.main_frame, 
                                   fg_color="white",
                                   corner_radius=0)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title and subtitle in content area
        title_label = ctk.CTkLabel(content_frame, 
                                  text="Edit Usage", 
                                  font=("Merriweather Bold", 20), 
                                  text_color="#1A374D")
        title_label.pack(anchor="w", pady=(0, 3))

        subtitle_label = ctk.CTkLabel(content_frame, 
                                     text="Every patient item usage will be processed here", 
                                     font=("Merriweather Sans", 11), 
                                     text_color="#666666")
        subtitle_label.pack(anchor="w", pady=(0, 20))

        # Scrollable frame for multiple rows 
        self.scrollable_frame = ctk.CTkScrollableFrame(content_frame,
                                                      height=320,
                                                      fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Store row widgets
        self.item_rows = []
        
        # Get patient and item data from database
        self.patient_data = self.get_patient_data()
        self.item_data = self.get_item_data()
        
        # Create patient selection row (first row)
        self.create_patient_row()
        
        # Create first item row
        self.add_item_row()

        # Bottom frame for buttons
        bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom")

        # Add more rows button
        self.add_row_button = ctk.CTkButton(bottom_frame,
                                           text="+ Add more rows",
                                           font=("Merriweather Sans", 11),
                                           fg_color="transparent",
                                           text_color="#1A374D",
                                           hover_color="#F0F0F0",
                                           width=120,
                                           height=25,
                                           command=self.add_item_row)
        self.add_row_button.pack(side="left", pady=(5, 0))

        # Submit button
        submit_button = ctk.CTkButton(bottom_frame,
                                     text="Submit",
                                     font=("Merriweather Bold", 14),
                                     fg_color="#1A374D",
                                     hover_color="#16C79A",
                                     text_color="white",
                                     width=100,
                                     height=35,
                                     corner_radius=8,
                                     command=self.submit_usage_changes)
        submit_button.pack(side="right", pady=(5, 0))

    def get_patient_data(self):
        """Get patient data from database"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("SELECT patient_id, patient_name FROM patient_list ORDER BY patient_id")
            result = cursor.fetchall()
            
            patient_dict = {}
            for patient_id, patient_name in result:
                patient_dict[str(patient_id)] = patient_name
            
            cursor.close()
            connect.close()
            
            return patient_dict
            
        except Exception as e:
            print(f"Error fetching patient data: {e}")
            return {"P001": "Sample Patient"}  # Fallback
    
    def get_item_data(self):
        """Get item data from database"""
        try:
            connect = db()
            cursor = connect.cursor()
            
            cursor.execute("SELECT item_name FROM supply ORDER BY item_name")
            result = cursor.fetchall()
            
            item_list = [row[0] for row in result]
            
            cursor.close()
            connect.close()
            
            return item_list
            
        except Exception as e:
            print(f"Error fetching item data: {e}")
            return ["Syringe", "Bandage", "Medicine"]  # Fallback

    def create_patient_row(self):
        """Create the patient selection row (Patient ID and Patient Name)"""
        # Create patient row frame
        patient_row_frame = ctk.CTkFrame(self.scrollable_frame, 
                                        fg_color="transparent",
                                        height=110)
        patient_row_frame.pack(fill="x", pady=(0, 20), padx=5)
        patient_row_frame.pack_propagate(False)

        # Configure grid for 2 columns (Patient ID, Patient Name)
        patient_row_frame.grid_columnconfigure(0, weight=1)
        patient_row_frame.grid_columnconfigure(1, weight=1)

        # Patient ID section
        patient_id_frame = ctk.CTkFrame(patient_row_frame, fg_color="transparent")
        patient_id_frame.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        patient_id_label = ctk.CTkLabel(patient_id_frame, 
                                       text="Patient ID", 
                                       font=("Merriweather Sans bold", 14), 
                                       text_color="#333333")
        patient_id_label.pack(anchor="w", pady=(0, 8))

        # Patient ID dropdown with real data
        self.patient_id_var = ctk.StringVar(value="Click to choose")
        patient_ids = ["Click to choose"] + list(self.patient_data.keys())
        self.patient_id_dropdown = ctk.CTkComboBox(patient_id_frame,
                                                  variable=self.patient_id_var,
                                                  values=patient_ids,
                                                  state="readonly",
                                                  width=220,
                                                  height=35,
                                                  font=("Merriweather Sans", 12),
                                                  fg_color="#e8e8e8",
                                                  border_width=1,
                                                  border_color="black",
                                                  button_color="#1A374D",
                                                  button_hover_color="#68EDC6",
                                                  dropdown_fg_color="white",
                                                  dropdown_hover_color="#68EDC6",
                                                  text_color="black",
                                                  dropdown_text_color="black")
        self.patient_id_dropdown.pack(fill="x")

        # Patient Name section (auto-populated)
        patient_name_frame = ctk.CTkFrame(patient_row_frame, fg_color="transparent")
        patient_name_frame.grid(row=0, column=1, sticky="ew", padx=(15, 0))

        patient_name_label = ctk.CTkLabel(patient_name_frame, 
                                         text="Patient Name", 
                                         font=("Merriweather Sans bold", 14), 
                                         text_color="#333333")
        patient_name_label.pack(anchor="w", pady=(0, 8))

        # Patient name display (read-only)
        self.patient_name_display = ctk.CTkEntry(patient_name_frame,
                                                width=220,
                                                height=35,
                                                font=("Merriweather Sans", 12),
                                                fg_color="#f5f5f5",
                                                border_width=1,
                                                border_color="gray",
                                                text_color="black",
                                                state="disabled")
        self.patient_name_display.pack(fill="x")

        # Function to update patient name when patient ID is selected
        def on_patient_id_change(*args):
            selected_id = self.patient_id_var.get()
            if selected_id in self.patient_data:
                patient_name = self.patient_data[selected_id]
                self.patient_name_display.configure(state="normal")
                self.patient_name_display.delete(0, "end")
                self.patient_name_display.insert(0, patient_name)
                self.patient_name_display.configure(state="disabled")
            else:
                self.patient_name_display.configure(state="normal")
                self.patient_name_display.delete(0, "end")
                self.patient_name_display.configure(state="disabled")

        # Bind the patient ID dropdown to update patient name
        self.patient_id_var.trace("w", on_patient_id_change)

    def delete_item_row(self, row_data):
        """Delete a specific item row"""
        print(f"Delete item button clicked. Current rows: {len(self.item_rows)}")
        
        # Don't allow deletion if this is the last row
        if len(self.item_rows) <= 1:
            print("Cannot delete - at least one item row must remain.")
            return
        
        # Remove the row from the list
        if row_data in self.item_rows:
            self.item_rows.remove(row_data)
            # Destroy the frame widget
            row_data['frame'].destroy()
            print(f"Successfully deleted item row. Remaining rows: {len(self.item_rows)}")
        else:
            print("Error: Row data not found in item_rows list")

    def add_item_row(self):
        """Add a new item row (Item Name and Quantity Used)"""
        row_index = len(self.item_rows)

        # Create item row frame 
        item_row_frame = ctk.CTkFrame(self.scrollable_frame, 
                                     fg_color="transparent",
                                     height=130)
        item_row_frame.pack(fill="x", pady=(0, 20), padx=5)
        item_row_frame.pack_propagate(False)

        # Configure grid for 3 columns (Item Name, Quantity Used, Delete Button)
        item_row_frame.grid_columnconfigure(0, weight=1)
        item_row_frame.grid_columnconfigure(1, weight=1)
        item_row_frame.grid_columnconfigure(2, weight=0)  

        # Item Name section
        item_frame = ctk.CTkFrame(item_row_frame, fg_color="transparent")
        item_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        item_label = ctk.CTkLabel(item_frame, 
                                 text="Item Name", 
                                 font=("Merriweather Sans bold", 14), 
                                 text_color="#333333")
        item_label.pack(anchor="w", pady=(0, 8))

        # Item dropdown with real items from database
        item_var = ctk.StringVar(value="Click to choose")
        item_values = ["Click to choose"] + self.item_data
        item_dropdown = ctk.CTkComboBox(item_frame,
                                       variable=item_var,
                                       values=item_values,
                                       state="readonly",
                                       width=200,
                                       height=35,
                                       font=("Merriweather Sans", 12),
                                       fg_color="#e8e8e8",
                                       border_width=1,
                                       border_color="black",
                                       button_color="#1A374D",
                                       button_hover_color="#68EDC6",
                                       dropdown_fg_color="white",
                                       dropdown_hover_color="#68EDC6",
                                       text_color="black",
                                       dropdown_text_color="black")
        item_dropdown.pack(fill="x")

        # Quantity Used section
        qty_frame = ctk.CTkFrame(item_row_frame, fg_color="transparent")
        qty_frame.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        qty_label = ctk.CTkLabel(qty_frame, 
                                text="Quantity Used", 
                                font=("Merriweather Sans bold", 14), 
                                text_color="#333333")
        qty_label.pack(anchor="w", pady=(0, 8))

        qty_var = ctk.StringVar()
        qty_entry = ctk.CTkEntry(qty_frame,
                                textvariable=qty_var,
                                width=200,
                                height=35,
                                font=("Merriweather Sans", 12),
                                fg_color="#e8e8e8",
                                border_width=1,
                                border_color="black",
                                text_color="black")
        qty_entry.pack(fill="x")

        # Add placeholder behavior for quantity
        qty_entry.insert(0, "Enter Quantity")
        qty_entry.configure(text_color="gray")

        def on_qty_focus_in(event):
            if qty_entry.get() == "Enter Quantity":
                qty_entry.delete(0, "end")
                qty_entry.configure(text_color="black")

        def on_qty_focus_out(event):
            if qty_entry.get() == "":
                qty_entry.insert(0, "Enter Quantity")
                qty_entry.configure(text_color="gray")

        qty_entry.bind('<FocusIn>', on_qty_focus_in)
        qty_entry.bind('<FocusOut>', on_qty_focus_out)

        # Store row data first (needed for delete function)
        row_data = {
            'frame': item_row_frame,
            'item_var': item_var,
            'item_dropdown': item_dropdown,
            'qty_var': qty_var,
            'qty_entry': qty_entry
        }

        # Delete button section
        delete_frame = ctk.CTkFrame(item_row_frame, fg_color="transparent")
        delete_frame.grid(row=0, column=2, sticky="ew", padx=(5, 0))

        spacer = ctk.CTkLabel(delete_frame, text="", height=20)
        spacer.pack()

        delete_button = ctk.CTkButton(delete_frame,
                                     text="🗑",
                                     font=("Arial", 14),
                                     fg_color="#dc3545",
                                     hover_color="#c82333",
                                     text_color="white",
                                     width=35,
                                     height=35,
                                     corner_radius=5,
                                     command=lambda: self.delete_item_row(row_data))
        delete_button.pack()
        
        # Add delete button to row data
        row_data['delete_button'] = delete_button
        
        self.item_rows.append(row_data)

    def set_stock_levels(self, avg_weekly_usage, delivery_time, current_stock_val):
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

    def set_supply_data(self, cursor, column, row, unique_id):
        try:
            query = f"""
            UPDATE supply
            SET {column} = %s 
            WHERE item_id = %s
            """
            
            cursor.execute(query, [row, unique_id])

        except Exception as e:
            print(f'error setting supply data (set_supply_data) in column {column}', e)

    def submit_usage_changes(self):
        """Process and submit usage changes to database"""
        print("Submit usage button clicked!")
        
        # Get patient information
        patient_id = self.patient_id_var.get()
        patient_name = self.patient_name_display.get() if self.patient_name_display.get() else ""
        
        # Validate patient selection
        if patient_id == "Click to choose":
            print("ERROR: Please select a patient ID.")
            return
        
        # Collect data from all item rows
        usage_changes = []
        
        for i, row in enumerate(self.item_rows):
            item_name = row['item_var'].get()
            quantity_str = row['qty_var'].get().strip()
            
            # Skip empty rows
            if (item_name == "Click to choose" and 
                (not quantity_str or quantity_str == "Enter Quantity")):
                continue
            
            # Basic validation
            if item_name == "Click to choose":
                print(f"ERROR: Please select an item for row {i+1}.")
                return
            
            if not quantity_str or quantity_str == "Enter Quantity":
                print(f"ERROR: Please enter quantity for row {i+1}.")
                return
            
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    print(f"ERROR: Quantity must be greater than 0 for row {i+1}.")
                    return
            except ValueError:
                print(f"ERROR: Please enter a valid number for quantity in row {i+1}.")
                return
            
            usage_changes.append({
                'item_name': item_name,
                'quantity_used': quantity
            })
        
        if not usage_changes:
            print("ERROR: Please fill at least one item row with complete information.")
            return
        
        try:
            connect = db()
            cursor = connect.cursor()
            
            item_names = [item['item_name'] for item in usage_changes]
            placeholders = ', '.join(['%s'] * len(item_names))
            
            cursor.execute(f"""
                SELECT item_id, item_name, current_stock FROM supply 
                WHERE item_name IN ({placeholders})
            """, item_names)
            
            existing_items = cursor.fetchall()
            existing_item_dict = {item[1]: {'item_id': item[0], 'current_stock': item[2]} for item in existing_items}
            
            # Check for non-existent items
            missing_items = [item for item in item_names if item not in existing_item_dict]
            if missing_items:
                print(f"ERROR: The following items don't exist in the database: {', '.join(missing_items)}")
                return
            
            # Check for insufficient stock
            insufficient_stock = []
            for item in usage_changes:
                item_name = item['item_name']
                quantity_needed = item['quantity_used']
                current_stock = existing_item_dict[item_name]['current_stock']
                
                if current_stock < quantity_needed:
                    insufficient_stock.append(f"{item_name} (Available: {current_stock}, Needed: {quantity_needed})")
            
            if insufficient_stock:
                print(f"ERROR: The following items don't have enough stock:\n{chr(10).join(insufficient_stock)}")
                return
            
            # Build the dynamic SQL query for stock reduction 
            stock_cases = []
            stock_params = []
            where_params = []
            
            for item in usage_changes:
                stock_cases.append("WHEN %s THEN current_stock - %s")
                stock_params.extend([item['item_name'], item['quantity_used']])
                where_params.append('%s')
            
            stock = ' '.join(stock_cases)
            names = ', '.join(where_params)
            
            # Build the parameters list
            store = stock_params + [item['item_name'] for item in usage_changes]
            
            # Execute the stock reduction query
            query = f"""
                UPDATE supply
                SET 
                    current_stock = CASE item_name
                        {stock}
                    END
                WHERE item_name IN ({names});
            """
            
            # Get username first for logging
            username = login_shared_states.get('logged_username', None)
            if username:
                cursor.execute("SELECT full_name FROM users WHERE username = %s", (username,))
                result = cursor.fetchone()
                user_fullname = result[0] if result else "Unknown User"
            else:
                user_fullname = "Unknown User"
            
            print("Executing query:", query)
            print("Parameters:", store)
            print("Number of usage changes:", len(usage_changes))
            print("Stock cases:", stock_cases)
            print("Patient ID:", patient_id)
            print("Username:", username)
            print("User fullname:", user_fullname)
            
            cursor.execute(query, store)
            
            from datetime import datetime
            now = datetime.now()
            today_date = datetime.now().date()
            
            # First, insert all usage records
            for item in usage_changes:
                item_id = existing_item_dict[item['item_name']]['item_id']
                
                print(f"Inserting usage: patient_id={patient_id}, item_id={item_id}, quantity={item['quantity_used']}")
                
                try:
                    cursor.execute("""
                        INSERT INTO item_usage (patient_id, item_id, quantity_used, usage_date, usage_time, usage_timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (patient_id, item_id, item['quantity_used'], 
                        now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S'), now))
                except Exception as usage_error:
                    print(f"Error inserting usage log: {usage_error}")
                    raise usage_error
                
                # Insert usage notification for each item
                try:
                    cursor.execute("""
                        INSERT INTO notification_logs (user_fullname, item_name, patient_id, 
                                                    notification_type, notification_timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_fullname, item['item_name'], patient_id, 
                        'Item Usage Recorded', now))
                except Exception as notif_error:
                    print(f"Error inserting notification log: {notif_error}")
            
            # Now check stock levels and handle alerts for each item separately
            for item in usage_changes:
                cursor.execute("""
                    SELECT item_id, average_weekly_usage, delivery_time_days, current_stock
                    FROM supply 
                    WHERE item_name = %s
                """, (item['item_name'],))
                
                result = cursor.fetchone()
                if result:
                    item_id, avg_weekly_usage, delivery_time, current_stock_val = result
                    
                    if avg_weekly_usage and delivery_time and current_stock_val is not None:
                        # Calculate stock status for THIS specific item
                        stock_status = self.set_stock_levels(avg_weekly_usage, delivery_time, current_stock_val)
                        
                        # Update the stock status in database
                        self.set_supply_data(cursor, 'stock_level_status', stock_status, item_id)
                        
                        print(f"""
                        Item Stock Status Update:
                        Item: {item['item_name']}
                        Status: {stock_status}
                        Current Stock: {current_stock_val}
                        """)
                        
                        # Only create alert and notification for critical/low stock
                        if stock_status in ['Critical Stock Level', 'Low Stock Level']:
                            # Update status_update field
                            self.set_supply_data(cursor, 'status_update', today_date, item_id)
                            
                            # Print alert message
                            print(f"""
                            Item Stock Status Alert
                            
                            {item['item_name']} is at {stock_status} and 
                            only has {current_stock_val} quantities left, please
                            inform the admin.
                            {now}
                            """)
                            
                            # Insert stock alert notification
                            try:
                                cursor.execute("""
                                    INSERT INTO notification_logs (user_fullname, item_name,
                                                                notification_type, notification_timestamp)
                                    VALUES (%s, %s, %s, %s)
                                """, (user_fullname, item['item_name'], 'Item Stock Status Alert', now))
                            except Exception as e:
                                print(f'Error inserting stock status alert notification: {e}')
                        
                        else:
                            print(f"{item['item_name']} stock level is {stock_status} - no alert needed")
                            
                    else:
                        print(f"Skipping stock level calculation for {item['item_name']} - missing required data")
                else:
                    print(f"No supply data found for {item['item_name']}")
            
            connect.commit()
            
            # Show success message
            message = f"Usage successfully recorded for {patient_name} (ID: {patient_id}):\n\n"
            for change in usage_changes:
                message += f"• {change['item_name']}: {change['quantity_used']} pc(s) used\n"
            
            print("SUCCESS:", message)
            
            # Clear the form
            self.clear_all_rows()
            
            # Refresh parent table if it exists
            if hasattr(self.master, 'refresh_table'):
                self.master.refresh_table()
            
            # Trigger supply page refresh through parent
            if hasattr(self.master, 'refresh_supply_page_after_usage'):
                self.master.refresh_supply_page_after_usage()
            
            print("Usage changes successfully committed to database")
            
        except Exception as e:
            connect.rollback()
            error_msg = f"Database error occurred: {str(e)}"
            print("ERROR:", error_msg)
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connect' in locals():
                connect.close()

    def clear_all_rows(self):
        """Clear all rows and reset to single empty row"""
        # Clear patient selection
        self.patient_id_var.set("Click to choose")
        self.patient_name_display.configure(state="normal")
        self.patient_name_display.delete(0, "end")
        self.patient_name_display.configure(state="disabled")
        
        # Remove all existing item rows
        for row in self.item_rows:
            row['frame'].destroy()
        
        self.item_rows.clear()
        
        # Add one fresh item row
        self.add_item_row()

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
        super().__init__(parent, "Patient Quantity Used Logs")  
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
                                   fg_color="#1A374D")  
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
        
        # Scrollable frame for usage data
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

    def refresh_table(self):
        """Refresh the quantity used table with latest data"""
        try:
            print(f"🔄 Refreshing quantity used data for patient {self.patient_id}")
            
            # Clear existing data in the scrollable frame
            for widget in self.usage_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Reload the data
            self.load_usage_data()
            
            print("✅ Quantity used table refreshed successfully!")
            
        except Exception as e:
            print(f"❌ Error refreshing quantity used table: {e}")

    def reload_data(self):
        """Alternative method name for refreshing data"""
        self.refresh_table()

    def refresh_data(self):
        """Another alternative method name for refreshing data"""
        self.refresh_table()

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
            
            # Query to get usage logs for this specific patient 
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