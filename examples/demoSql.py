import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "7605",
    database = "testdatabase"
    )
   
mycursor = db.cursor()

#mycursor.execute("CREATE TABLE Person (name VARCHAR(50), age smallint UNSIGNED, personID int PRIMARY KEY AUTO_INCREMENT)")


mycursor.execute("INSERT INTO PERSON (name, age) VALUES (%s,%s)", ("Joe", 22))
db.commit()

mycursor.execute("SELECT * FROM Person")


for x in mycursor:
   print(x)