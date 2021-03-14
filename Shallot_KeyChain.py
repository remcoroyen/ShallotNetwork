from Crypto.Util import number


def randomPrime(bitsize):
    return number.getPrime(bitsize)
        
def randomInt(bitsize):
    return number.getRandomInteger(bitsize)


class shallot_KeyChain:
    def __init__(self):
        self.keys = [];
        self.keyids = [];
        
    def newKey(self,key,keyID):
        self.keys.append(key)
        self.keyids.append(keyID)
        
    def hasKey(self,keyID):
        return keyID in self.keyids
        
    def getKey(self,keyID):
        if self.hasKey(keyID): return self.keys[self.keyids.index(keyID)]
        else: return None
        
    def destroyKey(self,keyID):
        if self.hasKey(keyID):
            index = self.keyids.index(keyID)
            self.keyids.pop(index)
            self.keys.pop(index)
        else:
            print('Key not found, none removed')
            
    def clear(self):
        for keyID in self.keyids:
            self.destroyKey(keyID)
        

        