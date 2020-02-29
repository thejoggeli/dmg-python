import dlog
import z80
import mem
import cartridge as car

z80.init()

quit = False
steps = 0
steps_default = 5

car.load_gb_file("roms/Super Mario Land (World).gb")

def print_spacer():
    dlog.print_msg("SYS", "============================================================================================================")

while(not quit):
    print_spacer()
    user_input = input("[ SYS ] >>> steps (def=" + str(steps_default) + "): ")
    if(user_input == "q"):
        quit = True
        break
    if(user_input.endswith("silent")):
        user_input = user_input.replace("silent", "")
        dlog.level = dlog.LEVEL_WARNING 
    try:
        steps = int(user_input)
        steps_default = steps
    except:
        steps = steps_default
    for i in range(0, steps):
        print_spacer()
        z80.execute()    
    dlog.level = dlog.LEVEL_ALL
    print_spacer()
    dlog.print_z80_st()
print_spacer()
z80.exit()