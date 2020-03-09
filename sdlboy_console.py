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
    viewport = None
    font = None
    monitor_ptr = 0
    monitor_texts = []
    def __init__(self):    
        self.viewport = sdl2.SDL_Rect(0, 0, 0, 0)
        self.font = sdlboy_text.get_font("console")
    def monitor_grow(self):
        text = sdlboy_text.Text(
            font=self.font,
            value="---", 
            buffer_size=16
        )
        text.set_position(4, 4+len(self.monitor_texts)*(self.font.char_height+4))    
        text.set_scale(1)
        self.monitor_texts.append(text)
    def monitor(self, str):
        if(self.monitor_ptr >= len(self.monitor_texts)):
            self.monitor_grow()
        self.monitor_texts[self.monitor_ptr].value = str
        self.monitor_texts[self.monitor_ptr].update()
        self.monitor_ptr += 1
    def render(self):                
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0, 0, 0, 127)
        sdl2.SDL_RenderFillRect(glob.renderer, self.viewport)         
        self.monitor_ptr = 0        
        self.monitor("FPS:" + str(sdlboy_time.fps))
        speed_estimate = "{0:.1f}".format(round(sdlboy_window.glob.speed_estimate*100))  
        self.monitor("Speed:" + speed_estimate + "%")         
        limiter = str(sdlboy_window.glob.cycle_limiter)
        if(limiter):
            self.monitor("Limiter:" + str(limiter))    
        else:
            self.monitor("Limiter:off")
            
        self.monitor("Control:" + str(has_control))
        self.monitor("T(Z80):" + "{0:.1f}".format(round(z80.state.time_passed, 1)))
        self.monitor("T(IRL):" + "{0:.1f}".format(round(sdlboy_time.since_start, 1)))
        
        # Z80
        self.monitor("BIOS:" + str(bool(mem.bios_running)))
        self.monitor("")
        self.monitor("======Z80======")
        znhc = 0
        znhc |= z80.reg.get_flag_z()<<3
        znhc |= z80.reg.get_flag_n()<<2
        znhc |= z80.reg.get_flag_h()<<1
        znhc |= z80.reg.get_flag_c()<<0
        ime = z80.state.interrupt_master_enable
        ie_byte = mem.read_byte_silent(0xFFFF)
        if_byte = mem.read_byte_silent(0xFF0F)
        self.monitor("  PC:" + "0x{0:0{1}X}".format(z80.reg.pc, 4))
        self.monitor("  SP:" + "0x{0:0{1}X}".format(z80.reg.sp, 4))
        self.monitor("ZNHC:" + "{0:0{1}b}".format(znhc,4))
        self.monitor("  AF:" + "0x{0:0{1}X}".format(z80.reg.get_af(), 4))
        self.monitor("  BC:" + "0x{0:0{1}X}".format(z80.reg.get_bc(), 4))
        self.monitor("  DE:" + "0x{0:0{1}X}".format(z80.reg.get_de(), 4))
        self.monitor("  HL:" + "0x{0:0{1}X}".format(z80.reg.get_hl(), 4)) 
        self.monitor(" IME:" + str(bool(ime)))
        self.monitor("  IE:" + "%{0:0{1}b}".format(ie_byte,5))
        self.monitor("  IF:" + "%{0:0{1}b}".format(if_byte,5))
        self.monitor("HALT:" + str(bool(z80.state.halted)))
        self.monitor("STOP:" + str(bool(z80.state.stopped)))
        
        # Cartridge
        self.monitor("")
        self.monitor("===CARTRIDGE===")
        self.monitor("ROM#:" + "0x{0:0{1}X}".format(car.mbc_state.rom_bank_selected, 2))
        self.monitor("RAM#:" + "0x{0:0{1}X}".format(car.mbc_state.ram_bank_selected, 2))
        lcdc = mem.read_byte_silent(0xFF40)
        stat = mem.read_byte_silent(0xFF41)
        scy  = mem.read_byte_silent(0xFF42)
        scx  = mem.read_byte_silent(0xFF43)
        ly   = mem.read_byte_silent(0xFF44)
        lyc  = mem.read_byte_silent(0xFF45)
        dma  = mem.read_byte_silent(0xFF46)
        bgp  = mem.read_byte_silent(0xFF47)
        obp0 = mem.read_byte_silent(0xFF48)
        obp1 = mem.read_byte_silent(0xFF49)
        wx   = mem.read_byte_silent(0xFF4B)
        wy   = mem.read_byte_silent(0xFF4A)
        
        # LCD
        self.monitor("")
        self.monitor("======LCD======")
        self.monitor("LCDC:" + "%{0:0{1}b}".format(lcdc, 8))
        self.monitor("STAT:" + "%{0:0{1}b}".format(stat, 8))
        self.monitor(" SCY:" + "{0:0{1}d}".format(scy, 3))
        self.monitor(" SCX:" + "{0:0{1}d}".format(scx, 3))
        self.monitor("  LY:" + "{0:0{1}d}".format(ly, 3))
        self.monitor(" LYC:" + "{0:0{1}d}".format(lyc, 3))
        self.monitor(" DMA:" + "0x{0:0{1}X}".format(dma, 2))
        self.monitor(" BGP:" + "%{0:0{1}b}".format(bgp, 8))
        self.monitor("OBP0:" + "%{0:0{1}b}".format(obp0, 8))
        self.monitor("OBP1:" + "%{0:0{1}b}".format(obp1, 8))
        self.monitor("  WY:" + "{0:0{1}d}".format(wy, 3))
        self.monitor("  WX:" + "{0:0{1}d}".format(wx, 3))
        for i in range(0, len(self.monitor_texts)):
            self.monitor_texts[i].render()
    def resize(self):
        self.viewport.x = 0
        self.viewport.y = 0
        self.viewport.w = 220
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
        self.print_line("type help for help")
    def help(self):
        self.print_line("q          quit").text.set_color(220, 220, 255)
        self.print_line("reset      hmmm ...").text.set_color(220, 220, 255)
        self.print_line("st         print state").text.set_color(220, 220, 255)
        self.print_line("s+N        N steps").text.set_color(220, 220, 255)
        self.print_line("t+N        N seconds").text.set_color(220, 220, 255)
        self.print_line("t=N        until t=N seconds").text.set_color(220, 220, 255)
        self.print_line("pc=N       run until pc=N").text.set_color(220, 220, 255)
        self.print_line("pc>N       run until pc<N").text.set_color(220, 220, 255)
        self.print_line("pc<N       run until pc>N").text.set_color(220, 220, 255)
        self.print_line("mem A B z  print memory A to B+B (z=show zeros)").text.set_color(220, 220, 255)
        self.print_line("rb A       read  byte").text.set_color(220, 220, 255)
        self.print_line("rw A       read  word").text.set_color(220, 220, 255)
        self.print_line("wb A B     write byte").text.set_color(220, 220, 255)
        self.print_line("wb A B     write word").text.set_color(220, 220, 255)
        self.print_line("limit      set max cycles/frame (0=off)").text.set_color(220, 220, 255)
        self.print_line("speed      set speed (1=off)").text.set_color(220, 220, 255)
        self.print_line("F1         toggle console").text.set_color(220, 220, 255)
        self.print_line("F2         toggle run").text.set_color(220, 220, 255)
        self.print_line("suffix all print everything").text.set_color(220, 220, 255)
        self.print_line("suffix war print warnings").text.set_color(220, 220, 255)    
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
        self.lines[self.line_ptr].text.set_color(255,255,255)
        return self.lines[self.line_ptr]

