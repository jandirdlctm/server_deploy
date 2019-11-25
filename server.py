from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from urllib.parse import urlparse, parse_qs
import json
from classes_db import ClassesDB
from http import cookies
from passlib.hash import bcrypt
from session_store import SessionStores


SESSION_STORE = SessionStores()

class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_cookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")

        BaseHTTPRequestHandler.end_headers(self)



    #goal: load cookie into self.cookie
    def load_cookie(self):
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()


    def send_cookie(self):
        for morsel in self.cookie.values():
            self.send_header("set-cookie", morsel.OutputString())

    #goal: load session into self.session
    def load_session(self):
        self.load_cookie()
        #if session ID in the cookie
        if "sessionId" in self.cookie:
            
            sessionId = self.cookie["sessionId"].value
             #if session ID exists in the session store.
                    #save the session for use later.(data_member)
            self.session = SESSION_STORE.getSession(sessionId)
            #otherwise, if session ID not in the session store
            if self.session == None:
                #create new session
                sessionId = SESSION_STORE.createSession()
                self.session = SESSION_STORE.getSession(sessionId)
                 #set the new session ID into the cookie.
                self.cookie["sessionId"] = sessionId
        #otherwise if session ID is NOT in the cookie
        else:
            sessionId = SESSION_STORE.createSession()
            self.session = SESSION_STORE.getSession(sessionId)
            self.cookie["sessionId"] = sessionId



        #either load session data based on session ID in cookie

        #OR  create a new session and session ID and cookie.
        #SUDO CODE.
        #1. if session ID in the cookie.
                #if session ID exists in the session store.
                    #save the session for use later.(data_member)
                #otherwise, if session ID not in the session store
                    #create a new session
                    #set the new session ID into the cookie.

            #otherwise, if session Id is NOT in the cookie.
                #create a new session
                #set the new session ID into the cookie.



    def handleNotFound(self):
        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("The class was not Found", "utf-8"))


    def do_OPTIONS(self):
        self.load_session()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, DELETE, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


    def loggedIn(self):
        if "userId" in self.session:
            return True
        else:
            return False



    def handleClassList(self):
        if self.loggedIn():
            self.send_response(200)
            #headers
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            db = ClassesDB()
            classes = db.getAllClasses()
            self.wfile.write(bytes(json.dumps(classes), "utf-8"))
        else:
            self.handle401()


    def handleClassCreate(self):
        
        if self.loggedIn():
            length = self.headers["Content-length"]
            body = self.rfile.read(int(length)).decode("utf-8")
            print("The text body:", body)
            parsed_body = parse_qs(body)
            print("the parsed body:", parsed_body)

            #saving the class
            clas = parsed_body["clas"][0]
            major = parsed_body["major"][0]
            professor = parsed_body["professor"][0]
            location = parsed_body["location"][0]
            rating = parsed_body["rating"][0]

        #sending the values to the data base
            db = ClassesDB()
            db.createClass(clas, major, professor, location, rating)

            self.send_response(201)
            self.end_headers()
        else:
            self.handle401()

    def handleClassDelete(self,id):
        #if "userdId" not in self.session:
         #   self.send_response(401)
          #  return
            #return
        #if the user is not logged in:
         #   self.handle401()
          #  return
        if self.loggedIn():
            db = ClassesDB()
            clas = db.getClass(id)

            if clas == None:
                self.handleNotFound()
            else:
                self.send_response(200)
                #headers
                self.send_header("Content-type", "application/json")
                self.end_headers()

                db.deleteClass(id)
                self.wfile.write(bytes(json.dumps(clas), "utf-8"))
        else:
            self.handle401()

    def handleClassRetrieve(self, id):
        db = ClassesDB()
        clas = db.getClass(id)

        if clas == None:
            self.handleNotFound()
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(clas), "utf-8"))


    def handleClassUpdate(self):
        parts = self.path.split("/")
        class_id = parts[2]
        db = ClassesDB()
        clas = db.getClass(class_id)

        if clas != None:

            #responding to the client
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            #self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(clas), "utf-8"))

            length = self.headers["Content-length"]

            #reading the body to a string
            body = self.rfile.read(int(length)).decode("utf-8")
            print("Body: ", body)

            #print the body as a string

            parsed_body = parse_qs(body)
            print("parsed body", parsed_body)

            clas = parsed_body["clas"][0]
            major = parsed_body["major"][0]
            professor = parsed_body["professor"][0]
            location = parsed_body["location"][0]
            rating = parsed_body["rating"][0]
            db.updateClass(clas,major,professor,location,rating,class_id)

            self.send_response(200)
            #self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
        else:
            self.handleNotFound()




    def do_DELETE(self):
        self.load_session()
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "classes":
            if id == None:
                self.handleClassList()
            else:
                self.handleClassDelete(id)

        else:
            self.handleNotFound()

    def do_GET(self):
        self.load_session()
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "classes":
            if id == None:
                self.handleClassList()
            else:
                self.handleClassRetrieve(id)

        else:
            self.handleNotFound()

    def do_POST(self):
        self.load_session()
        #create action
        path = self.path.split('?')
        print(path[0])
        print("Path: ", self.path)
        if path[0] == "/classes":
            self.handleClassCreate()
        elif path[0] == "/users":
            self.handleUserCreate()
        elif path[0] == "/sessions":
            self.handleSessionCreate()

        else:
            self.handleNotFound()

    def do_PUT(self):
        self.load_session()
        if self.path.split('/')[1:]:
            self.handleClassUpdate()
        else:
            self.handleNotFound()


    def handleSessionCreate(self):
        length = self.headers["Content-length"] #gets the length
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        print("this is the parsed body: ", parsed_body)
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]

        db = ClassesDB()
        user = db.getUserByEmail(email) #getting the user by its email
        #checking if the email exists
        if user == False:
            self.handle401()

        else:
            encrypass = db.getPassword(email) #encrypting the password
            if bcrypt.verify(password, encrypass): 
                self.session["userId"] = email
                self.send_response(201)
                self.end_headers()
                self.wfile.write(bytes("Created", "utf-8"))

            else:
                self.handle401()
                self.wfile.write(bytes("Invalid login info", "utf-8"))


    def handleUserCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        print("This is the parsed body: ", parsed_body)

        #saving the user

        firstName = parsed_body["fname"][0]
        lastName = parsed_body["lname"][0]
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]

        #password encrypt

        encryptedPassword = bcrypt.hash(password)

        db = ClassesDB()

        user = db.getUserByEmail(email)

        #checking if user exists

        print("Checking prior to see if user exists")
        if user == False:
            db.createUser(firstName, lastName, email, encryptedPassword)
            self.send_response(201)
            self.end_headers()
            self.wfile.write(bytes("User created", "utf-8"))
        else:
            self.send_response(422)
            self.end_headers()
            self.wfile.write(bytes("Email already exists", "utf-8"))

    def handle401(self):
        self.send_response(401)
        self.end_headers()
    





    


def run():
    db = ClassesDB()
    db.createClassTable()
    db.createUsersTable()
    db = None #disconnect

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)

    print("Server listening on", "{}:{}".format(*listen))
    server.serve_forever() 





    #listen = ('localhost', 8080)
    #server = HTTPServer(listen, MyRequestHandler)

    #print("Listening...")
    #server.serve_forever()

run()
