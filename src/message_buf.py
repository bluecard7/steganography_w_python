import sys 

terminate = 'Spaghettio'

class EncodeBuffer:
    def __init__(self):
        self.message = sys.stdin.read() + terminate
        self.pos = 0
        self.buf = ord(self.message[self.pos])
        self.mask = 3
        self.move = 0

    def next_two_bits(self):
        if self.mask == 768 and self.pos == len(self.message) - 1:
            return None

        if self.mask == 768 and self.pos < len(self.message):
            self.pos += 1
            self.buf = ord(self.message[self.pos])
            self.mask = 3
            self.move = 0

        result = self.buf & self.mask
        result >>= self.move
        self.mask <<= 2
        self.move += 2
        return result
        

class DecodeBuffer:
    def __init__(self):
        self.message = ''
        self.move = 0
        self.buf = 0

    def append_two_bits(self, byte):
        msg_bits = byte & 3
        msg_bits <<= self.move
        
        self.buf += msg_bits 
        self.move += 2

        if self.move == 8:
            self.message += chr(self.buf)
            self.move = 0
            self.buf = 0
    
    def check_end(self):
        return self.message.endswith(terminate)

    def output_msg(self):
        print(self.message)

if __name__ == '__main__':
    e = EncodeBuffer()
    d = DecodeBuffer()
    
    print(e.message)
    bits = e.next_two_bits()

    while not d.check_end():
        finish = d.append_two_bits(bits)
        bits = e.next_two_bits()
   
    d.output_msg()



        

