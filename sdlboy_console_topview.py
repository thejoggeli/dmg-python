import sdl2
import sdlboy_window
import sdlboy_monitor

class Glob:
    renderer = None
glob = Glob()

class Topview:
    is_open     = False
    active_view = None
    memview     = None
    tileview    = None
    viewport    = None
    def __init__(self):
        self.memview = Memview()
        self.viewport = sdl2.SDL_Rect(0, 0, 0, 0)
        glob.renderer = sdlboy_window.glob.renderer
    def set_view(self, view):
        if(self.active_view != view):
            if(self.active_view):
                self.active_view.set_open(False)
            self.active_view = view
            if(self.active_view):
                self.active_view.set_open(True)     
        self.is_open = self.active_view != None
    def open_memview(self):
        self.set_view(self.memview)
    def open_tileview(self):
        self.set_view(self.tileview)
    def close(self):
        self.set_view(None)
    def update(self):
        if(self.active_view):
            self.active_view.render()
    def render(self):
        if(self.active_view):
            sdl2.SDL_SetRenderDrawColor(glob.renderer, 0, 0, 0, 127) 
            sdl2.SDL_RenderFillRect(glob.renderer, self.viewport)    
            self.active_view.render()
    def resize(self):
        if(self.active_view):
            self.viewport.x = sdlboy_monitor.monitor.viewport.w
            self.viewport.y = 0
            self.viewport.w = sdlboy_window.glob.window_rect.w - self.viewport.x
            self.viewport.h = 200
        else:
            self.viewport.x = 0
            self.viewport.y = 0
            self.viewport.w = 0
            self.viewport.h = 0
            
class Memview:
    def set_open(self, b):
        pass
    def update(self):
        pass
    def render(self):
        pass
    def resize(self):
        pass