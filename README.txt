In order to run server.py, first, download MySQL and set it up. Set the username as "root", host as the "localhost" and password as "12345". 
Once done, open setup.py and run it to create all tables needed and the database. 

Once done with the setup.py, open the server.py. Note that you need to modify all values with open and send_file to include the correct paths.
Thus, modify lines: 282, 289, 296, 303, 325, 329, 419, 425, 430, 544, 553, 558, 636, 640, 759, 766, 773, 780, 799, 803, 905, 925, 947, 949, 1006, 1009, 1082, 1088 and 1092.
Note that when modifying the path, you take the path to the folder template and insert it before the name of the html file.
(i.e. change C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\ from 
C:\\Users\\Sharaf\\Desktop\\AUB\\FALL_22_23\\EECE_351\\351-Project\\templates\\getReservationsInDateRange.html).
Note that you need to put double \\ instead of 1 for python to read it as 1 \.

Once done with modifying send_file and open, run server.py. Running the server.py file will allow you to use the website directly. 
Open any browser of your choice and enter http://127.0.0.1:80/. Note that the website will be running on port 80.
Once you open the browser and enter the above IP and port, you will be able to use the website's functionality. 
First, log in to admin through pressing Log in, entering admin as email and admin as password.
Once you enter the admin page, you can change the availability of rooms, their prices, and change the admin's password.