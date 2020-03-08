import util_dlog as dlog
import util_events as events
import hw_z80 as z80
import hw_mem as mem
import ctypes

WIDTH = 160
HEIGHT = 144

class Color:
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.c_rgba = (ctypes.c_uint)((r<<24)|(r<<16)|(r<<8)|a)
        
color_map = [None]*4
color_map[3] = Color(0x00, 0x00, 0x00)
color_map[2] = Color(0x55, 0x55, 0x55)
color_map[1] = Color(0xAA, 0xAA, 0xAA)
color_map[0] = Color(0xFF, 0xFF, 0xFF)

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
    pixels_inital = [0xFF00FFFF]*WIDTH*HEIGHT
    pixels = ((ctypes.c_uint)*(WIDTH*HEIGHT))(*pixels_inital)
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
    mem.write_map[0xFF42] = write_byte_0xFF42
    mem.write_map[0xFF43] = write_byte_0xFF43
    mem.write_map[0xFF44] = write_byte_0xFF44
    mem.write_map[0xFF45] = write_byte_0xFF45
    mem.write_map[0xFF46] = write_byte_0xFF46
    mem.write_map[0xFF47] = write_byte_0xFF47
    mem.write_map[0xFF48] = write_byte_0xFF48
    mem.write_map[0xFF49] = write_byte_0xFF49
    mem.write_map[0xFF4A] = write_byte_0xFF4A
    mem.write_map[0xFF4B] = write_byte_0xFF4B
    
    mem.read_map[0xFF40] = read_byte
    mem.read_map[0xFF41] = read_byte
    mem.read_map[0xFF42] = read_byte
    mem.read_map[0xFF43] = read_byte
    mem.read_map[0xFF44] = read_byte
    mem.read_map[0xFF45] = read_byte
    mem.read_map[0xFF46] = read_byte
    mem.read_map[0xFF47] = read_byte
    mem.read_map[0xFF48] = read_byte
    mem.read_map[0xFF49] = read_byte
    mem.read_map[0xFF4A] = read_byte
    mem.read_map[0xFF4B] = read_byte
    
    mem.name_map[0xFF40] = lambda: "LCDC - LCD Control (R/W)"
    mem.name_map[0xFF41] = lambda: "STAT - LCD Status (R/W)"
    mem.name_map[0xFF42] = lambda: "LCY - LCY Status (R/W)"
    mem.name_map[0xFF43] = lambda: "LCX - LCX Status (R/W)"
    mem.name_map[0xFF44] = lambda: "LY - LCD Current Scanline (R)"
    mem.name_map[0xFF45] = lambda: "LYC - LY Compare (R/W)"
    mem.name_map[0xFF46] = lambda: "DMA - Transfer and Start Address (W)"
    mem.name_map[0xFF47] = lambda: "BGP - BG & Window Palette Data (R/W)"
    mem.name_map[0xFF48] = lambda: "OBP0 - Object Palette 0 Data (R/W)"
    mem.name_map[0xFF49] = lambda: "OBP1 - Object Palette 1 Data (R/W)"
    mem.name_map[0xFF4A] = lambda: "WY - Window Y Position (R/W)"
    mem.name_map[0xFF4B] = lambda: "WX - Window X Position (R/W)"

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
    
def render():
    lcdc   = mem.iomem[0x40]
    lcdc_7 = (lcdc>>7)&0x01 # LCD Control Operation
    lcdc_6 = (lcdc>>6)&0x01 # Window Tile Map Display Select
    lcdc_5 = (lcdc>>5)&0x01 
    lcdc_4 = (lcdc>>4)&0x01 
    lcdc_3 = (lcdc>>3)&0x01 # BG Tile Map Display Select
    lcdc_2 = (lcdc>>2)&0x01 
    lcdc_1 = (lcdc>>1)&0x01 
    lcdc_0 = (lcdc>>0)&0x01 # BG & Window Display
    
    # LCD operation is off
    if(lcdc_7 == 0):
        for i in range(0, len(pixels)):
            pixels[i] = color_map[0].c_rgba
        return
        
    # Background & Window Display
    if(lcdc_0 == 1):
        # BG & Window Palette Data
        bgp    = mem.iomem[0x47]
        bgp_76 = (bgp>>6)&0x3
        bgp_54 = (bgp>>4)&0x3
        bgp_32 = (bgp>>2)&0x3
        bgp_10 = (bgp>>0)&0x3        
        # BG Tile Map Display Select
        if(lcdc_3 == 0):
            # $9800-$9BFF
            pass
        else: 
            # $9C00-$9FFF
            pass
            
    
    return
    
def read_byte(addr):
    return mem.iomem[addr-0xFF00]
    
# LCDC – LCD Control (R/W)    
# Bit   Function                    Value=0             Value=1
# 7     Control Operation           Stop completey      Operation          
# 6     Tile Map Select             0x9800-0x9BFF       0x9C00-0x9FFF               
# 5     Window Display              Off                 On
# 4     BG&Window Tile Data Select  Off                 On
# 3     BG Tile Map Display Select  Off                 On
# 2     OBJ (Sprite) Size           8x8                 8x16 (WxH)    
# 1     OBJ (Sprite) Display        Off                 On
# 0     BG & Window Display         Off                 On
def write_byte_0xFF40(addr, byte):
    mem.iomem[0x40] = byte

# STAT – LCD Status (R/W)
def write_byte_0xFF41(addr, byte):    
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_byte_0xFF41 not implemented")
    mem.iomem[0x41] = byte

# SCY - Scroll Y
def write_byte_0xFF42(addr, byte):    
    mem.iomem[0x42] = byte

# SCX - Scroll X
def write_byte_0xFF43(addr, byte):    
    mem.iomem[0x43] = byte

# LY – LCD Current Scanline (R)
def write_byte_0xFF44(addr, byte):
    mem.iomem[0x44] = byte

# LYC – LY Compare (R/W)
def write_byte_0xFF45(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_0xFF45 not implemented")  
    mem.iomem[0x45] = byte 
   
# DMA - Transfer and Start Address
def write_byte_0xFF46(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_0xFF46 not implemented")  
    mem.iomem[0x46] = byte 
    
# BGP - BG & Window Palette Data (R/W)
def write_byte_0xFF47(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_0xFF47 not implemented")  
    mem.iomem[0x47] = byte 

# OBP0 - Object Palette 0 Data (R/W)
def write_byte_0xFF48(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_0xFF48 not implemented")  
    mem.iomem[0x48] = byte 
    
# OBP1 - Object Palette 1 Data (R/W)
def write_byte_0xFF49(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_0xFF49 not implemented")  
    mem.iomem[0x49] = byte 

# WY - Window Y Position (R/W)
def write_byte_0xFF4A(addr, byte):
    mem.iomem[0x4A] = byte 

# WX - Window X Position (R/W)
def write_byte_0xFF4B(addr, byte):
    mem.iomem[0x4B] = byte 
    
def print_state():
    dlog.print_msg(
        "LCD", 
        "Enabled=" + str(state.enabled) + "\t" + 
        "0xFF40=" + "0x{0:0{1}X}".format(mem.iomem[0x40], 2) + "\t" +
        "0xFF41=" + "0x{0:0{1}X}".format(mem.iomem[0x41], 2) + "\t" +
        "0xFF44=" + "0x{0:0{1}X}".format(mem.iomem[0x44], 2) + "\t" + 
        "0xFF45=" + "0x{0:0{1}X}".format(mem.iomem[0x45], 2),
        cat="lcddisplay"
    )
