import util_dlog as dlog
import util_events as events
import hw_z80 as z80
import hw_mem as mem
import hw_video as vid
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
        
pixels_sprites_p0 = None
pixels_sprites_p1 = None
pixels_background = None
lcd_background_color = None
sprite_color_palette = None
sprite_color_map     = None
bg_color_palette     = None
bg_color_map         = None

class State:
    enabled = 1
    #frame_count = 0
    frame_cycle_count = 0
    scanline_cycle_count = 0
    scanline_count = 0
state = State()

def init():

    global state
    state = State()
    
    global lcd_background_color
    global sprite_color_palette, sprite_color_map
    global bg_color_palette, bg_color_map
    
    lcd_background_color = Color(0xFF, 0xFF, 0xFF)
    
    sprite_color_palette    = [None]*4
    sprite_color_palette[3] = Color(0x00, 0x00, 0x00)
    sprite_color_palette[2] = Color(0x55, 0x55, 0x55)
    sprite_color_palette[1] = Color(0xAA, 0xAA, 0xAA)
    sprite_color_palette[0] = Color(0xFF, 0xFF, 0xFF)
    sprite_color_map        = [None]*4
    
    bg_color_palette    = [None]*4
    bg_color_palette[3] = Color(0x00, 0x00, 0x00)
    bg_color_palette[2] = Color(0x55, 0x55, 0x55)
    bg_color_palette[1] = Color(0xAA, 0xAA, 0xAA)
    bg_color_palette[0] = Color(0xFF, 0xFF, 0xFF)
    bg_color_map        = [None]*4

    global pixels_sprites_p0, pixels_sprites_p1, pixels_background
    pixels_sprites_pn_inital = [0xFF0000]*(176*176)
    pixels_background_inital = [0x00FF00]*(256*256)
    pixels_sprites_p0 = ((ctypes.c_uint)*(176*176))(*pixels_sprites_pn_inital)
    pixels_sprites_p1 = ((ctypes.c_uint)*(176*176))(*pixels_sprites_pn_inital)
    pixels_background = ((ctypes.c_uint)*(256*256))(*pixels_background_inital)
    set_pixel(pixels_background,   0,   0, 0xFF0000FF)
    set_pixel(pixels_background,   1,   1, 0x00FF00FF)
    set_pixel(pixels_background,   2,   2, 0x0000FFFF)
    set_pixel(pixels_background, 157,   0, 0x00000000)
    set_pixel(pixels_background, 158,   0, 0x00000000)
    set_pixel(pixels_background, 159,   1, 0xFFFFFFFF)
    set_pixel(pixels_background, 159,   2, 0xFFFFFFFF)
    set_pixel(pixels_background, 159, 143, 0x00FFFFFF)
    set_pixel(pixels_background, 158, 142, 0xFF00FFFF)
    set_pixel(pixels_background, 157, 141, 0xFFFF00FF)
    
def set_pixel(pixels, x, y, rgba):
    pixels[y*256+x] = rgba
    
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
            # reset V-Blank interrupt flag
           #mem.iomem[0x0F] &= 0xFE             
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
    if(mem.iomem[0x0F]&0x01):
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
            mem.iomem[0x41] = (mem.iomem[0x41]&0xFC)|0x00 
            # set STAT interrupt flag
            if(mem.iomem[0x41]&0x80 and mem.iomem[0x41]&0x03 != 0x00):
                mem.iomem[0x0F] |= 0x02
    
