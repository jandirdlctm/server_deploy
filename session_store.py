#TODO:
#need a dictionary( of dictionaries)
# add a new session to the session store
# retrieve an existing session from the session store
# we need to create a new sesssion ID
import os, base64

class SessionStores:
    #need a dictionary( of dictionaries)
    def __init__(self):
        self.sessions = {}

    # add a new session to the session store
    def createSession(self):
        sessionId = self.generateSessionId()
        self.sessions[sessionId] = {} #dictionary in a dictionary 
        return sessionId
    
    # retrieve an existing session from the session store
    def getSession(self, sessionId):
        if sessionId in self.sessions:
            return self.sessions[sessionId]
        else:
            return None
    # we need to create a new sesssion ID
    def generateSessionId(self):
        rnum = os.urandom(32) #random library to produce random data
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

