import sqlite3
db_file = "C:/Users/bilan/Downloads/mysports.db"
db = sqlite3.connect(db_file)
emp_list = []
i = 1
cursor = db.cursor()
sql_query = ("SELECT empno, ename, deptno "
		   "FROM emp")
cursor.execute(sql_query)
all_emp_rows = cursor.fetchall()
print(f"\t{'Empno':5}\t{'Name':9}{'Deptno':15}")
for emp_row in all_emp_rows:
    empno = emp_row[0]
    ename = emp_row[1]
    deptno = emp_row[2]
    emp_list.append(empno)
    print(f"{i}.\t{empno:5}\t{ename:9}\t{deptno}")
    i = i + 1
db.close()
num_in_list = int(input("Which employee record do you want? "))
sel_emp = emp_list[num_in_list-1]
print ("Selected emplyee is", sel_emp)




