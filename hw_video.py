import hw_mem as mem
import util_dlog as dlog
import util_events as events

videoram  = None
spritemem = None

def init():
    global videoram, spritemem
    videoram  = [0]*0x2000
    spritemem = [0]*0xA0
    # TODO implement sprite RAM bug

def map_memory():
    for i in range(0x8000, 0xA000):
        mem.read_map [i]    = videoram_read
        mem.write_map[i]    = videoram_write
        mem.name_map [i]    = videorame_name
    for i in range(0xFE00, 0xFEA0):
        mem.read_map [i]    = spritemem_read
        mem.write_map[i]    = spritemem_write
        mem.name_map [i]    = spritemem_name

# video ram
def videoram_read(addr):
    return videoram[addr-0x8000]
def videoram_write(addr, byte):
    addr -= 0x8000
    events.fire(events.EVENT_VIDEORAM_CHANGE, (addr, byte))
    videoram[addr] = byte
def videorame_name():
    return "Video RAM"

def spritemem_read(addr):
    return spritemem[addr-0xFE00]
def spritemem_write(addr, byte):
    addr -= 0xFE00
    events.fire(events.EVENT_SPRITEMEM_CHANGE, (addr, byte))
    spritemem[addr] = byte
def spritemem_name():
    return "Sprite Attribute Memory"

    