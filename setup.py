import mysql.connector

def createDatabase(username,password,host):
    con=mysql.connector.connect(user=username,password=password,host=host)
    cur = con.cursor()
    cur.execute("CREATE DATABASE website")
    con.commit()
    cur.close()
    con.close()
    return 0

def createTables(username,password,host):
    con=mysql.connector.connect(user=username,password=password,host=host,database='website')
    cur = con.cursor()
    cur.execute('''CREATE TABLE `doubleroom` (
  `id` int NOT NULL,
  `email` varchar(45) NOT NULL,
  `startDate` date NOT NULL,
  `endDate` date NOT NULL,
  `roomType` varchar(45) DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
''')
    cur.execute('''CREATE TABLE `doublesuite` (
  `id` int NOT NULL,
  `email` varchar(45) NOT NULL,
  `startDate` date NOT NULL,
  `endDate` date NOT NULL,
  `roomType` varchar(45) DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
''')
    cur.execute('''CREATE TABLE `roomsavailable` (
  `roomName` varchar(45) NOT NULL,
  `numOfRooms` int DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`roomName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
''')
    cur.execute('''CREATE TABLE `singleroom` (
  `id` int NOT NULL,
  `email` varchar(45) NOT NULL,
  `startDate` date NOT NULL,
  `endDate` date NOT NULL,
  `roomType` varchar(45) DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
''')
    cur.execute('''CREATE TABLE `suitefor1` (
  `id` int NOT NULL,
  `email` varchar(45) NOT NULL,
  `startDate` date NOT NULL,
  `endDate` date NOT NULL,
  `roomType` varchar(45) DEFAULT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
''')
    cur.execute('''CREATE TABLE `user` (
  `email` varchar(45) NOT NULL,
  `firstName` varchar(45) NOT NULL,
  `lastName` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`email`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
''')
    con.commit()
    cur.close()
    con.close()

def fillRoomsAvailable(username,password,host):
    con=mysql.connector.connect(user=username,password=password,host=host,database='website')
    cur = con.cursor()
    cur.execute("INSERT INTO roomsavailable VALUES (%s,%s,%s)",('singleroom', '1', '1'))
    cur.execute("INSERT INTO roomsavailable VALUES (%s,%s,%s)",('doubleroom', '1', '1'))
    cur.execute("INSERT INTO roomsavailable VALUES (%s,%s,%s)",('suitefor1', '1', '1'))
    cur.execute("INSERT INTO roomsavailable VALUES (%s,%s,%s)",('doublesuite', '1', '1'))
    con.commit()
    cur.close()
    con.close()

    
username="root"
password="12345"
host = "localhost"
createDatabase(username,password,host)
createTables(username,password,host)
fillRoomsAvailable(username,password,host)
