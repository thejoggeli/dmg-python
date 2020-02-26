import z80
import mem

enable_z80 = True
enable_mem_read = True
enable_mem_write = True

def init():
    print_msg("LOG", "init")

def print_error(src, msg):
    print("[ "+src+" ]" + "\tERROR! " + msg)

def print_msg(src, msg):
    print("[ "+src+" ]" + "\t" + msg)
    
def print_z80_st():
    print_msg(
        "Z80",
        "registers\t"
        "PC=" + "0x{0:0{1}X}".format(z80.reg.pc, 4) + "\t" +
        "B="  + "0x{0:0{1}X}".format(z80.reg.b, 2) + "\t" +
        "D="  + "0x{0:0{1}X}".format(z80.reg.d, 2) + "\t" +
        "H="  + "0x{0:0{1}X}".format(z80.reg.h, 2) + "\t" +
        "A="  + "0x{0:0{1}X}".format(z80.reg.a, 2) + "\t" +
        "Z N H C" + "\t\t" +
        "Cycles"
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
        str(z80.reg.get_flag_c()) + "\t\t" +
        str(z80.cycles)
    )
    
def print_z80_op():
    print_msg(
        "Z80", 
        "op_decode\t" + 
        "0x{0:0{1}X}".format(z80.op.code, 2) + "\t" + 
        z80.op.name(z80.op.code) + "\t" + 
        z80.op.params(z80.op.code))

def print_mem(action, addr, n1, value, n2):
    print_msg(
        "MEM",
        action + "\t" + 
        "0x{0:0{1}X}".format(addr, n1) + "\t" +
        "0x{0:0{1}X}".format(value, n2)
    )
