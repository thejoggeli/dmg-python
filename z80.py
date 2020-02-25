import dlog
import mem


class OP:
    cycles = 0
    code = 0
    map = [None]*256
    def name(self):
        return self.map[self.code][1]
    def params(self):
        return self.map[self.code][2]
    def add_to_map(self, code, data):
        if(self.map[code] == None):
            self.map[code] = data        
        else:
            dlog.print_error("Z80", "0x{0:0{1}X}".format(z80.reg.pc, 2) + " already mapped")
op = OP()

class Register:
    value = 0

class RegisterSet:

    b = 0
    c = 0
    d = 0
    e = 0
    h = 0
    l = 0
    a = 0
    f = 0
    pc = 0
    sp = 0
    
    def get_b(self):
        return self.b
    def get_c(self):
        return self.c
    def get_d(self):
        return self.d
    def get_e(self):
        return self.e
    def get_h(self):
        return self.h
    def get_l(self):
        return self.l
    def get_a(self):
        return self.a
    
    def set_b(self, byte):
        self.b = byte
    def set_c(self, byte):
        self.c = byte
    def set_d(self, byte):
        self.d = byte
    def set_e(self, byte):
        self.e = byte
    def set_h(self, byte):
        self.h = byte
    def set_l(self, byte):
        self.l = byte
    def set_a(self, byte):
        self.a = byte
    
    get_r_map = [get_b, get_c, get_d, get_e, get_h, get_l, None, get_a]
    set_r_map = [set_b, set_c, set_d, set_e, set_h, set_l, None, set_a]
    
    def get_bc(self):
        return self.c|(self.b<<8)
    def get_de(self):
        return self.e|(self.d<<8)    
    def get_hl(self):
        return self.l|(self.h<<8)
    def get_af(self):
        return self.f|(self.a<<8)
    def get_sp(self):
        return self.sp
    
    def set_bc(self, bc):
        self.b = (bc>>8)&0xFF
        self.c = bc&0xFF
    def set_de(self, de):
        self.d = (de>>8)&0xFF
        self.e = de&0xFF
    def set_hl(self, hl):
        self.h = (hl>>8)&0xFF
        self.l = hl&0xFF
    def set_af(self, af):
        self.a = (af>>8)&0xFF
        self.f = af&0xFF
    def set_sp(self, sp):
        self.sp = sp
        
    def dec_hl(self):
        hl = self.l|(self.h<<8)
        if(hl == 0):
            self.h = 0xFF
            self.l = 0xFF
        else:
            hl -= 1
            self.h = (hl>>8)&0xFF
            self.l = hl&0xFF

    def inc_hl(self):
        hl = self.l|(self.h<<8)
        if(hl == 0xFFFF):
            self.h = 0x00
            self.l = 0x00
        else:
            hl += 1
            self.h = (hl>>8)&0xFF
            self.l = hl&0xFF
        
    def __init__(self):
        pass
    def get_r(self, r):
        return self.get_r_map[r](self)
    def set_r(self, r, byte):
        return self.set_r_map[r](self, byte)
        
reg = RegisterSet()

cycles = 0

def init():
    pass
    
def execute():
    global op, reg, cycles
    
    # print current cpu state
    if(dlog.enable_z80):
        dlog.print_z80_st()
        
    # fetch op code
    op.code = mem.read_byte(reg.pc)
    reg.pc = (reg.pc+1)&0xFFFF
    
    # print opcode
    if(dlog.enable_z80):
        dlog.print_z80_op()
    
    # execute opcode
    op.map[op.code][0]()
    cycles = cycles + op.cycles
    
def exit():
    # print current cpu state
    if(dlog.enable_z80):
        dlog.print_z80_st()
    
def op_ld_r1_n():
    global reg, op
    r1 = (op.code >> 3)&0x07
    n = mem.read_byte(reg.pc)
    reg.set_r(r1, n)
    reg.pc += 1
    op.cycles = 8
def op_ld_r1_r2():
    global reg, op
    r1 = (op.code >> 3)&0x07
    r2 = (op.code >> 0)&0x07    
    reg.set_r(r1, reg.get_r(r2))
    op.cycles = 4
def op_ld_r1_hlmem():
    global reg, op
    r1 = (op.code >> 3)&0x07
    reg.set_r(r1, mem.read_byte(reg.get_hl()))
    op.cycles = 8
def op_ld_hlmem_r2():
    global reg, op
    r2 = (op.code >> 0)&0x07
    mem.write_byte(reg.get_hl(), reg.get_r(r2))
    op.cycles = 8
def op_ld_hlmem_n():
    global reg, op
    n = mem.read_byte(reg.pc)
    mem.write_byte(reg.get_hl(), n)
    reg.pc += 1
    op.cycles = 12
def op_ld_a_bcmem():
    global reg, op
    reg.set_a(mem.read_byte(reg.get_bc()))
    op.cycles = 8
def op_ld_a_demem():
    global reg, op
    reg.set_a(mem.read_byte(reg.get_de()))
    op.cycles = 8
