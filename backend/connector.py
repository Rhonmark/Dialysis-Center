import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )

# print(db_connection())

# def test():
#    print(os.getenv("DB_PORT"))

# if __name__ == "__main__":
#   test()