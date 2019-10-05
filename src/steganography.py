import sys
import zlib

from png_filters import reverse_filter, add_filter
from message_buf import EncodeBuffer, DecodeBuffer

image = None
width, height = 0, 0
bit_depth, color = 0, 0

image_arr = None
arr_size = None
index = 0

secret_img = None

def slice_arr(size):
    global index
    index += size
    return image_arr[index - size : index]

def write_to_secret(arr_slice):
    secret_img.write(arr_slice)

def PNG_sign():
    return slice_arr(8)

def read_IHDR():
    global width, height, bit_depth, color
    IHDR = slice_arr(25)
    width = int(IHDR[8:12].hex(), 16)
    height = int(IHDR[12:16].hex(), 16)
    bit_depth = int(IHDR[16:17].hex(), 16)
    color = int(IHDR[17:18].hex(), 16)
    return IHDR

def read_chunk_len():
    return slice_arr(4)

def read_chunk_type():
    return slice_arr(4)

def read_chunk_data(chunk_len):
    return slice_arr(chunk_len)

def read_crc():
    return slice_arr(4)



def encode_IDAT(chunk_data, encode_buf):
    # Keep in mind width and height are in terms of pixels!
    data = zlib.decompress(chunk_data)
    
    # data needs to be converted back to an array (decompressed bytes)
    data = bytearray(data)
    
    # when reversing filter, start top left and go right and down 
    for i in range(0, height):
        filter_type = data[i * width * 3 + i]
        scanline_start = i * width * 3 + i + 1
        reverse_filter(data, filter_type, scanline_start, width)
        # encode here
        
        j = 0
        bits = encode_buf.next_two_bits()
        while bits != None and j < width * 3 + 1:
            data[scanline_start + j] &= 0xFC
            data[scanline_start + j] += bits
            bits = encode_buf.next_two_bits()
            # controls which part of pixel to change
            j += 1 

    # when adding filter, start bottom right and go left and up
    for i in range(0, height)[::-1]:
        filter_type = data[i * width * 3 + i]
        scanline_start = i * width * 3 + i + 1
        add_filter(data, filter_type, scanline_start, width)

    # has to be "method code 8" based on http://www.libpng.org/pub/png/spec/1.2/PNG-Compression.html
    data = zlib.compress(data, level = 8) 
    return data

def encode():
    # Will handle message from stdin
    encode_buf = EncodeBuffer()

    # PNG signature (http://www.libpng.org/pub/png/spec/1.2/PNG-Rationale.html#R.PNG-file-signature)
    write_to_secret(PNG_sign())

    # PNG Chunks
    write_to_secret(read_IHDR())

    while index < arr_size:
        chunk_len = read_chunk_len()
        int_len = int(chunk_len.hex(), 16)
        write_to_secret(chunk_len)

        chunk_type = read_chunk_type()
        write_to_secret(chunk_type)
        
        chunk_data = read_chunk_data(int_len)
        
        if(chunk_type == bytearray(b'IDAT')):
            chunk_data = encode_IDAT(chunk_data, encode_buf)
        
        write_to_secret(chunk_data)
        write_to_secret(read_crc())



def decode_IDAT(chunk_data, decode_buf):
    zobj = zlib.decompressobj(zlib.MAX_WBITS)
    data = zobj.decompress(chunk_data)

    # data needs to be converted back to an array (decompressed bytes)
    data = bytearray(data)
    
    for i in range(0, height):
        filter_type = data[i * width * 3 + i]
        scanline_start = i * width * 3 + i + 1
        reverse_filter(data, filter_type, scanline_start, width)
        
        j = 0
        while not decode_buf.check_end() and j < width * 3 + 1:
            decode_buf.append_two_bits(data[scanline_start + j])
            # controls which part of pixel to change
            j += 1 

# Can be made more efficient by moving file pointer to IDAT chunks only
def decode():
    decode_buf = DecodeBuffer()

    PNG_sign()
    read_IHDR()

    while index < arr_size:
        chunk_len = read_chunk_len()
        int_len = int(chunk_len.hex(), 16)

        chunk_type = read_chunk_type()

        chunk_data = read_chunk_data(int_len)

        if(chunk_type == bytearray(b'IDAT')):
            decode_IDAT(chunk_data, decode_buf)
            if decode_buf.check_end():
                decode_buf.output_msg()
                return

        read_crc()

    decode_buf.output_msg()

'''
Images source: http://homepages.cae.wisc.edu/~ece533/images/

Lot of assumptions:
    For decode:
    - Assumes encoded image is called secret.png
    
    For encode:
    - Image to be encoded is RGB image
    - message to be hidden is in stdin
    - size of bits to hide will always be 2
'''
def driver():
    global image, image_arr, arr_size, secret_img
    if(len(sys.argv) < 2):
        print("No options detected")
        return 1

    if sys.argv[1] == "encode":
        image = open("../images/baboon.png", "rb")
        secret_img = open('../images/secret.png', 'wb')
        image_arr = bytearray(image.read())
        arr_size = len(image_arr)
        encode()

    elif sys.argv[1] == "decode":
        secret_img = open('../images/secret.png', 'rb')
        image_arr = bytearray(secret_img.read())
        arr_size = len(image_arr)
        decode()

if __name__ == '__main__':
    driver()