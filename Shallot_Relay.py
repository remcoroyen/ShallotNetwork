import threading
import socket 
import select

import Shallot_KeyChain
import Shallot_ReadConfigFile
import Shallot_Messages

class shallot_Relay(threading.Thread):
    
    def __init__(self,hostfilepath,hostname):
        self.hostname = hostname
        self.listenKeychain = Shallot_KeyChain.shallot_KeyChain()
        self.hostIP, self.hostPort = Shallot_ReadConfigFile.shallot_readConfigHostData(hostfilepath, self.hostname);
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			# listenSocket = socket that listens for incoming requests
        self.listenSocket.bind((self.hostIP,self.hostPort))
        self.listenSocket.listen(1)
        self.isRunning = True;
        threading.Thread.__init__(self)
        
    def run(self):
        #==========================================================
        while(self.isRunning):
            timeout = 1
            readable,writable,exceptional = select.select([self.listenSocket],[],[],timeout) 
            for sockread in readable:              
                conn,addr = sockread.accept()
                msg_version,msg_type,msg_length = Shallot_Messages.shallot_recvHeader(conn)
                
                if not(msg_version==1 and  msg_type>=0 and msg_type<=3):                # If the format of the header is wrong, generate and send error message
                    Shallot_Messages.shallot_sendErrorMessage(conn,0)
                    
                elif msg_type == 0:                                                     # A KEY_INIT message has been received, calculate key and send KEY_REPLY message
                    keyID,g,p,A = Shallot_Messages.shallot_recvKeyInit(conn,msg_length)
                    if self.listenKeychain.hasKey(keyID):										# KeyID already in use
                        Shallot_Messages.shallot_sendErrorMessage(conn,1)
                    else:																# Apply Diffie-Helmann
                        b = Shallot_KeyChain.randomInt(1024)
                        B = pow(g,b,p) 
                        key = pow(A,b,p)
                        self.listenKeychain.newKey(key,keyID)  
                        Shallot_Messages.shallot_sendKeyReply(conn,keyID,B)
                    
                elif msg_type == 1:                                                     # A KEY_REPLY message has been received, generate key for commuication with relay
                    print("Relays arent supposed to receive these messages")
                    
                elif msg_type == 2:                                                     # A Relay_Message has been received, decrypt, generate new header and send to next relay
                    
                    nextHopIP,nextHopPort,payload = Shallot_Messages.shallot_recvMessageRelay(conn,msg_length,self.listenKeychain)
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                    sock.connect((nextHopIP,nextHopPort))    
                    Shallot_Messages.shallot_sendall(sock,payload)
                    sock.close()
                    
                    print("Message relayed")
                    
                elif msg_type == 3:                                                     # An error message has been received. No idea yet what to do then
                    error_code = Shallot_Messages.shallot_recvErrorMessage(conn,msg_length)
                    if error_code == 0: print("an error message arrived: INVALID_MESSAGE_FORMAT") 
                    if error_code == 1: print("an error message arrived: INVALID_KEY_ID")
                    else: print("an error message arrived: UNKNOWN")
                    
                conn.close()               
        #==========================================================
        #executed upon closing the thread 
        self.listenSocket.close()
        print("closed relay")
        
    def close(self):
        self.isRunning = False