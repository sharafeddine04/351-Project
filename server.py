import datetime
import random
from flask import Flask,render_template,request,session
import mysql.connector
import smtplib
from email.message import EmailMessage
import ssl

app = Flask(__name__)
app.secret_key = 'osj'
name = ""
lastname = ""
email=""
password=""
number = random.randint(100000,999999)
capacity = {"singleroom":3, "doubleroom":4, "suitefor1":2, "doublesuite":2}
room = {"singleroom":"Single Room", "doubleroom":"Double Room", "suitefor1":"Suite For 1", "doublesuite":"Double Suite"}


@app.route('/')
def mainPage():
    return render_template("mainPage.html")

@app.route('/goToSignup', methods=["GET"])
def loadSignup():
    return render_template("signupPage.html")

@app.route('/goToLogin', methods=["GET"])
def loadLogin():
    return render_template("login.html")

@app.route('/signupVerification',methods=["POST"])
def signup():
    output=request.form.to_dict()
    session["name"]=output['fName']
    session["lastname"]=output['lName']
    session["email"]=output['email']
    session["password"]=output['password']
    confirmPass = output['confirmPassword']
    if "HumanVerification" not in output:
        error = "Verify that you are not a robot"
        return render_template("signupPage.html",error_statement=error,fName = session["name"], lName = session["lastname"], email = session["email"])    
    if session["name"] == "" or session["lastname"] == "" or session["email"] == "" or session["password"] == "":
        error = "None of the fields above can be empty"
        return render_template("signupPage.html",error_statement=error, fName = session["name"], lName = session["lastname"], email = session["email"])
    if confirmPass!=session["password"]:
        error = "Password is not the same as confirmed password"
        return render_template("signupPage.html",error_statement=error, fName = session["name"], lName = session["lastname"], email = session["email"])
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()   
    sql = 'SELECT * from user'
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    emailFound = False
    for i in range(n):
        if result[i][0]==session["email"]:
            emailFound = True
            break
    if emailFound:
        con.commit()
        cur.close()
        con.close()
        return render_template("unsuccessfulSignupEmail.html") 
    em = EmailMessage()
    context = ssl.create_default_context()
    gmail_user = "hotelreservationeece351@gmail.com"
    gmail_password = "fpdirumwuxzdzohj"
    em["From"] = gmail_user
    em["To"] = session["email"]
    em["Subject"] = "Verification Code Hotel Reservation"
    text = "Hello, your verification code is: " + str(number)
    em.set_content(text)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com',465, context = context)
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user,session["email"],em.as_string())
    except:
        print ('Something went wrong...')
    return render_template("signupVerification.html")

@app.route('/verifySignup',methods=["GET","POST"])     
def verifySignup():
    output=request.form.to_dict()
    new_code = output["code"]
    if str(number) == new_code:
        con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
        cur=con.cursor()
        cur.execute("insert into user values(%s,%s,%s,%s)",(session['email'],session["name"],session['lastname'],session["password"]))
        con.commit()
        cur.close()
        con.close()
        return render_template("profile.html")    
    else:
        return render_template("signupVerification.html",error = "Verification Code is not same as entered code")


@app.route('/login',methods=["POST","GET"])
def login():
    output=request.form.to_dict()
    session["email"]=output['email']
    session["password"]=output['password']
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    sql = '''SELECT * from user'''
    cur=con.cursor()   
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    emailFound = False
    for i in range(n):
        if result[i][0]==session["email"]:
            emailFound = True
            emailIndex = i
            break
    if emailFound:
        if session["password"]==result[emailIndex][3]:
            con.commit()
            cur.close()
            con.close()
            return render_template("profile.html")            
    con.commit()
    cur.close()
    con.close()
    error = "Incorrect Password" if emailFound else "Email Not Found"
    return render_template("login.html",error_statement=error, email = session['email'])   

@app.route("/resetPassword", methods= ["GET","POST"])
def loadVerification():
    return render_template("verificationCode.html")


verification_email = ""

@app.route("/sendVerification",methods = ["GET","POST"])
def sendVerification():
    output = request.form.to_dict()
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

number = random.randint(100000,999999)

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
    
    return render_template("mainPage.html",changePassSuccess="Password Changed Successfully")   

@app.route("/loadReservationPage",methods = ["GET","POST"])
def loadReservation():
    return render_template("reservationPage.html")   

@app.route("/checkAvailableRooms",methods = ["GET","POST"])
def reserve():
    output=request.form.to_dict()
    startDate = output["startDate"]
    startDate = datetime.date(int(startDate[0:4]),int(startDate[5:7]),int(startDate[8:10]))
    endDate = output["endDate"]
    endDate = datetime.date(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10]))
    roomType = output["roomType"]
    if endDate<=startDate:
        return render_template("reservationPage.html", error = "Please select a valid date range")
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    sql = 'SELECT * from '+roomType
    cur=con.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    max = len(result)+1
    numberOfRoomsUsed = 0
    for i in range(len(result)):
        start = result[i][2]
        end = result[i][3]
        if ((startDate<= end and startDate>=start) or (endDate<= end and endDate>=start) or (startDate<=start  and endDate>=end)):
            numberOfRoomsUsed+=1
    if (numberOfRoomsUsed < capacity[roomType]):
        cur.execute("insert into "+roomType+" values(%s,%s,%s,%s,%s)",(max,session['email'],startDate,endDate,roomType))
        con.commit()
        cur.close()
        con.close()
        return render_template("reservationPage.html", error = "successful")
    return render_template("reservationPage.html", error = "No "+ roomType +" available for reservation in selected date")

