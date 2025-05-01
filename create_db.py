import sqlite3 as sql

#connect to SQLite
con = sql.connect('db_web.db')

#Create a Connection
cur = con.cursor()

#Drop users table if already exsist.
cur.execute("DROP TABLE IF EXISTS colleges")

#Create colleges table  in db_web database
sql ='''CREATE TABLE "colleges" (
	"CID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"CNAME"	TEXT,
        "DNAME"	TEXT,
        "IMAGE"	TEXT,
        "SUMMARY" TEXT,
	"CONTACT"	TEXT
)'''
cur.execute(sql)

#commit changes
con.commit()

#close the connection
con.close()