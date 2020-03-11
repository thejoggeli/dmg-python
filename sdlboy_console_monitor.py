import sdl2
import sdlboy_text
import sdlboy_window
import sdlboy_time
import sdlboy_console
import sdlboy_console_component
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

class Monitor(sdlboy_console_component.ConsoleComponent):
    font = None
    monitor_ptr = 0
    monitor_texts = []
    line_spacing = 4
    def on_init(self):
        self.font = sdlboy_text.get_font("console")
        self.preferred_w = self.font.char_width*15
    def on_update(self):
        self.set_render_required()
    def on_render(self):
        self.monitor_ptr = 0        
        self.monitor("FPS:" + str(sdlboy_time.fps))
        speed_estimate = "{0:.1f}".format(round(sdlboy_window.glob.speed_estimate*100))  
        self.monitor("Speed:" + speed_estimate + "%")         
        limiter = str(sdlboy_window.glob.cycle_limiter)
        if(limiter):
            self.monitor("Limiter:" + str(limiter))    
        else:
            self.monitor("Limiter:off")
            
        self.monitor("T(Z80):" + "{0:.1f}".format(round(z80.state.time_passed, 1)))
        self.monitor("T(IRL):" + "{0:.1f}".format(round(sdlboy_time.since_start, 1)))
        
        # Z80
        self.monitor("BIOS:" + str(bool(mem.bios_running)))
        self.monitor("JOYP:" + "%{0:0{1}b}".format(mem.read_byte_silent(0xFF00),8))
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
        self.monitor(cld.decode_instruction_to_string(z80.state.instruction_location, with_addr=False))
        self.monitor(cld.decode_instruction_to_string(z80.reg.pc, with_addr=False))
        self.monitor("---------------")
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
    def on_resize(self):
        pass    
    def monitor_grow(self):
        text = sdlboy_text.Text(
            font=self.font,
            value="---", 
            buffer_size=16
        )
        text.set_position(0, len(self.monitor_texts)*(self.font.char_height+self.line_spacing))    
        self.monitor_texts.append(text)
    def monitor(self, str):
        if(self.monitor_ptr >= len(self.monitor_texts)):
            self.monitor_grow()
        self.monitor_texts[self.monitor_ptr].value = str
        self.monitor_texts[self.monitor_ptr].update()
        self.monitor_ptr += 1   
        
    