@app.route("/getPreviousReservations",methods = ["GET","POST"])
def previousReservaions():
    prevRes = []
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()
    sql = """SELECT * FROM singleroom WHERE email= \""""+session["email"]+"""\"
Union
SELECT * FROM doubleroom WHERE email=\""""+session["email"]+"""\"
Union
SELECT * FROM suitefor1 WHERE email=\""""+session["email"]+"""\"
Union
SELECT * FROM doublesuite WHERE email=\""""+session["email"]+"""\"
"""
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    singleroom = []
    doubleroom = []
    suitfor1 = []
    doublesuit = []
    today = datetime.date.today()
    for i in range(n):
        startDate = result[i][2]
        endDate = result[i][3]
        roomType = result[i][4]
        if today>=endDate:
            if roomType == "singleroom" :
                singleroom.append((startDate,endDate))
            if roomType == "doubleroom":
                doubleroom.append((startDate,endDate))
            if roomType == "suitefor1":
                suitfor1.append((startDate,endDate))
            if roomType == "doublesuite":
                doublesuit.append((startDate,endDate))
    allPrevRes=""
    n = len(singleroom)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Single Rooms:<br>"+str(singleroom[i][0])+" to "+str(singleroom[i][1])+"<br>"
        else:
            allPrevRes=allPrevRes+str(singleroom[i][0])+" to "+str(singleroom[i][1])+"<br>"
    n = len(doubleroom)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Double Rooms:<br>"+str(doubleroom[i][0])+" to "+str(doubleroom[i][1])+"<br>"
        else:
            allPrevRes=allPrevRes+str(doubleroom[i][0])+" to "+str(doubleroom[i][1])+"<br>"
    n = len(suitfor1)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Suite For 1:<br>"+str(suitfor1[i][0])+" to "+str(suitfor1[i][1])+"<br>"
        else:
            allPrevRes=allPrevRes+str(suitfor1[i][0])+" to "+str(suitfor1[i][1])+"<br>"
    n = len(doublesuit)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Double Suite:<br>"+str(doublesuit[i][0])+" to "+str(doublesuit[i][1])+"<br>"
        else:
            allPrevRes=allPrevRes+str(doublesuit[i][0])+" to "+str(doublesuit[i][1])+"<br>"     
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\getPreviousReservations.html","w")
    if (len(allPrevRes)==0):
        f.write("<p>No Reservations have been made</p>")
        f.close()
        return render_template("getPreviousReservations.html")
    
    f.write("<p>"+allPrevRes+"</p>")
    f.close()
    return render_template("getPreviousReservations.html")

@app.route("/getCurrentReservations",methods = ["GET","POST"])
def currentReservaions():
    curRes = []
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()
    sql = """SELECT * FROM singleroom WHERE email= \""""+session["email"]+"""\"
Union
SELECT * FROM doubleroom WHERE email=\""""+session["email"]+"""\"
Union
SELECT * FROM suitefor1 WHERE email=\""""+session["email"]+"""\"
Union
SELECT * FROM doublesuite WHERE email=\""""+session["email"]+"""\"
"""
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    singleroom = []
    doubleroom = []
    suitfor1 = []
    doublesuit = []
    today = datetime.date.today()
    for i in range(n):
        startDate = result[i][2]
        endDate = result[i][3]
        roomType = result[i][4]
        if today<startDate:
            if roomType == "singleroom" :
                singleroom.append((startDate,endDate))
            if roomType == "doubleroom":
                doubleroom.append((startDate,endDate))
            if roomType == "suitefor1":
                suitfor1.append((startDate,endDate))
            if roomType == "doublesuite":
                doublesuit.append((startDate,endDate))
    allPrevRes=""
    print(str(singleroom)+" "+str(doubleroom)+' '+str(suitfor1)+" "+str(doublesuit))
    n = len(singleroom)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Single Rooms:<br>"+'<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}" name = "'+str(singleroom[i][0])+" to "+str(singleroom[i][1])+'">'+str(singleroom[i][0])+" to "+str(singleroom[i][1])+'</a><br>'
        else:
            allPrevRes='<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}">'+str(singleroom[i][0])+" to "+str(singleroom[i][1])+'</a><br>'
    n = len(doubleroom)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Double Rooms:<br>"+'<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}">'+str(doubleroom[i][0])+" to "+str(doubleroom[i][1])+'</a><br>'
            print(allPrevRes)
        else:
            allPrevRes=allPrevRes+'<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}">'+str(doubleroom[i][0])+" to "+str(doubleroom[i][1])+'</a><br>'
    n = len(suitfor1)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Suite For 1:<br>"+'<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}">'+str(suitfor1[i][0])+" to "+str(suitfor1[i][1])+'</a><br>'
        else:
            allPrevRes=allPrevRes+'<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}">'+str(suitfor1[i][0])+" to "+str(suitfor1[i][1])+'</a><br>'
    n = len(doublesuit)
    for i in range(n):
        if i == 0:
            allPrevRes=allPrevRes+"Double Suite:<br>"+'<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}">'+str(doublesuit[i][0])+" to "+str(doublesuit[i][1])+'</a><br>'
        else:
            allPrevRes=allPrevRes+"Double Suite:<br>"+'<a href="'+"{"+"{"+'url_for('+"'modifyReservation'"+')'+"}"+'}">'+str(doublesuit[i][0])+" to "+str(doublesuit[i][1])+'</a><br>'
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\currentReservation.html","w")
    if (len(allPrevRes)==0):
        f.write("<p>No Reservations have been made</p>")
        f.close()
        return render_template("currentReservation.html")
    f.truncate(0)
    f.write("<p>"+allPrevRes+"</p>")
    f.close()
    return render_template("currentReservation.html")

@app.route("/modifyReservation",methods = ["GET","POST"])
def modifyReservation():
    print(name)
    return render_template("modifyReservation.html")

if __name__=='__main__':
    app.run(port = 80)
