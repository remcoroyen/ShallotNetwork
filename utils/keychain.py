from Crypto.Util import number


def random_prime(bit_size):
    return number.getPrime(bit_size)


def random_int(bit_size):
    return number.getRandomInteger(bit_size)


class KeyChain:
    def __init__(self):
        self.keys = []
        self.keyids = []
        
    def new_key(self, key, key_id):
        self.keys.append(key)
        self.keyids.append(key_id)
        
    def has_key(self, key_id):
        return key_id in self.keyids
        
    def get_key(self, key_id):
        if self.has_key(key_id):
            return self.keys[self.keyids.index(key_id)]
        else:
            return None
        
    def destroy_key(self, key_id):
        if self.has_key(key_id):
            index = self.keyids.index(key_id)
            self.keyids.pop(index)
            self.keys.pop(index)
        else:
            print('Key not found, none removed')
            
    def clear(self):
        for key_id in self.keyids:
            self.destroy_key(key_id)