def op_ld_a_nnmem():
    global reg, op
    lsb = mem.read_byte(reg.pc)
    msb = mem.read_byte(reg.pc+1)
    reg.set_a(mem.read_byte(lsb|(msb<<8)))
    reg.pc += 2
    op.cycles = 16
def op_ld_bcmem_a():
    global reg, op
    mem.write_byte(reg.get_bc(), reg.get_a())
    op.cycles = 8    
def op_ld_demem_a():
    global reg, op
    mem.write_byte(reg.get_de(), reg.get_a())
    op.cycles = 8    
def op_ld_nnmem_a():
    global reg, op
    lsb = mem.read_byte(reg.pc)
    msb = mem.read_byte(reg.pc+1)
    mem.write_byte(lsb|(msb<<8), reg.get_a())
    reg.pc += 2
    op.cycles = 16
def op_ld_a_ff00c():
    global reg, op
    reg.set_a(mem.read_byte(0xFF00|reg.get_c()))
    op.cycles = 8
def op_ld_ff00c_a():
    global reg, op
    mem.write_byte(0xFF00|reg.get_c(), reg.get_a())
    op.cycles = 8
def op_ld_a_ff00n():
    global reg, op
    n = mem.read_byte(reg.pc)
    reg.set_a(mem.read_byte(0xFF00|n))
    reg.pc += 1
    op.cycles = 12
def op_ld_ff00n_a():
    global reg, op
    n = mem.read_byte(reg.pc)
    mem.write_byte(0xFF00|n, reg.get_a())
    reg.pc += 1
    op.cycles = 12
def op_ldd_a_hlmem():
    global reg, op
    hl = reg.get_hl()
    reg.set_a(mem.read_byte(reg.get_hl()))
    reg.dec_hl()
    op.cycles = 8    
def op_ldd_hlmem_a():
    global reg, op
    hl = reg.get_hl() 
    mem.write_byte(reg.get_hl(), reg.get_a())
    reg.dec_hl()
    op.cycles = 8   
def op_ldi_a_hlmem(): 
    global reg, op
    hl = reg.get_hl()
    reg.set_a(mem.read_byte(reg.get_hl()))
    reg.inc_hl()
    op.cycles = 8    
def op_ldi_hlmem_a():
    global reg, op
    hl = reg.get_hl() 
    mem.write_byte(reg.get_hl(), reg.get_a())
    reg.inc_hl()
    op.cycles = 8   
def op_xxx():
    global reg, op
    dlog.print_error("Z80", "invalid opcode " + hex(op.code) + " at " +  hex(reg.pc-1))

op.map = [op_xxx]*256

op.map[0x7F] = [op_ld_r1_r2, "LD", "A,A"]
op.map[0x78] = [op_ld_r1_r2, "LD", "A,B"]
op.map[0x79] = [op_ld_r1_r2, "LD", "A,C"]
op.map[0x7A] = [op_ld_r1_r2, "LD", "A,D"]
op.map[0x7B] = [op_ld_r1_r2, "LD", "A,E"]
op.map[0x7C] = [op_ld_r1_r2, "LD", "A,H"]
op.map[0x7D] = [op_ld_r1_r2, "LD", "A,L"]
op.map[0x47] = [op_ld_r1_r2, "LD", "B,A"]
op.map[0x40] = [op_ld_r1_r2, "LD", "B,B"]
op.map[0x41] = [op_ld_r1_r2, "LD", "B,C"]
op.map[0x42] = [op_ld_r1_r2, "LD", "B,D"]
op.map[0x43] = [op_ld_r1_r2, "LD", "B,E"]
op.map[0x44] = [op_ld_r1_r2, "LD", "B,H"]
op.map[0x45] = [op_ld_r1_r2, "LD", "B,L"]
op.map[0x4F] = [op_ld_r1_r2, "LD", "C,A"]
op.map[0x48] = [op_ld_r1_r2, "LD", "C,B"]
op.map[0x49] = [op_ld_r1_r2, "LD", "C,C"]
op.map[0x4A] = [op_ld_r1_r2, "LD", "C,D"]
op.map[0x4B] = [op_ld_r1_r2, "LD", "C,E"]
op.map[0x4C] = [op_ld_r1_r2, "LD", "C,H"]
op.map[0x4D] = [op_ld_r1_r2, "LD", "C,L"]
op.map[0x57] = [op_ld_r1_r2, "LD", "D,A"]
op.map[0x50] = [op_ld_r1_r2, "LD", "D,B"]
op.map[0x51] = [op_ld_r1_r2, "LD", "D,C"]
op.map[0x52] = [op_ld_r1_r2, "LD", "D,D"]
op.map[0x53] = [op_ld_r1_r2, "LD", "D,E"]
op.map[0x54] = [op_ld_r1_r2, "LD", "D,H"]
op.map[0x55] = [op_ld_r1_r2, "LD", "D,L"]
op.map[0x5F] = [op_ld_r1_r2, "LD", "E,A"]
op.map[0x58] = [op_ld_r1_r2, "LD", "E,B"]
op.map[0x59] = [op_ld_r1_r2, "LD", "E,C"]
op.map[0x5A] = [op_ld_r1_r2, "LD", "E,D"]
op.map[0x5B] = [op_ld_r1_r2, "LD", "E,E"]
op.map[0x5C] = [op_ld_r1_r2, "LD", "E,H"]
op.map[0x5D] = [op_ld_r1_r2, "LD", "E,L"]
op.map[0x67] = [op_ld_r1_r2, "LD", "H,A"]
op.map[0x60] = [op_ld_r1_r2, "LD", "H,B"]
op.map[0x61] = [op_ld_r1_r2, "LD", "H,C"]
op.map[0x62] = [op_ld_r1_r2, "LD", "H,D"]
op.map[0x63] = [op_ld_r1_r2, "LD", "H,E"]
op.map[0x64] = [op_ld_r1_r2, "LD", "H,H"]
op.map[0x65] = [op_ld_r1_r2, "LD", "H,L"] 
op.map[0x6F] = [op_ld_r1_r2, "LD", "L,A"]
op.map[0x68] = [op_ld_r1_r2, "LD", "L,B"]
op.map[0x69] = [op_ld_r1_r2, "LD", "L,C"]
op.map[0x6A] = [op_ld_r1_r2, "LD", "L,D"]
op.map[0x6B] = [op_ld_r1_r2, "LD", "L,E"]
op.map[0x6C] = [op_ld_r1_r2, "LD", "L,H"]
op.map[0x6D] = [op_ld_r1_r2, "LD", "L,L"]

