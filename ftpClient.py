#client.py

import socket
import math
import sys
import time

class FTPclient:
    def __init__(self, serverIPname, serverIPport):

        self.IPsocket = None
        self.DTPsocket = None
        self.errorResp = False
        self.alive = False
        self.loggedIn = False
        self.user = None
        self.serverIPname = serverIPname
        self.serverIPport = serverIPport
        
    def initConnection(self):

        self.IPsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        try:

            self.IPsocket.connect((self.serverIPname,self.serverIPport))
            print(self.IPsocket.recv(1024).decode())
            
        except:

            errMSG = 'Failed to connect ' + self.serverIPname
            print(errMSG)
            self.errorResp = True
            time.sleep(3)
            return

        self.alive = True
        print('Connected to server :)')
    
    def login(self, userName, password):
        
        # enter username
        cmd = 'USER ' + userName
        self.send(cmd)
        self.printServerReply(self.getServerReply())
        
        if not self.errorResp:
            # enter password
            cmd = 'PASS ' + password
            self.send(cmd)
            self.printServerReply(self.getServerReply())

            if not self.errorResp:
                self.loggedIn = True
                self.user = userName
                print('Login Success\n')

                
    def send(self, cmd):

        self.IPsocket.send((cmd + '\r\n').encode())
        print('Client: ', cmd)

    def getServerReply(self):
        
        resp = self.IPsocket.recv(1024).decode()
        
        # Notify if this an error
        if resp[0] != '5' and resp[0] != '4':
            self.errorResp = False
        else:
            self.errorResp = True
        return resp
    
    def printServerReply(self,resp):
        print('Server :', resp)

    def startPassiveDTPconnection(self):
        
        #Ask for a passive connection
        cmd = 'PASV'
        self.send(cmd)
        resp = self.getServerReply()
        self.printServerReply(resp)

        if not self.errorResp:
            
            firstIndex = resp.find('(')
            endIndex  = resp.find(')')
            
            # Obtain the server DTP address and Port
            addr = resp[firstIndex+1:endIndex].split(',')
            self.serverDTPname = '.'.join(addr[:-2])
            self.serverDTPport = (int(addr[4])<<8) + int(addr[5])
            print(self.serverDTPname,self.serverDTPport)

            try:
                #Connect to the server DTP
                self.DTPsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.DTPsocket.connect((self.serverDTPname,self.serverDTPport))
                print('Passive Connection Success, Ready to receive\n')
                self.dataConnectionAlive = True

            except:

                print('Failed to connect to ', self.serverDTPname)
                self.dataConnectionAlive = False
                time.sleep(3)
                return
    
    def getList(self):
         
        # Cant't get list if disconnected
        if self.dataConnectionAlive and self.alive:

            cmd = 'LIST'
            self.send(cmd)
            self.printServerReply(self.getServerReply)

            print('\nReceiving Data\n')

            while True:
                # Get the directory list
                data = self.DTPsocket.recv(1024)
                print(data.decode())

                if not data:
                    break
           
            print('Downloading done\n')
            self.printServerReply(self.getServerReply)


def Main():
    
    # Testing ftp servers
    Po = [21,12000,21,21,12005]
    S  = ['speedtest.tele2.net', 'localhost','test.rebex.net','dlptest.com','localhost']
    U  = ['anonymous','Elias','demo','dlpuser@dlptest.com','tokelo']
    Pa = ['anonymous','aswedeal', 'password','5p2tvn92R0di8FdiLCfzeeT0b','1234']

    server = 1
    serverIP = Po[server]
    serverName = S[server]
    userName =  U[server]
    password = Pa[server]
    client = FTPclient(serverName,serverIP)
    client.initConnection()
    client.login(userName, password)
    client.startPassiveDTPconnection()
    client.getList()
    
Main()