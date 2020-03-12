import sdl2
import sdlboy_console_component
import sdlboy_time
import hw_video as vid
import ctypes
import math

class Color:
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.c_argb = (ctypes.c_uint)((a<<24)|(r<<16)|(g<<8)|b)

class Tileview(sdlboy_console_component.ConsoleComponent):
    pixels = None
    tiles_texture = None
    tiles_texture_rect = None
    tiles_color_map = None
    tiles_num_rows = 0
    tiles_num_cols = 0
    tiles_scale = 0
    tiles_spacing = 0
    last_render_time = 0
    def on_init(self):
        self.tiles_color_map = [None]*4
        self.tiles_color_map[3] = Color(0x00, 0x00, 0x00)
        self.tiles_color_map[2] = Color(0x55, 0x55, 0x55)
        self.tiles_color_map[1] = Color(0xAA, 0xAA, 0xAA)
        self.tiles_color_map[0] = Color(0xFF, 0xFF, 0xFF)
    def on_visible(self):
        if(self.tiles_texture == None):
            self.tiles_texture_rect = sdl2.SDL_Rect(0,0,0,0)
            self.tiles_texture_dst_rect = sdl2.SDL_Rect(0,0,0,0)       
    def on_update(self):
        if(sdlboy_time.since_start - self.last_render_time > 0.25):
            self.set_render_required()        
    def on_render(self):        
        self.last_render_time = sdlboy_time.since_start
        pixels = self.pixels
        color_map = self.tiles_color_map
        pattern_ptr = 0
        pixel_index = 0
        col_counter = 0
        for i in range(0, 512):
            # draw tile row by row 
            for j in range(0, 8):          
                byte_1 = vid.videoram[pattern_ptr]       
                byte_2 = vid.videoram[pattern_ptr+1]       
                pixels[pixel_index+0] = color_map[((byte_2>>6)&0x2)|((byte_1>>7)&0x1)].c_argba
                pixels[pixel_index+1] = color_map[((byte_2>>5)&0x2)|((byte_1>>6)&0x1)].c_argba
                pixels[pixel_index+2] = color_map[((byte_2>>4)&0x2)|((byte_1>>5)&0x1)].c_argba
                pixels[pixel_index+3] = color_map[((byte_2>>3)&0x2)|((byte_1>>4)&0x1)].c_argba
                pixels[pixel_index+4] = color_map[((byte_2>>2)&0x2)|((byte_1>>3)&0x1)].c_argba
                pixels[pixel_index+5] = color_map[((byte_2>>1)&0x2)|((byte_1>>2)&0x1)].c_argba
                pixels[pixel_index+6] = color_map[((byte_2>>0)&0x2)|((byte_1>>1)&0x1)].c_argba
                pixels[pixel_index+7] = color_map[((byte_2<<1)&0x2)|((byte_1>>0)&0x1)].c_argba
                # point to next pair of bytes
                pattern_ptr += 2                
                # point to next row
                pixel_index += self.tiles_texture_rect.w
            col_counter += 1
            if(col_counter == self.tiles_num_cols):
                col_counter = 0
                pixel_index += self.tiles_texture_rect.w*(self.tiles_spacing-1)
                pixel_index += 8
            else:
                pixel_index -= self.tiles_texture_rect.w*8
                pixel_index += (8+self.tiles_spacing)
        sdl2.SDL_UpdateTexture(
            self.tiles_texture,
            self.tiles_texture_rect,
            pixels,
            self.tiles_texture_rect.w*4
        )
        sdl2.SDL_RenderCopy(
            self.renderer,
            self.tiles_texture,
            self.tiles_texture_rect,
            self.tiles_texture_dst_rect
        )
    def on_resize(self):
        pass
    def set_tiles_dimensions(self, num_rows, num_cols, scale, spacing):
        if(num_rows == self.tiles_num_rows 
           and num_cols == self.tiles_num_cols 
           and scale == self.tiles_scale
           and spacing == self.tiles_spacing
        ):
            return        
        self.tiles_num_rows = num_rows
        self.tiles_num_cols = num_cols
        self.tiles_scale = scale
        self.tiles_spacing = spacing
        pixels_inital = [0]*(0x8000)
        self.pixels = ((ctypes.c_uint)*(256*256))(*pixels_inital)
        self.tiles_texture_rect.w = self.tiles_num_cols*(8+self.tiles_spacing)-self.tiles_spacing 
        self.tiles_texture_rect.h = self.tiles_num_rows*(8+self.tiles_spacing)-self.tiles_spacing
        self.tiles_texture_dst_rect.w = self.tiles_texture_rect.w*self.tiles_scale
        self.tiles_texture_dst_rect.h = self.tiles_texture_rect.h*self.tiles_scale
        if(self.tiles_texture):
            sdl2.SDL_DestroyTexture(self.tiles_texture)        
        self.tiles_texture = sdl2.SDL_CreateTexture(
            self.renderer, 
            sdl2.SDL_PIXELFORMAT_ARGB8888, 
            sdl2.SDL_TEXTUREACCESS_TARGET,
            self.tiles_texture_rect.w,
            self.tiles_texture_rect.h
        )
        self.preferred_h = self.tiles_texture_dst_rect.h
    def on_present_width(self, w):
        spacing = 1
        scale = 2
        tile_width = (8+spacing)*scale
        try:
            cols = math.floor(w/tile_width)
            cols = cols - (cols%8) # make cols multiple of 8 (round down)
            rows = math.ceil(512/cols)
        except Exception as e:
            cols = 64
            rows = 8
            print(e)        
        self.set_tiles_dimensions(rows, cols, scale, spacing)
                
                
                
                
                
                