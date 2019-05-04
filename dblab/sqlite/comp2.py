import sqlite3
import time


a = time.time()
conn = sqlite3.connect('example.db')
cur = conn.cursor()


instructor = 'SELECT name, day FROM CUSTOMERS CROSS JOIN RESERVATION'
student = 'SELECT name, day FROM CUSTOMERS CROSS JOIN RESERVATION'

instructor = 'SELECT * FROM CARS LIMIT 4 OFFSET 2'
student = 'SELECT * FROM CARS LIMIT 4 OFFSET 2'


SQL3 = '''select * from ({instructor}) EXCEPT select * from ({student})'''.format(instructor=instructor, student=student)


cur.execute(SQL3)
c = cur.fetchall()

conn.commit()
cur.close()
conn.close()

print(time.time()-a)
print(c)