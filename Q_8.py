#Question 8
import sqlite3
db_file = "C:/Users/bilan/Downloads/mysports.db"
db = sqlite3.connect(db_file)
cursor = db.cursor()
sql_query = ("SELECT ename, name " 
             "FROM customer c "
             "  INNER JOIN emp e ON c.repid = e.empno "
             "ORDER BY ename")
cursor.execute(sql_query)
all_rows = cursor.fetchall()
last_repname = ""
print (f"{'Sales Rep':10}\t{'Customer Name':40}\n")
for row in all_rows:
    repname = row[0]
    custname = row[1]
    if repname != last_repname:
        print(f"{repname:10}\t{custname:40}")
        last_repname = repname
    else:
        print(f"{'':10}\t{custname:40}")
    db.close()