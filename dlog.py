import z80
import mem
import sys

LEVEL_ALL = 20
LEVEL_WARNING = 10
LEVEL_ERROR = 0

level = LEVEL_ALL
silent = False
enable_z80 = True
enable_z80_interrupt = True
enable_mem_read = True
enable_mem_write = True
enable_car_state = True
enable_car_banking = True
enable_car_ram_enable = True

def init():
    pass

def print_error(src, msg):
    print("[ "+src+" ]" + "\tERROR! " + msg)
    sys.exit()

def print_warning(src, msg):
    if(level < LEVEL_WARNING):
        return
    print("[ "+src+" ]" + "\tWARNING! " + msg)

def print_msg(src, msg):
    if(level < LEVEL_ALL):
        return
    print("[ "+src+" ]" + "\t" + msg)
    
def print_z80_st():
    if(level < LEVEL_ALL):
        return
    if(enable_z80_interrupt):
        print_msg(
            "Z80", 
            "interrupt" + "\t" + 
            "IME=" + 
            str(z80.state.interrupt_master_enable) + "/" + 
            str(z80.state.interrupt_master_enable_skip_one_cycle) + "\t\t" + 
            "IE=" + "{0:0{1}b}".format(mem.mem_zeropage[0xFF],5) + "\t" +
            "IF=" + "{0:0{1}b}".format(mem.mem_zeropage[0x0F],5)
        )
    print_msg(
        "Z80",
        "registers\t"
        "PC=" + "0x{0:0{1}X}".format(z80.reg.pc, 4) + "\t" +
        "B="  + "0x{0:0{1}X}".format(z80.reg.b, 2) + "\t" +
        "D="  + "0x{0:0{1}X}".format(z80.reg.d, 2) + "\t" +
        "H="  + "0x{0:0{1}X}".format(z80.reg.h, 2) + "\t" +
        "A="  + "0x{0:0{1}X}".format(z80.reg.a, 2) + "\t" +
        "Z N H C" +
        "Step".rjust(13, " ") +
        "Cycles".rjust(13, " ") +
        "Time".rjust(10, " ")
    )
    print_msg(
        "Z80",
        "registers\t" +
        "SP=" + "0x{0:0{1}X}".format(z80.reg.sp, 4) + "\t" +
        "C="  + "0x{0:0{1}X}".format(z80.reg.c, 2) + "\t" +
        "E="  + "0x{0:0{1}X}".format(z80.reg.e, 2) + "\t" +
        "L="  + "0x{0:0{1}X}".format(z80.reg.l, 2) + "\t" +
        "F="  + "0x{0:0{1}X}".format(z80.reg.f, 2) + "\t" +
        str(z80.reg.get_flag_z()) + " " +
        str(z80.reg.get_flag_n()) + " " +
        str(z80.reg.get_flag_h()) + " " +
        str(z80.reg.get_flag_c()) +
        str(z80.state.step_nr).rjust(13, " ") +
        str(z80.state.cycles_total).rjust(13, " ") +
        "{0:.2f}".format(round(z80.state.time_passed, 2),2).rjust(10, " ")
    )
    
def print_z80_op():
    if(level < LEVEL_ALL):
        return
    info = z80.op.get_opcode_info(z80.op.prefix, z80.op.code)
    size = info[z80.OPCODE_INFO_SIZE]
    
    msg = ""
    msg += "op_decode\t"
    msg += "0x{0:0{1}X}".format(z80.op.prefix, 2) + "{0:0{1}X}".format(z80.op.code, 2) + "\t"
    msg += info[z80.OPCODE_INFO_NAME] + "\t"
    msg += info[z80.OPCODE_INFO_PARAMS]
    
    params_offset = 1 if z80.op.prefix == 0x00 else 2
    global enable_mem_read
    prev_read = enable_mem_read
    enable_mem_read = False
    for i in range(params_offset, size):
        param = mem.read_byte(z80.op.address+i)
        msg += "\t" + "0x{0:0{1}X}".format(param,2)           
    enable_mem_read = prev_read
    print_msg("Z80", msg)

def print_mem(action, addr, value, name):
    if(level < LEVEL_ALL):
        return
    print_msg(
        "MEM",
        action + "\t" + 
        "0x{0:0{1}X}".format(addr, 4) + "\t" +
        "0x{0:0{1}X}".format(value, 2) + "\t" +
        name
    )
