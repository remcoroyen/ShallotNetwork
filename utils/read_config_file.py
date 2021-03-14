import configparser
import socket
import json


def shallot_read_config_host_data(file_path, hostname):
    config = configparser.ConfigParser()
    config.read(file_path)
    if hostname in config['clients']:
        host_ip, host_port = json.loads(config['clients'][hostname])
        return host_ip, int(host_port)
    elif hostname in config['relays']:
        host_ip, host_port = json.loads(config['relays'][hostname])
        return host_ip, int(host_port)
    else:
        print("Error in shallot_readConfigHostData: host not found.")
        return None, None


def shallot_read_config_topology_ini(file_path):
    ip_list = []
    port_list = []
    config = configparser.ConfigParser()
    config.read(file_path)
    for client_name in config['clients']:
        ip, port = json.loads(config.get('clients', client_name))
        ip_list.append(ip)
        port_list.append(port)
    for relay_name in config['relays']:
        ip, port = json.loads(config.get('relays', relay_name))
        ip_list.append(ip)
        port_list.append(port)
    neighbours = []
    for node_Name in config['topology']:
        neighbourss = json.loads(config.get('topology', node_Name))
        neighbour_list = []
        for i in range(0, len(neighbourss), 2):
            neighbour_list.append([neighbourss[i], int(neighbourss[i+1])])
        neighbours.append(neighbour_list)
        
    return ip_list, port_list, neighbours


def shallot_read_config_host_ini(file_path):
    
    config = configparser.ConfigParser()
    config.read(file_path)
    clients = list(config['clients'])
    relays = list(config['relays'])
    return clients, relays


def shallot_write_ip_address_host_ini(file_path, ip_address):
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        for line in config[section]:
            host_ip, host_port = json.loads(config[section][line])
            config[section][line] = json.dumps([ip_address, host_port])
    with open(file_path, 'w') as configfile:
        config.write(configfile)    


def shallot_write_ip_address_topology_ini(file_path, ip_address):
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        if section != 'topology':
            for line in config[section]:
                host_ip, host_port = json.loads(config[section][line])
                config[section][line] = json.dumps([ip_address, host_port])
        else:
            for line in config[section]:
                line_content = json.loads(config[section][line])
                for i in range(0, len(line_content), 2):
                    line_content[i] = ip_address
                config[section][line] = json.dumps(line_content)
        
    with open(file_path, 'w') as configfile:
        config.write(configfile)  


def shallot_determine_ip_address():
    return socket.gethostbyname(socket.gethostname())