class Inputview:
    text = None
    viewport = None
    font = None
    cursor_timer = 0
    cursor_rect = None
    prev_messages = []
    prev_messages_ptr = -1
    prev_messages_max = 32
    cursor_position = 4
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
        if(self.cursor_timer <= 0.75):
            self.cursor_rect.x = self.viewport.x + self.cursor_position*self.font.char_width
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
            try:
                self.prev_messages.remove(self.text.value.strip())
            except:
                pass
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
        self.cursor_position = 4
        self.cursor_timer = 0.25        
        try:
            input_handler.handle_input(user_input)
        except Exception as e:
            dlog.print_msg("SYS", str(e))
            textview.print_line(str(e))
        dlog.enable.errors();    
    def write_chars(self, chars):
        self.text.value = self.text.value[:self.cursor_position] \
                        + chars \
                        + self.text.value[self.cursor_position:]
        self.text.update()
        self.cursor_position += len(chars)
        self.cursor_timer = 0.25           
    def write_delete(self, ctrl):
        if(self.cursor_position >= len(self.text.value)):
            return
        subtext = self.text.value[self.cursor_position:].strip()
        left = self.cursor_position
        if(ctrl):
            index = len(subtext)
            try: 
                index = subtext.index(" ")+1
            except ValueError:
                pass
            self.text.value = self.text.value[0:left] + subtext[index:]
        else:
            self.text.value = self.text.value[0:self.cursor_position] \
                            + self.text.value[self.cursor_position+1:]
        self.text.update()       
        self.cursor_timer = 0.25            
    def write_backspace(self, ctrl):
        if(self.cursor_position <= 4):
            return
        subtext = self.text.value[0:self.cursor_position].strip()
        right = self.cursor_position
        if(ctrl):
            index = 4
            try: 
                index = subtext.rindex(" ", 4)
            except ValueError:
                pass
            self.text.value = self.text.value[0:index] + self.text.value[right:]
            self.cursor_position = index
        else:
            self.text.value = self.text.value[0:self.cursor_position-1] \
                            + self.text.value[self.cursor_position:]                              
            self.cursor_position -= 1
        self.text.update()        
        self.cursor_timer = 0.25           
    def move_cursor(self, delta, ctrl):
        if(delta == 1):
            if(ctrl):
                while(True):                
                    self.cursor_position += 1
                    if(self.cursor_position >= len(self.text.value)):
                        self.cursor_position = len(self.text.value)
                        break
                    if(self.text.value[self.cursor_position-1] == " "):
                        break
            else:
                self.cursor_position += 1
                if(self.cursor_position >= len(self.text.value)):
                    self.cursor_position = len(self.text.value)        
        elif(delta == -1):
            if(ctrl):
                while(True):                
                    self.cursor_position -= 1
                    if(self.cursor_position <= 4):
                        self.cursor_position = 4
                        break
                    if(self.text.value[self.cursor_position-1] == " "):
                        break
            else:
                self.cursor_position -= 1
                if(self.cursor_position <= 4):
                    self.cursor_position = 4
        self.cursor_timer = 0.25            
    def move_history_up(self):
        if(self.prev_messages_ptr >= 0):
            self.text.value = self.prev_messages[self.prev_messages_ptr]
            self.prev_messages_ptr -= 1
        self.cursor_position = len(self.text.value)
        self.cursor_timer = 0.25           
    def move_history_down(self):
        self.prev_messages_ptr += 1
        if(self.prev_messages_ptr > len(self.prev_messages)-1):
            self.prev_messages_ptr = len(self.prev_messages)-1
        actual_ptr = self.prev_messages_ptr+1
        if(actual_ptr < len(self.prev_messages)): 
            self.text.value = self.prev_messages[actual_ptr]
        else:  
            self.text.value = ">>> "
        self.cursor_position = len(self.text.value)
        self.cursor_timer = 0.25           
    def clear(self):
        self.text.value = ">>> "
        self.cursor_position = 4

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
    input_handler.print_spacer()
   #dlog.print_error = print_error
   #dlog.print_warning = print_warning
   #dlog.print_msg = print_msg
        
