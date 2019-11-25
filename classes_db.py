#import sqlite3
import os
import psycopg2
import psycopg2.extras
import urllib.parse


#def dict_factory(cursor, row):
 #   d = {}
  #  for idx, col in enumerate(cursor.description):
   #     d[col[0]] = row[idx]
    #return d

class ClassesDB:
    def __init__(self):
        #self.connection = sqlite3.connect("classes_db.db")
        #self.connection.row_factory = dict_factory
        #self.cursor = self.connection.cursor()
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        
        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )    

        self.cursor = self.connection.cursor()




    def _del_(self):
        self.connection.close()

    def createClassTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS classes (id SERIAL PRIMARY KEY, clas TEXT, major TEXT, professor TEXT, location TEXT, rating INTEGER)")
        self.connection.commit()

    def createUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, fname TEXT, lname TEXT, email TEXT, password TEXT)")
        self.connection.commit()



    def createClass(self, clas, major, professor, location, rating):
        sql = "INSERT INTO classes (clas, major, professor, location, rating) VALUES (%s,%s,%s,%s,%s)"
        self.cursor.execute(sql, [clas, major, professor, location, rating])
        self.connection.commit()
        return None

    def getAllClasses(self):
        self.cursor.execute("SELECT * FROM classes ORDER BY id")
        return self.cursor.fetchall()

    def getClass(self, id):
        sql = "SELECT * FROM classes WHERE id = %s"
        self.cursor.execute(sql, [id])
        return self.cursor.fetchone()

    def deleteClass(self, id):
        sql = "DELETE FROM classes WHERE id = %s"
        self.cursor.execute(sql, [id])
        self.connection.commit()
        return None

    def updateClass(self, clas, major, professor, location, rating, id ):
        sql = "UPDATE classes SET clas = %s, major = %s, professor = %s, location = %s, rating = %s WHERE id = %s"
        self.cursor.execute(sql, [clas, major, professor, location, rating, id])
        self.connection.commit()
        return None
    
    def createUser(self, fname, lname, email, password):
        sql = "INSERT INTO users (fname, lname, email, password) VALUES (%s,%s,%s,%s)"
        self.cursor.execute(sql, [fname, lname, email, password])
        self.connection.commit()
        return None
  
    def getUserByEmail(self,email):
        sql = "SELECT email FROM users WHERE email = %s"
        self.cursor.execute(sql, [email])
        row = self.cursor.fetchone()
        try:
            if row['email'] == email:
                return True
            else:
                return False
        except:
            return False
       

    def getPassword(self, email):
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = self.cursor.fetchall()
        return row[0]['password']




