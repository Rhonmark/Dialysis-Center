from .connector import db_connection as db
import math
#running as relative import since no ui yet
# cursor.lastrowid to retrieve recent patient

def db_connection():
    connect = db()
    cursor = connect.cursor()

    return connect, cursor

def register_to_db(full_name, role, username, password, secret_question, secret_answer):
  try:
    connect, cursor = db_connection()
    # connect.start_transaction()
    query = """
        INSERT INTO users (full_name, role, username, password, secret_question, secret_answer)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (full_name, role, username, password, secret_question, secret_answer)
    cursor.execute(query, values)
    connect.commit()
    return "Registration Successful"
  except Exception as e:
    #   connect.rollback()
      print("Error with register user...", e)
  finally:
      cursor.close()
      connect.close()

def get_login_credentials(username, target_data):
    try:
      connect, cursor = db_connection()
      query = f"SELECT {target_data} FROM users WHERE username = %s"
      cursor.execute(query, [username])
      result = cursor.fetchone()
      return result[0] if result else None
    except Exception as e:
      print(f"Error getting {target_data} ", e)
    finally:
      cursor.close()
      connect.close()

def set_new_password(password, username):
  try:
    connect, cursor = db_connection()
    query = "UPDATE users SET password = %s WHERE username = %s"
    values = (password, username)
    cursor.execute(query, values)
    connect.commit()
    print("Password updated successfully!")
  except Exception as e:
    print("Error setting new password ", e)
  finally:
    cursor.close()
    connect.close()

def get_existing_credentials(username, target_field, table_name):
  try:
    connect, cursor = db_connection()

    query = f"SELECT COUNT(*) FROM {table_name} WHERE {target_field} = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()[0]

    if result > 0:
       return "Field already exist"
    else:
       return None

  except Exception as e:
    print(f"Error fetching unique count (get_existing_credentials function) ", e)
  finally:
     cursor.close()
     connect.close()

def submit_form_creation(column, row, table_name):
        try:
            connect = db()
            cursor = connect.cursor()

            # column_names = ', '.join(column)
            values_placeholder = ', '.join(['%s'] * len(row))

            query = f"""
                INSERT INTO {table_name}({column})
                VALUES({values_placeholder})
            """
            cursor.execute(query, tuple(row))
            unique_id = cursor.lastrowid  
            connect.commit()  
            
            return unique_id 
        
        except Exception as e:
            print("Patient info creation error: ", e)
            return False
        
        finally:
            cursor.close()
            connect.close()

def submit_form_subcreation(column, row, patient_id, table_name):
    try:
        connect = db()
        cursor = connect.cursor()

        # column_names = ', '.join(column)
        values_placeholder = ', '.join(['%s'] * (len(row) + 1))

        query = f"""  
            INSERT INTO {table_name}(patient_id, {column})
            VALUES({values_placeholder})
        """

        values = (patient_id, *tuple(row))

        cursor.execute(query, values)
        connect.commit()

        return True

    except Exception as e:
        print("Error submitting step 2-8 of the form: ", e)
        return False
    
    finally:
        cursor.close()
        connect.close()

def submit_form_extra(patient_id, medication_entries):
    try:
        connect = db()
        cursor = connect.cursor()

        # Check if patient exists
        cursor.execute("SELECT 1 FROM patient_info WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            print(f"Error: patient_id {patient_id} does not exist!")
            return False

        for medication in medication_entries:
            # Insert or select medicine
            cursor.execute("""
                INSERT INTO medicines (medication_name) 
                VALUES (%s)
                ON DUPLICATE KEY UPDATE medication_id = LAST_INSERT_ID(medication_id)
            """, (medication,))
            
            medication_id = cursor.lastrowid or \
                          cursor.execute("SELECT medication_id FROM medicines WHERE medication_name = %s", (medication,)).fetchone()[0]

            # Ensure link exists
            cursor.execute("""
                REPLACE INTO patient_medications (patient_id, medication_id) 
                VALUES (%s, %s)
            """, (patient_id, medication_id))

        connect.commit()
        return True

    except Exception as e:
        print("Error in submit_form_extra():", e)
        connect.rollback()
        return False

    finally:
        cursor.close()
        connect.close()

def retrieve_form_data(patient_id, target_column, column, table_name):
  try:
    data_retrieval = []
    connect, cursor = db_connection()

    # column_data = ', '.join(column)

    cursor.execute(f"""
        SELECT {column} FROM {table_name}
        WHERE {target_column} = {patient_id}
    """)
    
    result = cursor.fetchone()

    for i in result:
       data_retrieval.append(i)

    return data_retrieval

  except Exception as e:
     print("Error retrieving form data: ", e)
     return False
  
  finally:
     cursor.close()
     connect.close()

def wag_galawin():

  #ONLY WORKS WHEN INSERTING JUST HAPPENED, IF NOT DONT USE

  # cursor.execute("SELECT patient_name, age, gender FROM patient_list WHERE patient_id = %s", (patient_id, ))
  # result = cursor.fetchone()

  # cursor.execute("SELECT patient_name, age, gender FROM patient_list WHERE patient_id = LAST_ROW_ID(patient_id)")
  # result = cursor.fetchone()

  pass

def update_changes(unique_id, column, row, table_name):
  try:
    connect, cursor = db_connection()

    # merged = [f"{col} = {val}" for col, val in zip(column, row)]
    # data = ', '.join(merged)
    data = ', '.join([f"{col} = %s" for col in column])

    allowed_table = {"supply", "item_stock_levels"}
    allowed_column = {"item_name", "category", "restock_quantity", "restock_date"}

    if table_name not in allowed_table:
       raise ValueError("Invalid Table Name")
    if not set(column).issubset(allowed_column):
       raise ValueError("Invalid Column Name")

    query = f"""
        UPDATE {table_name}
        SET {data} 
        WHERE {unique_id} = %s
    """

    cursor.execute(query, row + (unique_id))

    connect.commit()
    return True

  except Exception as e:
     print("Error updating changes: ", e)
     return False

  finally:
     cursor.close()
     connect.close()

def supply_creation_id(column, row, table_name):
        
        try:
            connect = db()
            cursor = connect.cursor()

            # column_names = ', '.join(column)
            values_placeholder = ', '.join(['%s'] * len(row))

            if table_name == 'supply':
              query = f"""
                  INSERT INTO {table_name}({column}, date_registered)
                  VALUES({values_placeholder}, CURDATE())
              """

            elif table_name == 'item_usage':
              query = f"""
                  INSERT INTO {table_name}({column}, usage_date, usage_time, usage_timestamp)
                  VALUES({values_placeholder}, CURDATE(), CURTIME(), NOW())
              """

            cursor.execute(query, tuple(row))
            unique_id = cursor.lastrowid  
            connect.commit()  
            
            return unique_id 
        
        except Exception as e:
            print("Patient info creation error: ", e)
            return False
        
        finally:
            cursor.close()
            connect.close()

def update_patient_info(patient_id, data_dict):
    """Update patient information"""
    try:
        connect = db()
        cursor = connect.cursor()
        
        set_clause = ", ".join([f"{key} = %s" for key in data_dict.keys()])
        values = list(data_dict.values()) + [patient_id]
        
        query = f"UPDATE patient_info SET {set_clause} WHERE patient_id = %s"
        cursor.execute(query, values)
        
        connect.commit()
        cursor.close()
        connect.close()
        return True
        
    except Exception as e:
        print(f"Error updating patient info: {e}")
        return False

def update_patient_contact(patient_id, data_dict):
    """Update patient contact information"""
    try:
        connect = db()
        cursor = connect.cursor()
        
        set_clause = ", ".join([f"{key} = %s" for key in data_dict.keys()])
        values = list(data_dict.values()) + [patient_id]
        
        query = f"UPDATE patient_contact SET {set_clause} WHERE patient_id = %s"
        cursor.execute(query, values)
        
        connect.commit()
        cursor.close()
        connect.close()
        return True
        
    except Exception as e:
        print(f"Error updating patient contact: {e}")
        return False

def update_patient_relative(patient_id, data_dict):
    """Update patient relative information"""
    try:
        connect = db()
        cursor = connect.cursor()
        
        set_clause = ", ".join([f"{key} = %s" for key in data_dict.keys()])
        values = list(data_dict.values()) + [patient_id]
        
        query = f"UPDATE patient_relative SET {set_clause} WHERE patient_id = %s"
        cursor.execute(query, values)
        
        connect.commit()
        cursor.close()
        connect.close()
        return True
        
    except Exception as e:
        print(f"Error updating patient relative: {e}")
        return False

def update_patient_benefits(patient_id, data_dict):
    """Update patient benefits information"""
    try:
        connect = db()
        cursor = connect.cursor()
        
        set_clause = ", ".join([f"{key} = %s" for key in data_dict.keys()])
        values = list(data_dict.values()) + [patient_id]
        
        query = f"UPDATE patient_benefits SET {set_clause} WHERE patient_id = %s"
        cursor.execute(query, values)
        
        connect.commit()
        cursor.close()
        connect.close()
        return True
        
    except Exception as e:
        print(f"Error updating patient benefits: {e}")
        return False

def update_patient_history(patient_id, data_dict):
    """Update patient history information"""
    try:
        connect = db()
        cursor = connect.cursor()
        
        set_clause = ", ".join([f"{key} = %s" for key in data_dict.keys()])
        values = list(data_dict.values()) + [patient_id]
        
        query = f"UPDATE patient_history SET {set_clause} WHERE patient_id = %s"
        cursor.execute(query, values)
        
        connect.commit()
        cursor.close()
        connect.close()
        return True
        
    except Exception as e:
        print(f"Error updating patient history: {e}")
        return False

def update_patient_medications(patient_id, medication_list):
    """Update patient medications - delete old ones and insert new ones"""
    try:
        connect = db()
        cursor = connect.cursor()
        
        cursor.execute("DELETE FROM patient_medications WHERE patient_id = %s", (patient_id,))
        
        # Insert new medications 
        for medication_name in medication_list:
            if medication_name and medication_name.strip() and medication_name != "Type Here":
                # Check if medication exists in medicines table
                cursor.execute("SELECT medication_id FROM medicines WHERE medication_name = %s", (medication_name.strip(),))
                medication_result = cursor.fetchone()
                
                if medication_result:
                    medication_id = medication_result[0]
                else:
                    # Insert new medication
                    cursor.execute("INSERT INTO medicines (medication_name) VALUES (%s)", (medication_name.strip(),))
                    medication_id = cursor.lastrowid
                
                # Insert patient-medication relationship
                cursor.execute("INSERT INTO patient_medications (patient_id, medication_id) VALUES (%s, %s)", 
                             (patient_id, medication_id))
        
        connect.commit()
        cursor.close()
        connect.close()
        return True
        
    except Exception as e:
        print(f"Error updating patient medications: {e}")
        return False

def update_patient_list(patient_id, data_dict):
    
    """Update patient list (main table)"""
    try:
        connect = db()
        cursor = connect.cursor()
        
        set_clause = ", ".join([f"{key} = %s" for key in data_dict.keys()])
        values = list(data_dict.values()) + [patient_id]
        
        query = f"UPDATE patient_list SET {set_clause} WHERE patient_id = %s"
        cursor.execute(query, values)
        
        connect.commit()
        cursor.close()
        connect.close()
        return True
        
    except Exception as e:
        print(f"Error updating patient list: {e}")
        return False
    
def wawenta():
    ###############################EDIT STOCK SUPPLY#########################3
    ###############################EDIT STOCK SUPPLY#########################3
    ###############################EDIT STOCK SUPPLY#########################3

    connect = db()
    cursor = connect.cursor()

    user_input = [
        {"item_name": "Ivremectin", "quantity": 2, "expiry_date": "2025-08-01"},
        {"item_name": "Oppo", "quantity": 5, "expiry_date": "2025-08-01"},
        {"item_name": "Bioflu", "quantity": 3, "expiry_date": "2025-08-01"},  
    ]

    stock = ' '.join(f"WHEN %s THEN current_stock + %s" for _ in user_input)
    expiry = ' '.join(f"WHEN %s THEN %s" for _ in user_input)
    names = ', '.join(['%s'] * len(user_input))  

    store = []
    for item in user_input:
        store.extend([item['item_name'], item['quantity']]) 
        print('iq:', store)
    for item in user_input:
        store.extend([item['item_name'], item['expiry_date']]) 
        print('ie', store)

    store.extend([item['item_name'] for item in user_input])

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

    print(store)


    cursor.execute(query, store)
    connect.commit()

    ###############################EDIT USAGE PATIENT#########################3
    ###############################EDIT USAGE PATIENT#########################3
    ###############################EDIT USAGE PATIENT#########################3

    connect = db()
    cursor = connect.cursor()

    user_input = [
        {"item_name": "Ivremectin", "quantity": 2},
        {"item_name": "Oppo", "quantity": 5},
        {"item_name": "Bioflu", "quantity": 3},  
    ]

    stock = ' '.join(f"WHEN %s THEN current_stock - %s" for _ in user_input)
    names = ', '.join(['%s'] * len(user_input))  

    store = []
    for item in user_input:
        store.extend([item['item_name'], item['quantity']]) 

    store.extend([item['item_name'] for item in user_input])

    query = f"""
        UPDATE supply
        SET 
            current_stock = CASE item_name
                {stock}
            END
        WHERE item_name IN ({names});
    """

    print(store)


    cursor.execute(query, store)
    connect.commit()


    connect = db()
    cursor = connect.cursor()

    cursor.execute("SELECT item_name FROM supply")

    result = cursor.fetchall()

    usable_result = [i[0] for i in result]
    string_dropdown = ', '.join(usable_result)

    print(string_dropdown)

    connect = db()
    cursor = connect.cursor()

    cursor.execute("SELECT patient_name FROM patient_list WHERE patient_id = %s") #pasa mo nalang yung id after makapamili ni user

    result = cursor.fetchone()[0]

    print(result)

    ########################################@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

########################PATIENT STATUS TABLE##############################
# try:
#     connect = db()
#     cursor = connect.cursor()

#     cursor.execute("""
#         SELECT pl.patient_name, pi.status FROM patient_list pl
#         JOIN patient_info pi ON pl.patient_id = pi.patient_id
#     """)

