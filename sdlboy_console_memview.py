import sdlboy_console_component
import sdlboy_text
import sdlboy_time
import hw_mem as mem

class Line:
    text = None

class Memview(sdlboy_console_component.ConsoleComponent):
    start = 0xFF00
    end = 0x10000
    font = None
    line_head = None
    line_foot = None
    lines = []
    line_height = 0
    line_offset = 0    
    num_lines = 0
    preferred_h = 0
    last_render_time = 0
    draw_zeroes = False
    row_width = 32
    chars_per_row = 0
    def on_init(self):
        self.font = sdlboy_text.get_font("console")
        self.line_height = self.font.char_height+2
        self.line_offset = 1
        self.line_offset = 1
        self.line_head = Line()
        self.line_head.text = sdlboy_text.Text(
            font=self.font,
            value="",
            buffer_size=256
        )
        self.line_foot = Line()
        self.line_foot.text = sdlboy_text.Text(
            font=self.font,
            value="",
            buffer_size=256
        )
    def on_update(self):
        if(sdlboy_time.since_start - self.last_render_time > 0.25):
            self.set_render_required()        
    def on_render(self):
        self.last_render_time = sdlboy_time.since_start
        pos_x = 0
        pos_y = self.line_offset + self.line_height*3
        addr = self.start
        for i in range(0, self.num_lines):
            line = self.lines[i]
            line.text.set_position(pos_x, pos_y)
            line.text.value = "| {0:0{1}X}".format(addr, 4) + " |"
            k = 0
            for j in range(0, self.row_width):
                byte = mem.read_byte_silent(addr)
                if(byte == 0 and not self.draw_zeroes):
                    line.text.value += "    "  
                else:              
                    line.text.value += f" {byte:02X} "
                addr += 1
                k += 1
                if(k == 16 and j < self.row_width-1):
                    line.text.value += "| {0:0{1}X}".format(addr, 4) + " |"
            line.text.value += "|"
            line.text.update()
            line.text.render()
            pos_y += self.line_height
        self.line_head.text.set_position(0, self.line_offset + self.line_height)
        self.line_head.text.render()
        self.line_foot.text.set_position(0, self.line_offset)
        self.line_foot.text.render()
        self.line_foot.text.set_position(0, self.line_offset + self.line_height*2)
        self.line_foot.text.render()
        self.line_foot.text.set_position(0, self.line_offset + self.line_height*(self.num_lines+3))
        self.line_foot.text.render()
    def on_resize(self):
        self.line_head.text.update()
        self.line_foot.text.update()
    def set_range(self, start, end):
        # align start and end
        start = start - start%self.row_width
        end = (end+32) - (end%32) # make end multiple of 32 (round up)
        if(end > 0x10000):
            end = 0x10000
        self.start = start
        self.end = end   
        self.recalc_lines()
    def set_draw_zeroes(self, b):
        self.draw_zeroes = b
    def on_present_width(self, w):
        double_width = self.font.char_width*(32*4+17)
        print(double_width)
        print(w)
        if(w >= double_width and self.row_width != 32):
            self.row_width = 32
            self.recalc_lines()
            self.set_render_required()
        elif(w < double_width and self.row_width != 16):
            self.row_width = 16
            self.recalc_lines()
            self.set_render_required()
    
    def recalc_lines(self):
        # create new if not enough lines
        self.num_lines = int((self.end-self.start)/self.row_width)  
        print("recalc")
        diff = self.num_lines - len(self.lines)
        for i in range(0, diff):
            line = Line()
            line.text = sdlboy_text.Text(
                font=self.font,
                value="",
                buffer_size=256
            )
            self.lines.append(line)
        # empty lines
        for i in range(0, self.num_lines):
            self.lines[i].text.value = ""
            self.lines[i].text.update()
        self.preferred_h = self.line_height*(self.num_lines+4)
        self.set_resize_required()
        # header, foot        
        head = "| MEM  |"
        j = 0
        for i in range(0, self.row_width):
            head += f" {j:02X} "
            j += 1
            if(j==16 and i < self.row_width-1):
                head += "| MEM  |"
                j = 0
        self.line_head.text.value = head + "|"
        if(self.row_width == 16):
            self.chars_per_row = 16*4+9
        else:
            self.chars_per_row = 32*4+17
        self.line_foot.text.value = "".ljust(self.chars_per_row, "-")
    
    