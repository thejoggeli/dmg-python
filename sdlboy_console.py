import sdl2
import sdlboy_text
import sdlboy_window
import sdlboy_time
import sdlboy_input
import time
import hw_z80 as z80
import hw_mem as mem
import hw_lcd as lcd
import hw_cartridge as car
import hw_video as vid
import hw_gameboy as gameboy
import util_dlog as dlog
import util_config as config

is_open = False
has_control = False

class Glob:
    renderer = None
glob = Glob()

class Sideview:
    debug_texts = None
    viewport = None
    font = None
    def __init__(self):    
        self.viewport = sdl2.SDL_Rect(0, 0, 0, 0)
        self.debug_texts = [None]*10
        self.font = sdlboy_text.get_font("console")
        for i in range(0, len(self.debug_texts)):
            self.debug_texts[i] = sdlboy_text.Text(
                font=self.font,
                value="---", 
                buffer_size=16
            )
            self.debug_texts[i].set_position(4, 4+i*(self.font.char_height+4))    
            self.debug_texts[i].set_scale(1)
    def render(self):                
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0, 0, 0, 127)
        sdl2.SDL_RenderFillRect(glob.renderer, self.viewport)            
        self.debug_texts[0].value = "FPS:" + str(sdlboy_time.fps)
        self.debug_texts[1].value = "T(Z80):" + "{0:.1f}".format(round(z80.state.time_passed, 1))
        self.debug_texts[2].value = "T(IRL):" + "{0:.1f}".format(round(sdlboy_time.since_start, 1))
        self.debug_texts[3].value = "PC:" + "0x{0:0{1}X}".format(z80.reg.pc, 4)
        self.debug_texts[4].value = "SP:" + "0x{0:0{1}X}".format(z80.reg.sp, 4)
        self.debug_texts[5].value = "AF:" + "0x{0:0{1}X}".format(z80.reg.get_af(), 4)
        self.debug_texts[6].value = "BC:" + "0x{0:0{1}X}".format(z80.reg.get_bc(), 4)
        self.debug_texts[7].value = "DE:" + "0x{0:0{1}X}".format(z80.reg.get_de(), 4)
        self.debug_texts[8].value = "HL:" + "0x{0:0{1}X}".format(z80.reg.get_hl(), 4)                 
        self.debug_texts[9].value = "Control:" + str(has_control)
        for i in range(0, len(self.debug_texts)):
            self.debug_texts[i].update()
            self.debug_texts[i].render()
    def resize(self):
        self.viewport.x = 0
        self.viewport.y = 0
        self.viewport.w = 200
        self.viewport.h = int(sdlboy_window.glob.window_rect.h)
    
class Textview:
    num_lines = 256
    lines = None
    line_height = 0
    line_offset = 1
    line_ptr = 0
    viewport = None
    def __init__(self):
        self.viewport = sdl2.SDL_Rect(0, 0, 0, 0)
        self.lines = [None]*self.num_lines
        self.font = sdlboy_text.get_font("console")
        self.line_height = self.font.char_height+2
        for i in range(0, self.num_lines):
            line = Line()
            line.text = sdlboy_text.Text(
                font=self.font,
                value="",
                buffer_size=256
            )
            self.lines[i] = line            
    def render(self):    
        line_nr = self.line_ptr
        min_y = self.viewport.y - self.line_height
        pos_x = self.viewport.x
        pos_y = self.viewport.y + self.viewport.h - self.line_height + self.line_offset
        for i in range(0, self.num_lines):
            line = self.lines[line_nr]
            line.text.set_position(pos_x, pos_y)
            pos_y -= self.line_height
            line.text.render()
            if(pos_y < min_y):
                break
            # next line
            line_nr += 1
            if(line_nr >= self.num_lines):
                line_nr = 0 
    def resize(self):    
        self.viewport.x = inputview.viewport.x
        self.viewport.y = 0
        self.viewport.w = sdlboy_window.glob.window_rect.w - sideview.viewport.w
        self.viewport.h = sdlboy_window.glob.window_rect.h - inputview.viewport.h
    def print_line(self, msg):
        self.line_ptr -= 1
        if(self.line_ptr < 0):
            self.line_ptr = self.num_lines-1
        self.lines[self.line_ptr].text.value = msg
        self.lines[self.line_ptr].text.update()
        

