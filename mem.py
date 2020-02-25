import dlog

bytes = [0]*0x10000

def read_byte(addr):
    global bytes
    if(dlog.enable_mem_read):
        dlog.print_mem("read_byte", addr, bytes[addr])
    return bytes[addr]

def write_byte(addr, byte):
    global bytes
    if(dlog.enable_mem_write):
        dlog.print_mem("write_byte ", addr, byte)
    bytes[addr] = byte
