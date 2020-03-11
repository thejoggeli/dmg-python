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
    last_update_time = 0
    draw_zeroes = False
    row_width = 32
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
        if(sdlboy_time.since_start - self.last_update_time > 0.25):
            self.set_render_required()        
            self.last_update_time = sdlboy_time.since_start
    def on_render(self):
        pos_x = 0
        pos_y = self.line_offset + self.line_height*3
        addr = self.start
        for i in range(0, self.num_lines):
            line = self.lines[i]
            line.text.set_position(pos_x, pos_y)
            line.text.value = "| {0:0{1}X}".format(addr, 4) + " |"
            for j in range(0, self.row_width):
                byte = mem.read_byte_silent(addr)
                if(byte == 0 and not self.draw_zeroes):
                    line.text.value += "    "  
                else:              
                    line.text.value += f" {byte:02X} "
                addr += 1
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
        self.row_width = 32
        # align start and end
        start = start - start%self.row_width
        while(end%self.row_width != 0):
            end+=1
        if(end > 0x10000):
            end = 0x10000
        self.start = start
        self.end = end
        self.num_lines = int((end-start)/self.row_width)
        # create new if not enough lines
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
        for i in range(0, self.row_width):
            head += f" {i:02X} "
        self.line_head.text.value = head + "|"
        self.line_foot.text.value = "".ljust(self.row_width*4+9, "-")
    def set_draw_zeroes(self, b):
        self.draw_zeroes = b
    