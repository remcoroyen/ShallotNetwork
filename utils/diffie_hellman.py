import select
import socket

import utils


def diffie_hellman_key_exchange(path_list, keychain):
    # path_list: list of lists (nested) of ip's and corresponding port of subsequent relays
    key_id_list = []
    sockets_to_read = []
    sockets_to_write = []
    a_list = []
    p_list = []
    A_list = []
    temp_key_id_list = []
    for node in path_list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((node[0], node[1]))
        sockets_to_read.append(sock)
        sockets_to_write.append(sock)
    timeout = 1
    g = 2
    for sock in sockets_to_write:
        p = utils.keychain.random_prime(1024)
        a = utils.keychain.random_int(1024)
        A = pow(g, a, p)
        a_list.append(a)
        p_list.append(p)
        A_list.append(A)
        while True:  
            key_id = utils.keychain.random_int(32)
            if not keychain.has_key(key_id):
                break
        utils.messages.shallot_send_key_init(sock, key_id, g, p, A)
        temp_key_id_list.append(key_id)
    while len(key_id_list) < len(sockets_to_read):
        readable, writable, exceptional = select.select(sockets_to_read, sockets_to_write, [], timeout)
        for sock_index in range(0, len(writable)):
            sock = writable[sock_index]
            msg_version, msg_type, msg_length = utils.messages.shallot_rec_header(sock)
            if not(msg_version == 1 and  msg_type >= 0 and msg_type <= 3):
                print("Diffie Hellman error")
                utils.messages.shallot_send_error_message(sock, 0)
            elif msg_type == 1:  # A KEY_REPLY message has been received, generate key for commuication with relay
                key_id_other, B = utils.messages.shallot_rec_key_reply(sock, msg_length)
                key = pow(B, a_list[sock_index], p_list[sock_index])
                keychain.new_key(key, temp_key_id_list[sock_index])
                key_id_list.append(temp_key_id_list[sock_index])
            elif msg_type == 3:
                while True:  
                    key_id = utils.keychain.random_int(32)
                    if not keychain.hasKey(key_id):
                        break
                utils.messages.shallot_send_key_init(sock, key_id, g, p_list(sock_index), A_list(sock_index))
                temp_key_id_list[sock_index] = key_id
            else:
                continue
    for sock in sockets_to_read:
        sock.close() 
    return key_id_list
