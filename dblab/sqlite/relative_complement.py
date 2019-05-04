import sqlite3
import json

conn = sqlite3.connect('example.db')
cur = conn.cursor()


# instructor = 'SELECT name, day FROM CUSTOMERS CROSS JOIN RESERVATION'
# student = 'SELECT name, day FROM CUSTOMERS CROSS JOIN RESERVATION'
# attr = 'name'
# attr1 = 'day'

# SQL = '''SELECT * FROM ({instructor}) AS qwe
#     WHERE NOT EXISTS (
#         SELECT {columns} FROM ({student}) AS asd
#         WHERE
#             CASE
#                 WHEN qwe.{col} IS NULL AND asd.{col} IS NULL
#                 THEN 1
#                 WHEN qwe.{col} IS NULL AND asd.{col} IS NOT NULL
#                 THEN 0
#                 WHEN qwe.{col} IS NOT NULL AND asd.{col} IS NULL
#                 THEN 0
#                 ELSE qwe.{col} = asd.{col}
#             END    
#         AND
#             CASE
#                 WHEN qwe.{col1} IS NULL AND asd.{col1} IS NULL
#                 THEN 1
#                 WHEN qwe.{col1} IS NULL AND asd.{col1} IS NOT NULL
#                 THEN 0
#                 WHEN qwe.{col1} IS NOT NULL AND asd.{col1} IS NULL
#                 THEN 0
#                 ELSE qwe.{col1} = asd.{col1}
#             END    
#     );'''.format(instructor=instructor, student=student, columns='name,day', col='name', col1='day')

# SQL2 = '''{instructor} INTERSECT {student}'''.format(instructor=instructor, student=student)

# SQL3 = '''{instructor} EXCEPT {student}'''.format(instructor=instructor, student=student)



###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################

a = [1,2,3]

result_dict = {
    'result': 0,
    'result_string': a,
    'error': ''
}

result_json = json.dumps(result_dict)
js = json.loads(result_json)

print(js['result_string'][0])

print(result_json)
print(js)

def hello(st):
    st = st+'hello'
    print(st)


aa = 'a'
hello(aa)
print aa






cur.close()
conn.close()