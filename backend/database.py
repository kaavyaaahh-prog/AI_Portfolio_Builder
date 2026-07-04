"""
database.py
------------
Small helper module that gives every route a simple way to talk to MySQL.
Beginners: think of get_db_connection() as "open a phone line to MySQL"
and cursor.execute(...) as "say something into that phone line".
"""

import mysql.connector
from mysql.connector import Error
from config import Config


def get_db_connection():
    """
    Opens and returns a new MySQL connection using the settings in config.py.
    Every route should call this, use it, then close it.
    """
    try:
        connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="12345",
    database="ai_portfolio_builder"
)
        return connection
    except Error as e:
        print(f"[Database Error] Could not connect to MySQL: {e}")
        return None


def run_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    A convenience wrapper so route files don't repeat connect/cursor/close code.

    - fetchone=True  -> returns a single row (dict) or None
    - fetchall=True  -> returns a list of rows (dicts)
    - commit=True    -> used for INSERT / UPDATE / DELETE, returns lastrowid
    """
    connection = get_db_connection()
    if connection is None:
        return None

    result = None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())

        if commit:
            connection.commit()
            result = cursor.lastrowid
        elif fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
    except Error as e:
        print(f"[Database Error] Query failed: {e}")
        result = None
    finally:
        cursor.close()
        connection.close()

    return result
