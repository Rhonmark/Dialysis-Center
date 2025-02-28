from .connector import db_connection as db

def db_connection():
    connect = db()
    cursor = connect.cursor()
    return connect, cursor

def user_input_validation(username, password):
    if not username and not password:
        return "Both fields must be filled!"
    if not username:
        return "Username is missing!"
    if not password:
        return "Password is missing!"
    if len(username) < 8:
        return "Username must be at least 8 characters!"
    if len(password) < 6:
        return "Password must be at least 6 characters!"
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
        return "Secret Answer must be filled!"
    return None

def register_to_db(role, username, password, secret_answer):
    connect, cursor = db_connection()
    query = """
        INSERT INTO users (role, username, password, secret_answer)
        VALUES (%s, %s, %s, %s)
    """
    values = (role, username, password, secret_answer)
    cursor.execute(query, values)
    connect.commit()
    print("User registered successfully!")

def get_password_from_db(username):
    connect, cursor = db_connection()
    query = "SELECT password, role FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result if result else None

def get_answer_from_db(username):
    connect, cursor = db_connection()
    query = "SELECT secret_answer FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None

def get_username_from_db(username):
    connect, cursor = db_connection()
    query = "SELECT username FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None

def set_new_password(username, password):
    connect, cursor = db_connection()
    query = "UPDATE users SET password = %s WHERE username = %s"
    values = (password, username)
    cursor.execute(query, values)
    connect.commit()
    print("Password updated successfully!")

def forgot_validator(password, confirm_password):
    if len(password) < 6 or len(confirm_password) < 6:
        print("Password must be at least 6 characters")
        return
    if password in ["Enter new password", ""]:
        print("Input cannot be missing...")
        return
    if confirm_password in ["Confirm new password", ""]:
        print("Input cannot be missing...")
        return
    if password != confirm_password:
        print("Confirm your password...")
        return
    print("You have successfully updated your password")

def null_validator(username, password, secret_answer):
    fields = {
        username: "Username must be at least 8 characters or cannot be empty!",
        password: "Password must be at least 6 characters or cannot be empty!",
        secret_answer: "Secret Answer must be filled!"
    }
    for field, message in fields.items():
        if field in ["", message]:
            print(message)
            return True
    return False
