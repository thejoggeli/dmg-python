import hw_z80 as z80
import hw_mem as mem
import sys

silent = False

class Enable():
    debug = True
    sys = True
    z80 = True
    lcd = True
    mem_warnings = True
    mem_read = True
    mem_write = True
    car_state = True
    car_banking = True
    car_ram_enable = True
    
    def __init__(self, saveable):
        if(saveable):
            self.saved = Enable(False)
    
    def errors(self):    
        self.sys = False
        self.z80 = False
        self.lcd = False
        self.mem_warnings = False
        self.mem_read = False
        self.mem_write = False
        self.car_state = False
        self.car_banking = False
        self.car_ram_enable = False
    def warnings(self):    
        self.sys = False
        self.z80 = False
        self.lcd = False
        self.mem_warnings = True
        self.mem_read = False
        self.mem_write = False
        self.car_state = False
        self.car_banking = False
        self.car_ram_enable = False
    def all(self):    
        self.sys = True
        self.z80 = True
        self.lcd = True
        self.mem_warnings = True
        self.mem_read = True
        self.mem_write = True
        self.car_state = True
        self.car_banking = True
        self.car_ram_enable = True
             
    
enable = Enable(True);

def init():
    pass


def print_error_console(src, msg, cat="ERROR"):
    err = "["+src+"] "
    err += "ERROR".ljust(14)
    err += "PC=" + "0x{0:0{1}X}".format(z80.state.instruction_location, 4) + "\t"
   #err += "Step=" + str(z80.state.step_nr) + " / "
    err += msg
    print(err)
    sys.exit()

def print_warning_console(src, msg, cat="WARNING"):
    war = "["+src+"] "
    war += "WARNING".ljust(14)
    war += "PC=" + "0x{0:0{1}X}".format(z80.state.instruction_location, 4) + "\t"
   #war += "Step=" + str(z80.state.step_nr) + " / "
    war += msg
    print(war)
    
def print_msg_console(src, msg, cat=None):
    txt = "["+src+"] "
    if(cat):
        txt += cat.ljust(14)
    txt += msg
    print(txt)

print_error = print_error_console
print_warning = print_warning_console
print_msg = print_msg_console