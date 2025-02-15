from .connector import db_connection as db

def user_input_validation(username, password):
  if not username and not password:
    return("Both fields must be filled!")
  if not username:
    return("Username is missing!")
  if not password:
    return("Password is missing!")
  if len(username) < 8:
    return("Username must be at least 8 characters!")
  if len(password) < 6:
    return("Password must be at least 6 characters!")
  return None

def login_validation(username, password):
  validation_result = user_input_validation(username, password)
  if validation_result:
    return validation_result
  return None

def register_validation(username, password, secret_answer):
  validation_result = user_input_validation(username, password)
  if validation_result:
    return validation_result
  if not secret_answer:
    return("Secret Answer must be filled!")
  return None

def register_to_db(username, password, secret_answer):
  connect = db()
  cursor = connect.cursor()
  query = """
      INSERT INTO users (username, password, secret_answer)
      VALUES (%s, %s, %s)
  """
  values = (username, password, secret_answer)

  cursor.execute(query, values)
  connect.commit()

  print("User registered successfully!")

def get_password_from_db(username):
    connect = db()
    cursor = connect.cursor()
    query = "SELECT password FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()

    return result[0] if result else None
