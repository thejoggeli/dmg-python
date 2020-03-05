import dlog
import z80
import mem
import lcd
import cartridge as car

car.load_gb_file("roms/Super Mario Land (World).gb")
car.print_info()

z80.init()
car.init()
lcd.init()
mem.init()

car.map_memory()
lcd.map_memory()

car.print_info();

quit = False
steps = 0

def print_spacer():
    dlog.print_msg("SYS", "===========================================================================================================")

while(not quit):
    print_spacer()
    user_input = input("[ SYS ] >>> steps: ")
    dlog.enable.all();
    if(user_input == "q"):
        quit = True
        break
    if(user_input.endswith("ime0")):
        z80.state.interrupt_master_enable = 0
        continue
    if(user_input.endswith("ime1")):
        z80.state.interrupt_master_enable = 1
        z80.state.interrupt_master_enable_skip_one_cycle = 1
        continue
    if(user_input.endswith("if0")):
        mem.mem_zeropage[0x0F] |= 0x01
        continue
    if(user_input.endswith("if1")):
        mem.mem_zeropage[0x0F] |= 0x02
        continue
    if(user_input.endswith("if2")):
        mem.mem_zeropage[0x0F] |= 0x04
        continue
    if(user_input.endswith("if3")):
        mem.mem_zeropage[0x0F] |= 0x08
        continue
    if(user_input.endswith("if4")):
        mem.mem_zeropage[0x0F] |= 0x10
        continue
    if(user_input.endswith("ie0")):
        mem.mem_zeropage[0xFF] |= 0x01
        continue
    if(user_input.endswith("ie1")):
        mem.mem_zeropage[0xFF] |= 0x02
        continue
    if(user_input.endswith("ie2")):
        mem.mem_zeropage[0xFF] |= 0x04
        continue
    if(user_input.endswith("ie3")):
        mem.mem_zeropage[0xFF] |= 0x08
        continue
    if(user_input.endswith("ie4")):
        mem.mem_zeropage[0xFF] |= 0x10
        continue
    if(user_input.endswith("s+")):
        user_input = user_input.replace("s+", "")
        dlog.enable.errors()
    elif(user_input.endswith("s")):
        user_input = user_input.replace("s", "")
        dlog.enable.warnings()
    try:
        steps = int(user_input)
    except:
        steps = 1
    for i in range(0, steps):
        if(dlog.enable.sys):
            print_spacer()
        lcd.update()
        car.update()
        z80.update()
    print_spacer()
    lcd.print_state()
    car.print_state()
    z80.print_state()
print_spacer()
lcd.print_state()
car.print_state()
z80.print_state()
z80.exit()