#  coding: utf-8 
from logging.config import listen
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/




class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        validDir  = ["/", "deep"]
 
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data.decode("utf-8"))
        dataString = self.data.decode("utf-8")
        # in linux, new line is \n only so becareful
        # .splitlines() split regardless of newline type
        dataStrList = dataString.splitlines()  
        isFavicon = False
        # because they always senc favion request
        print(dataStrList[0])
        if "/favicon.ico" not in dataStrList[0]:
            # check the case for request for base.css
            if (".css" in dataStrList[0]):
                # we need the full path to  ....../base.css
                cssFileName = getPath(dataStrList[0])  # should return /base.css
                absPathOfCSS = getFullPath(cssFileName)
                respondingHeader = respondToCss(absPathOfCSS)

                self.request.sendall(bytearray(respondingHeader, 'utf-8'))
                return

            
            # Handle valid html file request like GET / or GET /deep/  
            # send index.html

            #print(dataStrList)
            #print("we got ", getPath(dataStrList[0]))
            print ("Got a request of: %s\n" % self.data)
            isFavicon = True
            localPath = getPath(dataStrList[0])  # this is / or /deep or /deep/

            ret = checkGETPath(localPath, dataStrList[0])
            if (ret != "OK dir path" and ret != "OK file path"):
                # then ret == one of 301 or 404 headers
                self.request.sendall(bytearray(ret, 'utf-8'))
                return
            elif (ret == "OK dir path"):
                # return index.html
                indexHtmlHeader =  returnIndexHtml(localPath)
                self.request.sendall(bytearray(indexHtmlHeader, 'utf-8'))
                return
            elif (ret == "OK file path"):
                # here, localpath = "/.../___.html"
                # open this 
                absPath = getFullPath(localPath)  # should work
                #:w
                header = returnHtmlfile(localPath)
                self.request.sendall(bytearray(header, 'utf-8'))
                return


            # if its OK dir path, we just return index html
            absPath = getFullPath(localPath)
            #print("abs path is ", absPath)

            status_code = 200
            reason_phrase = "OK"
            Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
            content_type = f'Content-Type: text/html; charset=UTF-8\r\n'

            # both equivalent

            localPath = getPath(dataStrList[0])
            absPath = getFullPath(localPath)
            msgContent = ""

            #TODO: instead of hardcoding index.html, we find whatever html file in that directory
            #  TODO: DO NOT HARDCODE INDEX.HTML AND HE MIGHT MAKE ANOTHER   
            htmlFileName = localPath.replace('/', '') + ".html"
            if (localPath == '/'):
                htmlFileName = "index.html"  
            #TODO: ANOTHER THING WE NEED TO do is find any html file in that directory
            with open(absPath + "index.html") as file:
                msgContent = file.read()
                #print(msgContent)

            l = len(msgContent.encode('utf-8'))
            msgLength = f'Content-Length: {str(l)}\r\n'
            ResponseHeader = f"{Status_Line}{content_type}{msgLength}\r\n{msgContent}"
            #print(ResponseHeader)
            # no I will get the file
            # append htmlcontent to the header

            self.request.sendall(bytearray(ResponseHeader, 'utf-8'))

        
        # manually build the response header()
        # use sendall for headers + file content
        #self.request.sendall(bytearray("OK",'utf-8'))
        # write("")



def checkGETPath(localPath, requestMsg):
    # TODO: check if the localPath file exist in the directory
    # Loop invariant: local path = /.....
    # 1. check if the /deep is a valid directory
    # 2. if not then check if this is a valid path to directory
    print("localpath", localPath)
    if ("GET" not in requestMsg):  # TODO: this should be at the very top
        return return405Header()
    print("in checkGET localpath is ", localPath)
    validPaths = {"/", "/deep/"}
    if (localPath[-1] != '/' and ".html" not in localPath):  # case: folder that  doesnt end with / 
        print()
        print("301 errorRRRRRRRRRRRR")
        print()  
        return return301Header(localPath)
    else:  # how to do it 
        print("not 301")
        # here local path is /../.html(check if html is valid) or /folder/(check if folder is valid) 
        if (".html" in localPath):  # check if this path to html file exist
            flag = os.path.exists(getFullPath(localPath)) 
            print()
            print("requestedPath exist? ", flag)
            print()
            if (flag):
                return "OK file path"
            return return404Header()  # case: path to .html file dont exist
        else:  # case requested path is /../folder/ to a valid folder format
            print()
            flag = os.path.exists(getFullPath(localPath))
            if (flag):  # this folder exist
                return "OK dir path"
            return return404Header()  # folder dont exist
    # else this path is fine
    return "OK path"
