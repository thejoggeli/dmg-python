import time
import hw_z80 as z80
import hw_mem as mem
import hw_lcd as lcd
import hw_cartridge as car
import hw_video as vid
import hw_gameboy as gameboy
import util_events as events
import util_dlog as dlog

gameboy.init()
car.print_info()

quit = False
steps = 0

def print_spacer():
    dlog.print_msg("SYS", "===========================================================================================================")

def do_loop():
    if(dlog.enable.sys):
        print_spacer()
    gameboy.tick()
    
# COMMAND .....................................................
# q             quit
# N             run for N steps
# t+N           run for N seconds
# t=N           run until CPU time = N seconds
# pc=N          run until program counter = N        
# pc>N          run until program counter > N        
# pc<N          run until program counter < N        
# st            print state
# rb A          read byte from memory address A
# wb A B        write byte B to memory address A
# rw A          read word from memory address A
# ww A B        write word B to memory address A
# setie N       set interrupt enabled bit N
# setif N       set interrupt reqiested bit N
# ime 1         interrupt master enable 
# ime 0         interrupt master disable 
# SUFFIX ......................................................
# -             print warnings only
# --            print nothing
# perf          perf

print_spacer()
while(not quit):
    user_input = input("[ SYS ] >>> Command:\t")
    dlog.enable.all();
    
    printPerformance = False
    suffixFound = True
    while(suffixFound):
        suffixFound = False
        user_input = user_input.strip()
        if(user_input.endswith("--")):
            user_input = user_input.replace("--", "").strip()
            dlog.enable.errors()
            suffixFound = True
        if(user_input.endswith("-")):
            user_input = user_input.replace("-", "").strip()
            dlog.enable.warnings()
            suffixFound = True
        if(user_input.endswith("perf")):
            user_input = user_input.replace("perf", "").strip()
            printPerformance = True
            suffixFound = True
    
    if(user_input == "q"):
        quit = True
        break
    if(user_input.startswith("st")):
        print_spacer()
        lcd.print_state()
        car.print_state()
        z80.print_state()
        print_spacer()
        continue
    if(user_input.startswith("rb")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        mem.read_byte(addr)
        print_spacer()
        continue
    if(user_input.startswith("rw")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        mem.read_word(addr)
        print_spacer()
        continue
    if(user_input.startswith("wb")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        byte = int(split[2], 16)
        mem.write_byte(addr, byte)
        print_spacer()
        continue
    if(user_input.startswith("ww")):
        split = user_input.split(" ")
        addr = int(split[1], 16)
        word = int(split[2], 16)
        mem.write_word(addr, word)
        print_spacer()
        continue
    if(user_input.startswith("ime 0")):
        z80.state.interrupt_master_enable = 0
        print_spacer()
        continue
    if(user_input.startswith("ime 1")):
        z80.state.interrupt_master_enable = 1
        z80.state.interrupt_master_enable_skip_one_cycle = 1
        print_spacer()
        continue
    if(user_input.startswith("setif")):
        n = int(user_input.replace("setif", ""))
        mem.write_byte(0xFF0F, mem.read_byte(0xFF0F)|(0x01 << n))
        print_spacer()
        continue
    if(user_input.startswith("setie")):
        n = int(user_input.replace("setie", ""))
        mem.write_byte(0xFFFF, mem.read_byte(0xFFFF)|(0x01 << n))
        print_spacer()
        continue
        
    real_time_start = time.time()
    cpu_time_start = z80.state.time_passed
    
    if(user_input.startswith("t")):
        val = user_input.replace("t", "").strip()
        if(val.startswith("+")):
            # loop for N seconds
            target_time = float(val.replace("+", "").strip())
            target_time += z80.state.time_passed
            while(z80.state.time_passed < target_time):
                do_loop()             
        else:
            # loop until cpu time = N seconds
            target_time = float(val.replace("=", "").strip())
            while(z80.state.time_passed < target_time):
                do_loop()
    elif(user_input.startswith("pc")):
        val = user_input.replace("pc", "").strip()
        if(val.startswith(">")):
            # loop until z80_pc > target_pc
            target_pc = int(val.replace(">", ""), 16)
            while(z80.reg.pc <= target_pc):
                do_loop()
        elif(val.startswith("<")):
            # loop until z80_pc < target_pc
            target_pc = int(val.replace("<", ""), 16)
            while(z80.reg.pc >= target_pc):
                do_loop()
        else:
            # loop until z80_pc = target_pc            
            target_pc = int(val.replace("=", ""), 16)
            while(z80.reg.pc != target_pc):
                do_loop()    
        print("[ SYS ] PC is now at " + "0x{0:0{1}X}".format(z80.reg.pc, 4))
    else:
        # loop for n steps
        steps = 1
        try:
            steps = int(user_input)
        except:
            steps = 1
        for i in range(0, steps):
            do_loop()
    real_time_passed = time.time() - real_time_start
    print_spacer()
    if(real_time_passed > 1 or printPerformance):
         # print performance            
        cpu_time_passed = z80.state.time_passed - cpu_time_start
        time_str = "{0:.3f}".format(round(real_time_passed, 3))
        cpu_time_str = "{0:.3f}".format(round(cpu_time_passed, 3))    
        time_ratio = -1
        if(real_time_passed != 0):
            time_ratio = cpu_time_passed/real_time_passed
        print(
            "[ MSG ] >>> Perform:" + "\t" +
            "CPU=" + cpu_time_str + "s\t" + 
            "Real=" + time_str + "s\t"
            "Ratio=" + str(round(time_ratio,3))
        )
lcd.print_state()
car.print_state()
z80.print_state()
z80.exit()

