import sqlite3


conn = sqlite3.connect()
cur = conn.cursor()

def get_columns_of_result(instructor):
    cur.execute(instructor)
    names_of_columns = [des[0] for des in cur.description]
    

SQL = '''SELECT * FROM (%(instructor)s) AS qwe
    WHERE NOT EXISTS (
        SELECT %(columns)s FROM (%(student)s) AS asd
        WHERE
            CASE
                WHEN qwe.%(col)s IS NULL AND asd.%(col)s IS NULL
                THEN 1
                WHEN qwe.%(col)s IS NULL AND asd.%(col)s IS NOT NULL
                THEN 0
                WHEN qwe.%(col)s IS NOT NULL AND asd.%(col)s IS NULL
                THEN 0
                ELSE qwe.%(col)s = asd.%(col)s
            END        
    );
'''

SQL_data = {
    instructor: 'SELECT name, day FROM CUSTOMERS LEFT JOIN RESERVATION USING (customer_id)'
    student: 'SELECT name, day FROM CUSTOMERS LEFT JOIN RESERVATION USING (customer_id) ORDER BY name DESC'
}

additional_condition = '''
        AND
            CASE
                WHEN qwe.%(col)s IS NULL AND asd.%(col)s IS NULL
                THEN 1
                WHEN qwe.%(col)s IS NULL AND asd.%(col)s IS NOT NULL
                THEN 0
                WHEN qwe.%(col)s IS NOT NULL AND asd.%(col)s IS NULL
                THEN 0
                ELSE qwe.%(col)s = asd.%(col)s
            END
'''


cur.execute(SQL, SQL_data)
result = cur.fetchall()
if result.count == 0:
    print("done")
else:
    print("wrong")