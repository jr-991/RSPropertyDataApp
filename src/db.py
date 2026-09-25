import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="abc123",
    database="real_estate_db"
)

cursor = mydb.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS real_estate_db")