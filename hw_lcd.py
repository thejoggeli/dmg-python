import util_dlog as dlog
import util_events as events
import hw_z80 as z80
import hw_mem as mem
import hw_video as vid
import ctypes

class Color:
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.c_argb = (ctypes.c_uint)((a<<24)|(r<<16)|(g<<8)|b)

pixels_background_back = None
pixels_sprites_p1_back = None
pixels_sprites_p0_back = None

pixels_background_front = None
pixels_sprites_p1_front = None
pixels_sprites_p0_front = None

color_t = None # transparent
color_0 = None # lightest
color_1 = None # light
color_2 = None # dark
color_3 = None # darkest

color_palette_background = None
color_palette_sprites_p1 = None
color_palette_sprites_p0 = None

color_map_background = None
color_map_sprites_p1 = None
color_map_sprites_p0 = None

class State:
    enabled = 1
    #frame_count = 0
    frame_cycle_count = 0
    scanline_cycle_count = 0
    scanline_count = 0
    is_on = False    
    lcdc_b7 = 0
    lcdc_b6 = 0
    lcdc_b5 = 0
    lcdc_b4 = 0
    lcdc_b3 = 0
    lcdc_b2 = 0
    lcdc_b1 = 0
    lcdc_b0 = 0    
    background_tile_map_offset = 0x1800
    
state = None

def init():

    global state
    state = State()
    
    global color_t, color_0, color_1, color_2, color_3    
    global color_palette_background, color_map_background
    global color_palette_sprites_p1, color_map_sprites_p1
    global color_palette_sprites_p0, color_map_sprites_p0    
    color_t = Color(0, 0, 0, 0)
    color_0 = Color(0xFF, 0xFF, 0xFF, 255)
    color_1 = Color(0xAA, 0xAA, 0xAA, 255)
    color_2 = Color(0x55, 0x55, 0x55, 255)
    color_3 = Color(0x00, 0x00, 0x00, 255)      
    color_palette_background = [color_0, color_1, color_2, color_3]
    color_palette_sprites_p1 = [color_0, color_1, color_2, color_3]
    color_palette_sprites_p0 = [color_t, color_1, color_2, color_3]     
    color_map_background     = [color_0, color_0, color_0, color_0]
    color_map_sprites_p1     = [color_0, color_0, color_0, color_0]
    color_map_sprites_p0     = [color_t, color_0, color_0, color_0]
        
    # screen on buffers
    global pixels_background_back, pixels_background_front
    global pixels_sprites_p1_back, pixels_sprites_p1_front
    global pixels_sprites_p0_back, pixels_sprites_p0_front
    pixels_inital = [0]*(176*176)   
    pixels_background_front = ((ctypes.c_uint)*(176*176))(*pixels_inital)
    pixels_sprites_p1_front = ((ctypes.c_uint)*(176*176))(*pixels_inital)
    pixels_sprites_p0_front = ((ctypes.c_uint)*(176*176))(*pixels_inital)        
    pixels_background_back  = ((ctypes.c_uint)*(176*176))(*pixels_inital)
    pixels_sprites_p1_back  = ((ctypes.c_uint)*(176*176))(*pixels_inital)
    pixels_sprites_p0_back  = ((ctypes.c_uint)*(176*176))(*pixels_inital)
    
    set_pixel(pixels_background_front,   0,   0, 0xFF0000FF)
    set_pixel(pixels_background_front,   1,   1, 0x00FF00FF)
    set_pixel(pixels_background_front,   2,   2, 0x0000FFFF)
    set_pixel(pixels_background_front, 157,   0, 0x00000000)
    set_pixel(pixels_background_front, 158,   0, 0x00000000)
    set_pixel(pixels_background_front, 159,   1, 0xFFFFFFFF)
    set_pixel(pixels_background_front, 159,   2, 0xFFFFFFFF)
    set_pixel(pixels_background_front, 159, 143, 0x00FFFFFF)
    set_pixel(pixels_background_front, 158, 142, 0xFF00FFFF)
    set_pixel(pixels_background_front, 157, 141, 0xFFFF00FF)
    
    # TODO possible memory leak
    # do ctypes.c_uint arrays need to be deleted manually on reset?

