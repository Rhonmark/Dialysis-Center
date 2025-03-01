from .connector import db_connection as db

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