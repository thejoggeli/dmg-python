import util_dlog as dlog
import util_events as events
import hw_z80 as z80
import hw_mem as mem
import ctypes

WIDTH = 160
HEIGHT = 144

pixels = None 

class State:
    enabled = 1
    #frame_count = 0
    frame_cycle_count = 0
    scanline_cycle_count = 0
    scanline_count = 0
state = State()

def init():
    global pixels
    pixels = ((ctypes.c_int)*(WIDTH*HEIGHT))()
    pixels[0*WIDTH+0] = 0xFF0000FF
    pixels[1*WIDTH+1] = 0x00FF00FF
    pixels[2*WIDTH+2] = 0x0000FFFF
    pixels[1*WIDTH-1] = 0xFFFFFFFF
    pixels[1*WIDTH-2] = 0xFFFFFFFF
    pixels[1*WIDTH-3] = 0xFFFFFFFF
    pixels[2*WIDTH-1] = 0xFFFFFFFF
    pixels[3*WIDTH-1] = 0xFFFFFFFF
    pixels[WIDTH*HEIGHT-1] = 0x00FFFFFF
    pixels[WIDTH*HEIGHT-WIDTH*1-2] = 0xFF00FFFF
    pixels[WIDTH*HEIGHT-WIDTH*2-3] = 0xFFFF00FF
    
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
        events.fire(events.EVENT_SCANLINE_CHANGE, (state.scanline_count))
        
    # TODO implement 0xFF40   
    # TODO implement 0xFF41 
    # TODO implement 0xFF45
            
    if(dlog.enable.lcd):
        print_state()
    
def read_byte(addr):
    return mem.iomem[addr-0xFF00]
    
# LCDC – LCD Control (R/W)    
# Bit   Function                    Value=0             Value=1
# 7     Control Operation           Stop completey      Operation          
# 6     Tile Map Select             0x9800-0x9BFF       0x9C00-0x9FFF               
# 5     Window Display              Off                 On
# 4     BG&Window Tile Data Select  Off                 On
# 3     BG Tile Map Display Select  Off                 On
# 3     BG Tile Map Display Select  Off                 On
def write_byte_0xFF40(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_byte_0xFF40 not implemented")
    mem.iomem[0x40] = byte

# STAT – LCD Status (R/W)
def write_byte_0xFF41(addr, byte):    
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_byte_0xFF41 not implemented")
    mem.iomem[0x41] = byte

# LY – LCD Current Scanline (R)
def write_byte_0xFF44(addr, byte):
    mem.iomem[0x44] = byte

# LYC – LY Compare (R/W)
def write_byte_0xFF45(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_0xFF45 not implemented")  
    mem.iomem[0x45] = byte 
    
def print_state():
   #frame = "F=" + str(state.frame_count) + "/" + str(state.frame_cycle_count)
   #scanline = "S=" + str(state.scanline_count) + "/" + str(state.scanline_cycle_count)
    dlog.print_msg(
        "LCD", 
        "lcdisplay" + "\t" +
        "Enabled=" + str(state.enabled) + "\t" + 
       #"FC=" + str(state.frame_cycle_count)+ "\t"
        "0xFF40=" + "0x{0:0{1}X}".format(mem.iomem[0x40], 2) + "\t" +
        "0xFF41=" + "0x{0:0{1}X}".format(mem.iomem[0x41], 2) + "\t" +
        "0xFF44=" + "0x{0:0{1}X}".format(mem.iomem[0x44], 2) + "\t" + 
        "0xFF45=" + "0x{0:0{1}X}".format(mem.iomem[0x45], 2) + "\t"
       #frame.ljust(16, " ") +
       #scanline.ljust(16, " ")
    )