class Inputview:
    text = None
    viewport = None
    font = None
    cursor_timer = 0
    cursor_rect = None
    prev_messages = []
    prev_messages_ptr = -1
    prev_messages_max = 32
    def __init__(self):
        self.font = sdlboy_text.get_font("console")   
        self.text = sdlboy_text.Text(
            font=self.font,
            value=">>> ",
            buffer_size=256
        )
        self.text.update()
        self.viewport = sdl2.SDL_Rect(0, 0, 0, 0) 
        self.cursor_rect = sdl2.SDL_Rect(0, 0, 0, 0) 
        saved_history = config.get("sdlboy_console_history", False)
        if(saved_history):
            self.prev_messages = saved_history
            self.prev_messages_ptr = len(self.prev_messages)-1
    def render(self):
        self.text.set_position(self.viewport.x, self.viewport.y + textview.line_offset)
        self.text.update()
        self.text.render()
        self.cursor_timer += sdlboy_time.delta_time
        if(self.cursor_timer >= 1.5):
            self.cursor_timer = 0.0
        if(self.cursor_timer >= 0.75):
            self.cursor_rect.x = self.viewport.x + self.text.width
            self.cursor_rect.y = self.viewport.y + textview.line_height
            self.cursor_rect.w = self.font.char_width
            self.cursor_rect.h = -4
            sdl2.SDL_SetRenderDrawColor(glob.renderer, 255, 255, 255, 255)
            sdl2.SDL_RenderFillRect(glob.renderer, self.cursor_rect)
    def resize(self):
        self.viewport.x = sideview.viewport.x + sideview.viewport.w + 4
        self.viewport.y = sdlboy_window.glob.window_rect.h - textview.line_height-4
        self.viewport.w = sdlboy_window.glob.window_rect.w - sideview.viewport.w
        self.viewport.h = sdlboy_window.glob.window_rect.h - self.viewport.y    
    def on_enter(self):
        user_input = self.text.value[4:].strip()
        textview.print_line(self.text.value.strip())
        if(len(self.text.value.strip()) > 4):
            self.prev_messages.append(self.text.value.strip())
            self.prev_messages_ptr = len(self.prev_messages)-1
            if(len(self.prev_messages) > self.prev_messages_max):
                start = len(self.prev_messages)-self.prev_messages_max
                end   = len(self.prev_messages)
                self.prev_messages = self.prev_messages[start:end]
                self.prev_messages_ptr = self.prev_messages_max-1              
            config.set("sdlboy_console_history", self.prev_messages)
            config.save()
        self.text.value = ">>> "
        self.text.update()
        if(has_control):
            try:
                handle_input(user_input)
            except:
                dlog.print_msg("SYS", "invalid input")

class Line:
    text = None
    
sideview = None
textview = None
inputview = None

def init():
    global sideview, textview, inputview
    glob.renderer = sdlboy_window.glob.renderer
    sideview = Sideview()
    textview = Textview()
    inputview = Inputview()
   #dlog.print_error = print_error
   #dlog.print_warning = print_warning
   #dlog.print_msg = print_msg
        
def open():
    global is_open, has_control
    sdl2.SDL_SetRenderDrawBlendMode(glob.renderer, sdl2.SDL_BLENDMODE_BLEND)
    is_open = True
    has_control = True
    resize()
    sdl2.SDL_StartTextInput();
    dlog.enable.all()
def close():
    global is_open, has_control
    is_open = False
    sdl2.SDL_StopTextInput();
    has_control = False
    dlog.enable.errors()
    
def update():    
    pass
    
