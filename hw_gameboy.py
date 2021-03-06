import util_dlog as dlog
import util_code_loader as cld
import hw_z80 as z80
import hw_mem as mem
import hw_lcd as lcd
import hw_cartridge as car
import hw_video as vid
import hw_joypad as joy
import hw_timer as tim
import sys

roms = {
    "mario1":    "Super Mario Land (JUE) (V1.1) [!].gb",
    "mario2":    "Super Mario Land 2 - 6 Golden Coins (USA, Europe).gb",
    "tetris":    "Tetris (World) (Rev A).gb",
    "donkey2":   "Donkey Kong Land 2 (USA, Europe) (SGB Enhanced).gb",
    "pokemon":   "Pokemon - Blue Version (UE) [S][!].gb",
}

def init():
    game = "tetris"
    if(len(sys.argv) > 1):
        arg_game = sys.argv[1]
        if(arg_game in roms):
            game = arg_game
    car.load_gb_file("roms/"+roms[game])
    car.print_info()
    reset()
    
def reset():
    z80.init()
    car.init()
    lcd.init()
    mem.init()
    vid.init()
    joy.init()
    tim.init()
    car.map_memory()
    lcd.map_memory()
    vid.map_memory()
    joy.map_memory()    
    tim.map_memory()    
    
def tick():
    if(dlog.enable.lcd):
        lcd.print_state()
    if(dlog.enable.car_state):
        car.print_state()
    z80.update()
    lcd.update()
    car.update()
    tim.update()

def run_for_n_seconds(n):
    # loop for N seconds
    target_time = n + z80.state.time_passed
    while(z80.state.time_passed < target_time):
        tick()
