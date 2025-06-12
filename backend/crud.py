from .connector import db_connection as db
import math
#running as relative import since no ui yet
# cursor.lastrowid to retrieve recent patient

def db_connection():
    connect = db()
    cursor = connect.cursor()

    cursor.execute("SELECT patient_name, age, gender FROM patient_list ORDER BY patient_id DESC LIMIT 1")
    result = cursor.fetchone()

    print(result)

    return connect, cursor

def register_to_db(role, username, password, secret_question, secret_answer):
  try:
    connect, cursor = db_connection()
    # connect.start_transaction()
    query = """
        INSERT INTO users (role, username, password, secret_question, secret_answer)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (role, username, password, secret_question, secret_answer)
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
                  INSERT INTO {table_name}({column}, usage_date, usage_time)
                  VALUES({values_placeholder}, CURDATE(), CURTIME())
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

