from .connector import db_connection as db

def db_connection():
    connect = db()
    cursor = connect.cursor()
    return connect, cursor

def register_to_db(role, username, password, secret_question, secret_answer):
    connect, cursor = db_connection()
    query = """
        INSERT INTO users (role, username, password, secret_question, secret_answer)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (role, username, password, secret_question, secret_answer)
    cursor.execute(query, values)
    connect.commit()
    print("User registered successfully!")

def get_password_from_db(username):
    connect, cursor = db_connection()
    query = "SELECT password, role FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None

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

def set_new_password(password, username):
    connect, cursor = db_connection()
    query = "UPDATE users SET password = %s WHERE username = %s"
    values = (password, username)
    cursor.execute(query, values)
    connect.commit()
    print("Password updated successfully!")

def get_secret_question (username):
    connect, cursor = db_connection()
    query = "SELECT secret_question FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None

def get_role (username):
    connect, cursor = db_connection()
    query = "SELECT role FROM users WHERE username = %s"
    cursor.execute(query, [username])
    result = cursor.fetchone()
    return result[0] if result else None