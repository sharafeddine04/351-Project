import datetime
import random
from flask import Flask,render_template,request,session, send_file
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
capacity = {}
room = {"singleroom":"Single Room", "doubleroom":"Double Room", "suitefor1":"Suite For 1", "doublesuite":"Double Suite"}
adminUsername = "admin"
adminsPass = "admin"
pricePerRoom = {}

@app.route('/')
def mainPage():
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    sql = '''SELECT * from roomsavailable'''
    cur=con.cursor()   
    cur.execute(sql)
    result = cur.fetchall()
    print(result)
    n = len(result)
    for i in range(n):
        capacity[result[i][0]] = result[i][1]
        pricePerRoom[result[i][0]] = result[i][2]
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
    session["firstName"]=output['fName']
    session["lastName"]=output['lName']
    session["email"]=output['email']
    session["password"]=output['password']
    confirmPass = output['confirmPassword']
    if "HumanVerification" not in output:
        error = "Verify that you are not a robot"
        return render_template("signupPage.html",error_statement=error,fName = session["firstName"], lName = session["lastName"], email = session["email"])    
    if session["firstName"] == "" or session["lastName"] == "" or session["email"] == "" or session["password"] == "":
        error = "None of the fields above can be empty"
        return render_template("signupPage.html",error_statement=error, fName = session["firstName"], lName = session["lastName"], email = session["email"])
    if confirmPass!=session["password"]:
        error = "Password is not the same as confirmed password"
        return render_template("signupPage.html",error_statement=error, fName = session["firstName"], lName = session["lastName"], email = session["email"])
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
        cur.execute("insert into user values(%s,%s,%s,%s)",(session['email'],session["firstName"],session['lastName'],session["password"]))
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
    if session["email"]==adminUsername and session["password"]==adminsPass:
        return render_template("adminsPage.html")
    elif session["email"]==adminUsername and not(session["password"]==adminsPass):
        return render_template("login.html",error_statement="Incorrect admin password", email = session['email'])
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    sql = '''SELECT * from user'''
    cur=con.cursor()   
    cur.execute(sql)
    result = cur.fetchall()
    n = len(result)
    emailFound = False
    for i in range(n):
        if result[i][0]==session["email"]:
            session["firstName"] = result[i][1]
            session["lastName"] = result[i][2]
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

def checkIfResAvailable(startDate,endDate,result,roomType):
    numberOfRoomsUsed = 0
    for i in range(len(result)):
        start = result[i][2]
        end = result[i][3]
        if ((startDate<= end and startDate>=start) or (endDate<= end and endDate>=start) or (startDate<=start  and endDate>=end)):
            numberOfRoomsUsed+=1
    if (numberOfRoomsUsed < capacity[roomType]):
        return True
    return False

@app.route("/loadReservationPage",methods = ["GET","POST"])
def loadReservation():
    output=request.form.to_dict()
    startDate = output["startDate"]
    startDate = datetime.date(int(startDate[0:4]),int(startDate[5:7]),int(startDate[8:10]))
    endDate = output["endDate"]
    endDate = datetime.date(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10]))
    if endDate<startDate:
        return render_template("profile.html",error_statement="Please select a valid date range")
    session["startDate"]=startDate.strftime("%m/%d/%Y")
    session["endDate"]=endDate.strftime("%m/%d/%Y")
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    typeOfAvailableRoom=[]
    cur=con.cursor()
    for key in room:
        sql = "SELECT * FROM "+key
        cur.execute(sql)
        result = cur.fetchall()
        if checkIfResAvailable(startDate, endDate, result, key):
            typeOfAvailableRoom.append(key)
    if len(typeOfAvailableRoom) == 0:
        string = "There are no rooms available between "+str(startDate)+" and "+str(endDate)+"<br><form method = \"Post\" action=\"backToProfile\"> <input type=\"submit\" name=\"backToProfile\" id = \"backToProfile\" value = \"Press here to go back to your profile\"><br></form>"
        f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html",'w')
        f.write("<html><p>"+string+"</p></html>")
        f.close()
        con.commit()
        cur.close()
        con.close()
        return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html")   
    string = "The rooms available between "+str(startDate)+" and "+str(endDate)+" are:<br><form method = \"Post\" action=\"confirmationPage\">"
    diffDate = (endDate-startDate).days
    for i in range(len(typeOfAvailableRoom)):
        price = pricePerRoom[typeOfAvailableRoom[i]]*diffDate
        string = string+'<input type="submit" name="'+typeOfAvailableRoom[i]+'" id = "'+typeOfAvailableRoom[i]+'" value = "'+room[typeOfAvailableRoom[i]]+'">Price:'+str(price)+'$ <br><br>'
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html",'w')
    f.write("<html><p>"+string+"</form></p></html>")
    f.close()
    con.commit()
    cur.close()
    con.close()
    return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html")   

