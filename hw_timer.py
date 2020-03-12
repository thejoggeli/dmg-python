import hw_mem as mem
import hw_z80 as z80

class State:
    div_cycle_counter = 0
    timer_on = 0
    timer_clock = 0
    timer_cycle_counter = 0
    timer_cycles_per_increment = 0
state = None

timer_cycles_per_increment_map = [
    1024, 16, 64, 256,
]

def init():
    global state
    state = State()
    
def map_memory():
    mem.read_map[0xFF04]  = read_byte
    mem.read_map[0xFF05]  = read_byte
    mem.read_map[0xFF06]  = read_byte
    mem.read_map[0xFF07]  = read_byte
    
    mem.write_map[0xFF04] = write_byte_0xFF04
    mem.write_map[0xFF05] = write_byte_0xFF05
    mem.write_map[0xFF06] = write_byte_0xFF06
    mem.write_map[0xFF07] = write_byte_0xFF07
    
    mem.name_map[0xFF04] = lambda: "DIV - Divider Register (R/W)"
    mem.name_map[0xFF05] = lambda: "TIMA - Timer Counter (R/W)"
    mem.name_map[0xFF06] = lambda: "TMA - Timer Modulo (R/W)"
    mem.name_map[0xFF07] = lambda: "TAC - Timer Control (R/W)"

def update():
    # increment DIV
    state.div_cycle_counter += z80.state.cycles_delta
    if(state.div_cycle_counter >= 256):
        state.div_cycle_counter -= 256
        mem.iomem[0x04] = (mem.iomem[0x04]+1)&0xFF
        
    # increment TIMA
    if(state.timer_on):
        state.timer_cycle_counter += z80.state.cycles_delta
        if(state.timer_cycle_counter >= state.timer_cycles_per_increment):
            state.timer_cycle_counter -= state.timer_cycles_per_increment
            mem.iomem[0x05] = mem.iomem[0x05]+1
            if(mem.iomem[0x05] == 256):
                # load TMA into TIMA
                mem.iomem[0x05] = mem.iomem[0x06]
                # request interrupt if timer interrupt enabled and IME=1 and 
                ie_flag = mem.read_byte_silent(0xFFFF)
                if(ie_flag&0x04 and z80.state.interrupt_master_enable):
                    if_flag = mem.read_byte_silent(0xFF0F)
                    mem.write_byte(0xFF0F, if_flag|0x04)
                
def read_byte(addr):
    return mem.iomem[addr-0xFF00]

# DIV - Divider Register (R/W)
def write_byte_0xFF04(addr, byte):
    mem.iomem[0x04] = 0x00

# TIMA - Timer Counter (R/W)
def write_byte_0xFF05(addr, byte):
    mem.iomem[0x05] = byte
    
# TMA - Timer Modulo (R/W)
def write_byte_0xFF06(addr, byte):
    mem.iomem[0x06] = byte
    
# TAC - Timer Control (R/W)
def write_byte_0xFF07(addr, byte):
    mem.iomem[0x07] = byte&0x07
    state.timer_on = (byte>>2)&0x01
    state.timer_clock = (byte)&0x03
    state.timer_cycles_per_increment = timer_cycles_per_increment_map[state.timer_clock]
    if(not state.timer_on):
        state.timer_cycle_counter = 0
    