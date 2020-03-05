import z80
import dlog
import mem

class State:
    enabled = 1
    frame_count = 0
    frame_cycle_count = 0
    scanline_cycle_count = 0
    scanline_count = 0
state = State()

def init():
    pass
    
def map_memory():
    mem.io_write_map[0x40] = write_40
    mem.io_write_map[0x41] = write_41
    mem.io_write_map[0x44] = write_44
    mem.io_write_map[0x45] = write_45
    
    mem.io_read_map[0x40] = read_nofun
    mem.io_read_map[0x41] = read_nofun
    mem.io_read_map[0x44] = read_nofun
    mem.io_read_map[0x45] = read_nofun
    
    mem.io_name_map[0x40] = lambda addr: "LCDC - LCD Control (R/W)"
    mem.io_name_map[0x41] = lambda addr: "STAT - LCD Status (R/W)"
    mem.io_name_map[0x44] = lambda addr: "LY - LCD Current Scanline (R)"
    mem.io_name_map[0x45] = lambda addr: "LYC - LY Compare (R/W)"

def update():
    state.frame_cycle_count += z80.state.cycles_delta
    state.scanline_cycle_count += z80.state.cycles_delta
    
    # update 0xFF44
    if(state.scanline_cycle_count >= 456):
        state.scanline_cycle_count -= 456
        state.scanline_count += 1
        if(state.scanline_count >= 154):
            state.scanline_count -= 154
            state.frame_count += 1
            state.frame_cycle_count -= 70224
        mem.io_mem[0x44] = state.scanline_count
        
    # update 0xFF40h
    # TODO
    
    # update 0xFF41h
    # TODO
    
    # update 0xFF45h
    # TODO
            
    if(dlog.enable.lcd):
        print_state()
    
def read_nofun(addr):
    pass
    
# LCDC – LCD Control (R/W)    
def write_40(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_40 not implemented")

# STAT – LCD Status (R/W)
def write_41(addr, byte):    
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_41 not implemented")

# LY – LCD Current Scanline (R)
def write_44(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_44 not implemented")

# LYC – LY Compare (R/W)
def write_45(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_45 not implemented")   
    
def print_state():
    frame = "F=" + str(state.frame_count) + "/" + str(state.frame_cycle_count)
    scanline = "S=" + str(state.scanline_count) + "/" + str(state.scanline_cycle_count)
    dlog.print_msg(
        "LCD", 
        "lcdisplay" + "\t" +
        "Enabled=" + str(state.enabled) + "\t" + 
        frame.ljust(16, " ") +
        scanline.ljust(16, " ")
    )
