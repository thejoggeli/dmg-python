import util_dlog as dlog
import os
import sdl2
from sdl2 import sdlimage as sdlimage

class Glob:
    fonts = {}
    renderer = None
glob = Glob()

def init(renderer):
    glob.renderer = renderer

def load_font(name, file="font.png", char_size=(14,18), characters=None):
    file = os.path.abspath(file)
    font = Font(name, file, char_size, characters)
    glob.fonts[name] = font
    return font
    
def get_font(name):
    return glob.fonts[name]

class Font:
    name = ""
    file = ""
    char_width = 0
    char_height = 0
    char_map = {}
    characters = [
        ' !"#$%&\'()*+,-./01',
        '23456789:;<=>?@ABC',
        'DEFGHIJKLMNOPQRSTU',
        'VWXYZ[\\]^_`abcdefg',
        'hijklmnopqrstuvwxy',
        'z{|}~',
    ]   
    texture = None
    def __init__(self, name, file, char_size, characters=None):   
        self.name = name
        self.file = file
        self.char_width = char_size[0]
        self.char_height = char_size[1] 
        
        # load image
        surface = sdlimage.IMG_Load(file.encode("utf-8"))
        if(not surface):
            dlog.print_msg("ZTEXT", "Failed to load image: " + file)
            error = sdlimage.IMG_GetError()
            dlog.print_msg("ZTEXT", str(error))
        else :
            self.texture = sdl2.SDL_CreateTextureFromSurface(glob.renderer, surface)            
            sdl2.SDL_SetTextureBlendMode(self.texture, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_FreeSurface(surface)
        
        # build character map
        if(characters):
            self.characters = characters
        for y in range(0, len(self.characters)):
            for x in range(0, len(self.characters[y])):
                c = self.characters[y][x]
                self.char_map[c] = Character(x*self.char_width, y*self.char_height)
                
    def locate(self, char, rect):
        if char in self.char_map:
            c = self.char_map[char]
            rect.x = c.x
            rect.y = c.y
    
class Character:
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
class Text:
    font = None
    value = ""
    texture = None
    buffer_size = 10
    buffer_rect = None
    char_src_rect = None
    char_dst_rect = None
    width = 0
    width_total = 0
    height = 0
    target_rect = 0
    scale = 1
    def __init__(self, font=None, value="", buffer_size=32):
        self.font = font
        self.value = value      
        self.target_rect = sdl2.SDL_Rect(
            0, 0, font.char_width, font.char_height,
        )
        self.char_src_rect = sdl2.SDL_Rect(
            0, 0, font.char_width, font.char_height
        )
        self.char_dst_rect = sdl2.SDL_Rect(
            0, 0, font.char_width, font.char_height
        )
        self.buffer_rect = sdl2.SDL_Rect(
            0, 0, 
            self.font.char_width * buffer_size,
            self.font.char_height
        )
        self.set_buffer_size(buffer_size) 
        height = font.char_height
    def set_buffer_size(self, size):
        self.buffer_size = size
        self.buffer_rect.x = 0
        self.buffer_rect.y = 0
        self.buffer_rect.w = self.font.char_width * self.buffer_size
        self.buffer_rect.h = self.font.char_height
        if(self.texture):
            sdl2.SDL_DestroyTexture(self.texture)            
        self.texture = sdl2.SDL_CreateTexture(
            glob.renderer, 
            sdl2.SDL_PIXELFORMAT_RGBA8888, 
            sdl2.SDL_TEXTUREACCESS_TARGET,
            self.buffer_rect.w,
            self.buffer_rect.h
        )        
        sdl2.SDL_SetTextureBlendMode(self.texture, sdl2.SDL_BLENDMODE_BLEND)
        self.width_total = self.buffer_rect.w
        self.target_rect.w = int(self.scale*self.buffer_rect.w)
        self.target_rect.h = int(self.scale*self.buffer_rect.h)
    def update(self):
        prev_target = sdl2.SDL_GetRenderTarget(glob.renderer)
        sdl2.SDL_SetRenderTarget(glob.renderer, self.texture)
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0, 0, 0, 0)
        sdl2.SDL_RenderClear(glob.renderer);
        length = len(self.value)
        if(length > self.buffer_size):
            length = self.buffer_size
        self.char_dst_rect.x = 0
        for i in range(0, length):    
            char = self.value[i]
            self.font.locate(char, self.char_src_rect)
            sdl2.SDL_RenderCopy(
                glob.renderer, 
                self.font.texture,
                self.char_src_rect,
                self.char_dst_rect,
            )
            self.char_dst_rect.x += self.font.char_width
        self.width = length*self.font.char_width
        sdl2.SDL_SetRenderTarget(glob.renderer, prev_target)
    def set_position(self, x, y):
        self.target_rect.x = x
        self.target_rect.y = y
    def set_scale(self, s):
        self.scale = s
        self.target_rect.w = int(s*self.buffer_rect.w)
        self.target_rect.h = int(s*self.buffer_rect.h)
    def set_color(self, r, g, b):
        sdl2.SDL_SetTextureColorMod(self.texture, r, g, b)
    def render(self):
        sdl2.SDL_RenderCopy(
            glob.renderer, 
            self.texture, 
            self.buffer_rect, 
            self.target_rect
        )