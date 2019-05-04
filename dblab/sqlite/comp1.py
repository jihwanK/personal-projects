import sqlite3
import time

b = time.time()

conn = sqlite3.connect('example.db')
cur = conn.cursor()


instructor = 'SELECT name, day FROM CUSTOMERS CROSS JOIN RESERVATION'
student = 'SELECT name, day FROM CUSTOMERS CROSS JOIN RESERVATION'


SQL = '''SELECT * FROM ({instructor}) AS qwe
    WHERE NOT EXISTS (
        SELECT {columns} FROM ({student}) AS asd
        WHERE
            qwe.{col}=asd.{col}
        AND
            qwe.{col1}=asd.{col1}

    );'''.format(instructor=instructor, student=student, columns='name,day', col='name', col1='day')


cur.execute(SQL)
a = cur.fetchall()


conn.commit()


cur.close()
conn.close()

print(time.time()-b)
print(a)