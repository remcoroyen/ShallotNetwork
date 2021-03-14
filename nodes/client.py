import threading
import socket 
import select

import utils.read_config_file as read_config_utils
import utils.keychain as kc
import utils.messages as msgs
import utils.diffie_hellman as diffie_hellman
import utils.dijkstra as dijkstra


class Client(threading.Thread):
    
    def __init__(self, host_file_path, topology_file_path, hostname):
        self.hostname = hostname
        self.listenKeychain = kc.KeyChain()
        self.IPs, self.Ports, self.Neighbours = read_config_utils.shallot_read_config_topology_ini(topology_file_path)
        self.hostIP, self.hostPort = read_config_utils.shallot_read_config_host_data(host_file_path, self.hostname)
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.bind((self.hostIP, self.hostPort))
        self.listen_sock.listen(1)
        self.isRunning = True
        threading.Thread.__init__(self)
        
    def run(self):
        # To Receive messages   (This is all needed for Bob)
        while self.isRunning:
            timeout = 1
            readable, writable, exceptional = select.select([self.listen_sock], [], [], timeout)
            for sock_read in readable:
                conn, _ = sock_read.accept()
                msg_version, msg_type, msg_length = msgs.shallot_rec_header(conn)

                if not(msg_version == 1 and  msg_type >= 0 and msg_type <= 3):
                    # If the format of the header is wrong, generate and send error message
                    msgs.shallot_send_error_message(conn, 0)
                    
                elif msg_type == 0:
                    # A KEY_INIT message has been received, calculate key and send KEY_REPLY message
                    key_id, g, p, A = msgs.shallot_rec_key_init(conn, msg_length)
                    if self.listenKeychain.has_key(key_id):
                        msgs.shallot_send_error_message(conn, 1)
                    else:
                        b = kc.random_int(1024)
                        B = pow(g, b, p)
                        s = pow(A, b, p)
                        self.listenKeychain.new_key(s, key_id)
                        msgs.shallot_send_key_reply(conn, key_id, B)
                    
                elif msg_type == 1:
                    # A KEY_REPLY message has been received, generate key for commuication with relay
                    print("You are not supposed to receive these messages here")
                    
                elif msg_type == 2:
                    # A Relay_Message has been received, decrypt, generate new header and send to next relay
                    next_hop, _, message_received_bytes = msgs.shallot_rec_message_relay(
                        conn, msg_length, self.listenKeychain)
                    if next_hop is None and message_received_bytes is None:
                        error_code = 1
                        msgs.shallot_send_error_message(conn, error_code)
                        print("Key not found\n An error message has been sent (INVALID_KEY_ID)")
                        conn.close()
                        continue
                    if next_hop == self.hostIP:
                        message_received = message_received_bytes.decode()
                        print(self.hostname+" received: "+message_received)
                    else:
                        print("Error: "+self.hostname+" is not final destination")
                    
                elif msg_type == 3:
                    # An error message has been received. No idea yet what to do then
                    error_code = msgs.shallot_rec_error_message(conn, msg_length)
                    if error_code == 0:
                        print("an error message arrived: INVALID_MESSAGE_FORMAT")
                    if error_code == 1:
                        print("an error message arrived: INVALID_KEY_ID")
                    else:
                        print("an error message arrived: UNKNOWN")
                    
                conn.close()
        # executed upon closing the thread
        self.listen_sock.close()
        print("closed client "+self.hostname)
        
    def close(self):
        self.isRunning = False
    
    def send_message(self, message, recipient):
        # Executed to send a message  (This is all needed for Alice)
        message_bytes = str.encode(message)
    
        print("Computing path...")
        source = [self.hostIP, self.hostPort]
        destination = [recipient.hostIP, recipient.hostPort]
        pathlist = dijkstra.shallot_RandomDijkstra(source, destination, self.IPs, self.Ports, self.Neighbours)
        # pathlist nested list of this form: [[recipient.hostIP,recipient.hostPort]] (in reversed order!)
        print("Path found:")
        print(list(reversed(pathlist)))

        onion_keychain = kc.KeyChain()
        diffie_hellman.diffie_hellman_key_exchange(pathlist, onion_keychain)
        print("Keys exchanged")
        payload = msgs.shallot_create_onion(message_bytes, pathlist, onion_keychain)
        onion_keychain.clear()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock.connect((pathlist[-1][0], pathlist[-1][1]))
        msgs.shallot_send_all(sock, payload)
        sock.close()
    
        print(self.hostname+" sent: "+message)
