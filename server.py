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
    return render_template("mainPage.html")

@app.route('/goToSignup', methods=["GET"])
def loadSignup():
    return render_template("signupPage.html")

@app.route('/goToLogin', methods=["GET"])
def loadLogin():
    return render_template("login.html")

@app.route('/signup',methods=["POST"])
def signup():
    output=request.form.to_dict()
    name=output['fName']
    lastname=output['lName']
    email=output['email']
    password=output['password']
    confirmPass = output['confirmPassword']
    if "HumanVerification" not in output:
        error = "Verify that you are not a robot"
        return render_template("signupPage.html",error_statement=error,fName = name, lName = lastname, email = email)    
    if name == "" or lastname == "" or email == "" or password == "":
        error = "None of the fields above can be empty"
        return render_template("signupPage.html",error_statement=error, fName = name, lName = lastname, email = email)
    if confirmPass!=password:
        error = "Password is not the same as confirmed password"
        return render_template("signupPage.html",error_statement=error, fName = name, lName = lastname, email = email)
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()   
    sql = 'SELECT * from user'
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    emailFound = False
    for i in range(n):
        if result[i][0]==email:
            emailFound = True
            break
    if emailFound:
        con.commit()
        cur.close()
        con.close()
        return render_template("unsuccessfulSignupEmail.html")         
    cur.execute("insert into user values(%s,%s,%s,%s)",(email,name,lastname,password))
    con.commit()
    cur.close()
    con.close()
    return render_template("profile.html"),email

@app.route('/login',methods=["POST","GET"])
def login():
    output=request.form.to_dict()
    email=output['email']
    password=output['password']
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    sql = '''SELECT * from user'''
    cur=con.cursor()   
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    emailFound = False
    for i in range(n):
        if result[i][0]==email:
            emailFound = True
            emailIndex = i
            break
    if emailFound:
        if password==result[emailIndex][3]:
            con.commit()
            cur.close()
            con.close()
            return render_template("profile.html")            
    con.commit()
    cur.close()
    con.close()
    error = "Incorrect Password"
    return render_template("login.html",error_statement=error, email = email)         



if __name__=='__main__':
    app.run()
