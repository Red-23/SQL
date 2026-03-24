import sqlite3
db_file = "C:/Users/bilan/Downloads/mysports.db"
db = sqlite3.connect(db_file)
cursor = db.cursor()
sql_query = ("SELECT * "
		   "FROM product")
cursor.execute(sql_query)
prod_row = cursor.fetchone()
print(prod_row)

print()
#Excerise 2
sql_query = ("SELECT custid, area, name "
         	   "FROM customer")
cursor.execute(sql_query)
all_cust_rows = cursor.fetchall()
for cust_row in all_cust_rows:
    print(cust_row)
db.close()

