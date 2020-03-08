import util_dlog as dlog
import hw_z80 as z80
import hw_mem as mem
import hw_lcd as lcd
import hw_cartridge as car
import hw_video as vid

def init():
    car.load_gb_file("roms/Super Mario Land (JUE) (V1.1) [!].gb")
    car.print_info()
    z80.init()
    car.init()
    lcd.init()
    mem.init()
    vid.init()
    car.map_memory()
    lcd.map_memory()
    vid.map_memory()
    
def tick():
    if(dlog.enable.lcd):
        lcd.print_state()
    if(dlog.enable.car_state):
        car.print_state()
    z80.update()
    lcd.update()
    car.update()
