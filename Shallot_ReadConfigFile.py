import configparser
import socket
import json

def shallot_readConfigHostData(filePath, hostname):
    config = configparser.ConfigParser()
    config.read(filePath)
    if hostname in config['clients']:
        hostIP,hostPort = json.loads(config['clients'][hostname])
        return hostIP,int(hostPort)
    elif hostname in config['relays']:
        hostIP,hostPort = json.loads(config['relays'][hostname])
        return hostIP,int(hostPort)    
    else:
        print("Error in shallot_readConfigHostData: host not found.")
        return None,None

def shallot_readConfigTopologyini(filePath):
    IPList = []
    PortList = []
    config = configparser.ConfigParser()
    config.read(filePath)    
    for clientname in config['clients']:
        IP,Port = json.loads(config.get('clients',clientname))
        IPList.append(IP)
        PortList.append(Port)
    for relayname in config['relays']: 
        IP,Port = json.loads(config.get('relays',relayname))
        IPList.append(IP)
        PortList.append(Port)        
    Neighbours = []    
    for nodeName in config['topology']:
        neighbourss = json.loads(config.get('topology',nodeName))
        neighbourList = []
        for i in range(0,len(neighbourss),2):
            neighbourList.append([neighbourss[i],int(neighbourss[i+1])])
        Neighbours.append(neighbourList)
        
    return IPList,PortList,Neighbours       

def shallot_readConfigHostini(filePath):
    
    config = configparser.ConfigParser()
    config.read(filePath)
    clients = list(config['clients'])
    relays = list(config['relays'])
    return clients,relays

def shallot_writeIPAddressHostini(filePath,IPAddress):
    config = configparser.ConfigParser()
    config.read(filePath)
    for section in config.sections():
        for line in config[section]:
            hostIP,hostPort = json.loads(config[section][line])
            config[section][line] = json.dumps([IPAddress,hostPort])
    with open(filePath, 'w') as configfile:
        config.write(configfile)    
        
def shallot_writeIPAddressTopologyini(filePath,IPAddress):
    config = configparser.ConfigParser()
    config.read(filePath)
    for section in config.sections():
        if section != 'topology':
            for line in config[section]:
                hostIP,hostPort = json.loads(config[section][line])
                config[section][line] = json.dumps([IPAddress,hostPort])
        else:
            for line in config[section]:
                lineContent = json.loads(config[section][line])
                for i in range(0,len(lineContent),2):
                    lineContent[i] = IPAddress
                config[section][line] = json.dumps(lineContent)   
        
    with open(filePath, 'w') as configfile:
        config.write(configfile)  
        
def shallot_determineIPAddress():
    return socket.gethostbyname(socket.gethostname())