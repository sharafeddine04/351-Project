import random
from flask import Flask,render_template,request,session
import mysql.connector
import person

app = Flask(__name__)
app.secret_key = 'osj'
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
    session["email"] = email
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
    error = "Incorrect Password" if emailFound else "Email Not Found"
    return render_template("login.html",error_statement=error, email = email)   

number = random.randint(100000,999999)

@app.route("/resetPassword", methods= ["GET","POST"])
def loadVerification():
    return render_template("verificationCode.html")


verification_email = ""

@app.route("/sendVerification",methods = ["GET","POST"])
def sendVerification():
    output = request.form.to_dict()
    import smtplib
    from email.message import EmailMessage
    import ssl
    context = ssl.create_default_context()
    gmail_user = "hotelreservationeece351@gmail.com"
    gmail_password = "fpdirumwuxzdzohj"
    verification_email = output["email"]

    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()   
    sql = 'SELECT * from user'
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    emailFound = False
    for i in range(n):
        if result[i][0]==verification_email:
            emailFound = True
            break
    con.commit()
    cur.close()
    con.close()
    if emailFound:
        session["verification_email"] = output["email"]
        em = EmailMessage()
        em["From"] = gmail_user
        em["To"] = verification_email
        em["Subject"] = "Verification Code Hotel Reservation"
        text = "Hello, your verification code is: " + str(number)
        em.set_content(text)
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com',465, context = context)
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user,verification_email,em.as_string())
        except:
            print ('Something went wrong...')
        return render_template("verificationCode.html",email = verification_email)
    else:
        error = "Email not found"
        return render_template("verificationCode.html",error_statement = error)


@app.route('/verificationCode',methods=["GET","POST"])     
def resetPassword():
    output=request.form.to_dict()
    new_code = output["code"]
    if str(number) == new_code:
        return render_template("newPassword.html")
    else:
        return render_template("verificationCode.html",error = "Verification Code is nt same as entered code", email = session["verification_email"])

@app.route("/changePassword",methods = ["GET","POST"])
def newPassword():
    output=request.form.to_dict()
    password = output["newPassword"]
    confirmpassword = output["confirmNewPassword"]
    if password!=confirmpassword:
        error = "Passwords dont match"
        return render_template("newPassword.html", error_statement = error)
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()
    cur.execute("UPDATE user SET password = %s WHERE email=%s",(password,session["verification_email"]))
    con.commit()
    cur.close()
    con.close()
    
    return render_template("mainPage.html")   

if __name__=='__main__':
    app.run()
