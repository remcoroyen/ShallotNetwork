import threading
import socket 
import select

import Shallot_KeyChain
import Shallot_ReadConfigFile
import Shallot_Messages
import Shallot_DiffieHellman
import Shallot_Dijkstra

class shallot_Client(threading.Thread):
    
    def __init__(self,hostfilepath,topologyfilepath,hostname):
        self.hostname = hostname
        self.listenKeychain = Shallot_KeyChain.shallot_KeyChain()
        self.IPs,self.Ports,self.Neighbours = Shallot_ReadConfigFile.shallot_readConfigTopologyini(topologyfilepath);
        self.hostIP, self.hostPort = Shallot_ReadConfigFile.shallot_readConfigHostData(hostfilepath, self.hostname);
        self.listensock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listensock.bind((self.hostIP,self.hostPort))
        self.listensock.listen(1)
        self.isRunning = True;
        threading.Thread.__init__(self)
        
    def run(self):
        #==========================================================
        # To Receive messages   (This is all needed for Bob)
        while(self.isRunning):
            timeout = 1
            readable,writable,exceptional = select.select([self.listensock],[],[],timeout) 
            for sockread in readable:             
                conn,addr = sockread.accept()
                msg_version,msg_type,msg_length = Shallot_Messages.shallot_recvHeader(conn)
                
                if not(msg_version==1 and  msg_type>=0 and msg_type<=3):                # If the format of the header is wrong, generate and send error message
                    Shallot_Messages.shallot_sendErrorMessage(conn,0)
                    
                elif msg_type == 0:                                                     # A KEY_INIT message has been received, calculate key and send KEY_REPLY message
                    keyID,g,p,A = Shallot_Messages.shallot_recvKeyInit(conn,msg_length)
                    if self.listenKeychain.hasKey(keyID):
                        Shallot_Messages.shallot_sendErrorMessage(conn,1)
                    else:
                        b = Shallot_KeyChain.randomInt(1024)
                        B = pow(g,b,p) 
                        s = pow(A,b,p)
                        self.listenKeychain.newKey(s,keyID)  
                        Shallot_Messages.shallot_sendKeyReply(conn,keyID,B)
                    
                elif msg_type == 1:                                                     # A KEY_REPLY message has been received, generate key for commuication with relay
                    print("You are not supposed to receive these messages here")
                    
                elif msg_type == 2:                                                     # A Relay_Message has been received, decrypt, generate new header and send to next relay
                    nextHop,nextHopPort,message_received_bytes = Shallot_Messages.shallot_recvMessageRelay(conn,msg_length,self.listenKeychain)
                    if nextHop == None and message_received_bytes == None:
                        error_code = 1
                        Shallot_Messages.shallot_sendErrorMessage(conn,error_code)
                        print("Key not found\n An error message has been sent (INVALID_KEY_ID)")
                        conn.close()    #because of the continue
                        continue
                    if nextHop == self.hostIP:
                        message_received = message_received_bytes.decode()
                        print(self.hostname+" received: "+message_received)
                    else:
                        print("Error: "+self.hostname+" is not final destination")
                    
                elif msg_type == 3:                                                     # An error message has been received. No idea yet what to do then
                    error_code = Shallot_Messages.shallot_recvErrorMessage(conn,msg_length)
                    if error_code == 0: print("an error message arrived: INVALID_MESSAGE_FORMAT") 
                    if error_code == 1: print("an error message arrived: INVALID_KEY_ID")
                    else: print("an error message arrived: UNKNOWN")
                    
                conn.close()   
        #==========================================================
        #executed upon closing the thread 
        self.listensock.close()
        print("closed client "+self.hostname)
        
    def close(self):
        self.isRunning = False
    
    def sendMessage(self,message,recipient):
    #==========================================================
    # Executed to send a message  (This is all needed for Alice)
        message_bytes = str.encode(message)
    
        print("Computing path...")
        source = [self.hostIP, self.hostPort]
        destination = [recipient.hostIP, recipient.hostPort]
        pathlist = Shallot_Dijkstra.shallot_RandomDijkstra(source,destination,self.IPs,self.Ports,self.Neighbours)        # pathlist nested list of this form: [[recipient.hostIP,recipient.hostPort]] (in reversed order!)
        print("Path found:")
        print(list(reversed(pathlist)))

        onionKeychain = Shallot_KeyChain.shallot_KeyChain();
        Shallot_DiffieHellman.shallot_DiffieHellmanKeyExchange(pathlist,onionKeychain)
        print("Keys exchanged")
        payload = Shallot_Messages.shallot_createOnion(message_bytes,pathlist,onionKeychain)
        onionKeychain.clear()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock.connect((pathlist[-1][0],pathlist[-1][1]))    
        Shallot_Messages.shallot_sendall(sock,payload)
        sock.close()
    
        print(self.hostname+" sent: "+message)
    #==========================================================
    