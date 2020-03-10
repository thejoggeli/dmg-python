import sdlboy_console_component

class Memview(sdlboy_console_component.ConsoleComponent):
    start = 0xFF00
    end = 0x10000
    def on_init(self):
        pass
    def on_update(self):
        pass
    def on_render(self):
        pass
    def on_resize(self):
        pass        
    def set_range(self, start, end):
        self.start = start
        self.end = end