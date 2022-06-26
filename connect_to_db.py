from mysql.connector import connect, Error
import os
import pandas as pd


def connect_to_db() -> connect:
    """
    Connect to the database.

    Returns:
        connect
            Database connection.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
        password = f.read()
    try:
        db = connect(
            host="35.199.127.241",
            user="looqbox-challenge",
            password=password,
            database="looqbox_challenge",
        )
    except Error as e:
        print(e)
        exit(1)
    return db
