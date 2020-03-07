import dlog
import z80
import mem
import lcd
import cartridge as car
import time
import video as vid
import events



def init():
    car.load_gb_file("roms/Super Mario Land (JUE) (V1.1) [!].gb")
    z80.init()
    car.init()
    lcd.init()
    mem.init()
    vid.init()
    car.map_memory()
    lcd.map_memory()
    vid.map_memory()
    
def tick():    
    z80.update()
    lcd.update()
    car.update()