from connector import db_connection as db

connect = db()
cursor = connect.cursor()