def open():
    global is_open
    sdl2.SDL_SetRenderDrawBlendMode(glob.renderer, sdl2.SDL_BLENDMODE_BLEND)
    sdl2.SDL_StartTextInput();
    is_open = True
    resize()
    dlog.enable.errors()
def close():
    global is_open
    is_open = False
    sdl2.SDL_StopTextInput();
    set_control(False)
    dlog.enable.errors()
    
def set_control(b):
    global has_control
    has_control = b
    
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
        inputview.write_chars(event.text.text.decode("utf-8"))
    if(event.type == sdl2.SDL_KEYDOWN):
        key = event.key.keysym.sym
        if(key == 127):
            if(sdlboy_input.is_key_down(1073742048)):
                # CTRL-Delete
                inputview.write_delete(True)
            else:
                # Delete
                inputview.write_delete(False)
        elif(key == 8):
            if(sdlboy_input.is_key_down(1073742048)):
                # CTRL-Backspace
                inputview.write_backspace(True)
            else:
                # Backspace
                inputview.write_backspace(False)
        elif(key == 13):
            # Enter
            inputview.on_enter()
        elif(key == 99 and sdlboy_input.is_key_down(1073742048)):
            # CTRL-C
            inputview.clear()
        elif(key == 1073741883):         
            has_control = not has_control
            if(has_control):
                dlog.enable.all()
            else:
                dlog.enable.errors()
        elif(key == 1073741906):
            # Up
            inputview.move_history_up()
        elif(key == 1073741905):
            # Down
            inputview.move_history_down()
        elif(key == 1073741903):
            # right
            if(sdlboy_input.is_key_down(1073742048)):
                inputview.move_cursor(+1, True)
            else:
                inputview.move_cursor(+1, False)                
        elif(key == 1073741904):
            # left
            if(sdlboy_input.is_key_down(1073742048)):
                inputview.move_cursor(-1, True)
            else:
                inputview.move_cursor(-1, False)       

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
    
