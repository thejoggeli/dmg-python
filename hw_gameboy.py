import util_dlog as dlog
import hw_z80 as z80
import hw_mem as mem
import hw_lcd as lcd
import hw_cartridge as car
import hw_video as vid

def init():
    #car.load_gb_file("roms/Super Mario Land (JUE) (V1.1) [!].gb")
    #car.load_gb_file("roms/Donkey Kong Land 2 (USA, Europe) (SGB Enhanced).gb")
    #car.load_gb_file("roms/Super Mario Land 2 - 6 Golden Coins (USA, Europe).gb")
    car.load_gb_file("roms/Tetris (World) (Rev A).gb")
    car.print_info()
    reset()
    
def reset():
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

def run_for_n_seconds(n):
    # loop for N seconds
    target_time = n + z80.state.time_passed
    while(z80.state.time_passed < target_time):
        tick()
