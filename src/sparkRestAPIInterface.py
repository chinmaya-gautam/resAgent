import urllib2
#from wbxtf.WBXTFLogex import *
import json

class sparkRestAPI:

    def __init__(self):
        pass

    def getRequest(self, requestURL):
        try:
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(
                url= requestURL,
            )
            request.get_method = lambda: "GET"
            response = opener.open(request)
            # WBXTFLogDebug("getRequest response=\n%s" % response)
            return response
        except urllib2.HTTPError:
            #WBXTFLogInfo("Server responded with 404")
            return None
        except Exception, e:
            #WBXTFLogError("getRequest:%s exception=%s" % (requestURL ,e))
            return None

    def postRequest(self, requestURL, requestData):
        try:
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(
                url=requestURL,
                data=requestData,
                headers={"Content-Type": "application/json", }
            )
            request.get_method = lambda: "POST"
            response = opener.open(request)
            return response
        except Exception, e:
            #WBXTFLogError("postRequest:%s postData:%s exception=%s" % (requestURL,requestData,e))
            return None

    def isAlive(self, ip):

        try:
            requestURL = "http://%s:8000/isalive" % ip
            ret = self.getRequest(requestURL)
            if ret == None:
                return False
            if ret.code == 200:
                return True
        except Exception as e:
            #WBXTFLogError("Exception checking if spark is running: %s" % str(e))
            return False

    def isLoggedIn(self, ip):
        try:
            requestURL = "http://%s:8000/isloggedin" % ip
            ret = self.getRequest(requestURL)
            if ret.code == 204:
                return False
            elif ret.code == 200:
                return True
            else:
                #WBXTFLogWarning("Unknown return code %s, assuming not logged in" % ret.code)
                return False

        except Exception as e:
            #WBXTFLogError("Exception checking if spark is logged in : %s" % str(e))
            return False

    def loggedInUser(self, ip):
        try:
            requestURL = "http://%s:8000/loggedinuser" % ip
            ret = self.getRequest(requestURL)
            if ret.code == 204:
                return "Not logged in"
            elif ret.code == 200:
                body= json.loads(ret.read())
                return body['email']
            else:
                #WBXTFLogWarning("Unknown return code %s" % ret.code)
                return "NA"

        except Exception as e:
           # WBXTFLogError("Exception retrieving logged in user : %s" % str(e))
            return "NA"

    def pairedDeviceID(self, ip):
        try:
            requestURL = "http://%s:8000/paireddeviceid" % ip
            ret = self.getRequest(requestURL)
            if ret == None:
                return "Not Paired"
            if ret.code == 404:
                return "Not Paired"
            elif ret.code == 200:
                body = json.loads(ret.read())
                return body['id']
            else:
                #WBXTFLogWarning("Unknown return code %s" % ret.code)
                return "NA"

        except Exception as e:
            #WBXTFLogError("Exception retrieving paired device ID : %s" % str(e))
            return "NA"

    def callState(self, ip):
        try:
            requestURL = "http://%s:8000/callstate" % ip
            ret = self.getRequest(requestURL)
            if ret.code == 200:
                body= ret.read()
                return (body.split('.')[1].strip('"')).upper()
            else:
                #WBXTFLogWarning("Unknown return code %s" % ret.code)
                return "NA"

        except Exception as e:
           # WBXTFLogError("Exception retrieving call state : %s" % str(e))
            return "NA"

    def isInLobby(self, ip):
        try:
            requestURL = "http://%s:8000/isinlobby" % ip
            ret = self.getRequest(requestURL)
            if ret == None:
                return False
            if ret.code == 204:
                return False
            if ret.code == 200:
                return True
        except Exception as e:
            #WBXTFLogError("Exception checking if call is in lobby or not: %s" % str(e))
            return False

    def applicationVersion(self, ip):
        try:
            requestURL = "http://%s:8000/applicationversion" % ip
            ret = self.getRequest(requestURL)
            if ret.code == 200:
                body= ret.read()
                return body
            else:
                #WBXTFLogWarning("Unknown return code %s" % ret.code)
                return "NA"

        except Exception as e:
           # WBXTFLogError("Exception retrieving call state : %s" % str(e))
            return "NA"

    def mediaStats(self, ip):
        try:
            requestURL = "http://%s:8000/mediastats" % ip
            ret = self.getRequest(requestURL)
            if ret.code == 200:
                body = ret.read()
                stats = json.loads(body)
                if not stats:
                    stats = {}   # This is for the case when there are no media stats available
                return stats
            else:
                #WBXTFLogWarning("Unknown return code %s" % ret.code)
                return {}

        except Exception as e:
           # WBXTFLogError("Exception retrieving call state : %s" % str(e))
            return {}

    def packetStats(self, ip):
        try:
            requestURL = "http://%s:8000/packetstats" % ip
            ret = self.getRequest(requestURL)
            if ret.code == 200:
                body = ret.read()
                stats = json.loads(body)
                if not stats:
                    stats = {} # This is for the case when there are no packet stats available
                return stats
            else:
                # WBXTFLogWarning("Unknown return code %s" % ret.code)
                return {}

        except Exception as e:
            # WBXTFLogError("Exception retrieving call state : %s" % str(e))
            return {}
