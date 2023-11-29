import os
import psycopg2 

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

def insert_tags(genre,tag_name):
    connection = get_connection()
    cursor = connection.cursor()
    sql = 'INSERT INTO tags VALUES (default,%s,%s)'
    
    cursor.execute(sql,(genre,tag_name))
    
    connection.commit()
    cursor.close()
    connection.close() 
    
def select_tag():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT * FROM tags"

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows