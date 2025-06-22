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
    

################################EDIT STOCK SUPPLY#########################3
################################EDIT STOCK SUPPLY#########################3
################################EDIT STOCK SUPPLY#########################3

# connect = db()
# cursor = connect.cursor()

# user_input = [
#     {"item_name": "Ivremectin", "quantity": 2, "expiry_date": "2025-08-01"},
#     {"item_name": "Oppo", "quantity": 5, "expiry_date": "2025-08-01"},
#     {"item_name": "Bioflu", "quantity": 3, "expiry_date": "2025-08-01"},  
# ]

# stock = ' '.join(f"WHEN %s THEN current_stock + %s" for _ in user_input)
# expiry = ' '.join(f"WHEN %s THEN %s" for _ in user_input)
# names = ', '.join(['%s'] * len(user_input))  

# store = []
# for item in user_input:
#     store.extend([item['item_name'], item['quantity']]) 
#     print('iq:', store)
# for item in user_input:
#     store.extend([item['item_name'], item['expiry_date']]) 
#     print('ie', store)

# store.extend([item['item_name'] for item in user_input])

# query = f"""
#     UPDATE supply
#     SET 
#         current_stock = CASE item_name
#             {stock}
#         END,
#         new_expiry_date = CASE item_name
#             {expiry}
#         END
#     WHERE item_name IN ({names});
# """

# print(store)


# cursor.execute(query, store)
# connect.commit()

################################EDIT USAGE PATIENT#########################3
################################EDIT USAGE PATIENT#########################3
################################EDIT USAGE PATIENT#########################3

# connect = db()
# cursor = connect.cursor()

# user_input = [
#     {"item_name": "Ivremectin", "quantity": 2},
#     {"item_name": "Oppo", "quantity": 5},
#     {"item_name": "Bioflu", "quantity": 3},  
# ]

# stock = ' '.join(f"WHEN %s THEN current_stock - %s" for _ in user_input)
# names = ', '.join(['%s'] * len(user_input))  

# store = []
# for item in user_input:
#     store.extend([item['item_name'], item['quantity']]) 

# store.extend([item['item_name'] for item in user_input])

# query = f"""
#     UPDATE supply
#     SET 
#         current_stock = CASE item_name
#             {stock}
#         END
#     WHERE item_name IN ({names});
# """

# print(store)


# cursor.execute(query, store)
# connect.commit()


# connect = db()
# cursor = connect.cursor()

# cursor.execute("SELECT item_name FROM supply")

# result = cursor.fetchall()

# usable_result = [i[0] for i in result]
# string_dropdown = ', '.join(usable_result)

# print(string_dropdown)

# connect = db()
# cursor = connect.cursor()

#cursor.execute("SELECT patient_name FROM patient_list WHERE patient_id = %s") #pasa mo nalang yung id after makapamili ni user

#result = cursor.fetchone()[0]

#print(result)

#########################################@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# def data_count(column, value, table_name, period=None, date_column=None, join_table=None, join_condition=None):
#     from datetime import datetime, timedelta
#     import calendar
#     try:
#         connect = db()
#         cursor = connect.cursor()
        
#         if period and date_column:
#             today = datetime.now().date()
            
#             if period.lower() == 'weekly':
#                 # Get current week (Monday to Sunday)
#                 days_since_monday = today.weekday()
#                 start_of_week = today - timedelta(days=days_since_monday)
#                 end_of_week = start_of_week + timedelta(days=6)
                
#                 if join_table and join_condition:
#                     cursor.execute(f"""
#                         SELECT COUNT(*) FROM {table_name}
#                         JOIN {join_table} ON {join_condition}
#                         WHERE {table_name}.{column} = '{value}' 
#                         AND {join_table}.{date_column} >= '{start_of_week}' 
#                         AND {join_table}.{date_column} <= '{end_of_week}'
#                     """)
#                 else:
#                     cursor.execute(f"""
#                         SELECT COUNT(*) FROM {table_name}
#                         WHERE {column} = '{value}' 
#                         AND {date_column} >= '{start_of_week}' 
#                         AND {date_column} <= '{end_of_week}'
#                     """)
                
#             elif period.lower() == 'monthly':
#                 # Get current month
#                 start_of_month = today.replace(day=1)
#                 last_day = calendar.monthrange(today.year, today.month)[1]
#                 end_of_month = today.replace(day=last_day)
                