def render():

    lcdc   = mem.iomem[0x40]
    lcdc_7 = (lcdc>>7)&0x01 # LCD Control Operation
    lcdc_6 = (lcdc>>6)&0x01 # Window Tile Map Display Select
    lcdc_5 = (lcdc>>5)&0x01 
    lcdc_4 = (lcdc>>4)&0x01 # BG & Window Tile Data Select
    lcdc_3 = (lcdc>>3)&0x01 # BG Tile Map Display Select
    lcdc_2 = (lcdc>>2)&0x01 
    lcdc_1 = (lcdc>>1)&0x01 
    lcdc_0 = (lcdc>>0)&0x01 # BG & Window Display
    
    # LCD operation is off
    if(lcdc_7 == 0):
        for i in range(0, len(pixels_background)):
            pixels_background[i] = lcd_background_color.c_rgba
        return
        for i in range(0, len(pixels_sprites_p0)):
            pixels_sprites_p0[i] = lcd_background_color.c_rgba
            pixels_sprites_p1[i] = lcd_background_color.c_rgba
        return
        
    # Background & Window Display
    if(lcdc_0 == 1):
        # BG & Window Palette Data
        bgp = mem.iomem[0x47]        
        bg_color_map[3] = bg_color_palette[(bgp>>6)&0x3]
        bg_color_map[2] = bg_color_palette[(bgp>>4)&0x3]
        bg_color_map[1] = bg_color_palette[(bgp>>2)&0x3]
        bg_color_map[0] = bg_color_palette[(bgp>>0)&0x3]
                
        # BG Tile Map Display Select
        bg_tile_map_ptr_start = 0
        bg_tile_map_ptr_end   = 0 
        if(lcdc_3 == 0):
            # 0x9800-0x9BFF
            bg_tile_map_ptr_start = 0x9800-0x8000
            bg_tile_map_ptr_end   = 0x9C00-0x8000
        else: 
            # 0x9C00-0x9FFF
            bg_tile_map_ptr_start = 0x9C00-0x8000
            bg_tile_map_ptr_end   = 0xA000-0x8000
                
        # BG & Window Tile Data Select
        if(lcdc_4 == 0):
            # 0x8800-0x97FF with signed offset
            tile_x_index = 0
            pixel_index_offset = 0            
            for bg_tile_map_ptr in range(bg_tile_map_ptr_start, bg_tile_map_ptr_end):
                # find tile data
                bg_tile_data_ptr = vid.videoram[bg_tile_map_ptr]            
                if(bg_tile_data_ptr > 127):
                    bg_tile_data_ptr -= 256
                bg_tile_data_ptr = bg_tile_data_ptr*16 + 0x1000
                # draw tile
                pixel_index = pixel_index_offset
                for i in range(0, 8):        
                    byte_1 = vid.videoram[bg_tile_data_ptr]       
                    byte_2 = vid.videoram[bg_tile_data_ptr+1]       
                    pixels_background[pixel_index+0] = bg_color_map[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_rgba
                    pixels_background[pixel_index+1] = bg_color_map[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_rgba
                    pixels_background[pixel_index+2] = bg_color_map[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_rgba
                    pixels_background[pixel_index+3] = bg_color_map[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_rgba
                    pixels_background[pixel_index+4] = bg_color_map[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_rgba
                    pixels_background[pixel_index+5] = bg_color_map[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_rgba
                    pixels_background[pixel_index+6] = bg_color_map[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_rgba
                    pixels_background[pixel_index+7] = bg_color_map[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_rgba
                    pixel_index += 256
                    bg_tile_data_ptr += 2                
                # next tile
                tile_x_index += 1
                if(tile_x_index == 32):
                    tile_x_index = 0
                    pixel_index_offset += (256*7+8)
                else:
                    pixel_index_offset += 8         
        else:
            # 0x8000-0x8FFF with unsigned offset
            tile_x_index = 0
            pixel_index_offset = 0            
            for bg_tile_map_ptr in range(bg_tile_map_ptr_start, bg_tile_map_ptr_end):
                # find tile data
                bg_tile_data_ptr = vid.videoram[bg_tile_map_ptr]*16
                # draw tile
                pixel_index = pixel_index_offset
                for i in range(0, 8):          
                    byte_1 = vid.videoram[bg_tile_data_ptr]       
                    byte_2 = vid.videoram[bg_tile_data_ptr+1]       
                    pixels_background[pixel_index+0] = bg_color_map[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_rgba
                    pixels_background[pixel_index+1] = bg_color_map[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_rgba
                    pixels_background[pixel_index+2] = bg_color_map[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_rgba
                    pixels_background[pixel_index+3] = bg_color_map[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_rgba
                    pixels_background[pixel_index+4] = bg_color_map[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_rgba
                    pixels_background[pixel_index+5] = bg_color_map[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_rgba
                    pixels_background[pixel_index+6] = bg_color_map[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_rgba
                    pixels_background[pixel_index+7] = bg_color_map[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_rgba
                    pixel_index += 256
                    bg_tile_data_ptr += 2                
                # next tile
                tile_x_index += 1
                if(tile_x_index == 32):
                    tile_x_index = 0
                    pixel_index_offset += (256*7+8)
                else:
                    pixel_index_offset += 8
                    
    # OBJ (Sprite) Display
    if(lcdc_1):
        spritemem_ptr = 0
        if(lcdc_2):
            # 8x16 sprites  
            for i in range(0, 40):
                # read spritemem
                y       = vid.spritemem[spritemem_ptr]-16
                x       = vid.spritemem[spritemem_ptr+1]-8            
                pattern = vid.spritemem[spritemem_ptr+2]&0xFE
                flags   = vid.spritemem[spritemem_ptr+3]    
                # TODO implement flags
                # color map
                sprite_color_map[0] = sprite_color_palette[0]
                sprite_color_map[1] = sprite_color_palette[1]
                sprite_color_map[2] = sprite_color_palette[2]
                sprite_color_map[3] = sprite_color_palette[3]
                # draw pattern
                pattern_ptr = pattern*16
                pixel_ptr = y*176+x
                for i in range(0, 16):
                    byte_1 = vid.videoram[pattern_ptr]       
                    byte_2 = vid.videoram[pattern_ptr+1]       
                    pixels_sprites_p0[pixel_ptr+0] = sprite_color_map[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+1] = sprite_color_map[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+2] = sprite_color_map[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+3] = sprite_color_map[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+4] = sprite_color_map[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+5] = sprite_color_map[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+6] = sprite_color_map[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+7] = sprite_color_map[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_rgba
                    pixel_ptr += 176
                    pattern_ptr += 2
                # increment for next sprite
                spritemem_ptr += 4      
        else:
            # 8x8 sprites            
            for i in range(0, 40):
                # read spritemem
                y       = vid.spritemem[spritemem_ptr]-16
                x       = vid.spritemem[spritemem_ptr+1]-8            
                pattern = vid.spritemem[spritemem_ptr+2]            
                flags   = vid.spritemem[spritemem_ptr+3]   
                # TODO implement flags 
                # color map
                sprite_color_map[0] = sprite_color_palette[0]
                sprite_color_map[1] = sprite_color_palette[1]
                sprite_color_map[2] = sprite_color_palette[2]
                sprite_color_map[3] = sprite_color_palette[3]
                # draw pattern
                pattern_ptr = pattern*16
                pixel_ptr = y*176+x
                for i in range(0, 8):
                    byte_1 = vid.videoram[pattern_ptr]       
                    byte_2 = vid.videoram[pattern_ptr+1]       
                    pixels_sprites_p0[pixel_ptr+0] = sprite_color_map[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+1] = sprite_color_map[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+2] = sprite_color_map[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+3] = sprite_color_map[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+4] = sprite_color_map[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+5] = sprite_color_map[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+6] = sprite_color_map[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_rgba
                    pixels_sprites_p0[pixel_ptr+7] = sprite_color_map[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_rgba
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
    mem.iomem[0x47] = byte 

# OBP0 - Object Palette 0 Data (R/W)
def write_byte_0xFF48(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_byte_0xFF48 not implemented")  
    mem.iomem[0x48] = byte 
    
# OBP1 - Object Palette 1 Data (R/W)
def write_byte_0xFF49(addr, byte):
    if(dlog.enable.mem_warnings):
        dlog.print_warning("LCD", "write_byte_0xFF49 not implemented")  
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
