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
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data.decode("utf-8"))
        dataString = self.data.decode("utf-8")
        # in linux, new line is \n only so becareful
        # .splitlines() split regardless of newline type
        dataStrList = dataString.splitlines()  
        isFavicon = False
        # because they always senc favion request
        if "/favicon.ico" not in dataStrList[0]:
            #print(dataStrList)
            #print("we got ", getPath(dataStrList[0]))
            print ("Got a request of: %s\n" % self.data)
            isFavicon = True
            localPath = getPath(dataStrList[0])
            absPath = getFullPath(localPath)
            print("abs path is ", absPath)

            status_code = 200
            reason_phrase = "OK"
            Status_Line = f'HTTP/1.1 {str(status_code)} {reason_phrase}\r\n'
            content_type = f'Content-Type: text/html; charset=UTF-8\r\n'
            ResponseHeader = f""

            # both equivalent

            localPath = getPath(dataStrList[0])
            absPath = getFullPath(localPath)
            fullFile = ""

            
            with open(absPath + "index.html") as file:
                fullFile = file.read()
                print(fullFile)
            # no I will get the file

        
        # manually build the response header()
        # use sendall for headers + file content
        self.request.sendall(bytearray("OK",'utf-8'))
        # write("")
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