def resize():
    sideview.resize()
    inputview.resize()
    textview.resize()

def render():
    sdl2.SDL_SetRenderDrawColor(glob.renderer, 0x00, 0x40, 0x80, 0xB0)
    sdl2.SDL_RenderFillRect(glob.renderer, sdlboy_window.glob.window_rect)    
    sideview.render()
    textview.render()
    inputview.render()
    
def handle_event(event):
    global has_control       
    if(event.type == sdl2.SDL_TEXTINPUT):     
        inputview.text.value += event.text.text.decode("utf-8")
        inputview.text.update()
    if(event.type == sdl2.SDL_KEYDOWN):
        key = event.key.keysym.sym
        if(key == 8 and len(inputview.text.value) > 4):
            if(sdlboy_input.is_key_down(1073742048)):
                # CTRL-Backspace
                inputview.text.value = inputview.text.value.rstrip()
                try: 
                    index = inputview.text.value.rindex(" ", 4)
                    inputview.text.value = inputview.text.value[0:index]
                except ValueError:
                    inputview.text.value = ">>> "
            else:
                # Backspace
                inputview.text.value = inputview.text.value[0:len(inputview.text.value)-1]
            inputview.text.update()
        elif(key == 13):
            # Enter
            inputview.on_enter()
        elif(key == 99 and sdlboy_input.is_key_down(1073742048)):
            # CTRL-C
            inputview.text.value = ">>> "
            inputview.text.update()            
        elif(key == 1073741883):         
            has_control = not has_control
            if(has_control):
                dlog.enable.all()
            else:
                dlog.enable.errors()
        elif(key == 1073741906):
            # Up
            if(inputview.prev_messages_ptr >= 0):
                inputview.text.value = inputview.prev_messages[inputview.prev_messages_ptr]
                inputview.prev_messages_ptr -= 1
        elif(key == 1073741905):
            # Down
            inputview.prev_messages_ptr += 1
            if(inputview.prev_messages_ptr > len(inputview.prev_messages)-1):
                inputview.prev_messages_ptr = len(inputview.prev_messages)-1
            actual_ptr = inputview.prev_messages_ptr+1
            if(actual_ptr < len(inputview.prev_messages)): 
                inputview.text.value = inputview.prev_messages[actual_ptr]
            else:  
                inputview.text.value = ">>> "
            

def print_error(src, msg):
    err = src + " ERROR\t\t"
    err += "PC=" + "0x{0:0{1}X}".format(z80.state.instruction_location, 4) + "\t"
   #err += "Step=" + str(z80.state.step_nr) + " / "
    err += msg
    textview.print_line(replace_tab(err))
    print(err)
    sys.exit()

def print_warning(src, msg):
    war = src + " WARNING! \t"
    war += "PC=" + "0x{0:0{1}X}".format(z80.state.instruction_location, 4) + "\t"
   #war += "Step=" + str(z80.state.step_nr) + " / "
    war += msg
    textview.print_line(replace_tab(war))
    
def print_msg(src, msg):
    msg = src + " " + msg
    textview.print_line(replace_tab(msg))
    
def print_line(msg):
    textview.print_line(replace_tab(msg))
    
def replace_tab(s, tabstop = 4):
    result = str()
    for c in s:
        if c == '\t':
            while (len(result) % tabstop != 0):
                result += ' ';
        else:
            result += c    
    return result
    
def print_spacer():
    dlog.print_msg("SYS", "=======================================================================================")

def do_loop():
    if(dlog.enable.sys):
        print_spacer()
    gameboy.tick()