@app.route("/backToProfile",methods = ["GET","POST"])
def profile():
    return render_template("profile.html")

@app.route("/confirmationPage",methods = ["GET","POST"])
def confirm():
    output=request.form.to_dict()
    for k in output:
        session["roomType"]=k
    print(session["startDate"])
    print(session["endDate"])
    startDate = datetime.date(int(session["startDate"][6:11]), int(session["startDate"][0:2]), int(session["startDate"][3:5]))
    endDate = datetime.date(int(session["endDate"][6:11]), int(session["endDate"][0:2]), int(session["endDate"][3:5]))
    numOfDays = endDate-startDate
    numOfDays = numOfDays.days
    price = pricePerRoom[session["roomType"]]*numOfDays
    session["price"]=price
    string = "<h2>Confirm your Reservation</h2><br>Date: "+session["startDate"]+" to "+session["endDate"]+"<br> Room Type: "+room[session["roomType"]]+"<br>Total Price:"+str(price)+"$<br><form method = \"Post\" action=\"confirmReservation\"><input type=\"submit\" name=\"confirm\" id = \"confirm\" value = \"Confirm Reservation\"></form>"
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\confirmation.html",'w')
    f.write("<html><p>"+string+"</p></html>")
    f.close()
    return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\confirmation.html")   

@app.route("/confirmReservation", methods=["GET","POST"])
def confirmRes():
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    sql = 'SELECT * from '+session["roomType"]
    cur=con.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    max = len(result)+1
    cur.execute('SELECT * from '+session["roomType"])
    result1 = cur.fetchall()
    y=int(max)
    for i in range(len(result1)):
        if(result1[i][0]==y):
            y+=1
    max=y
    session["startDate"] = datetime.date(int(session["startDate"][6:11]), int(session["startDate"][0:2]), int(session["startDate"][3:5]))
    session["endDate"] = datetime.date(int(session["endDate"][6:11]), int(session["endDate"][0:2]), int(session["endDate"][3:5]))
    print(session["roomType"])
    cur.execute("insert into "+session["roomType"]+" values(%s,%s,%s,%s,%s)",(max,session['email'],session["startDate"],session["endDate"],session["roomType"]))
    print("insert into "+session["roomType"]+" values(%s,%s,%s,%s,%s)",(max,session['email'],session["startDate"],session["endDate"],session["roomType"]))
    con.commit()
    cur.close()
    con.close()
    return render_template("profile.html",error_statement = "Reservation made successfully")

