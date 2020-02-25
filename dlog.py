import z80
import mem

enable_z80 = True
enable_mem_read = True
enable_mem_write = True

def init():
    print_msg("LOG", "init")

def print_error(src, msg):
    print("[ "+src+" ]" + ":\tERROR! " + msg)

def print_msg(src, msg):
    print("[ "+src+" ]" + "\t" + msg)
    
def print_z80_st():
    print_msg("Z80", "cycles\t\t" + str(z80.cycles)) 
    print_msg(
        "Z80",
        "registers_16\t" +
        "PC=" + "0x{0:0{1}X}".format(z80.reg.pc, 4) + "\t" +
        "SP=" + "0x{0:0{1}X}".format(z80.reg.sp, 4)
    )
    print_msg(
        "Z80",
        "registers_8\t" +
        "A="  + "0x{0:0{1}X}".format(z80.reg.a, 2) + "\t" +
        "B="  + "0x{0:0{1}X}".format(z80.reg.b, 2) + "\t" +
        "C="  + "0x{0:0{1}X}".format(z80.reg.c, 2) + "\t" +
        "D="  + "0x{0:0{1}X}".format(z80.reg.d, 2) + "\t" +
        "E="  + "0x{0:0{1}X}".format(z80.reg.e, 2) + "\t" +
        "H="  + "0x{0:0{1}X}".format(z80.reg.h, 2) + "\t" +
        "L="  + "0x{0:0{1}X}".format(z80.reg.l, 2)
    )
    
def print_z80_op():
    print_msg("Z80", "op_decode\t" + "0x{0:0{1}X}".format(z80.op.code, 2) + "\t" + z80.op.name() + "\t" + z80.op.params())

def print_mem(action, addr, n1, value, n2):
    print_msg(
        "MEM",
        action + "\t" + 
        "0x{0:0{1}X}".format(addr, n1) + "\t" +
        "0x{0:0{1}X}".format(value, n2)
    )
