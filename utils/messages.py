import utils.cypher as cypher


def shallot_rec_header(sock):
    raw_header = shallot_rec_all(sock, 4)
    version_and_type = raw_header[0]  # bytes are represented like this: b'\x00\x10' or bytes([0,16])
    msg_length = int.from_bytes(raw_header[2:4], byteorder='big')
    # byteorder = 'big' -> the most significant byte is at the beginning of the byte array
    msg_version = int((version_and_type & 0xf0) >> 4)  # (mask) 0xf0 = 11110000, >> rightshift by 4 bits
    msg_type = int(version_and_type & 0x0f)  # (mask) 0x0f = 00001111
    return msg_version, msg_type, msg_length


def shallot_send_error_message(sock, error_code):  # error_code is an integer
    msg_version = 1
    msg_type = 3
    msg_ver_and_typ = (msg_version << 4) | msg_type
    temp = error_code.to_bytes(2, byteorder='big')+bytes([0, 0])  # 2 bytes error code + 2 bytes padding
    header = msg_ver_and_typ.to_bytes(1, byteorder='big') + bytes([0]) + (len(temp)//4+1).to_bytes(2, byteorder='big')
    # temp must be a multiple of 4 or else the length is incorrect!
    shallot_send_all(sock, header+temp)
    return header + temp


def shallot_send_key_init(sock, key_id, g, p, a):
    msg_version = 1
    msg_type = 0
    msg_ver_and_typ = (msg_version << 4) | msg_type
    temp = key_id.to_bytes(4, byteorder='big')+g.to_bytes(4, byteorder='big')+p.to_bytes(128, byteorder='big') + a.\
        to_bytes(128, byteorder='big')
    header = msg_ver_and_typ.to_bytes(1, byteorder='big') + bytes([0]) + (len(temp)//4+1).to_bytes(2, byteorder='big')
    # temp must be a multiple of 4 or else the length is incorrect!
    shallot_send_all(sock, header+temp)
    return header + temp


def shallot_send_key_reply(sock, key_id, b):
    msg_version = 1
    msg_type = 1
    msg_ver_and_typ = (msg_version << 4) | msg_type
    temp = key_id.to_bytes(4, byteorder='big')+b.to_bytes(128, byteorder='big')
    header = msg_ver_and_typ.to_bytes(1, byteorder='big') + bytes([0]) + (len(temp)//4+1).to_bytes(2, byteorder='big')
    # temp must be a multiple of 4 or else the length is incorrect!
    shallot_send_all(sock, header+temp)
    return header + temp


def shallot_create_onion(message, path_list, keychain):  # pathlist and keychain.keyids should be same length
    
    if len(keychain.keyids) != len(path_list):
        print('Error in createOnion: length of pathlist and keys are not the same')
        return None

    payload = message
    for i in range(len(path_list)):
        key_id = keychain.keyids[i]
        if i == 0:
            next_hop = path_list[i][0]
            next_port = path_list[i][1]
        else:
            next_hop = path_list[i-1][0]
            next_port = path_list[i-1][1]
        payload = shallot_construct_onion_peel(key_id, next_hop, next_port, payload, keychain)
    return payload


def shallot_construct_onion_peel(key_id, next_hop, next_port, payload, keychain):
    # nextHop: IP in string (eg '192.168.0.1'), nextPort in integer, payload: payload in bytes
    msg_version = 1
    msg_type = 2
    msg_ver_and_typ = (msg_version << 4) | msg_type
    next_hop = next_hop.split('.')
    ip = b''
    for i in range(4):
        ip += (int(next_hop[i])).to_bytes(1, byteorder='big')
    next_port = next_port.to_bytes(4, byteorder='big')
    data = ip + next_port + payload
    key = keychain.get_key(key_id)
    if key is None:
        print("In: shallot_constructOnionPeel\n Error: This should not happen, no message sent")
        return None
    data_encrypted = cypher.shallot_encrypt(data, key)  # padding included
    header = msg_ver_and_typ.to_bytes(1, byteorder='big') + bytes([0]) + (len(data_encrypted)//4+2).to_bytes(
        2, byteorder='big')
    # data_encrypted must be a multiple of 4 or else the length is incorrect! This is ensured by shallot_encrypt.
    return header + key_id.to_bytes(4, byteorder='big') + data_encrypted


def shallot_rec_message_relay(sock, msg_length, keychain):
    raw_message = shallot_rec_all(sock, (msg_length-1)*4)
    key_id = int.from_bytes(raw_message[0:4], byteorder='big')
    data_encrypted = raw_message[4:]
    key = keychain.get_key(key_id)
    if key is None:
        return None, None
    data_decrypted = cypher.shallot_decrypt(data_encrypted, key)  # unpadding included
    next_hop = str(data_decrypted[0])+'.'+str(data_decrypted[1])+'.'+str(data_decrypted[2])+'.'+str(data_decrypted[3])
    next_port = int.from_bytes(data_decrypted[4:8], byteorder='big')
    payload = data_decrypted[8:]
    return next_hop, next_port, payload


def shallot_rec_error_message(sock, msg_length):
    raw_message = shallot_rec_all(sock, (msg_length-1)*4)
    error_code = int.from_bytes(raw_message[0:2], byteorder='big')
    return error_code


def shallot_rec_key_init(sock, msg_length):
    raw_message = shallot_rec_all(sock, (msg_length-1)*4)
    key_id = int.from_bytes(raw_message[0:4], byteorder='big')
    g = int.from_bytes(raw_message[4:8], byteorder='big')
    p = int.from_bytes(raw_message[8:136], byteorder='big')
    a = int.from_bytes(raw_message[136:264], byteorder='big')
    return key_id, g, p, a


def shallot_rec_key_reply(sock, msg_length):
    raw_message = shallot_rec_all(sock, (msg_length-1)*4)
    key_id = int.from_bytes(raw_message[0:4], byteorder='big')
    b = int.from_bytes(raw_message[4:132], byteorder='big')
    return key_id, b


def shallot_rec_all(sock, n):               # n = length in bytes of message
    data = b''                              # len(data) = 0
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def shallot_send_all(sock, message):
    sock.sendall(message)                                # send message
