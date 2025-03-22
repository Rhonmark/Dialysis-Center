from.connector import db_connection as db
#running as relative import since no ui yet

def db_connection():
    connect = db()
    cursor = connect.cursor()
    return connect, cursor

def register_to_db(role, username, password, secret_question, secret_answer):
  try:
    connect, cursor = db_connection()
    connect.start_transaction()
    query = """
        INSERT INTO users (role, username, password, secret_question, secret_answer)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (role, username, password, secret_question, secret_answer)
    cursor.execute(query, values)
    connect.commit()
    return "Registration Successful"
  except Exception as e:
      connect.rollback()
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

def get_existing_credentials(username, target_data):
  try:
    connect, cursor = db_connection()
    query = f"SELECT {target_data} FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()[0]

    if result > 0:
       return "Username already taken"
    else:
       return None

  except Exception as e:
    print(f"Error fetching {target_data} ", e)
  finally:
     cursor.close()
     connect.close()

def submit_form_creation(column, row, table_name):
        try:
            connect = db()
            cursor = connect.cursor()

            values_placeholder = ', '.join(['%s'] * len(row))

            query = f"""
                INSERT INTO {table_name}({column})
                VALUES({values_placeholder})
            """
            cursor.execute(query, tuple(row))
            pk_patient_id = cursor.lastrowid  
            connect.commit()  
            
            return pk_patient_id 
        
        except Exception as e:
            print("Patient info creation error: ", e)
            return False
        
        finally:
            cursor.close()
            connect.close()

def submit_form_subcreation(column, row, pk_patient_id, table_name):
    try:
        connect = db()
        cursor = connect.cursor()

        values_placeholder = ', '.join(['%s'] * (len(row) + 1))

        query = f"""  
            INSERT INTO {table_name}(patient_id, {column})
            VALUES({values_placeholder})
        """

        values = (pk_patient_id, *tuple(row))

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

            for medication in medication_entries:

              cursor.execute("INSERT IGNORE INTO medicines(medication_name) VALUES (%s)", (medication, ))

              cursor.execute("SELECT medication_id FROM medicines WHERE medication_name = %s", (medication, ))
              medication_id = cursor.fetchone()[0]

              cursor.execute("INSERT IGNORE INTO patient_medications VALUES (%s, %s)", (patient_id, medication_id))

            connect.commit()

            return True
        
        except Exception as e:
            print("Patient info creation error: ", e)
            return False
        
        finally:
            cursor.close()
            connect.close()


