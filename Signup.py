import cgi

form = cgi.FieldStorage()

firstname=form.getvalue("fname")

print(firstname)