import mysql.connector

con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
cur=con.cursor()   
sql = 'SELECT * from singleroom'
cur.execute(sql)
result = cur.fetchall()
v=result[0][0]
n = len(result)
for i in range(n):
    if result[i][0]>v:
        v = result[i][0]
v+=1
cur.execute("insert into singleroom values(%s,%s,%s)",(v,"2022-10-20","2022-10-30"))
con.commit()
cur.close()
con.close()