@app.route("/getPreviousReservations",methods = ["GET","POST"])
def previousReservaions():
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
    #f = open("C:\\Users\\jgsou\\OneDrive\\Desktop\\AUB\\EECE 351\\351-Project\\getPreviousReservations.html","w")
    if (len(allPrevRes)==0):
        f.write("<p>No Reservations have been made</p>")
        f.close()
        return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\getPreviousReservations.html")
    
    f.write("<p>"+allPrevRes+"</p>")
    f.close()
    return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\getPreviousReservations.html")

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
    id1 =[]
    id2=[]
    id3=[]
    id4=[]
    doubleroom = []
    suitfor1 = []
    doublesuit = []
    today = datetime.date.today()
    for i in range(n):
        startDate = result[i][2]
        endDate = result[i][3]
        roomType = result[i][4]
        if today<=startDate:
            if roomType == "singleroom" :
                singleroom.append((startDate,endDate))
                id1.append(result[i][0])
            if roomType == "doubleroom":
                doubleroom.append((startDate,endDate))
                id2.append(result[i][0])
            if roomType == "suitefor1":
                suitfor1.append((startDate,endDate))
                id3.append(result[i][0])
            if roomType == "doublesuite":
                doublesuit.append((startDate,endDate))
                id4.append(result[i][0])
    tot=0
    allPrevRes=""
    n=len(singleroom)
    tot +=n
    allPrevRes="<html>\n <body>\n <form method='POST' action = '/modifyReservation'> \n<label for='modifyrooms'>Pick a reservation:</label>\n <select name='modifyroom' id='reservations'>\n"
    u =  "<optgroup label='single rooms'>\n"
    if n>0:
        allPrevRes +=u
    for i in range(n):
        
        ma= ""
        ma+= str(singleroom[i][0])+" to "+str(singleroom[i][1])
        z="singleroom"
        z+=str(id1[i])
        allPrevRes += "<option value='" +str(z)+ "'>" +ma+"</option>\n"
    if n>0:
        allPrevRes+="</optgroup>"
    
    n=len(doubleroom)
    tot+=n
    u =  "<optgroup label='double rooms'>\n"
    if n>0:
        allPrevRes +=u
    for i in range(n):
        ma= ""
        ma+= str(doubleroom[i][0])+" to "+str(doubleroom[i][1])
        z="doubleroom"
        z+=str(id2[i])
        allPrevRes += "<option value='" +str(z)+ "'>" +ma+"</option>\n"
    if n>0:
        allPrevRes+="</optgroup>"

    n=len(suitfor1)
    tot+=n
    u =  "<optgroup label='suite for 1'>\n"
    if n>0:
        allPrevRes +=u
    for i in range(n):
        ma= ""
        ma+= str(suitfor1[i][0])+" to "+str(suitfor1[i][1])
        z="suitefor1"
        z+=str(id3[i])
        allPrevRes += "<option value='" +str(z)+ "'>" +ma+"</option>\n"
    if n>0:
        allPrevRes+="</optgroup>"
    
    n=len(doublesuit)
    tot+=n
    u =  "<optgroup label='double suite'>\n"
    if n>0:
        allPrevRes +=u
    for i in range(n):
        ma= ""
        ma+= str(doublesuit[i][0])+" to "+str(doublesuit[i][1])
        z="doublesuite"
        z+=str(id4[i])
        allPrevRes += "<option value='" +str(z)+ "'>" +ma+"</option>\n"
    if n>0:
        allPrevRes+="</optgroup>"


    allPrevRes += "</select>\n<input type='submit' name='submitSignup' id = 'modify' value ='modify'>\n"
    allPrevRes+= "<input type='submit' name='submitSignup' id = 'cancel' value ='Cancel Reservation'>\n"
    allPrevRes += "<input type ='submit' name = 'submitSignup' id = 'getInvoice' value = 'Get Invoice'>\n"
    allPrevRes+= "</form>\n</body>\n</html></p>"
    #f = open("C:\\Users\\jgsou\\OneDrive\\Desktop\\AUB\\EECE 351\\351-Project\\currentReservation.html","w")
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\currentReservation.html","w")
    #print(allPrevRes)
    if tot>0:
        f.write("<p>"+allPrevRes+"</p>")
        for i in range(100):
            ppp=i
        f.close()      
        return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\currentReservation.html")
    else:
        f.write("<p>No current reservations</p>")
        f.close()
        return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\currentReservation.html")

