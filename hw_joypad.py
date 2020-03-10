import hw_mem as mem

BTN_A      = 0
BTN_B      = 1
BTN_SELECT = 2
BTN_START  = 3

DIR_RIGHT  = 0
DIR_LEFT   = 1
DIR_UP     = 2
DIR_DOWN   = 3

SET_MAP   = [ 0x01,  0x02,  0x04,  0x08]
RESET_MAP = [~0x01, ~0x02, ~0x04, ~0x08]

# 1 = released
# 0 = pressed
class State:
    btn_values = 0xF
    dir_values = 0xF
state = None

def init():
    global state
    state = State()    
    mem.iomem[0x00] = 0xCF 
    pass
    
def map_memory():
    mem.name_map [0xFF00] = lambda: "P1 (Joypad) (R/W)"
    mem.read_map [0xFF00] = read_byte_0xFF00
    mem.write_map[0xFF00] = write_byte_0xFF00
    
def read_byte_0xFF00(addr):
    # Bits 5-4 from memory
    byte = mem.iomem[0x00]&0x30
    # Bits 6-7 are always 1
    byte |= 0xC0
    # Bits 0-3
    if(byte&0x20 == 0):
        # read btn
        byte |= state.btn_values
    elif(byte&0x10 == 0):
        # read dir
        byte |= state.dir_values
    return byte

def write_byte_0xFF00(addr, byte):
    # Only bits 5-4 writeable
    mem.iomem[0x00] = (mem.iomem[0x00]&0xCF)|(byte&0x30)
    
def press_btn(btn):
    mem.iomem[0x0F] |= 0x10 # P1 interrupt
    state.btn_values &= RESET_MAP[btn] # reset bit

def release_btn(btn):
    state.btn_values |= SET_MAP[btn] # set bit

def press_dir(dir):
    mem.iomem[0x0F] |= 0x10 # P1 interrupt
    state.dir_values &= RESET_MAP[dir] # reset bit

def release_dir(dir):
    state.dir_values |= SET_MAP[dir] # set bit