def set_pixel(pixels, x, y, rgba):
    pixels[(y+16)*176+x+8] = rgba
    
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
    mem.read_map[0xFF41] = read_byte_0xFF41
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
    
    mem.name_map[0xFF40] = lambda: "LCDC (LCD Control) (R/W)"
    mem.name_map[0xFF41] = lambda: "STAT (LCD Status) (R/W)"
    mem.name_map[0xFF42] = lambda: "LCY (LCY Status) (R/W)"
    mem.name_map[0xFF43] = lambda: "LCX (LCX Status) (R/W)"
    mem.name_map[0xFF44] = lambda: "LY (LCD Current) Scanline (R)"
    mem.name_map[0xFF45] = lambda: "LYC (LY Compare) (R/W)"
    mem.name_map[0xFF46] = lambda: "DMA (Transfer and Start Address) (W)"
    mem.name_map[0xFF47] = lambda: "BGP (BG & Window Palette Data) (R/W)"
    mem.name_map[0xFF48] = lambda: "OBP0 (Object Palette 0 Data) (R/W)"
    mem.name_map[0xFF49] = lambda: "OBP1 (Object Palette 1 Data) (R/W)"
    mem.name_map[0xFF4A] = lambda: "WY (Window Y Position) (R/W)"
    mem.name_map[0xFF4B] = lambda: "WX (Window X Position) (R/W)"

def update():
    global pixels_background_back, pixels_background_front
    global pixels_sprites_p1_back, pixels_sprites_p1_front
    global pixels_sprites_p0_back, pixels_sprites_p0_front
    state.frame_cycle_count += z80.state.cycles_delta
    state.scanline_cycle_count += z80.state.cycles_delta
        
    # update 0xFF44
    if(state.scanline_cycle_count >= 456):
        # new scanline
        state.scanline_cycle_count -= 456
        state.scanline_count += 1        
        if(state.scanline_count == 154):
            state.scanline_count = 0      
            state.frame_cycle_count -= 70224
            render_sprites()
            # reset V-Blank interrupt flag
           #mem.iomem[0x0F] &= 0xFE       
            # swap buffers
            temp = pixels_background_back
            pixels_background_back = pixels_background_front
            pixels_background_front = temp
            temp = pixels_sprites_p1_back
            pixels_sprites_p1_back = pixels_sprites_p1_front
            pixels_sprites_p1_front = temp
            temp = pixels_sprites_p0_back
            pixels_sprites_p0_back = pixels_sprites_p0_front
            pixels_sprites_p0_front = temp
        elif(state.scanline_count == 144):
            # set V-Blank interrupt flag
            mem.iomem[0x0F] |= 0x01     
            # set STAT interrupt flag  
            if(mem.iomem[0x41]&0x10):
                mem.iomem[0x0F] |= 0x02 
        if(mem.iomem[0x41]&0x40 and state.scanline_count == mem.iomem[0x45]):
            mem.iomem[0x0F] |= 0x02 # set STAT interrupt flag
        # write new scanline to LY
        mem.iomem[0x44] = state.scanline_count
        # fire new scanline event
        events.fire(events.EVENT_SCANLINE_CHANGE, (state.scanline_count))
        # STAT bit 2
        if(mem.iomem[0x45] == mem.iomem[0x44]):
            mem.iomem[0x41] |= 0x04 # set bit 2
        else:
            mem.iomem[0x41] &= 0xFB # reset bit 2

    # set STAT mode
    if(state.scanline_count >= 144):
        # mode 1 = V-Blank
        if(mem.iomem[0x41]&0x03 != 0x01):
            # mode changed
            mem.iomem[0x41] = (mem.iomem[0x41]&0xFC)|0x01 
    elif(state.scanline_cycle_count < 80):
        # mode 2 = searching OAM
        if(mem.iomem[0x41]&0x03 != 0x02):
            # mode changed
            mem.iomem[0x41] = (mem.iomem[0x41]&0xFC)|0x02 
            # set STAT interrupt flag
            if(mem.iomem[0x41]&0x20):
                mem.iomem[0x0F] |= 0x02 
    elif(state.scanline_cycle_count < 160):
        # mode 3 = transfering data
        if(mem.iomem[0x41]&0x03 != 0x03):
            # mode changed
            mem.iomem[0x41] = (mem.iomem[0x41]&0xFC)|0x03 
    else: 
        # mode 0 = H-Blank
        if(mem.iomem[0x41]&0x03 != 0x00): 
            # mode changed
            render_scanline(state.scanline_count)
            mem.iomem[0x41] = (mem.iomem[0x41]&0xFC)|0x00 
            # set STAT interrupt flag
            if(mem.iomem[0x41]&0x80 and mem.iomem[0x41]&0x03 != 0x00):
                mem.iomem[0x0F] |= 0x02

