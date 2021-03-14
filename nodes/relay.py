import socket
import select
import threading

import utils


class Relay(threading.Thread):
    
    def __init__(self, host_file_path, hostname):
        self.hostname = hostname
        self.listenKeychain = utils.keychain.KeyChain()
        self.hostIP, self.hostPort = utils.read_config_file.shallot_read_config_host_data(host_file_path, self.hostname)
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket listening for incoming requests
        self.listenSocket.bind((self.hostIP, self.hostPort))
        self.listenSocket.listen(1)
        self.isRunning = True
        threading.Thread.__init__(self)
        
    def run(self):
        while self.isRunning:
            timeout = 1
            readable, writable, exceptional = select.select([self.listenSocket], [], [], timeout)
            for sock_read in readable:
                conn, _ = sock_read.accept()
                msg_version, msg_type, msg_length = utils.messages.shallot_rec_header(conn)
                
                if not(msg_version == 1 and  msg_type >= 0 and msg_type <= 3):
                    # If the format of the header is wrong, generate and send error message
                    utils.messages.shallot_send_error_message(conn, 0)
                    
                elif msg_type == 0:  # A KEY_INIT message has been received, calculate key and send KEY_REPLY message
                    key_id, g, p, a = utils.messages.shallot_rec_key_init(conn, msg_length)
                    if self.listenKeychain.has_key(key_id):  # KeyID already in use
                        utils.messages.shallot_send_error_message(conn, 1)
                    else:  # Apply Diffie-Helmann
                        b = utils.keychain.random_int(1024)
                        B = pow(g, b, p)
                        key = pow(a, b, p)
                        self.listenKeychain.new_key(key, key_id)
                        utils.messages.shallot_send_key_reply(conn, key_id, B)
                    
                elif msg_type == 1:  # A KEY_REPLY message has been received, generate key for commuication with relay
                    print("Relays arent supposed to receive these messages")
                    
                elif msg_type == 2:
                    # A Relay_Message has been received, decrypt, generate new header and send to next relay
                    
                    next_hop_ip, next_hop_port, payload = utils.messages.shallot_rec_message_relay(
                        conn, msg_length, self.listenKeychain)
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                    sock.connect((next_hop_ip, next_hop_port))
                    utils.messages.shallot_send_all(sock, payload)
                    sock.close()
                    
                    print("Message relayed")
                    
                elif msg_type == 3:  # An error message has been received. No idea yet what to do then
                    error_code = utils.messages.shallot_rec_error_message(conn, msg_length)
                    if error_code == 0:
                        print("an error message arrived: INVALID_MESSAGE_FORMAT")
                    if error_code == 1:
                        print("an error message arrived: INVALID_KEY_ID")
                    else:
                        print("an error message arrived: UNKNOWN")
                    
                conn.close()
        #  executed upon closing the thread
        self.listenSocket.close()
        print("closed relay")
        
    def close(self):
        self.isRunning = False
