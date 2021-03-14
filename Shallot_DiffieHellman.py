import socket 
import Shallot_KeyChain
import Shallot_Messages
import select

def shallot_DiffieHellmanKeyExchange(pathList,keychain):                # pathlist: list of lists (nested) of ip's and corresponding port of subsequent relays
    keyIDlist = []
    socketsToRead = []
    socketsToWrite = []
    aList = [] 
    pList = []
    AList = []
    tempKeyIDList = []
    for node in pathList:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        sock.connect((node[0],node[1]))
        socketsToRead.append(sock)
        socketsToWrite.append(sock)
    timeout = 1
    g = 2
    for sock in socketsToWrite: 
        p = Shallot_KeyChain.randomPrime(1024)
        a = Shallot_KeyChain.randomInt(1024);
        A = pow(g,a,p)        
        aList.append(a)
        pList.append(p)
        AList.append(A)
        while True:  
            keyID = Shallot_KeyChain.randomInt(32) 
            if not keychain.hasKey(keyID): break
        Shallot_Messages.shallot_sendKeyInit(sock,keyID,g,p,A)
        tempKeyIDList.append(keyID)
    while len(keyIDlist)<len(socketsToRead) :
        readable,writable,exceptional = select.select(socketsToRead,socketsToWrite,[],timeout)    
        for sockindex in range(0,len(writable)):
            sock = writable[sockindex]
            msg_version,msg_type,msg_length = Shallot_Messages.shallot_recvHeader(sock)
            if not(msg_version==1 and  msg_type>=0 and msg_type<=3): 
                print("Diffie Hellman error")
                Shallot_Messages.shallot_sendErrorMessage(sock,0)
            elif msg_type == 1:                                                     # A KEY_REPLY message has been received, generate key for commuication with relay
                keyIDother,B = Shallot_Messages.shallot_recvKeyReply(sock,msg_length)    
                key = pow(B,aList[sockindex],pList[sockindex])
                keychain.newKey(key,tempKeyIDList[sockindex]) 
                keyIDlist.append(tempKeyIDList[sockindex]) 
                foundKeyID = True;
            elif msg_type == 3:
                while True:  
                    keyID = Shallot_KeyChain.randomInt(32) 
                    if not keychain.hasKey(keyID): break
                Shallot_Messages.shallot_sendKeyInit(sock,keyID,g,pList(sockindex),AList(sockindex))     
                tempKeyIDList[sockindex] = keyID
            else: continue
    for sock in socketsToRead: 
        sock.close() 
    return keyIDlist