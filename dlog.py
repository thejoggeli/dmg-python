import z80
import mem
import sys

silent = False

class Enable():
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

def print_error(src, msg):
    print("[ "+src+" ]" + "\tERROR! " + msg)
    sys.exit()

def print_warning(src, msg):
    print("[ "+src+" ]" + "\tWARNING! " + msg)

def print_msg(src, msg):
    print("[ "+src+" ]" + "\t" + msg)