def returnHtmlfile(localPath: str):
    absPath = getFullPath(localPath)
    status_code = 200
    reason_phrase = "OK"
    Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
    content_type = f'Content-Type: text/html; charset=UTF-8\r\n'
    with open(absPath) as file:
        msgContent = file.read()
        #print(msgContent)
        l = len(msgContent.encode('utf-8'))
        msgLength = f'Content-Length: {str(l)}\r\n'
        ResponseHeader = f"{Status_Line}{content_type}{msgLength}\r\n{msgContent}"
        #print(ResponseHeader)
        # no I will get the file
        # append htmlcontent to the header
        return ResponseHeader

def returnIndexHtml(localPath: str):
    status_code = 200
    reason_phrase = "OK"
    Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
    content_type = f'Content-Type: text/html; charset=UTF-8\r\n'

    absPath = getFullPath(localPath)  # abs path neesd to be /.../folder/index.html
    with open(absPath + "index.html") as file:
        msgContent = file.read()
        #print(msgContent)

        l = len(msgContent.encode('utf-8'))
        msgLength = f'Content-Length: {str(l)}\r\n'
        ResponseHeader = f"{Status_Line}{content_type}{msgLength}\r\n{msgContent}"
        #print(ResponseHeader)
        # no I will get the file
        # append htmlcontent to the header

        return ResponseHeader 

def return301Header(localpath: str):
    #HTTP/1.1 301 Moved Permanently
    #Location: http://www.example.org/index.asp
    #location = "http://127.0.0.1:8080/deep/"  # TODO: this has to change
    location = "http://127.0.0.1:8080" + localpath + "/"  # add / to correct directory
    print("in 301, location is", location) 
    status_code = 301
    reason_phrase = "Moved Permanently"
    Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
    ResponseHeader = f"{Status_Line}Location: {location}\r\n"
    return ResponseHeader

def return404Header():
    status_code = 404
    reason_phrase = "Not Found"
    Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
    msg = "404 Not Found"
    l = len(msg.encode('utf-8'))
    msgLength = f'Content-Length: {str(l)}\r\n'
    ResponseHeader = f"{Status_Line}{msgLength}\r\n{msg}"
    print(ResponseHeader)
    return ResponseHeader

def return405Header():
    status_code = 405
    reason_phrase = "Method Not Allowed"
    Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
    msg = "405 Method Not Allowed"
    l = len(msg.encode('utf-8'))
    msgLength = f'Content-Length: {str(l)}\r\n'
    ResponseHeader = f"{Status_Line}{msgLength}\r\n{msg}"
    print(ResponseHeader)
    return ResponseHeader
"""
given absolute path to css filename   : ...../base.css for example


"""
def respondToCss(absPathOfCss):
    # make the response header?
    # open the file
    # absPathOfCss = ....../base.css
    status_code = 200
    reason_phrase = "OK"
    Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
    content_type = f'Content-Type: text/css; charset=UTF-8\r\n'
    cssContent = ""
    with open(absPathOfCss) as file:
        cssContent = file.read()

    l = len(cssContent.encode('utf-8'))
    msgLength = f'Content-Length: {str(l)}\r\n'
    ResponseHeader = f"{Status_Line}{content_type}{msgLength}\r\n{cssContent}"
    # the sigh
    
    #print("Response Hearing ", ResponseHeader)
    return ResponseHeader

"""
parse the request header to get the path
"""
def getPath(requestStr: str) -> str:
    # given "GET /deep/ Http...." return /deep/
    listForm = requestStr.split(" ")
    a = listForm[1]
    return a

"""
using the path we got from getPath, we get abspath
"""
def getFullPath(localPath: str) -> str:
    # note we gotta check if the local path is valid
    # like /deep is bad /deep/ is good 
    # maybe have the check in another function
    currentDir = os.getcwd()
    absPath = currentDir + "/www" + localPath
    return absPath




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    
    
    """
    listen()
    accpet()
    recv()




    Q1: 
    while():
        recv()

    Q2:

    """

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