op.map[0x3E] = [op_ld_r1_n, "LD", "A,n"]
op.map[0x06] = [op_ld_r1_n, "LD", "B,n"]
op.map[0x0E] = [op_ld_r1_n, "LD", "C,n"]
op.map[0x16] = [op_ld_r1_n, "LD", "D,n"]
op.map[0x1E] = [op_ld_r1_n, "LD", "E,n"]
op.map[0x26] = [op_ld_r1_n, "LD", "H,n"]
op.map[0x2E] = [op_ld_r1_n, "LD", "L,n"]

op.map[0xEA] = [op_ld_nnmem_a,  "LD", "(nn),A"]
op.map[0x02] = [op_ld_bcmem_a,  "LD", "(BC),A"]
op.map[0x12] = [op_ld_demem_a,  "LD", "(DE),A"]
op.map[0x77] = [op_ld_hlmem_r2, "LD", "(HL),A"]
op.map[0x70] = [op_ld_hlmem_r2, "LD", "(HL),B"]
op.map[0x71] = [op_ld_hlmem_r2, "LD", "(HL),C"]
op.map[0x72] = [op_ld_hlmem_r2, "LD", "(HL),D"]
op.map[0x73] = [op_ld_hlmem_r2, "LD", "(HL),E"]
op.map[0x74] = [op_ld_hlmem_r2, "LD", "(HL),H"]
op.map[0x75] = [op_ld_hlmem_r2, "LD", "(HL),L"]
op.map[0x36] = [op_ld_hlmem_n,  "LD", "(HL),n"]

op.map[0xFA] = [op_ld_a_nnmem,  "LD", "A,(nn)"]
op.map[0x0A] = [op_ld_a_bcmem,  "LD", "A,(BC)"]
op.map[0x1A] = [op_ld_a_demem,  "LD", "A,(DE)"]
op.map[0x7E] = [op_ld_r1_hlmem, "LD", "A,(HL)"]
op.map[0x46] = [op_ld_r1_hlmem, "LD", "B,(HL)"]
op.map[0x4E] = [op_ld_r1_hlmem, "LD", "C,(HL)"]
op.map[0x56] = [op_ld_r1_hlmem, "LD", "D,(HL)"]
op.map[0x5E] = [op_ld_r1_hlmem, "LD", "E,(HL)"]
op.map[0x66] = [op_ld_r1_hlmem, "LD", "H,(HL)"]
op.map[0x6E] = [op_ld_r1_hlmem, "LD", "L,(HL)"]

op.map[0xF2] = [op_ld_a_ff00c, "LD", "A,(0xFF00+C)"]
op.map[0xE2] = [op_ld_ff00c_a, "LD", "(0xFF00+C),A"]
op.map[0xF0] = [op_ld_a_ff00n, "LD", "A,(0xFF00+n)"]
op.map[0xE0] = [op_ld_ff00n_a, "LD", "(0xFF00+n),A"]

op.map[0x3A] = [op_ldd_a_hlmem, "LDD", "A,(HL)"]
op.map[0x32] = [op_ldd_hlmem_a, "LDD", "(HL),A"]
op.map[0x2A] = [op_ldi_a_hlmem, "LDI", "A,(HL)"]
op.map[0x22] = [op_ldi_hlmem_a, "LDI", "(HL),A"]

















