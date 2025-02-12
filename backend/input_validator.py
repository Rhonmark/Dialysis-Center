from connector import db_connection as db

connect = db()
cursor = connect.cursor()

def login_user_input():
  username = input("Input Username: ").strip(' ')
  password = input("Input Password: ").strip(' ')
  return username, password

def register_user_input():
  username = input("Input Username: ").strip(' ')
  password = input("Input Password: ").strip(' ')
  secret_answer = input("Input Secret Answer: ").strip(' ')
  return username, password, secret_answer

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
  return validation_result

def register_validation(username, password, secret_answer):
  validation_result = user_input_validation(username, password)
  if validation_result:
    return validation_result
  if not secret_answer:
    return("Secret Answer must be filled!")
  return ("Registration Successful!")

def register_to_db(username, password, secret_answer):
  query = """
      INSERT INTO users (username, password, secret_answer)
      VALUES (%s, %s, %s)
  """
  values = (username, password, secret_answer)
  cursor.execute(query, values)

  connect.commit()

  print("User registered successfully!")

def login_user(username, password):
    try:
        query = """
            SELECT password FROM users WHERE username = %s
        """
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]
            if password == stored_password:
                return "Login Success!"
            else:
                return "Incorrect password!"
        else:
            return "Username not found!"
    except Exception as e:
        print(f"Error during login: {e}")
        return "Error during login!"

def test_registration():
    username_register, password_register, answer_register = register_user_input()
    registration_result = register_validation(username_register, password_register, answer_register)
    print(registration_result)

    if registration_result == "Registration Successful!":
        register_to_db(username_register, password_register, answer_register)

# Testing login
def test_login():
    username_login, password_login = login_user_input()
    login_result = login_validation(username_login, password_login)
    print(login_result)

    if login_result == "Login Success!":
        login_result = login_user(username_login, password_login)
        print(login_result)

# Main flow
def main():
    choice = input("Do you want to Register (R) or Login (L)? ").strip().lower()
    if choice == 'r':
        test_registration()
    elif choice == 'l':
        test_login()
    else:
        print("Invalid option, please choose 'R' for Register or 'L' for Login.")

if __name__ == "__main__":
    main()