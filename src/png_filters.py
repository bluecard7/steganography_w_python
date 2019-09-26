# References: 
# https://www.w3.org/TR/PNG-Filters.html
# https://www.w3.org/TR/2003/REC-PNG-20031110/#9Filters

# Filters are done on channels / corresponding bytes

# type 0: do nothing (there's no filter)
def none(data, pos, scanline_start, width):
    pass

# type 1
def sub(data, pos, scanline_start, width):
    if pos - 3 < scanline_start: return
    data[pos] = (data[pos] - data[pos - 3]) % 256
 
def rev_sub(data, pos, scanline_start, width):
    if pos - 3 < scanline_start: return 
    data[pos] = (data[pos] + data[pos - 3]) % 256

# type 2
def up(data, pos, scanline_start, width):
    if scanline_start == 1: return
    data[pos] = (data[pos] - data[pos - width * 3 - 1]) % 256 

def rev_up(data, pos, scanline_start, width):
    if scanline_start == 1: return
    data[pos] = (data[pos] + data[pos - width * 3 - 1]) % 256 

# type 3
def avg(data, pos, scanline_start, width):
    if scanline_start == 1 and  pos - 3 < scanline_start: return

    if scanline_start == 1: 
        data[pos] = (data[pos] - 
                     data[pos - 3] // 2 ) % 256
        return

    if pos - 3 < scanline_start: 
        data[pos] = (data[pos] - 
                     data[pos - width * 3 - 1] // 2) % 256
        return

    data[pos] = (data[pos] - 
                (data[pos - 3] + data[pos - width * 3 - 1]) // 2) % 256

def rev_avg(data, pos, scanline_start, width):
    if scanline_start == 1 and  pos - 3 < scanline_start: return

    if scanline_start == 1: 
        data[pos] = (data[pos] + 
                     data[pos - 3] // 2 ) % 256
        return

    if pos - 3 < scanline_start: 
        data[pos] = (data[pos] + 
                     data[pos - width * 3 - 1] // 2) % 256
        return

    data[pos] = (data[pos] + 
                (data[pos - 3] + data[pos - width * 3 - 1]) // 2) % 256

# type 4
def paeth_predictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)

    if pa <= pb and pa <= pc: return a
    if pb <= pc: return b
    return c

def paeth(data, pos, scanline_start, width):
    if scanline_start == 1 and pos - 3 < scanline_start: return
    
    if scanline_start == 1: # same as sub
        data[pos] = (data[pos] - data[pos - 3]) % 256
        return

    if pos - 3 < scanline_start: # same as up
        data[pos] = (data[pos] - data[pos - width * 3 - 1]) % 256
        return

    data[pos] = (data[pos] - 
                 paeth_predictor(data[pos - 3], data[pos - width * 3 - 1], data[pos - width * 3 - 4])) % 256


def rev_paeth(data, pos, scanline_start, width):
    if scanline_start == 1 and pos - 3 < scanline_start: return 

    if scanline_start == 1: # same as rev_sub
        data[pos] = (data[pos] + data[pos - 3]) % 256
        return

    if pos - 3 < scanline_start: # same as rev_up
        data[pos] = (data[pos] + data[pos - width * 3 - 1]) % 256
        return

    data[pos] = (data[pos] +
                 paeth_predictor(data[pos - 3], data[pos - width * 3 - 1], data[pos - width * 3 - 4])) % 256

add_filters = [none, sub, up, avg, paeth]
rev_filters = [none, rev_sub, rev_up, rev_avg, rev_paeth]

# when adding filter, start bottom right and go left and up
def add_filter(data, filter_type, scanline_start, width):
    for i in range(scanline_start, scanline_start + width * 3)[::-1]:
        add_filters[filter_type](data, i, scanline_start, width)

# when reversing filter, start top left and go right and down 
def reverse_filter(data, filter_type, scanline_start, width):
    for i in range(scanline_start, scanline_start + width * 3):
        rev_filters[filter_type](data, i, scanline_start, width)