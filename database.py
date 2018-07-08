import sqlite3
import pandas as pd
conn = sqlite3.connect('result.sqlite')
curr = conn.cursor()


def create_db(code):  #create table
    curr.execute('''CREATE TABLE if NOT EXISTS result
              (roll text UNIQUE,Name text ,  sgpa text,cgpa text,status text)''')
    try:
        curr.execute(''' ALTER TABLE result
          ADD  '%s' text; '''%code )
        conn.commit()
    except:
        pass


def add_to_db(code, grade, roll, name, sgpa, cgpa, status): #fill grades of the student in table
    curr.execute('INSERT or IGNORE into result(roll,Name,sgpa,cgpa,status) values(?,?,?,?,?) ', (roll, name, sgpa, cgpa, status,))
    curr.execute('UPDATE result set  {} = ? where roll = ? '.format(code), (grade,roll))
    conn.commit()


def end():
    df = pd.read_sql('SELECT * FROM RESULT', conn)
    df.to_excel('result.xls')