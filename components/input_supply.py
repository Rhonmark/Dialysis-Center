import customtkinter as ctk
from tkinter import Toplevel
from tkcalendar import Calendar
from PIL import Image
from backend.crud import supply_creation_id, get_existing_credentials
from backend.connector import db_connection as db
import math

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

        # Restock Date
        ctk.CTkLabel(self, text="Restock Date", font=label_font, fg_color="white", text_color="black").place(x=1020, y=150)
        self.entry_restock_date = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0,
                                 bg_color="white")
        self.entry_restock_date.place(x=1020, y=200)
        
        if not self.is_editing:
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
                print('error retrieving data', e)

        def update_supply_data(cursor, item_id, supply_information):
            try:
                # Extract values from dictionary
                item_name = supply_information['item_name']
                category = supply_information['category']
                restock_quantity = supply_information['restock_quantity']
                restock_date = supply_information['restock_date']
                avg_weekly_usage = supply_information['average_weekly_usage']
                delivery_time = supply_information['delivery_time_days']
                
                if restock_quantity > 0:
                    cursor.execute("""
                        UPDATE supply 
                        SET item_name = %s, category = %s, restock_quantity = %s, 
                        restock_date = %s, average_weekly_usage = %s, delivery_time_days = %s
                        WHERE item_id = %s 
                    """, (item_name, category, restock_quantity, restock_date, avg_weekly_usage, delivery_time, item_id))
                    print(f"Updated supply item with ID: {item_id} and added {restock_quantity} to stock")
                else:
                    cursor.execute("""
                        UPDATE supply 
                        SET item_name = %s, category = %s, 
                        restock_date = %s, average_weekly_usage = %s, delivery_time_days = %s
                        WHERE item_id = %s 
                    """, (item_name, category, restock_date, avg_weekly_usage, delivery_time, item_id))
                    print(f"Updated supply item with ID: {item_id} without changing stock")
                
                return True
                
            except KeyError as e:
                print(f"Missing required key in supply_information: {e}")
                return False
            except Exception as e:
                print(f"Error updating supply item: {e}")
                return False
        
        def set_supply_data(cursor, column, value, item_id):
            try:
                cursor.execute(f"""
                    UPDATE supply
                    SET {column} = %s
                    WHERE item_id = %s
                """, (value, item_id))
            except Exception as e:
                print(f'Error with updating {column}. Error: {e}')

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
            good_level = current_stock_val * 0.7

            if current_stock_val <= critical_stock_level:
                status = 'Critical Stock Level'

            elif current_stock_val <= low_stock_level:
                status = 'Low Stock Level'

            elif current_stock_val <= good_level:
                status = 'Good Stock Level'
            
            else:
                status = 'Excellent Stock Level'         

            return status       

        def on_save_click():
            item_name = self.entry_itemname.get().strip()
            category = self.entry_category.get().strip()
            restock_date = self.entry_restock_date.get().strip()
            avg_weekly_usage_str = self.entry_averageuse.get().strip()      
            delivery_time_str = self.entry_delivery_date.get().strip()

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
            if not restock_date or restock_date == "Select date":
                restock_date = None

            supply_information = {
                'item_name': item_name.capitalize(),
                'category': category,
                'current_stock': current_stock,
                'restock_quantity': restock_quantity,
                'restock_date': restock_date,
                'average_weekly_usage': avg_weekly_usage,
                'delivery_time_days': delivery_time
            }

            supply_column = ', '.join(supply_information.keys())
            supply_row = [f"{entries}" for entries in supply_information.values()]

            try:
                connect = db()
                cursor = connect.cursor()

                if self.is_editing:

                    success = update_supply_data(cursor, self.edit_data['item_id'], supply_information)

                    if not success: 
                        CTkMessageBox.show_success("Failed", "Failed to update supply item!", parent=self)

                    restock_quantity_result = retrieve_supply_data(cursor, 'restock_quantity', self.edit_data['item_id'])
                    current_stock_result = retrieve_supply_data(cursor, 'current_stock', self.edit_data['item_id'])
                    avg_weekly_usage_result = retrieve_supply_data(cursor, 'average_weekly_usage', self.edit_data['item_id'])
                    delivery_time_result = retrieve_supply_data(cursor, 'delivery_time_days', self.edit_data['item_id'])

                    #check if there's new input
                    if current_stock_result == supply_information['restock_quantity']:
                        current_stock_val = supply_information['restock_quantity'] 
                    else:
                        current_stock_val = current_stock_result + restock_quantity_result 

                    #cursor, column, value, item_id
                    set_supply_data(cursor, 'current_stock', current_stock_val, self.edit_data['item_id'])
                    set_supply_data(cursor, 'max_supply', current_stock_val, self.edit_data['item_id'])
                    current_stock_val = retrieve_supply_data(cursor, 'current_stock', self.edit_data['item_id'])

                    status = set_stock_levels(avg_weekly_usage_result, delivery_time_result, current_stock_val)
                    set_supply_data(cursor, 'stock_level_status', status, self.edit_data['item_id'])

                    connect.commit()

                    CTkMessageBox.show_success("Success", "Supply information updated successfully!", parent=self)

                else:
                    #dictionary call, remains unchanged
                    supply_information

                    check_uniqueness = get_existing_credentials(item_name, 'item_name', table_name='supply')

                    if check_uniqueness:
                        CTkMessageBox.show_error("Error", 'Item already exists', parent=self)
                        return

                    item_id = supply_creation_id(supply_column, supply_row, table_name='supply')

                    if item_id: 
                        item_id_store.append(item_id)
                        print('Item ID: ', item_id)
                        CTkMessageBox.show_success("Success", "Supply information saved successfully!", parent=self)
                    else:
                        print('Item ID creation error')
                        return
                    
                    connect.commit()
                    
                    avg_weekly_usage_result = retrieve_supply_data(cursor, 'average_weekly_usage', item_id)
                    delivery_time_result = retrieve_supply_data(cursor, 'delivery_time_days', item_id)
                    current_stock_result = retrieve_supply_data(cursor, 'current_stock', item_id)
                    
                    status = set_stock_levels(avg_weekly_usage_result, delivery_time_result, current_stock_result)
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
        
        # Clear and set restock date
        self.entry_restock_date.delete(0, "end")
        restock_date = self.edit_data.get('restock_date')
        if restock_date:
            self.entry_restock_date.insert(0, str(restock_date))
            self.entry_restock_date.configure(text_color="black")
        
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
    restock_date = supply_data[4] if len(supply_data) > 4 else "N/A"
    date_registered = supply_data[5] if len(supply_data) > 5 else "N/A"
    average_weekly_usage = supply_data[8] if len(supply_data) > 6 else "N/A"
    delivery_time_days = supply_data [10] if len(supply_data) > 7 else "N/A"

    # Display current stock as remaining stock
    self.currentstock_Output.configure(text=str(current_stock))
    self.LastRestock_Date_Output.configure(text=restock_date)
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

        print("item_id:", self.item_id)

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

        # Quantity Used Input
        ctk.CTkLabel(self, text="Patient ID", font=label_font, fg_color="white", text_color="black").place(x=120, y=150)
        self.entry_patient_id = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        self.entry_patient_id.place(x=120, y=200)
        create_underline(120, 230, 180)
        add_placeholder(self.entry_patient_id, "Type here")

        # Patient ID Input
        ctk.CTkLabel(self, text="Quantity Used", font=label_font, fg_color="white", text_color="black").place(x=420, y=150)
        self.entry_quantity_used = ctk.CTkEntry(self, width=180, height=30, font=entry_font, text_color="black", fg_color="white", border_width=0, bg_color="white")
        self.entry_quantity_used.place(x=420, y=200)
        create_underline(420, 230, 180)
        add_placeholder(self.entry_quantity_used, "Type here")

        # Submit function
        def on_submit_click():
            quantity_used = self.entry_quantity_used.get().strip()
            patient_id = self.entry_patient_id.get().strip()
            
            usage_information = {
                'item_id': self.item_id,
                'patient_id': patient_id,
                'quantity_used': quantity_used
            }

            usage_column = ', '.join(usage_information.keys())
            usage_rows = [f'{entries}' for entries in usage_information.values()]

            usage_id = supply_creation_id(usage_column, usage_rows, table_name='item_usage')

            if usage_id:
                print(f'usage id creation successful: {usage_id}')


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