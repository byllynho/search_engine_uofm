#!/usr/bin/python

print ("Content-type:text/html\n\n")
print ("<html>")
print ("<head>")
print ("<title>Memphis Search</title>")
print("<div><h1 align='center' style='padding-top:5%'>Memphis Search</h1></div>")
print ("</head>")
print ("<body>")
print("<form action='search.py' method='post'>")
print("<div style='text-align:center'><input type='text' style ='corner-radius:5px;height:50px' name='searchQuery' size='100' placeholder='What would you like to search?'></div>")
print("<div style='text-align:center'><input type='submit' style ='height:36px;color:blue;background-color:lightgrey;font-size:16px' name='search' value='Search'/></div>")
print("</form>")
