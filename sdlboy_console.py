import sdl2
import sdlboy_text
import sdlboy_window
import sdlboy_time
import sdlboy_input
import sdlboy_monitor
import sdlboy_console_textview
import sdlboy_console_inputview
import sdlboy_console_topview
import time
import hw_z80 as z80
import hw_mem as mem
import hw_lcd as lcd
import hw_cartridge as car
import hw_video as vid
import hw_gameboy as gameboy
import util_dlog as dlog
import util_config as config
import util_code_loader as cld

is_open = False
has_control = False
allow_input = False

class Glob:
    renderer = None
glob = Glob()

textview = None
inputview = None
topview = None

def init():
    global textview, inputview
    global topview, topview_tile, topview_mem
    glob.renderer = sdlboy_window.glob.renderer
    textview = sdlboy_console_textview.Textview()
    inputview = sdlboy_console_inputview.Inputview()
    topview = sdlboy_console_topview.Topview()
    input_handler.print_spacer()
   #dlog.print_error = print_error
   #dlog.print_warning = print_warning
   #dlog.print_msg = print_msg
        
def set_open(b):
    global is_open
    if(is_open == b):
        return
    is_open = b
    if(is_open):
        # open
        sdl2.SDL_SetRenderDrawBlendMode(glob.renderer, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_StartTextInput();
        is_open = True
        set_allow_input(False)
        topview.open_memview()
        dlog.enable.errors()
    else:   
        #close 
        is_open = False
        sdl2.SDL_StopTextInput();
        dlog.enable.errors()
        set_allow_input(True)

def set_control(b):
    global has_control
    has_control = b
    
def set_allow_input(b):
    global allow_input
    allow_input = b
    
def update():
    topview.update()
    
def resize():
    inputview.resize()
    topview.resize()
    textview.resize()

def render():
    if(has_control):
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0x80, 0x00, 0x40, 0xB0)   
    else:
        sdl2.SDL_SetRenderDrawColor(glob.renderer, 0x00, 0x40, 0x80, 0xB0) 
    sdl2.SDL_RenderFillRect(glob.renderer, sdlboy_window.glob.window_rect)    
    textview.render()
    inputview.render()
    topview.render()
    
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
        elif(key == 27):
            # ESC
            if(topview.is_open):
                topview.close()
                resize()
        elif(key == 1073741885):       
            # F4
            set_control(not has_control)
            if(has_control):
                dlog.enable.all()
            else:
                dlog.enable.errors()
        elif(key == 1073741884):       
            # F3
            set_allow_input(not allow_input)
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
    spacer = "".ljust(71, "=")
    def print_spacer(self):
        dlog.print_msg("SYS", self.spacer)
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
            textview.print_line(head + "|", bg=(0,0,0,127))
    
            dlog.print_msg("SYS", "".ljust(71, "-"))
            textview.print_line("".ljust(71, "-"), bg=(0,0,0,127))
            
            # body
            line = None
            for addr in range(start, end):
                if(addr%16==0):
                    if(line):
                        dlog.print_msg("SYS", line + "|")
                        textview.print_line(line + "|", bg=(0,0,0,127))
                    left = (addr&0xFFF0)
                    line = "{0:0{1}X}".format(left, 4) + " |"
                byte = mem.read_byte(addr)
                if(zeros):
                    line += " {0:0{1}X} ".format(byte, 2)               
                else:
                    line += " {0:0{1}X} ".format(byte, 2).replace("00", "  ") 
            dlog.print_msg("SYS", line + "|")
            textview.print_line(line + "|", bg=(0,0,0,127))
            textview.print_line("".ljust(71, "-"), bg=(0,0,0,127))
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
            lcd.render()
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
            lcd.render()
            dlog.print_msg("SYS", "PC is now at " + "0x{0:0{1}X}".format(z80.reg.pc, 4))
        elif(user_input.strip() == ""):
            if(log_free):
                dlog.enable.all()
            instr = cld.decode_instruction_to_string(z80.reg.pc)
            textview.print_line(instr)
            self.do_loop()            
            lcd.render()
        elif(user_input.startswith("s")):
            if(log_free):
                dlog.enable.errors()
            user_input = user_input.replace("s", "")
            user_input = user_input.replace("+", "")
            steps = int(user_input)
            for i in range(0, steps):
                self.do_loop()              
            lcd.render()
        else:       
            if(log_free): 
                dlog.enable.all() 
            try:
                steps = int(user_input)        
                for i in range(0, steps):
                    instr = cld.decode_instruction_to_string(z80.reg.pc)
                    textview.print_line(instr)
                    self.do_loop()              
                lcd.render()
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


    


    