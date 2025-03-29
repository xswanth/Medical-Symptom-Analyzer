import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="hostname",
        user="root",
        password="password",
        database="medical_symptom_analyzer"
    )

conn=get_db_connection()
my_cursor=conn.cursor()

my_cursor.execute("show tables;")
for db in my_cursor:
    print(db)
    
