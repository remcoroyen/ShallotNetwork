from nodes.client import Client
from nodes.relay import Relay
import utils.read_config_file as read_configs

print("\nStarting up the Shallot network:\n")

IPAddress = read_configs.shallot_determine_ip_address()
read_configs.shallot_write_ip_address_host_ini('config/host.ini', IPAddress)
read_configs.shallot_write_ip_address_topology_ini('config/topology.ini', IPAddress)

client_nameList, relay_nameList = read_configs.shallot_read_config_host_ini('config/host.ini')

clients = {}  # This initiates a dictionary where the name and the object will be mapped

for client_name in client_nameList:
    clients[client_name] = Client("config/host.ini", "config/topology.ini", client_name)
    clients[client_name].start()

relays = []
for relay_name in relay_nameList:
    relay = Relay("config/host.ini", relay_name)
    relay.start()
    relays.append(relay)

for client_name in clients:
    print("Host "+clients[client_name].hostname+" running at IP, Port: "+clients[client_name].hostIP+", "+str(
        clients[client_name].hostPort))

for i in range(0, len(relays)):
    print(relays[i].hostname + " at IP, Port: " + relays[i].hostIP + ", " + str(relays[i].hostPort))


# User Interface
running = True
print("\n\nWho are you? (Type quit to exit application)")
while running: 
    sender = input()
    if sender in clients:
        print("\n\nHello " + sender + ", who do you want to send a message to? (Type quit to exit application)")
        break
    elif sender == "quit":
        running = False 
    else:
        print("\n\n" + sender + " is not recognized. Please try again")       
    
while running: 
    receiver = input()
    if receiver in clients and receiver != sender:
        print("\n\nEvery message you type is send from " + sender + " to " + receiver +
              " (Type quit to exit application)")
        break
    elif receiver == sender:
        print("\n\nYou can't send a message to yourself. Who do you want to send a message instead?")
    elif receiver == "quit":
        running = False 
    else:
        print("\n\n" + receiver + " is not recognized. Please try again")       

                
while running:
    text = input()
    if text == "quit":
        running = False  
    else:
        clients[sender].send_message(text, clients[receiver])
    
for client_name in clients:
    clients[client_name].close()
for relay in relays:
    relay.close()    
