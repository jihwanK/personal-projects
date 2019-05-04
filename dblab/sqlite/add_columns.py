import sqlite3
import random

conn = sqlite3.connect("example.db")
cur = conn.cursor()

cur.execute('delete from reservation')
cur.execute('delete from customers')
cur.execute('delete from cars')
cur.execute('delete from orders')
#conn.commit()

for i in range(1000):
    r = random.randint(1, 10005)
    name = 'u' + str(r)
    sql_res = 'insert into reservation (customer_id, day) values (?, ?)'
    sql_cust = 'insert into customers (name) values ("{name}")'.format(name=name)
    rr = random.randint(1, 1001)

    cur.execute(sql_cust)
    #conn.commit()
    cur.execute(sql_res, (rr,r))
    #conn.commit()

for i in range(1000):
    r = random.randint(1, 10005)
    name = 'u' + str(r)
    sql_car = 'insert into cars (name, price) values (?, ?)'
    price = random.randrange(10000, 100000, 1000)

    cur.execute(sql_car, (name, price))
    #conn.commit()

for i in range(1000):
    price = random.randrange(10000, 100000, 1000)
    r = random.randint(1, 10005)
    customer = 'u' + str(r)
    sql_orders = 'insert into orders (order_price, customer) values (?, ?)'

    cur.execute(sql_orders, (price, customer))
    #conn.commit()

    
conn.commit()
cur.close()
conn.close()