@app.route("/modifyReservation",methods = ["GET","POST"])
def modifyReservation():
    output = request.form.to_dict()
    session["modification"] = output["modifyroom"]
    print(session["modification"])
    if output["submitSignup"]=="modify":
        return render_template("modifyReservation.html")
    elif output["submitSignup"] == "Get Invoice":
        from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Spacer
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        tableData = [["Check-In Date", "Check-Out Date", "Room Type", "Room Price"]]
        con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
        cur=con.cursor()
        sql = """
        SELECT * FROM singleroom WHERE email= \""""+session["email"]+"""\"
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
        total_price = 0
        for i in range(n):
            temp = {"doubleroom" : "Double Room" , "singleroom" : "Single Room" , "suitefor1": "Single Suite", "doublesuite": "Double Suite"}
            start = result[i][2]
            end = result[i][3]
            diff = (end-start).days
            price = diff*pricePerRoom[result[i][4]]
            tableData.append([str(result[i][2]) , str(result[i][3]) , temp[result[i][4]], str(price)])
            total_price += price
        tableData.append(["Total" ,"" , "" , str(total_price)])
        tableData.append(["Signature" , "" , "" , "__________"])
        docu = SimpleDocTemplate("invoice.pdf", pagesize=A4)
        styles = getSampleStyleSheet()
        doc_style = styles["Heading1"]
        doc_style.alignment = 1
        title = Paragraph("ROOM RESERVATION INVOICE", doc_style)
        style = TableStyle([
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("GRID", (0, 0), (4, 4), 1, colors.chocolate),
                ("BACKGROUND", (0, 0), (3, 0), colors.skyblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ])
        table = Table(tableData, style=style)
        cur.execute(sql)
        docu.build([title, Spacer(1,20), Paragraph("Dear " + session["firstName"] + " " + session["lastName"] + ", this is the invoice for your room reservation(s)"), Spacer(1,20), table])
        em = EmailMessage()
        context = ssl.create_default_context()
        gmail_user = "hotelreservationeece351@gmail.com"
        gmail_password = "fpdirumwuxzdzohj"
        em["From"] = gmail_user
        em["To"] = session["email"]
        em["Subject"] = "Room Reservation Invoice"
        text = "Dear " + session["firstName"] + " " + session["lastName"] + ",\n\nPlease find attached the invoice for your reservation(s)"
        em.set_content(text)
        with open("invoice.pdf","r") as invoice:
            content = invoice.read()
            em.add_attachment(content, subtype = "pdf", filename = "invoice.pdf")
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com',465, context = context)
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user,session["email"],em.as_string())
        except:
            print ('Something went wrong...')
        return render_template("currentReservation.html")

    else:
        res = output["modifyroom"]
        print(res)
        inte=['1','2','3','4','5','6','7','8','9','0']
        n = len(res)
        j=0
        t=""
        for i in range(n):
            if res[i] not in inte:
                t+=res[i]
            else:
                j=i
                break
        ma = res[j:n]
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

        if t=="singleroom":
            cur.execute("DELETE FROM singleroom where id=\""""+ma+"""\"""")
            con.commit()
        elif t=="doubleroom":
            cur.execute("DELETE FROM doubleroom where id=\""""+ma+"""\"""")
            con.commit()
        elif t =="doublesuite":
            cur.execute("DELETE FROM doublesuite where id=\""""+ma+"""\"""")
            con.commit()
        else:
            cur.execute("DELETE FROM suitefor1 where id=\""""+ma+"""\"""")
            con.commit()
        return render_template("profile.html",error_statement = "Your previous reservation of a "+room[str(t)]+" has been deleted")

def checkIfResAvailableNew(startDate,endDate,startOld,endOld,result,roomType):
    numberOfRoomsUsed = 0
    for i in range(len(result)):
        start = result[i][2]
        end = result[i][3]
        if ((startDate<= end and startDate>=start) or (endDate<= end and endDate>=start) or (startDate<=start  and endDate>=end)):
            numberOfRoomsUsed+=1
    if ((startOld<= endDate and startOld>=startDate) or (endOld<= endDate and endOld>=startDate) or (startOld<=startDate  and endOld>=endDate)):
        numberOfRoomsUsed-=1
    if (numberOfRoomsUsed < capacity[roomType]):
        return True
    return False

