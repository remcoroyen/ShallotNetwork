import socket
import select

import Shallot_Cypher

def shallot_recvHeader(sock):
    raw_header = shallot_recvall(sock,4)
    versionandtype = raw_header[0]                                      #bytes are represented like this: b'\x00\x10' or bytes([0,16])
    msg_length = int.from_bytes(raw_header[2:4], byteorder='big')       #byteorder = 'big' -> the most significant byte is at the beginning of the byte array
    msg_version = int((versionandtype&0xf0)>>4)                         #(mask) 0xf0 = 11110000, >> rightshift by 4 bits
    msg_type = int(versionandtype&0x0f)                                 #(mask) 0x0f = 00001111
    return msg_version,msg_type,msg_length 

def shallot_sendErrorMessage(sock,error_code):                          #error_code is an integer
    msg_version = 1
    msg_type = 3
    msg_verAndTyp = (msg_version<<4)|msg_type
    temp = (error_code).to_bytes(2,byteorder='big')+bytes([0,0])        #2 bytes error code + 2 bytes padding
    header = (msg_verAndTyp).to_bytes(1,byteorder='big') + bytes([0]) + (len(temp)//4+1).to_bytes(2,byteorder='big')  #temp must be a multiple of 4 or else the length is incorrect!
    shallot_sendall(sock,header+temp)
    return header + temp

def shallot_sendKeyInit(sock,keyID,g,p,A):
    msg_version = 1
    msg_type = 0
    msg_verAndTyp = (msg_version<<4)|msg_type
    temp = keyID.to_bytes(4,byteorder='big')+g.to_bytes(4,byteorder='big')+(p).to_bytes(128,byteorder='big')+(A).to_bytes(128,byteorder='big')
    header = (msg_verAndTyp).to_bytes(1,byteorder='big') + bytes([0]) + (len(temp)//4+1).to_bytes(2,byteorder='big')  #temp must be a multiple of 4 or else the length is incorrect!
    shallot_sendall(sock,header+temp)
    return header + temp

def shallot_sendKeyReply(sock,keyID,B):
    msg_version = 1
    msg_type = 1
    msg_verAndTyp = (msg_version<<4)|msg_type
    temp = keyID.to_bytes(4,byteorder='big')+(B).to_bytes(128,byteorder='big')
    header = (msg_verAndTyp).to_bytes(1,byteorder='big') + bytes([0]) + (len(temp)//4+1).to_bytes(2,byteorder='big')  #temp must be a multiple of 4 or else the length is incorrect!
    shallot_sendall(sock,header+temp)
    return header + temp

def shallot_createOnion(message,pathlist,keychain):            # pathlist and keychain.keyids should be same length
    
    if len(keychain.keyids) != len(pathlist):
        print('Error in createOnion: length of pathlist and keys are not the same')
        return None

    payload = message
    for i in range(len(pathlist)):
        keyID = keychain.keyids[i]
        if i==0:
            nextHop = pathlist[i][0]
            nextPort = pathlist[i][1]
        else:
            nextHop = pathlist[i-1][0]
            nextPort = pathlist[i-1][1]
        payload = shallot_constructOnionPeel(keyID,nextHop,nextPort,payload,keychain)
    return payload

def shallot_constructOnionPeel(keyID,nextHop,nextPort,payload,keychain):        #nextHop: IP in string (eg '192.168.0.1'), nextPort in integer, payload: payload in bytes
    msg_version = 1
    msg_type = 2
    msg_verAndTyp = (msg_version<<4)|msg_type
    nextHop = nextHop.split('.')
    IP = b''
    for i in range(4): IP += (int(nextHop[i])).to_bytes(1,byteorder='big')
    nextPort = nextPort.to_bytes(4,byteorder='big')
    data = IP+nextPort+payload
    key = keychain.getKey(keyID)
    if key == None:
        print("In: shallot_constructOnionPeel\n Error: This should not happen, no message sent")
        return None
    data_encrypted = Shallot_Cypher.shallot_encrypt(data,key)        #padding included
    header = (msg_verAndTyp).to_bytes(1,byteorder='big') + bytes([0]) + (len(data_encrypted)//4+2).to_bytes(2,byteorder='big')  #data_encrypted must be a multiple of 4 or else the length is incorrect! This is ensured by shallot_encrypt.
    return header + keyID.to_bytes(4,byteorder='big') + data_encrypted

#def shallot_sendMessageRelay(sock,keyID,nextHop,nextPort,payload,keychain):        #nextHop: IP in string (eg '192.168.0.1'), payload: payload in bytes
#    msg_version = 1
#    msg_type = 2
#    msg_verAndTyp = (msg_version<<4)|msg_type
#    nextHop = nextHop.split('.')
#    IP = b''
#    for i in range(4): IP += (int(nextHop[i])).to_bytes(1,byteorder='big')
#    nextPort = nextPort.to_bytes(4,byteorder='big')
#    data = IP+nextPort+payload
#    key = keychain.getKey(keyID)
#    if key == None:
#        print("In: shallot_sendMessageRelay\n Error: This should not happen, no message sent")
#        return None
#    data_encrypted = Shallot_Cypher.shallot_encrypt(data,key)        #padding included
#    header = (msg_verAndTyp).to_bytes(1,byteorder='big') + bytes([0]) + (len(data_encrypted)//4+2).to_bytes(2,byteorder='big')
#    shallot_sendall(sock,header+keyID.to_bytes(4,byteorder='big')+data_encrypted)
#    return header + keyID.to_bytes(4,byteorder='big') + data_encrypted

#deze updaten overal waar gebruikt!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:
def shallot_recvMessageRelay(sock,msg_length,keychain):
    raw_message = shallot_recvall(sock,(msg_length-1)*4)
    keyID = int.from_bytes(raw_message[0:4], byteorder='big')
    data_encrypted = raw_message[4:]
    key = keychain.getKey(keyID)
    if key == None:
        return None,None
    data_decrypted = Shallot_Cypher.shallot_decrypt(data_encrypted,key)        #unpadding included
    nextHop = str(data_decrypted[0])+'.'+str(data_decrypted[1])+'.'+str(data_decrypted[2])+'.'+str(data_decrypted[3])
    nextPort = int.from_bytes(data_decrypted[4:8], byteorder='big')
    payload = data_decrypted[8:]
    return nextHop,nextPort,payload

def shallot_recvErrorMessage(sock,msg_length):
    raw_message = shallot_recvall(sock,(msg_length-1)*4)
    errorcode = int.from_bytes(raw_message[0:2], byteorder='big')
    return errorcode

def shallot_recvKeyInit(sock,msg_length):
    raw_message = shallot_recvall(sock,(msg_length-1)*4)
    KeyID = int.from_bytes(raw_message[0:4], byteorder='big')
    g = int.from_bytes(raw_message[4:8], byteorder='big')
    p = int.from_bytes(raw_message[8:136], byteorder='big')
    A = int.from_bytes(raw_message[136:264], byteorder='big')
    return KeyID,g,p,A

def shallot_recvKeyReply(sock,msg_length):
    raw_message = shallot_recvall(sock,(msg_length-1)*4)
    KeyID = int.from_bytes(raw_message[0:4], byteorder='big')
    B = int.from_bytes(raw_message[4:132], byteorder='big')
    return KeyID,B

def shallot_recvall(sock, n):               # n = length in bytes of message
    data = b''                              # len(data) = 0
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def shallot_sendall(sock, message):
    sock.sendall(message)                                # send message
    #try:
        #sock.setblocking(0)
        #timeout = 10
        #readable,writable,exceptional = select.select([sock],[],[],timeout)             # Check whether we received a return message from the other side with a timout of 1 
        #for s in readable:
            #raw_header = s.recv(4,socket.MSG_PEEK)                                      # If return message is received, peek at the header 
            #if raw_header:
                #versionandtype = raw_header[0] 
                #msg_length = int.from_bytes(raw_header[2:4], byteorder='big')   
                #msg_version = int((versionandtype&0xf0)>>4)                       
                #msg_type = int(versionandtype&0x0f)
                #if msg_type    == 3:                                                    # If the header is for an error message, peek at the error message 
                    #print("An error return message received")
                    #raw_headerAndMessage = s.recv(4+msg_length,socket.MSG_PEEK)
                    #errorcode = int.from_bytes(raw_headerAndMessage[4:6], byteorder='big')
                    #if errorcode ==    0:                                               # If it is a format error, resend message. 
                        #raw_headerAndMessage = s.recv(4+msg_length)
                        #print("Error return message was format error, thus resend message")
                        #shallot_sendall(sock,message)                            
    #except ConnectionResetError:
        #print("A wild error occured")