import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="farmerdb",
    port=3307
)

print("✅ MySQL Connected Successfully")
