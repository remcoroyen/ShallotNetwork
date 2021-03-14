import Shallot_Client
import Shallot_Relay 
import Shallot_ReadConfigFile
import configparser

print("\nStarting up the Shallot network:\n")

IPAddress = Shallot_ReadConfigFile.shallot_determineIPAddress()
Shallot_ReadConfigFile.shallot_writeIPAddressHostini('config/host.ini',IPAddress)
Shallot_ReadConfigFile.shallot_writeIPAddressTopologyini('config/topology.ini',IPAddress)

clientnameList,relaynameList = Shallot_ReadConfigFile.shallot_readConfigHostini('config/host.ini')

clients = {} # This initiates a dictionary where the name and the object will be mapped

for clientname in clientnameList:
    clients[clientname] = Shallot_Client.shallot_Client("config/host.ini", "config/topology.ini", clientname)
    clients[clientname].start()

relays = []
for relayname in relaynameList:
    relay = Shallot_Relay.shallot_Relay("config/host.ini",relayname)
    relay.start()
    relays.append(relay)

for clientname in clients:
    print("Host "+clients[clientname].hostname+" running at IP, Port: "+clients[clientname].hostIP+", "+str(clients[clientname].hostPort))

for i in range(0,len(relays)):
    print(relays[i].hostname + " at IP, Port: "+ relays[i].hostIP + ", " + str(relays[i].hostPort))


# User Interface
running = True
print("\n\nWho are you? (Type quit to exit application)")
while running: 
    sender = input()
    if sender in clients:
        print("\n\nHello " + sender + ", who do you want to send a message to? (Type quit to exit application)")
        break;  
    elif sender == "quit" :
        running = False 
    else:
        print("\n\n" + sender + " is not recognized. Please try again")       
    
while running: 
    receiver = input()
    if receiver in clients and receiver != sender :
        print("\n\nEvery message you type is send from " + sender + " to " + receiver + " (Type quit to exit application)")      
        break;                        
    elif receiver == sender:
        print("\n\nYou can't send a message to yourself. Who do you want to send a message instead?")
    elif receiver == "quit" :
        running = False 
    else:
        print("\n\n" + receiver + " is not recognized. Please try again")       

                
while running:
    text = input()
    if text == "quit" :
        running = False  
    else:
        clients[sender].sendMessage(text,clients[receiver])
    
for clientname in clients:
    clients[clientname].close()
for relay in relays:
    relay.close()    
    