#     result = cursor.fetchall()
    
#     name_store = []
#     status_store = []

#     for name, status in result:
#         name_store.append(name)
#         status_store.append(status)

#     print(name_store)
#     print(status_store)

# except Exception as e:

#     print('Error fetching active and inactive patient', e)

# finally: 
#     cursor.close()
#     connect.close()


########################REORDER TABLE##############################
# try:
#     connect = db()
#     cursor = connect.cursor()

#     cursor.execute("""
#         SELECT item_name, reorder_quantity, stock_level_status, supplier_name FROM supply
#         WHERE stock_level_status = 'Critical Stock Level' OR stock_level_status = 'Low Stock Level'
#         ORDER BY stock_level_status, supplier_name
#     """)

#     result = cursor.fetchall()
    
#     name_store = []
#     reorderqty_store = []
#     status_store = []
#     supplier_store = []

#     for name, reorderqty, status, supplier in result:
#         name_store.append(name)
#         reorderqty_store.append(reorderqty)
#         status_store.append(status)
#         supplier_store.append(supplier)

#     print(name_store)
#     print(reorderqty_store)
#     print(status_store)
#     print(supplier_store)

# except Exception as e:

#     print('Error fetching reorder quantity', e)

# finally: 
#     cursor.close()
#     connect.close()