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

def get_password_from_db(username):
  try:
    connect, cursor = db_connection()
    query = "SELECT password, role FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None
  except Exception as e:
    print("Error getting password ", e)
  finally:
    cursor.close()
    connect.close()

def get_answer_from_db(username):
  try:
    connect, cursor = db_connection()
    query = "SELECT secret_answer FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None
  except Exception as e:
    print("Error getting secret_answer ", e)
  finally:
    cursor.close()
    connect.close()

def get_username_from_db(username):
  try:
    connect, cursor = db_connection()
    query = "SELECT username FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None
  except Exception as e:
    print("Error getting username ", e)
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

def get_secret_question (username):
  try:
    connect, cursor = db_connection()
    query = "SELECT secret_question FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None
  except Exception as e:
      print("Error getting secret_question ", e)
  finally:
      cursor.close()
      connect.close()

def get_role (username):
  try: 
    connect, cursor = db_connection()
    query = "SELECT role FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None
  except Exception as e:
      print("Error getting role ", e)
  finally:
      cursor.close()
      connect.close()

def get_usernames(username):
  try:
    connect, cursor = db_connection()
    query = "SELECT COUNT(*) FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()[0]

    if result > 0:
       return "Username already taken"
    else:
       return None

  except Exception as e:
    print("Error fetching username ", e)
  finally:
     connect.close()
     cursor.close()

def create_patient_info(last_name, first_name, middle_name, status, access_type, birthdate,
                              age, gender, height, civil_status, religion, address):
  try:
   connect, cursor = db_connection()
   query = """
          INSERT INTO patient_info(last_name, first_name, middle_name, status, access_type, birthdate,
                              age, gender, height, civil_status, religion, address)
          VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
   """
   values = (last_name, first_name, middle_name, status, access_type, birthdate,
                              age, gender, height, civil_status, religion, address)
   cursor.execute(query, values)
   connect.commit()
   return " "
  except Exception as e:
    print("Patient info creation error: ", e)
  finally:
    connect.close()
    cursor.close()

def create_contact_person(last_name, first_name, middle_name, contact_number, relationship, address):
  try:
    connect, cursor = db_connection()
    query = """
            INSERT INTO patient_contact(last_name, first_name, middle_name, contact_number, relationship, address)
            VALUES(%s, %s, %s, %s, %s, %s)
    """ 
    values = (last_name, first_name, middle_name, contact_number, relationship, address)
    cursor.execute(query, values)
    connect.commit()
    return " "
  except Exception as e:
    print("Contact person information creation error: ", e)
  finally:
    connect.close()
    cursor.close()

def create_relative_info(last_name, first_name, middle_name, contact_number, address):
  try:
    connect, cursor = db_connection()

    query = """
            INSERT INTO patient_relative(last_name, first_name, middle_name, contact_number, address)
            VALUES (%s, %s, %s, %s, %s)
    """
    values = last_name, first_name, middle_name, contact_number, address
    cursor.execute(query, values)
    connect.commit()
    return " "

  except Exception as e:
    print("Error creating relative info: ", e)
  
  finally:
    cursor.close()
    connect.close()

def create_patient_history(family_history, medical_history, present_illness_history, past_illness_history, first_diagnosis, 
                           first_dialysis, mode, access_type, first_hemodialysis, clinical_impression):
  try:
    connect, cursor = db_connection()
    query = """"
            INSERT INTO patient_history(family_history, medical_history, present_illness_history, past_illness_history, first_diagnosis, 
                            first_dialysis, mode, access_type, first_hemodialysis, clinical_impression)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s)
    """
    values = (family_history, medical_history, present_illness_history, past_illness_history, first_diagnosis, 
                            first_dialysis, mode, access_type, first_hemodialysis, clinical_impression)
    cursor.execute(query, values)
    connect.commit()
  except Exception as e:
    print("Patient history creation error: ", e)
  finally:
    connect.close()
    cursor.close()

def create_philheath_info(philhealth_number, membership_type, is_pwd, is_senior, pwd_id, senior_id):
  try: 
    connect, cursor = db_connection()

    query = """
          INSERT INTO patient_benefits(philhealth_number, membership_type, is_pwd, is_senior, pwd_id, senior_id)
          VALUES(%s, %s, %s, %s, %s, %s)
    """    
    values =(philhealth_number, membership_type, is_pwd, is_senior, pwd_id, senior_id)

    cursor.execute(query, values)
    connect.commit()

    print("Successful creating philheath info")

  except Exception as e:
    print("Philhealth info creation error: ", e)
  
  finally:
    cursor.close()
    connect.close()

def create_medication_taken(drugs_taken):
  try:
    connect, cursor = db_connection()
    query = "INSERT INTO medications VALUES (%s)"
    values = (drugs_taken,)
    cursor.execute(query, values)
    connect.commit()
  except Exception as e:
    print("Medication creation error: ", e)
  finally:
    connect.close()
    cursor.close()

def add_patient(patient_name, date_registered, medical_condition, age, gender):
  pass

# def fetch_patients():
#   try:
#     patients = []
#     connect, cursor = db_connection()
    
#     cursor.execute("""
#           SELECT * FROM patient_list
#     """)

#     for i in cursor:
#       patients.append(i)

#     print(patients)
  

#   except Exception as e:
#     print("error fetching patients: ", e)

# fetch_patients()

create_philheath_info(philhealth_number = '12312312', membership_type = 'single', is_pwd = 1, is_senior = 1, pwd_id = '12312312', senior_id = '321321')