import mysql.connector

def get_db_connection():
    """
    Create and return a new MySQL database connection.
    Update host, user, password, and database with your actual values.
    """
    conn = mysql.connector.connect(
        host="localhost",          # or your DB server host
        user="root",               # your MySQL username
        password="root",  # your MySQL password
        database="farmerdb",   # your database name
        port=3307                  # default MySQL port
    )
    return conn
