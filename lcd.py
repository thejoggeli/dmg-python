import z80
import dlog
import mem

class State:
    enabled = 1
    #frame_count = 0
    frame_cycle_count = 0
    scanline_cycle_count = 0
    scanline_count = 0
state = State()

def init():
    pass
    
def map_memory():
    mem.write_map[0xFF40] = write_byte_0xFF40
    mem.write_map[0xFF41] = write_byte_0xFF41
    mem.write_map[0xFF44] = write_byte_0xFF44
    mem.write_map[0xFF45] = write_byte_0xFF45
    
    mem.read_map[0xFF40] = read_byte
    mem.read_map[0xFF41] = read_byte
    mem.read_map[0xFF44] = read_byte
    mem.read_map[0xFF45] = read_byte
    
    mem.name_map[0xFF40] = lambda: "LCDC - LCD Control (R/W)"
    mem.name_map[0xFF41] = lambda: "STAT - LCD Status (R/W)"
    mem.name_map[0xFF44] = lambda: "LY - LCD Current Scanline (R)"
    mem.name_map[0xFF45] = lambda: "LYC - LY Compare (R/W)"

def update():
    state.frame_cycle_count += z80.state.cycles_delta
    state.scanline_cycle_count += z80.state.cycles_delta
    
    # update 0xFF44
    if(state.scanline_cycle_count >= 456):
        state.scanline_cycle_count -= 456
        state.scanline_count += 1
        if(state.scanline_count >= 154):
            state.scanline_count -= 154
           #state.frame_count += 1
            state.frame_cycle_count -= 70224
        mem.write_byte(0xFF44, state.scanline_count)
        
    # TODO implement 0xFF40   
    # TODO implement 0xFF41 
    # TODO implement 0xFF45
            
    if(dlog.enable.lcd):
        print_state()
    
def read_byte(addr):
    return mem.io_mem[addr-0xFF00]
    
# LCDC – LCD Control (R/W)    
def write_byte_0xFF40(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_byte_0xFF40 not implemented")
    mem.io_mem[0x40] = byte

# STAT – LCD Status (R/W)
def write_byte_0xFF41(addr, byte):    
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_byte_0xFF41 not implemented")
    mem.io_mem[0x41] = byte

# LY – LCD Current Scanline (R)
def write_byte_0xFF44(addr, byte):
    mem.io_mem[0x44] = byte

# LYC – LY Compare (R/W)
def write_byte_0xFF45(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_0xFF45 not implemented")  
    mem.io_mem[0x45] = byte 
    
def print_state():
   #frame = "F=" + str(state.frame_count) + "/" + str(state.frame_cycle_count)
   #scanline = "S=" + str(state.scanline_count) + "/" + str(state.scanline_cycle_count)
    dlog.print_msg(
        "LCD", 
        "lcdisplay" + "\t" +
        "Enabled=" + str(state.enabled) + "\t" + 
        #"FC=" + str(state.frame_cycle_count)+ "\t"
        "0xFF40=" + "0x{0:0{1}X}".format(mem.io_mem[0x40], 2) + "\t" +
        "0xFF41=" + "0x{0:0{1}X}".format(mem.io_mem[0x41], 2) + "\t" +
        "0xFF44=" + "0x{0:0{1}X}".format(mem.io_mem[0x44], 2) + "\t" + 
        "0xFF45=" + "0x{0:0{1}X}".format(mem.io_mem[0x45], 2) + "\t"
       #frame.ljust(16, " ") +
       #scanline.ljust(16, " ")
    )
