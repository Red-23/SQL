import sqlite3
db_file = "C:/Users/bilan/Downloads/mysports.db"
db = sqlite3.connect(db_file)
cursor = db.cursor()
empname = input("Enter an employee name to display: ")
sql_query = ("SELECT ename, monthly_sal "
             "FROM emp "
            "WHERE UPPER(ename)=UPPER(?)")
cursor.execute(sql_query, (empname,))
emp_row =cursor.fetchone()
if emp_row:
    ename = emp_row [0]
    monthly_sal = emp_row [1]
    print(f"The employee {ename} earns a monthly salary of £{monthly_sal:.2f}")
else:
    print ("No employee found with name")
db.close()