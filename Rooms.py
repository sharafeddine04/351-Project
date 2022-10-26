import datetime
import random
from flask import Flask,render_template,request
import mysql.connector
import person

app = Flask(__name__)

name = ""
lastname = ""
email=""
password=""

@app.route('/')
def mainPage():
    return render_template("roomPage.html")

@app.route('/roomreservation', methods=["GET","POST"])
def loadSignup():
    output=request.form.to_dict()
    print(output)
    date1 = str(output["startDate"])
    date = datetime.date(int(date1[0:4]),int(date1[5:7]),int(date1[8:10]))
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()   
    sql = 'SELECT * from singleroom'
    cur.execute(sql)
    result = cur.fetchall()
    n=len(result)
    for i in range(n):
        if date<result[i][1]:
            print(date,result[i][1])
    return render_template("roomPage.html")

if __name__=='__main__':
    app.run()
