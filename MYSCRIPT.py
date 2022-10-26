names=[]
import cgi
form = cgi.FieldStorage() 

# prints the value of <input name='name'/> 
print("Name in form: ",form.getvalue("fname")) 
while (True):
    name=form.getvalue("fname")
    if str(name)!="None":
        print(name)
        break
    

f = open("myfile.txt", "w")


