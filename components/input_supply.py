import customtkinter as ctk
from tkinter import Toplevel, ttk
from tkcalendar import Calendar
from PIL import Image
from backend.crud import supply_creation_id, get_existing_credentials
from backend.connector import db_connection as db
import math
from datetime import date

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

        if not self.is_editing:
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
        
        if not self.is_editing:
            ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=495, y=145)
        
        create_underline(420, 230, 140)

        # Current Stock (add mode) / Restock Quantity (edit mode)
        if self.is_editing:
            # Edit mode: Show Restock Quantity field
            ctk.CTkLabel(self, text="Restock Quantity", font=label_font, fg_color="white", text_color="black").place(x=720, y=150)
            self.entry_restock_quantity = ctk.CTkEntry(self, width=150, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
            self.entry_restock_quantity.place(x=720, y=200)
            create_underline(720, 230, 180)
        
        else:
            # Add mode: Show Current Stock field
            ctk.CTkLabel(self, text="Current Stock", font=label_font, fg_color="white", text_color="black").place(x=720, y=150)
            self.entry_current_stock = ctk.CTkEntry(self, width=150, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
            self.entry_current_stock.place(x=720, y=200)
            ctk.CTkLabel(self, text="*Required", font=required_font, text_color="#008400", bg_color="white").place(x=890, y=145)
            create_underline(720, 230, 180)
            add_placeholder(self.entry_current_stock, "Type here")

        # Second Row - Average Weekly Usage
        ctk.CTkLabel(self, text="Average Weekly Usage", font=label_font, fg_color="white", text_color="black").place(x=120, y=300)
        self.entry_averageuse = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                      bg_color="white")
        self.entry_averageuse.place(x=120, y=350)
   
        if not self.is_editing:
            ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red", bg_color="white").place(x=300, y=295)
        
        create_underline(120, 380, 180)
        if not self.is_editing:
            add_placeholder(self.entry_averageuse, "Type here")

        # Delivery Time in Days
        ctk.CTkLabel(self, text="Delivery Time in Days", font=label_font, fg_color="white", text_color="black").place(x=420, y=300)
        self.entry_delivery_date = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                 bg_color="white")
        self.entry_delivery_date.place(x=420, y=350)
        
        if not self.is_editing:
            ctk.CTkLabel(self, text="*Not Required", font=not_required_font, text_color="red", bg_color="white").place(x=580, y=295)
        
        create_underline(420, 380, 140)
        if not self.is_editing:
            add_placeholder(self.entry_delivery_date, "Type here")

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

        def on_save_click():
            item_name_val = self.entry_itemname.get().strip()
            category = self.entry_category.get().strip()
            avg_weekly_usage_str = self.entry_averageuse.get().strip()      
            delivery_time_str = self.entry_delivery_date.get().strip()
            item_name = ' '.join(item.capitalize() for item in item_name_val.split())

            item_id_store = []

            if not item_name or item_name == "Type here":
                CTkMessageBox.show_error("Input Error", "Item Name is required.", parent=self)
                return
            if not category:
                CTkMessageBox.show_error("Input Error", "Category is required.", parent=self)
                return
            
            if self.is_editing:
                restock_quantity_str = self.entry_restock_quantity.get().strip()
                if not restock_quantity_str:
                    restock_quantity = 0
                else:
                    try:
                        restock_quantity = int(restock_quantity_str)
                        if restock_quantity < 0:
                            CTkMessageBox.show_error("Input Error", "Restock quantity cannot be negative.", parent=self)
                            return
                    except ValueError:
                        CTkMessageBox.show_error("Input Error", "Restock quantity must be a valid number.", parent=self)
                        return
                current_stock = None 
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

            # Handle optional numeric fields
            try:
                if avg_weekly_usage_str and avg_weekly_usage_str != "Type here":
                    avg_weekly_usage = float(avg_weekly_usage_str)
                    if avg_weekly_usage < 0:
                        CTkMessageBox.show_error("Input Error", "Average weekly usage cannot be negative.", parent=self)
                        return
                else:
                    avg_weekly_usage = 0
            except ValueError:
                CTkMessageBox.show_error("Input Error", "Average weekly usage must be a valid number.", parent=self)
                return

            try:
                # Delivery time - allow empty or placeholder for optional field
                if delivery_time_str and delivery_time_str != "Type here":
                    delivery_time = int(delivery_time_str)
                    if delivery_time < 0:
                        CTkMessageBox.show_error("Input Error", "Delivery time cannot be negative.", parent=self)
                        return
                else:
                    delivery_time = 0
            except ValueError:
                CTkMessageBox.show_error("Input Error", "Delivery time must be a valid number.", parent=self)
                return

            # Handle date field - set to None if empty or placeholder
            # if not restock_date or restock_date == "Select date":
            #     restock_date = None

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

            try:
                connect = db()
                cursor = connect.cursor()

                if self.is_editing:
                    # Get current stock BEFORE updating
                    current_stock_before = retrieve_supply_data(cursor, 'current_stock', self.edit_data['item_id'])
                    
                    # Update the supply record (but don't change current_stock yet)
                    cursor.execute("""
                        UPDATE supply 
                        SET item_name = %s, category = %s, restock_quantity = %s, 
                        average_weekly_usage = %s, delivery_time_days = %s
                        WHERE item_id = %s 
                    """, (item_name, category, restock_quantity, avg_weekly_usage, delivery_time, self.edit_data['item_id']))

                    # Only add restock quantity to current stock if restock_quantity > 0
                    if restock_quantity > 0:
                        cursor.execute("""
                            INSERT INTO restock_logs(item_id, restock_quantity, restock_date)
                            VALUES(%s, %s, %s)
                        """, (self.edit_data['item_id'], restock_quantity, date.today()))

                        new_current_stock = current_stock_before + restock_quantity
                        print(f"Updated supply item with ID: {self.edit_data['item_id']} and added {restock_quantity} to stock")
                        print(f"Stock changed from {current_stock_before} to {new_current_stock}")  
                    else:
                        new_current_stock = current_stock_before
                        print(f"Updated supply item with ID: {self.edit_data['item_id']} without changing stock")

                    set_supply_data(cursor, 'current_stock', new_current_stock, self.edit_data['item_id'])

                    # Update max_supply if the new stock is higher
                    #cursor, column, unique_id
                    max_supply_current = retrieve_supply_data(cursor, 'max_supply', self.edit_data['item_id'])
                    if max_supply_current is None or new_current_stock > max_supply_current:
                        set_supply_data(cursor, 'max_supply', new_current_stock, self.edit_data['item_id'])

                    # Get updated values for calculations
                    avg_weekly_usage_result = retrieve_supply_data(cursor, 'average_weekly_usage', self.edit_data['item_id'])
                    delivery_time_result = retrieve_supply_data(cursor, 'delivery_time_days', self.edit_data['item_id'])

                    if avg_weekly_usage_result > 0 and delivery_time_result > 0:
                        status = set_stock_levels(avg_weekly_usage, delivery_time, new_current_stock)
                        set_supply_data(cursor, 'stock_level_status', status, self.edit_data['item_id'])

                    connect.commit()
                    CTkMessageBox.show_success("Success", "Supply information updated successfully!", parent=self)

                else:

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
                    avg_weekly_usage_result = retrieve_supply_data(cursor, 'average_weekly_usage', item_id)
                    delivery_time_result = retrieve_supply_data(cursor, 'delivery_time_days', item_id)

                    if avg_weekly_usage_result > 0 and delivery_time_result > 0:
                        status = set_stock_levels(avg_weekly_usage, delivery_time_result, current_stock_val)
                        set_supply_data(cursor, 'stock_level_status', status, item_id)

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
        
        # Clear and set
        if self.is_editing:
            self.entry_restock_quantity.delete(0, "end")
            restock_qty = self.edit_data.get('restock_quantity')
            if restock_qty is None or restock_qty == 0:
                self.entry_restock_quantity.insert(0, "0")
            else:
                self.entry_restock_quantity.insert(0, str(restock_qty))
            self.entry_restock_quantity.configure(text_color="black")

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

            usage_information = {
                'item_id': self.item_id,
                'patient_id': patient_id,
                'quantity_used': quantity_used
            }

            try:
                connect = db()
                cursor = connect.cursor()

                # Check if there's enough stock
                current_stock = retrieve_supply_data(cursor, 'current_stock', self.item_id)
                if current_stock < quantity_used:
                    print(f"Insufficient stock. Available: {current_stock}, Requested: {quantity_used}")
                    return

                usage_column = ', '.join(usage_information.keys())
                usage_rows = [f'{entries}' for entries in usage_information.values()]

                usage_id = supply_creation_id(usage_column, usage_rows, table_name='item_usage')

                if usage_id:
                    print(f'usage id creation successful: {usage_id}')

                    # IMPORTANT: Only update current_stock, DO NOT change max_supply
                    total_stock = current_stock - quantity_used
                    set_supply_data(cursor, 'current_stock', total_stock, self.item_id)
                    print(f'Item ID {self.item_id}: Previous stock was {current_stock} now updated to {total_stock}')
                    print(f'IMPORTANT: max_supply remains unchanged when using quantity')

                    # Update stock level status
                    current_stock_val = retrieve_supply_data(cursor, 'current_stock', self.item_id)
                    avg_weekly_usage_result = retrieve_supply_data(cursor, 'average_weekly_usage', self.item_id)
                    delivery_time_result = retrieve_supply_data(cursor, 'delivery_time_days', self.item_id)

                    if avg_weekly_usage_result > 0 and delivery_time_result > 0:
                        status = set_stock_levels(avg_weekly_usage_result, delivery_time_result, current_stock_val)
                        set_supply_data(cursor, 'stock_level_status', status, self.item_id)

                    connect.commit()
                    
                    print(f"Stock updated successfully! New stock: {total_stock}")
                    
                    # Refresh 
                    if hasattr(self.master, 'selected_supply_id') and self.master.selected_supply_id == self.item_id:
                        self.master.refresh_detailed_view()
                        print("Detailed view refreshed with new stock levels")
                    
                    # Also refresh the table view
                    if hasattr(self.master, 'refresh_table'):
                        self.master.refresh_table()
                        print("Table view refreshed")
                    
                    self.close_window()

            except Exception as e:
                print('Error with editing supply stocks', e)
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

        # Content frame 
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        # Title and subtitle container 
        title_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_container.pack(fill="x", padx=20, pady=(20, 30))

        # Title
        title_label = ctk.CTkLabel(
            title_container, 
            text="Quantity Used Logs", 
            font=("Merriweather bold", 22), 
            text_color="#1A374D"
        )
        title_label.pack(anchor="w")

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_container, 
            text="Every item usage will appear here", 
            font=("Merriweather", 14), 
            text_color="#666666"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Table frame
        self.table_frame = ctk.CTkFrame(self.content_frame, fg_color="#1A374D", border_width=2, border_color="black")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Tree container
        tree_container = ctk.CTkFrame(self.table_frame, fg_color="black")
        tree_container.pack(fill="both", expand=True, padx=1, pady=1)

        # Configure table style
        style = ttk.Style()
        style.configure("UsageLogs.Treeview", font=("Merriweather Sans", 12), rowheight=35)
        style.configure("UsageLogs.Treeview.Heading", font=("Merriweather Sans bold", 13))
        style.map("UsageLogs.Treeview", background=[("selected", "#68EDC6")])        # Table columns
        columns = ("patient_id", "patient_details", "item_used", "timestamp")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15, style="UsageLogs.Treeview")
        self.tree.pack(side="left", fill="both", expand=True)

        # Table headers
        headers = [
            ("Patient ID", 150),
            ("Patient Details", 300),
            ("Item Used", 250),
            ("Timestamp", 200),
        ]
        
        for (text, width), col in zip(headers, columns):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(tree_container, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Add some sample data 
        self.add_sample_data()

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

    def add_sample_data(self):
        """Add sample data to demonstrate the table structure"""
        sample_data = [
            ("P001", "John Doe - Age 45", "Dialysis Filter", "2024-12-15 10:30:25"),
            ("P002", "Jane Smith - Age 52", "Saline Solution", "2024-12-15 11:15:42"),
            ("P003", "Mike Johnson - Age 38", "Disposable Tubing", "2024-12-15 14:22:18"),
            ("P001", "John Doe - Age 45", "Medical Gauze", "2024-12-15 15:45:33"),
            ("P004", "Sarah Wilson - Age 61", "Antiseptic Wipes", "2024-12-15 16:10:27"),
        ]
        
        for row in sample_data:
            self.tree.insert("", "end", values=row)

class RestockLogWindow(SupplyBaseWindow):
    def __init__(self, parent, item_id=None):
        super().__init__(parent, "Restock Log")
        
        # Store the item_id
        self.item_id = item_id
        print("Restock Log - item_id:", self.item_id)