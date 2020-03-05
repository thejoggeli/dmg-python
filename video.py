import mem
import dlog

def init():
    # TODO implement sprite RAM bug
    pass

def map_memory():
    for i in range(0xFE00, 0xFEA0):
        mem.read_map [i]    = spritemem_read
        mem.write_map[i]    = spritemem_write
        mem.name_map [i]    = spritemem_name

spritemem = [0]*0xA0
def spritemem_read(addr):
    return spritemem[addr-0xFE00]
def spritemem_write(addr, byte):
    spritemem[addr-0xFE00] = byte
def spritemem_name():
    return "Sprite Attribute Memory"

    