@app.route("/makeModification", methods=["GET","POST"])
def provideNewDate():
    output = request.form.to_dict()
    startDate = output["startDate"]
    startDate = datetime.date(int(startDate[0:4]),int(startDate[5:7]),int(startDate[8:10]))
    endDate = output["endDate"]
    endDate = datetime.date(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10]))
    if endDate<startDate:
        return render_template("modifyReservation.html",error="Please select a valid date range")
    session["newStartDate"]=startDate.strftime("%m/%d/%Y")
    session["newEndDate"]=endDate.strftime("%m/%d/%Y")
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    typeOfAvailableRoom=[]
    cur=con.cursor()
    res = session["modification"]
    inte=['1','2','3','4','5','6','7','8','9','0']
    n = len(res)
    j=0
    t=""
    for i in range(n):
        if res[i] not in inte:
            t+=res[i]
        else:
            j=i
            break
    ma = res[j:n]
    if res[0]=='s' and res[1]=='u':
        t="suitefor1"
        ma=res[len(t):n]
    sql = "SELECT * FROM "+t+" where id = "+ma
    cur.execute(sql)
    oldRes = cur.fetchall()
    oldRedervationStartDate = oldRes[0][2]
    oldRedervationEndDate = oldRes[0][3]
    for key in room:
        sql = "SELECT * FROM "+key
        cur.execute(sql)
        result = cur.fetchall()
        if key != t and checkIfResAvailable(startDate, endDate, result, key) :
            typeOfAvailableRoom.append(key)
        if key == t and checkIfResAvailableNew(startDate, endDate, oldRedervationStartDate, oldRedervationEndDate, result, key):
            typeOfAvailableRoom.append(key)
    if len(typeOfAvailableRoom) == 0:
        string = "There are no rooms available between "+str(startDate)+" and "+str(endDate)+"<br><form method = \"Post\" action=\"backToProfile\"> <input type=\"submit\" name=\"backToProfile\" id = \"backToProfile\" value = \"Press here to go back to your profile\"><br></form>"
        f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html",'w')
        f.write("<html><p>"+string+"</p></html>")
        f.close()
        con.commit()
        cur.close()
        con.close()
        return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html")   
    string = "The rooms available between "+str(startDate)+" and "+str(endDate)+" are:<br><form method = \"Post\" action=\"confirmationPageModified\">"
    diffDate = (endDate-startDate).days
    for i in range(len(typeOfAvailableRoom)):
        price = pricePerRoom[typeOfAvailableRoom[i]]*diffDate
        string = string+'<input type="submit" name="'+typeOfAvailableRoom[i]+'" id = "'+typeOfAvailableRoom[i]+'" value = "'+room[typeOfAvailableRoom[i]]+'">Price:'+str(price)+'$ <br><br>'
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html",'w')
    f.write("<html><p>"+string+"</form></p></html>")
    f.close()
    con.commit()
    cur.close()
    con.close()
    return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\availableRooms.html")   

@app.route("/confirmationPageModified",methods = ["GET","POST"])
def confirmModification():
    output=request.form.to_dict()
    for k in output:
        session["roomType"]=k
    print(session["startDate"])
    print(session["endDate"])
    startDate = datetime.date(int(session["newStartDate"][6:11]), int(session["newStartDate"][0:2]), int(session["newStartDate"][3:5]))
    endDate = datetime.date(int(session["newEndDate"][6:11]), int(session["newEndDate"][0:2]), int(session["newEndDate"][3:5]))
    numOfDays = endDate-startDate
    numOfDays = numOfDays.days
    price = pricePerRoom[session["roomType"]]*numOfDays
    session["newPrice"]=price
    string = "<h2>Confirm your Reservation</h2><br>Date: "+session["newStartDate"]+" to "+session["newEndDate"]+"<br> Room Type: "+room[session["roomType"]]+"<br>Total Price:"+str(price)+"$<br><form method = \"Post\" action=\"confirmModifyingReservation\"><input type=\"submit\" name=\"confirm\" id = \"confirm\" value = \"Confirm Reservation\"></form>"
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\confirmationModifying.html",'w')
    f.write("<html><p>"+string+"</p></html>")
    f.close()
    return send_file("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\confirmationModifying.html")   