def render_scanline(scanline):
    # Background & Window Display
    if(state.lcdc_b0 == 1):
        scroll_y = mem.iomem[0x42]
        scroll_x = mem.iomem[0x43]
        tilemap_ptr = int(scroll_x/8) + 32*(int((scanline+scroll_y)/8)) + state.background_tile_map_offset
        pixel_ptr = 176*(16+scanline)+8 - scroll_x%8
        pixel_ptr_end = 176*(16+scanline) + 168
        pattern_row = (scanline+scroll_y)%8
        tilemap_ptr_wrap = (tilemap_ptr+32)-(tilemap_ptr%32) # make end multiple of 32 (round up)
        if(state.lcdc_b4 == 0):
            while(pixel_ptr < pixel_ptr_end):
                pattern_ptr = vid.videoram[tilemap_ptr]
                if(pattern_ptr > 127):
                    pattern_ptr -= 256
                pattern_ptr = pattern_ptr*16 + 2*pattern_row + 0x1000 
                byte_1 = vid.videoram[pattern_ptr]       
                byte_2 = vid.videoram[pattern_ptr+1]   
                pixels_background_back[pixel_ptr+0] = color_map_background[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_argb
                pixels_background_back[pixel_ptr+1] = color_map_background[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_argb
                pixels_background_back[pixel_ptr+2] = color_map_background[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_argb
                pixels_background_back[pixel_ptr+3] = color_map_background[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_argb
                pixels_background_back[pixel_ptr+4] = color_map_background[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_argb
                pixels_background_back[pixel_ptr+5] = color_map_background[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_argb
                pixels_background_back[pixel_ptr+6] = color_map_background[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_argb
                pixels_background_back[pixel_ptr+7] = color_map_background[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_argb
                pixel_ptr += 8
                tilemap_ptr += 1
                if(tilemap_ptr == tilemap_ptr_wrap):
                    tilemap_ptr -= 32
        else:
            while(pixel_ptr < pixel_ptr_end):     
                pattern_ptr = vid.videoram[tilemap_ptr]*16 + 2*pattern_row   
                byte_1 = vid.videoram[pattern_ptr]       
                byte_2 = vid.videoram[pattern_ptr+1]   
                pixels_background_back[pixel_ptr+0] = color_map_background[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_argb
                pixels_background_back[pixel_ptr+1] = color_map_background[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_argb
                pixels_background_back[pixel_ptr+2] = color_map_background[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_argb
                pixels_background_back[pixel_ptr+3] = color_map_background[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_argb
                pixels_background_back[pixel_ptr+4] = color_map_background[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_argb
                pixels_background_back[pixel_ptr+5] = color_map_background[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_argb
                pixels_background_back[pixel_ptr+6] = color_map_background[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_argb
                pixels_background_back[pixel_ptr+7] = color_map_background[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_argb
                pixel_ptr += 8
                tilemap_ptr += 1
                if(tilemap_ptr == tilemap_ptr_wrap):
                    tilemap_ptr -= 32
            
def render_sprites():
    
    for i in range(0, 176*176):
        pixels_sprites_p0_back[i] = color_t.c_argb
        pixels_sprites_p1_back[i] = color_t.c_argb
    
    # OBJ (Sprite) Display
    if(state.lcdc_b1):
        spritemem_ptr = 0
        if(state.lcdc_b2):
            pass
        else:
            # 8x8 sprites            
            for i in range(0, 40):
                # read spritemem
                y       = vid.spritemem[spritemem_ptr]
                x       = vid.spritemem[spritemem_ptr+1]    
                if(x > 0 and y > 0 and x < 168 and y < 160):
                    pattern = vid.spritemem[spritemem_ptr+2]            
                    flags   = vid.spritemem[spritemem_ptr+3]   
                    # TODO implement flags 
                    # TODO select color map (p0, p1)
                    # draw pattern
                    pattern_ptr = pattern*16
                    pixel_ptr = y*176+x
                    for i in range(0, 8):
                        byte_1 = vid.videoram[pattern_ptr]       
                        byte_2 = vid.videoram[pattern_ptr+1]       
                        pixels_sprites_p0_back[pixel_ptr+0] = color_map_sprites_p0[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_argb
                        pixels_sprites_p0_back[pixel_ptr+1] = color_map_sprites_p0[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_argb
                        pixels_sprites_p0_back[pixel_ptr+2] = color_map_sprites_p0[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_argb
                        pixels_sprites_p0_back[pixel_ptr+3] = color_map_sprites_p0[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_argb
                        pixels_sprites_p0_back[pixel_ptr+4] = color_map_sprites_p0[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_argb
                        pixels_sprites_p0_back[pixel_ptr+5] = color_map_sprites_p0[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_argb
                        pixels_sprites_p0_back[pixel_ptr+6] = color_map_sprites_p0[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_argb
                        pixels_sprites_p0_back[pixel_ptr+7] = color_map_sprites_p0[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_argb
                        pixel_ptr += 176
                        pattern_ptr += 2
                # increment for next sprite
                spritemem_ptr += 4                    
    return

def perform_dma(base_addr):
    addr = base_addr << 8
    if(dlog.enable.lcd):
        dlog.print_msg("LCD", "DMA at address " + "0x{0:0{1}X}".format(addr, 4), cat="dma")
    for i in range(0, 0xA0):
        vid.spritemem[i] = mem.read_byte(addr)
        addr += 1

def read_byte(addr):
    return mem.iomem[addr-0xFF00]
    
def read_byte_0xFF41(addr):
    byte = mem.iomem[0x41]
    byte |= 0x80 # bit 7 always 1    
    if(mem.iomem[0x40]&0x80==0):
        byte &= 0xF8 # bits 0-2 off if lcd off
    return byte
    
def read_byte_debug(addr):
    dlog.print_msg("LCD", "ACCESS " + "0x{0:0{1}X}".format(addr, 4))
    return mem.iomem[addr-0xFF00]
    
# LCDC – LCD Control (R/W)    
# Bit   Function                    Value=0             Value=1
# 7     Control Operation           Stop completey      Operation          
# 6     Window Tile Map Select      0x9800-0x9BFF       0x9C00-0x9FFF               
# 5     Window Display              Off                 On
# 4     BG&Window Tile Data Select  Off                 On
# 3     BG Tile Map Select          Off                 On
# 2     OBJ (Sprite) Size           8x8                 8x16 (WxH)    
# 1     OBJ (Sprite) Display        Off                 On
# 0     BG & Window Display         Off                 On
def write_byte_0xFF40(addr, byte):
    global pixels_background, pixels_sprites_p0, pixels_sprites_p1
    state.lcdc_b7 = (byte>>7)&0x01 # LCD Control Operation
    state.lcdc_b6 = (byte>>6)&0x01 # Window Tile Map Display Select
    state.lcdc_b5 = (byte>>5)&0x01 
    state.lcdc_b4 = (byte>>4)&0x01 # BG & Window Tile Data Select
    state.lcdc_b3 = (byte>>3)&0x01 # BG Tile Map Display Select
    state.lcdc_b2 = (byte>>2)&0x01 
    state.lcdc_b1 = (byte>>1)&0x01 
    state.lcdc_b0 = (byte>>0)&0x01 # BG & Window Display
        
    if(state.lcdc_b3 == 0):
        state.background_tile_map_offset = 0x1800
    else: 
        state.background_tile_map_offset = 0x1C00
    
    mem.iomem[0x40] = byte

# STAT – LCD Status (R/W)
def write_byte_0xFF41(addr, byte):
    # bits 2-0 are readonly
    mem.iomem[0x41] = (byte&0xF8)|(mem.iomem[0x41]&0x07)

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
    mem.iomem[0x45] = byte 
   
# DMA - Transfer and Start Address
def write_byte_0xFF46(addr, byte):
    mem.iomem[0x46] = byte 
    perform_dma(byte)
    
# BGP - BG & Window Palette Data (R/W)
def write_byte_0xFF47(addr, byte):
    global color_map_background
    color_map_background[3] = color_palette_background[(byte>>6)&0x3]
    color_map_background[2] = color_palette_background[(byte>>4)&0x3]
    color_map_background[1] = color_palette_background[(byte>>2)&0x3]
    color_map_background[0] = color_palette_background[(byte>>0)&0x3]
    mem.iomem[0x47] = byte     

# OBP0 - Object Palette 0 Data (R/W)
def write_byte_0xFF48(addr, byte):
    global color_map_background
    color_map_sprites_p0[3] = color_palette_sprites_p0[(byte>>6)&0x3]
    color_map_sprites_p0[2] = color_palette_sprites_p0[(byte>>4)&0x3]
    color_map_sprites_p0[1] = color_palette_sprites_p0[(byte>>2)&0x3]
    color_map_sprites_p0[0] = color_palette_sprites_p0[(byte>>0)&0x3]
    mem.iomem[0x48] = byte 
    
# OBP1 - Object Palette 1 Data (R/W)
def write_byte_0xFF49(addr, byte):
    color_map_sprites_p1[3] = color_palette_sprites_p1[(byte>>6)&0x3]
    color_map_sprites_p1[2] = color_palette_sprites_p1[(byte>>4)&0x3]
    color_map_sprites_p1[1] = color_palette_sprites_p1[(byte>>2)&0x3]
    color_map_sprites_p1[0] = color_palette_sprites_p1[(byte>>0)&0x3]
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
