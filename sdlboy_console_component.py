import sdl2
import sdlboy_window
import sdlboy_console
import sdlboy_color

class ConsoleComponent:
    render_requested = False
    viewport_texture = None
    viewport_local = None
    viewport_global_inner = None
    viewport_global_outer = None
    renderer = None
    bg = None
    is_visible = False
    padding_left = 0
    padding_right = 0
    padding_top = 0
    padding_bottom = 0
    preferred_w = 0
    preferred_h = 0
    def __init__(self):
        self.bg = sdlboy_color.Color(0, 0, 0, 0)
        self.renderer = sdlboy_window.glob.renderer
        self.viewport_local = sdl2.SDL_Rect(0, 0, 0, 0)
        self.viewport_global_outer = sdl2.SDL_Rect(0, 0, 0, 0)
        self.viewport_global_inner = sdl2.SDL_Rect(0, 0, 0, 0)
        self.on_init()
    def set_visible(self, v):
        if(self.is_visible == v):
            return
        self.is_visible = v
        if(not v):
            self.viewport_global_outer.x = 0
            self.viewport_global_outer.y = 0
            self.viewport_global_outer.w = 0
            self.viewport_global_outer.h = 0
            self.viewport_global_inner.x = 0
            self.viewport_global_inner.y = 0
            self.viewport_global_inner.w = 0
            self.viewport_global_inner.h = 0
            self.viewport_local.x  = 0
            self.viewport_local.y  = 0
            self.viewport_local.w  = 0
            self.viewport_local.h  = 0
            self.on_invisible()
        else:
            self.on_visible()        
        self.set_resize_required()
    def update(self):
        self.on_update()
    def render(self):
        if(self.render_requested):
            # render to texture
            prev_target = sdl2.SDL_GetRenderTarget(self.renderer)
            sdl2.SDL_SetRenderTarget(self.renderer, self.viewport_texture)
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
            sdl2.SDL_RenderClear(self.renderer)            
            self.on_render()
            sdl2.SDL_SetRenderTarget(self.renderer, prev_target)
            self.render_requested = False
        # render texture to screen
        if(self.bg.a > 0):
            sdl2.SDL_SetRenderDrawColor(self.renderer, self.bg.r, self.bg.g, self.bg.b, self.bg.a)
            sdl2.SDL_RenderFillRect(self.renderer, self.viewport_global_outer)
        sdl2.SDL_RenderCopy(
            self.renderer,
            self.viewport_texture,
            self.viewport_local,
            self.viewport_global_inner
        )   
    def set_padding(self, top, right, bottom, left):
        self.padding_top = top
        self.padding_right = right
        self.padding_bottom = bottom
        self.padding_left = left
        self.viewport_global_inner.x = self.viewport_global_outer.x + self.padding_left
        self.viewport_global_inner.y = self.viewport_global_outer.y + self.padding_top
        self.viewport_global_inner.w = self.viewport_global_outer.w - self.padding_left - self.padding_right
        self.viewport_global_inner.h = self.viewport_global_outer.h - self.padding_top  - self.padding_bottom
        self.viewport_local.w = self.viewport_global_inner.w
        self.viewport_local.h = self.viewport_global_inner.h
        self.set_render_required()
    def set_background(self, r, g, b, a):
        self.bg.set_components(r, g, b, a)
    def set_viewport(self, x, y, w, h):
        if(not self.is_visible):
            return
        self.viewport_global_outer.x = x
        self.viewport_global_outer.y = y
        self.viewport_global_outer.w = w
        self.viewport_global_outer.h = h
        self.viewport_global_inner.x = self.viewport_global_outer.x + self.padding_left
        self.viewport_global_inner.y = self.viewport_global_outer.y + self.padding_top
        self.viewport_global_inner.w = self.viewport_global_outer.w - self.padding_left - self.padding_right
        self.viewport_global_inner.h = self.viewport_global_outer.h - self.padding_top  - self.padding_bottom
        self.viewport_local.x  = 0
        self.viewport_local.y  = 0
        self.viewport_local.w  = self.viewport_global_inner.w
        self.viewport_local.h  = self.viewport_global_inner.h
        if(self.viewport_texture):
            sdl2.SDL_DestroyTexture(self.viewport_texture)
        self.viewport_texture = sdl2.SDL_CreateTexture(
            self.renderer, 
            sdl2.SDL_PIXELFORMAT_ARGB8888, 
            sdl2.SDL_TEXTUREACCESS_TARGET,
            self.viewport_local.w,
            self.viewport_local.h
        )        
        sdl2.SDL_SetTextureBlendMode(self.viewport_texture, sdl2.SDL_BLENDMODE_BLEND)
        self.render_requested = True
        self.on_resize()
    def on_init(self):
        pass
    def on_visible(self):
        pass
    def on_invisible(self):
        pass
    def on_update(self):
        pass
    def on_render(self):
        pass
    def on_resize(self):
        pass
    def set_resize_required(self):
        sdlboy_console.resize()
    def set_render_required(self):
        self.render_requested = True
    def on_present_width(self, w):
        pass
    def on_present_height(self, h):
        pass