def handle_input(user_input):
    dlog.print_msg("SYS", ">>> " + user_input)
    dlog.enable.all();    
    printPerformance = False
    suffixFound = True
    while(suffixFound):
        suffixFound = False
        user_input = user_input.strip()
        if(user_input.endswith("--")):
            user_input = user_input.replace("--", "").strip()
            dlog.enable.errors()
            suffixFound = True
        if(user_input.endswith("-")):
            user_input = user_input.replace("-", "").strip()
            dlog.enable.warnings()
            suffixFound = True
        if(user_input.endswith("perf")):
            user_input = user_input.replace("perf", "").strip()
            printPerformance = True
            suffixFound = True
    
    if(user_input == "q"):
        quit = True
        return
    if(user_input.startswith("st")):
        print_spacer()
        lcd.print_state()
        car.print_state()
        z80.print_state()
        print_spacer()
        return
    if(user_input.startswith("rb")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        mem.read_byte(addr)
        print_spacer()
        return
    if(user_input.startswith("rw")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        mem.read_word(addr)
        print_spacer()
        return
    if(user_input.startswith("wb")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        byte = int(split[2], 16)
        mem.write_byte(addr, byte)
        print_spacer()
        return
    if(user_input.startswith("ww")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        word = int(split[2], 16)
        mem.write_word(addr, word)
        print_spacer()
        return
    if(user_input.startswith("ime 0")):
        z80.state.interrupt_master_enable = 0
        print_spacer()
        return
    if(user_input.startswith("ime 1")):
        z80.state.interrupt_master_enable = 1
        z80.state.interrupt_master_enable_skip_one_cycle = 1
        print_spacer()
        return
    if(user_input.startswith("setif")):
        n = int(user_input.replace("setif", ""))
        mem.write_byte(0xFF0F, mem.read_byte(0xFF0F)|(0x01 << n))
        print_spacer()
        return
    if(user_input.startswith("setie")):
        n = int(user_input.replace("setie", ""))
        mem.write_byte(0xFFFF, mem.read_byte(0xFFFF)|(0x01 << n))
        print_spacer()
        return
        
    real_time_start = time.time()
    cpu_time_start = z80.state.time_passed
    
    if(user_input.startswith("t")):
        val = user_input.replace("t", "").strip()
        if(val.startswith("+")):
            # loop for N seconds
            target_time = float(val.replace("+", "").strip())
            target_time += z80.state.time_passed
            while(z80.state.time_passed < target_time):
                do_loop()             
        else:
            # loop until cpu time = N seconds
            target_time = float(val.replace("=", "").strip())
            while(z80.state.time_passed < target_time):
                do_loop()
    elif(user_input.startswith("pc")):
        val = user_input.replace("pc", "").strip()
        if(val.startswith(">")):
            # loop until z80_pc > target_pc
            target_pc = int(val.replace(">", ""), 16)
            while(z80.reg.pc <= target_pc):
                do_loop()
        elif(val.startswith("<")):
            # loop until z80_pc < target_pc
            target_pc = int(val.replace("<", ""), 16)
            while(z80.reg.pc >= target_pc):
                do_loop()
        else:
            # loop until z80_pc = target_pc            
            target_pc = int(val.replace("=", ""), 16)
            while(z80.reg.pc != target_pc):
                do_loop()    
        dlog.print_msg("SYS", "PC is now at " + "0x{0:0{1}X}".format(z80.reg.pc, 4))
    else:
        # loop for n steps
        steps = 1
        try:
            steps = int(user_input)
        except:
            steps = 1
        for i in range(0, steps):
            do_loop()
    real_time_passed = time.time() - real_time_start
    print_spacer()
    if(real_time_passed > 1 or printPerformance):
         # print performance            
        cpu_time_passed = z80.state.time_passed - cpu_time_start
        time_str = "{0:.3f}".format(round(real_time_passed, 3))
        cpu_time_str = "{0:.3f}".format(round(cpu_time_passed, 3))    
        time_ratio = -1
        if(real_time_passed != 0):
            time_ratio = cpu_time_passed/real_time_passed
        dlog.print_msg(
            "SYS",
            ">>> Perform:" + "\t" +
            "CPU=" + cpu_time_str + "s\t" + 
            "Real=" + time_str + "s\t"
            "Ratio=" + str(round(time_ratio,3))
        )
    
    