#                 if join_table and join_condition:
#                     cursor.execute(f"""
#                         SELECT COUNT(*) FROM {table_name}
#                         JOIN {join_table} ON {join_condition}
#                         WHERE {table_name}.{column} = '{value}' 
#                         AND {join_table}.{date_column} >= '{start_of_month}' 
#                         AND {join_table}.{date_column} <= '{end_of_month}'
#                     """)
#                 else:
#                     cursor.execute(f"""
#                         SELECT COUNT(*) FROM {table_name}
#                         WHERE {column} = '{value}' 
#                         AND {date_column} >= '{start_of_month}' 
#                         AND {date_column} <= '{end_of_month}'
#                     """)
#         else:
#             # Original query without date filtering
#             cursor.execute(f"""
#                 SELECT COUNT(*) FROM {table_name}
#                 WHERE {column} = '{value}'
#             """)
        
#         count_result = cursor.fetchone()
#         count = count_result[0] if count_result else 0
    
#         if period and date_column:
#             if period.lower() == 'weekly':
#                 date_range = f"{start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}"
#             elif period.lower() == 'monthly':
#                 date_range = f"{start_of_month.strftime('%B %Y')}"
            
#             return {
#                 'count': count,
#                 'date_range': date_range,
#                 'period': period.lower()
#             }
#         else:
#             return count
        
#     except Exception as e:
#         print(f'Error finding column ({column}), value ({value}) in table: {table_name}', e)
#         return 0
#     finally:
#         cursor.close()
#         connect.close()

# # Usage examples with JOIN:

# # Regular counts (no date filtering) - still works the same
# active_patient = data_count('status', 'Active', table_name='patient_info')
# inactive_patient = data_count('status', 'Inactive', table_name='patient_info')

# # Weekly/Monthly counts with JOIN (assuming patient_info and patient_list share a common ID)
# weekly_active = data_count(
#     column='status', 
#     value='Active', 
#     table_name='patient_info',
#     period='weekly', 
#     date_column='date_registered',
#     join_table='patient_list',
#     join_condition='patient_info.patient_id = patient_list.patient_id'  # Adjust based on your actual column names
# )

# monthly_active = data_count(
#     column='status', 
#     value='Active', 
#     table_name='patient_info',
#     period='monthly', 
#     date_column='date_registered',
#     join_table='patient_list',
#     join_condition='patient_info.patient_id = patient_list.patient_id'  # Adjust based on your actual column names
# )

# print('active patients: ', active_patient)
# print('inactive patients: ', inactive_patient)

# print(monthly_active)
# print(weekly_active)

# weekly_act_keys = [f'{items}' for items in weekly_active.keys()]
# weekly_act_usable_keys = ', '.join(weekly_act_keys)


# weekly_act_values = [f'{items}' for items in weekly_active.values()]
# weekly_act_usable_values = ', '.join(weekly_act_values)

# for key, value in zip(weekly_act_keys, weekly_act_values):
#     print(key, value)

# def data_count_no_join(column, value, table_name, period=None, date_column=None):

#     from datetime import datetime, timedelta
#     import calendar

#     try:
#         connect = db()
#         cursor = connect.cursor()
        
#         if period and date_column:
#             today = datetime.now().date()
            
#             if period.lower() == 'weekly':
#                 days_since_monday = today.weekday()
#                 start_of_week = today - timedelta(days=days_since_monday)
#                 end_of_week = start_of_week + timedelta(days=6)
                
#                 cursor.execute(f"""
#                     SELECT COUNT(*) FROM {table_name}
#                     WHERE {column} = '{value}' 
#                     AND {date_column} >= '{start_of_week}' 
#                     AND {date_column} <= '{end_of_week}'
#                 """)
                
#             elif period.lower() == 'monthly':
#                 start_of_month = today.replace(day=1)
#                 last_day = calendar.monthrange(today.year, today.month)[1]
#                 end_of_month = today.replace(day=last_day)
                
#                 cursor.execute(f"""
#                     SELECT COUNT(*) FROM {table_name}
#                     WHERE {column} = '{value}' 
#                     AND {date_column} >= '{start_of_month}' 
#                     AND {date_column} <= '{end_of_month}'
#                 """)

#             else:
#                 cursor.execute(f"""
#                     SELECT COUNT(*) FROM {table_name}
#                     WHERE {column} = '{value}'
#                 """)
        
#         count_result = cursor.fetchone()
#         return count_result[0] if count_result else 0
        
#     except Exception as e:
#         print(f'Error finding column ({column}), value ({value}) in table: {table_name}', e)
#         return 0
#     finally:
#         cursor.close()
#         connect.close()

# lowstock_count = data_count_no_join('stock_level_status', 'Low Stock Level', 'supply', 'current', 'date_registered')
# criticalstock_count = data_count_no_join('stock_level_status', 'Critical Stock Level', 'supply', 'current', 'date_registered')

# print(lowstock_count)
# print(criticalstock_count)