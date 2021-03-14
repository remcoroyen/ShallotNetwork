from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def shallot_encrypt(data, key): 			    # key from diffie-hellmann exchange (integer), data bytearray
    data = shallot_padd(data, 128)			    # AES requires 128 bit
    key = key.to_bytes(128, byteorder='big')    # key is 1024 bits = 128 bytes
    iv = key[:16]							    # 16x8 = 128 bits iv -> can be xor'd with the datablocks (CBC)
    key = key[-32:]							    # AES: three different key lengths: 128, 192 and 256 (=32*8) bits
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor() 
    data_encrypted = encryptor.update(data)+encryptor.finalize()
    return data_encrypted


def shallot_decrypt(data_encrypted, key):
    key = key.to_bytes(128, byteorder='big')
    iv = key[:16]  # 16x8 = 128 bits iv -> can be xor'd with the datablocks (CBC)
    key = key[-32:]
    backend = default_backend() 
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor() 
    data = decryptor.update(data_encrypted)+decryptor.finalize()
    data = shallot_unpadd(data, 128)
    return data    


def shallot_padd(data, blocksize=32):
    padder = padding.PKCS7(blocksize).padder()
    data_padded = padder.update(data)+padder.finalize() 
    return data_padded


def shallot_unpadd(data_padded, blocksize=32):
    unpadder = padding.PKCS7(blocksize).unpadder()
    data = unpadder.update(data_padded)+unpadder.finalize() 
    return data
