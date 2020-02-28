import dlog

bytes = [0]*0x10000

def read_byte(addr, silent=False):
    global bytes
    if(dlog.enable_mem_read and not silent):
        dlog.print_mem("read_byte", addr, 4, bytes[addr], 2)
    return bytes[addr]

def write_byte(addr, byte, silent=False):
    global bytes
    if(dlog.enable_mem_write and not silent):
        dlog.print_mem("write_byte ", addr, 4, byte, 2)
    bytes[addr] = byte
    
def read_word(addr):
    global bytes
    if(dlog.enable_mem_read):
        dlog.print_mem("read_word", addr, 4, (bytes[addr+1]<<8)|bytes[addr], 4)
    return (bytes[addr+1]<<8)|bytes[addr]

def write_word(addr, word):
    global bytes
    if(dlog.enable_mem_write):
        dlog.print_mem("write_word ", addr, 4, word, 4)
    bytes[addr+1] = (word>>8)&0xFF
    bytes[addr] = word&0xFF

