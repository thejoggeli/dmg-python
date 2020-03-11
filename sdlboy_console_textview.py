import sdl2
import sdlboy_text
import sdlboy_console_component

class Line:
    text = None
    bg = None
    
class Textview(sdlboy_console_component.ConsoleComponent):
    num_lines = 256
    lines = None
    line_height = 0
    line_offset = 0
    line_ptr = 0
    line_rect = 0
    def on_init(self):
        self.line_rect = sdl2.SDL_Rect(0, 0, 0, 0)
        self.lines = [None]*self.num_lines
        self.font = sdlboy_text.get_font("console")
        for i in range(0, self.num_lines):
            line = Line()
            line.text = sdlboy_text.Text(
                font=self.font,
                value="",
                buffer_size=256
            )
            self.lines[i] = line         
        self.line_height = self.font.char_height+2
        self.line_offset = 1
        self.print_line("type help for help")
    def on_update(self):
        pass
    def on_render(self):
        line_nr = self.line_ptr
        min_y = 0 - self.line_height
        pos_x = 0
        pos_y = self.viewport_local.h - self.line_height + self.line_offset
        for i in range(0, self.num_lines):
            line = self.lines[line_nr]
            line.text.set_position(pos_x, pos_y)
            if(line.bg):            
                sdl2.SDL_SetRenderDrawColor(self.renderer, line.bg[0], line.bg[1], line.bg[2], line.bg[3])
                self.line_rect.x = pos_x
                self.line_rect.y = pos_y
                self.line_rect.w = line.text.width
                self.line_rect.h = self.line_height
                sdl2.SDL_RenderFillRect(self.renderer, self.line_rect)
            line.text.update()
            line.text.render()
            pos_y -= self.line_height
            if(pos_y < min_y):
                break
            # next line
            line_nr += 1
            if(line_nr >= self.num_lines):
                line_nr = 0
    def on_resize(self):
        pass
    def help(self):
        self.print_line("q          quit").text.set_color(255, 255, 0)
        self.print_line("reset      hmmm ...").text.set_color(255, 255, 0)
        self.print_line("st         print state").text.set_color(255, 255, 0)
        self.print_line("s+N        N steps").text.set_color(255, 255, 0)
        self.print_line("t+N        N seconds").text.set_color(255, 255, 0)
        self.print_line("t=N        until t=N seconds").text.set_color(255, 255, 0)
        self.print_line("pc=N       run until pc=N").text.set_color(255, 255, 0)
        self.print_line("pc>N       run until pc<N").text.set_color(255, 255, 0)
        self.print_line("pc<N       run until pc>N").text.set_color(255, 255, 0)
        self.print_line("mem A B z  print memory A to B+B (z=show zeros)").text.set_color(255, 255, 0)
        self.print_line("rb A       read  byte").text.set_color(255, 255, 0)
        self.print_line("rw A       read  word").text.set_color(255, 255, 0)
        self.print_line("wb A B     write byte").text.set_color(255, 255, 0)
        self.print_line("wb A B     write word").text.set_color(255, 255, 0)
        self.print_line("limit      set max cycles/frame (0=off)").text.set_color(255, 255, 0)
        self.print_line("speed      set speed (1=off)").text.set_color(255, 255, 0)
        self.print_line("F1         toggle console").text.set_color(255, 255, 0)
        self.print_line("F2         toggle monitor").text.set_color(255, 255, 0)
        self.print_line("F3         toggle play mode").text.set_color(255, 255, 0)
        self.print_line("F4         toggle auto/manual").text.set_color(255, 255, 0)
        self.print_line("suffix all print everything").text.set_color(255, 255, 0)
        self.print_line("suffix war print warnings").text.set_color(255, 255, 0)   
    def print_line(self, msg, bg=None):
        self.line_ptr -= 1
        if(self.line_ptr < 0):
            self.line_ptr = self.num_lines-1
        self.lines[self.line_ptr].text.value = msg
        self.lines[self.line_ptr].text.set_color(255,255,255)
        self.lines[self.line_ptr].text.update()
        self.lines[self.line_ptr].bg = bg
        self.set_render_required()
        return self.lines[self.line_ptr]
    