@app.route("/confirmModifyingReservation", methods=["GET","POST"])
def confirmModifyingRes():
    res = session["modification"]
    inte=['1','2','3','4','5','6','7','8','9','0']
    n = len(res)
    j=0
    t=""
    for i in range(n):
        if res[i] not in inte:
            t+=res[i]
        else:
            j=i
            break
    ma = res[j:n]
    if res[0]=='s' and res[1]=='u':
        t="suitefor1"
        ma=res[len(t):n]
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()
    cur.execute("DELETE FROM "+t+" where id=\""""+ma+"""\"""")
    con.commit()
    sql = 'SELECT * from '+session["roomType"]
    cur.execute(sql)
    result = cur.fetchall()
    max = len(result)+1
    cur.execute('SELECT * from '+session["roomType"])
    result1 = cur.fetchall()
    y=int(max)
    for i in range(len(result1)):
        if(result1[i][0]==y):
            y+=1
    max=y
    session["startDate"] = datetime.date(int(session["newStartDate"][6:11]), int(session["newStartDate"][0:2]), int(session["newStartDate"][3:5]))
    session["endDate"] = datetime.date(int(session["newEndDate"][6:11]), int(session["newEndDate"][0:2]), int(session["newEndDate"][3:5]))
    print(session["roomType"])
    cur.execute("insert into "+session["roomType"]+" values(%s,%s,%s,%s,%s)",(max,session['email'],session["startDate"],session["endDate"],session["roomType"]))
    print("insert into "+session["roomType"]+" values(%s,%s,%s,%s,%s)",(max,session['email'],session["startDate"],session["endDate"],session["roomType"]))
    con.commit()
    cur.close()
    con.close()
    return render_template("profile.html",error_statement = "Reservation modified successfully")

@app.route("/modifyNumberRooms", methods=["GET","POST"])
def loadModifyRoomNumbers():
    return render_template("modifyAvailableRooms.html")

@app.route("/modifyRoomsCapacity", methods=["GET","POST"])
def modifyRoomNubers():
    output = request.form.to_dict()
    roomType = output["modifyRoomsCapacity"]
    action = output["submit"]
    if (action == "Increase Rooms"):
        l = "increased"
        roomCap = int(output["numberOfRooms"])
    elif (action == "Decrease Rooms"):
        l = "decreased"
        roomCap = -int(output["numberOfRooms"])
        if capacity[roomType]<-roomCap:
            return render_template("modifyAvailableRooms.html", update = "Number of rooms to be decreased is greater than  number of available rooms")
    capacity[roomType] += roomCap
    con=mysql.connector.connect(user='root',password='12345',host='localhost',database='website')
    cur=con.cursor()
    print("DELETE FROM roomsavailable where ('roomName' =\""""+roomType+"""\")""")
    cur.execute(cur.execute("UPDATE roomsavailable SET numOfRooms = %s WHERE roomName=%s",(capacity[roomType],roomType)))
    con.commit()
    update = str(capacity[roomType])+" from "+room[roomType]+" are now available"
    return render_template("adminsPage.html", update = update)
    
@app.route("/checkUsers", methods=["GET","POST"])
def loadCheckUsers():
    f = open("C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\checkAndModifyUsers.html",'w')
    
    return render_template("modifyAvailableRooms.html")


if __name__=='__main__':
    app.run(port = 80)