class InputHandler:
    def print_spacer(self):
        dlog.print_msg("SYS", "=======================================================================================")
    def do_loop(self):
        if(dlog.enable.sys):
            self.print_spacer()
        gameboy.tick() 
    def handle_input(self, user_input):        
        dlog.print_msg("SYS", ">>> " + user_input)
        dlog.enable.errors();    
        print_perf = False
        suffix_found = True
        log_free = True
        while(suffix_found):
            suffix_found = False
            user_input = user_input.strip()
            if(user_input.endswith("all")):
                user_input = user_input.replace("all", "").strip()
                dlog.enable.all()
                log_free = False
                suffix_found = True
            if(user_input.endswith("war")):
                user_input = user_input.replace("war", "").strip()
                dlog.enable.warnings()
                log_free = False
                suffix_found = True
            if(user_input.endswith("perf")):
                user_input = user_input.replace("perf", "").strip()
                print_perf = True
                suffix_found = True       
        
        if(user_input == "q"):
            sdlboy_window.glob.exit_requested = True
            return
        elif(user_input == "help"):
            textview.help()
            return
        elif(user_input.startswith("mem")):
            if(log_free):
                dlog.enable.errors()
            self.print_spacer()
            zeros = False
            if(user_input.strip().endswith("z")):
                user_input = user_input.replace("z", "").strip()
                zeros = True
            
            split = user_input.replace("mem", "").strip().split(" ")
            start = int(split[0], 16)
            start = start - start%16
            end   = start+int(split[1], 16)
            while(end%16 != 0):
                end+=1
            
            # head
            head = "MEM  |"
            for i in range(0, 16):
                head += "  {0:0{1}X} ".format(i, 1)
            dlog.print_msg("SYS", head + "|")
    
            dlog.print_msg("SYS", "".ljust(71, "-"))
            
            # body
            line = None
            for addr in range(start, end):
                if(addr%16==0):
                    if(line):
                        dlog.print_msg("SYS", line + "|")
                    left = (addr&0xFFF0)
                    line = "{0:0{1}X}".format(left, 4) + " |"
                byte = mem.read_byte(addr)
                if(zeros):
                    line += " {0:0{1}X} ".format(byte, 2)               
                else:
                    line += " {0:0{1}X} ".format(byte, 2).replace("00", "  ") 
            dlog.print_msg("SYS", line + "|")
            self.print_spacer()
            return
        elif(user_input.startswith("reset")):
            sdlboy_window.reset()
            return
        elif(user_input.startswith("limit")):
            val = user_input.replace("limit", "")
            sdlboy_window.glob.cycle_limiter = int(val)            
            return
        elif(user_input.startswith("speed")):
            ratio = float(user_input.replace("speed", ""))
            if(ratio == 1):
                sdlboy_window.glob.cycle_limiter = 0
            else:
                sdlboy_window.glob.cycle_limiter = int(70224.0*ratio)
            return
        elif(user_input.startswith("st")):
            if(log_free):
                dlog.enable.all()
            self.print_spacer()
            lcd.print_state()
            car.print_state()
            z80.print_state()
            self.print_spacer()
            return
        elif(user_input.startswith("rb")):
            if(log_free):
                dlog.enable.all()
            split = user_input.split(" ")
            addr = int(split[1], 16)
            mem.read_byte(addr)
            self.print_spacer()
            return
        elif(user_input.startswith("rw")):
            if(log_free):
                dlog.enable.all()
            split = user_input.split(" ")
            addr = int(split[1], 16)
            mem.read_word(addr)
            self.print_spacer()
            return
        elif(user_input.startswith("wb")):
            if(log_free):
                dlog.enable.all()
            split = user_input.split(" ")
            addr = int(split[1], 16)
            byte = int(split[2], 16)
            mem.write_byte(addr, byte)
            self.print_spacer()
            return
        elif(user_input.startswith("ww")):
            if(log_free):
                dlog.enable.all()
            split = user_input.split(" ")
            addr = int(split[1], 16)
            word = int(split[2], 16)
            mem.write_word(addr, word)
            self.print_spacer()
            return
        elif(user_input.startswith("ime 0")):
            if(log_free):
                dlog.enable.all()
            z80.state.interrupt_master_enable = 0
            self.print_spacer()
            return
        elif(user_input.startswith("ime 1")):
            if(log_free):
                dlog.enable.all()
            z80.state.interrupt_master_enable = 1
            z80.state.interrupt_master_enable_skip_one_cycle = 1
            self.print_spacer()
            return
        elif(user_input.startswith("setif")):
            if(log_free):
                dlog.enable.all()
            n = int(user_input.replace("setif", ""))
            mem.write_byte(0xFF0F, mem.read_byte(0xFF0F)|(0x01 << n))
            self.print_spacer()
            return
        elif(user_input.startswith("setie")):
            if(log_free):
                dlog.enable.all()
            n = int(user_input.replace("setie", ""))
            mem.write_byte(0xFFFF, mem.read_byte(0xFFFF)|(0x01 << n))
            self.print_spacer()
            return
            
        real_time_start = time.time()
        cpu_time_start = z80.state.time_passed
        
        if(user_input.startswith("t")):
            if(log_free):
                dlog.enable.errors()
            val = user_input.replace("t", "").strip()
            if(val.startswith("+")):
                # loop for N seconds
                target_time = float(val.replace("+", "").strip())
                target_time += z80.state.time_passed
                while(z80.state.time_passed < target_time):
                    self.do_loop()             
            else:
                # loop until cpu time = N seconds
                target_time = float(val.replace("=", "").strip())
                while(z80.state.time_passed < target_time):
                    self.do_loop()
        elif(user_input.startswith("pc")):
            if(log_free):
                dlog.enable.errors()
            val = user_input.replace("pc", "").strip()
            if(val.startswith(">")):
                # loop until z80_pc > target_pc
                target_pc = int(val.replace(">", ""), 16)
                while(z80.reg.pc <= target_pc):
                    self.do_loop()
            elif(val.startswith("<")):
                # loop until z80_pc < target_pc
                target_pc = int(val.replace("<", ""), 16)
                while(z80.reg.pc >= target_pc):
                    self.do_loop()
            elif(val.startswith("=")):
                # loop until z80_pc = target_pc            
                target_pc = int(val.replace("=", ""), 16)
                while(z80.reg.pc != target_pc):
                    self.do_loop()   
            else:
                raise ValueError("invalid input")
            dlog.print_msg("SYS", "PC is now at " + "0x{0:0{1}X}".format(z80.reg.pc, 4))
        elif(user_input.strip() == ""):
            if(log_free):
                dlog.enable.all()
            self.do_loop()   
        elif(user_input.startswith("s")):
            if(log_free):
                dlog.enable.errors()
            user_input = user_input.replace("s", "")
            user_input = user_input.replace("+", "")
            steps = int(user_input)
            for i in range(0, steps):
                self.do_loop()     
        else:       
            if(log_free): 
                dlog.enable.all() 
            try:
                steps = int(user_input)        
                for i in range(0, steps):
                    self.do_loop()              
            except:           
                raise ValueError("invalid input")
        real_time_passed = time.time() - real_time_start
        self.print_spacer()
        if(real_time_passed > 1 or print_perf):
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
input_handler = InputHandler()


    


    