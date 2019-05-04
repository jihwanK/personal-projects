from math import pow
import sqlite3



##############################################################################
#
# table for encoding the url
#
##############################################################################

table = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'



##############################################################################
#
# DB connection 
#
##############################################################################

db = sqlite3.connect('shorturl.db')
cursor = db.cursor()



##############################################################################
#
# process for encoding and decoding of url
#
##############################################################################

def encode(urlid):
	tmp = []
	code = []

	while urlid > 0:
	 	remainder = urlid % 62
	 	tmp.append(remainder)
	 	urlid = int(urlid / 62)

	for k in tmp:
		code.append(table[k])

	return code

def decode(suburl):
	code = []
	num = 0

	for i in range(0, len(suburl)):
		code.append(table.find(suburl[i]))
		num = num + int(pow(62, i))*code[i] 

	return num



##############################################################################
#
# DB connection open, close and query
#
##############################################################################

def pre_insert_into_db(longurl):
	sql = 'SELECT url_id FROM url WHERE long_url=?;'
	data = (longurl,)
	cursor.execute(sql, data)
	id = cursor.fetchall()
	return id

def insert_into_db(longurl):
	data = (longurl,)
	if pre_insert_into_db(longurl) == []:
		sql = 'INSERT INTO url (long_url) VALUES (?);'
		cursor.execute(sql, data)
	sql = 'SELECT url_id FROM url WHERE long_url=?;'
	cursor.execute(sql, data)
	id = cursor.fetchone()[0]
	return id

def find_from_db(deco):
	sql = 'SELECT long_url FROM url WHERE url_id=?;'
	data = (deco,)
	cursor.execute(sql, data)
	url = cursor.fetchone()[0]
	return url

def close_db():
	db.commit()
	cursor.close()
	db.close()



##############################################################################
#
# print the short virsion of url and original version of url
#
##############################################################################

def print_short_url(code):
	sub_url = encode(code)
	short_url = 'http://localhost/'
	for ch in sub_url:
		short_url = short_url + ch
	print(short_url)
	return short_url

def print_original_url(url):
	splited = url.split('/')
	sub_url = splited[3]
	deco = decode(sub_url)
	original_url = find_from_db(deco)
	print(original_url)
	return original_url



##############################################################################
#
# implement code to run this program
#
##############################################################################

url = raw_input('insert url please: ')

code = insert_into_db(url)

short_url = print_short_url(code)
original_url = print_original_url(short_url)

# print(short_url)
# print(original_url)

close_db()