import dlog
import mem


class OP:
    cycles = 0
    code = 0
    map = [None]*256
    def name(self, opcode):
        return self.map[opcode][1]
    def params(self, opcode):
        return self.map[opcode][2]
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
    
    def set_bc(self, word):
        self.b = (word>>8)&0xFF
        self.c = word&0xFF
    def set_de(self, word):
        self.d = (word>>8)&0xFF
        self.e = word&0xFF
    def set_hl(self, word):
        self.h = (word>>8)&0xFF
        self.l = word&0xFF
    def set_af(self, word):
        self.a = (word>>8)&0xFF
        self.f = word&0xFF
    def set_sp(self, word):
        self.sp = word
        
    def dec_hl(self):
        word = self.l|(self.h<<8)
        if(word == 0):
            self.h = 0xFF
            self.l = 0xFF
        else:
            word -= 1
            self.h = (word>>8)&0xFF
            self.l = word&0xFF

    def inc_hl(self):
        word = self.l|(self.h<<8)
        if(word == 0xFFFF):
            self.h = 0x00
            self.l = 0x00
        else:
            word += 1
            self.h = (word>>8)&0xFF
            self.l = word&0xFF
            
    def reset_flags(self):
        self.f = 0x00
        
    def set_flag_z(self):
        self.f |= 0x80
    def set_flag_n(self):
        self.f |= 0x40    
    def set_flag_h(self):
        self.f |= 0x20
    def set_flag_c(self):
        self.f |= 0x10
    
    def reset_flag_z(self):
        self.f &= 0x7F
    def reset_flag_n(self):
        self.f &= 0xBF
    def reset_flag_h(self):
        self.f &= 0xDF
    def reset_flag_c(self):
        self.f &= 0xEF
    
    def get_flag_z(self):
        return (self.f >> 7) & 0x01
    def get_flag_n(self):
        return (self.f >> 6) & 0x01
    def get_flag_h(self):
        return (self.f >> 5) & 0x01
    def get_flag_c(self):
        return (self.f >> 4) & 0x01    
    
    get_r_map = [get_b, get_c, get_d, get_e, get_h, get_l, None, get_a]
    set_r_map = [set_b, set_c, set_d, set_e, set_h, set_l, None, set_a]
        
    get_rp_map = [get_bc, get_de, get_hl, get_sp]
    set_rp_map = [set_bc, set_de, set_hl, set_sp]
        
    get_rp2_map = [get_bc, get_de, get_hl, get_af]
    set_rp2_map = [set_bc, set_de, set_hl, set_af]
        
    def get_r(self, r):
        return self.get_r_map[r](self)
    def set_r(self, r, byte):
        return self.set_r_map[r](self, byte)
        
    def get_rp(self, rp):
        return self.get_rp_map[rp](self)
    def set_rp(self, rp, word):
        return self.set_rp_map[rp](self, word)
        
    def get_rp2(self, rp2):
        return self.get_rp_map[rp2](self)
    def set_rp2(self, rp2, word):
        return self.set_rp_map[rp2](self, word)
        
    def __init__(self):
        pass
                
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
    op.code = mem.read_byte(reg.pc); reg.pc += 1
    if(reg.pc > 0xFFFF):
        reg.pc &= 0xFFFF
        dlog.print_error("Z80", "pc wrap in execute (what is actual behavior?)")
    
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

######################################################## OP LD (8-bit)###
def op_ld_r1_n():
    r1 = (op.code >> 3)&0x07 #y
    n = mem.read_byte(reg.pc); reg.pc += 1
    reg.set_r(r1, n)
    op.cycles = 8
def op_ld_r1_r2():
    r1 = (op.code >> 3)&0x07 #y
    r2 = (op.code >> 0)&0x07 #z  
    reg.set_r(r1, reg.get_r(r2))
    op.cycles = 4
def op_ld_r1_hlmem():
    r1 = (op.code >> 3)&0x07 #y
    reg.set_r(r1, mem.read_byte(reg.get_hl()))
    op.cycles = 8
def op_ld_hlmem_r2():
    r2 = (op.code >> 0)&0x07 #y
    mem.write_byte(reg.get_hl(), reg.get_r(r2))
    op.cycles = 8
def op_ld_hlmem_n():
    n = mem.read_byte(reg.pc); reg.pc += 1
    mem.write_byte(reg.get_hl(), n)
    op.cycles = 12
def op_ld_a_bcmem():
    reg.set_a(mem.read_byte(reg.get_bc()))
    op.cycles = 8
def op_ld_a_demem():
    reg.set_a(mem.read_byte(reg.get_de()))
    op.cycles = 8
def op_ld_a_nnmem():
    lsb = mem.read_byte(reg.pc); reg.pc += 1
    msb = mem.read_byte(reg.pc); reg.pc += 1
    reg.set_a(mem.read_byte(lsb|(msb<<8)))
    op.cycles = 16
def op_ld_bcmem_a():
    mem.write_byte(reg.get_bc(), reg.get_a())
    op.cycles = 8    
def op_ld_demem_a():
    mem.write_byte(reg.get_de(), reg.get_a())
    op.cycles = 8    
def op_ld_nnmem_a():
    lsb = mem.read_byte(reg.pc); reg.pc += 1
    msb = mem.read_byte(reg.pc); reg.pc += 1
    mem.write_byte(lsb|(msb<<8), reg.get_a())    
    op.cycles = 16
def op_ld_a_ff00c():
    reg.set_a(mem.read_byte(0xFF00|reg.get_c()))
    op.cycles = 8
def op_ld_ff00c_a():
    mem.write_byte(0xFF00|reg.get_c(), reg.get_a())
    op.cycles = 8
def op_ld_a_ff00n():
    n = mem.read_byte(reg.pc); reg.pc += 1
    reg.set_a(mem.read_byte(0xFF00|n))    
    op.cycles = 12
def op_ld_ff00n_a():
    n = mem.read_byte(reg.pc); reg.pc += 1
    mem.write_byte(0xFF00|n, reg.get_a())    
    op.cycles = 12
def op_ldd_a_hlmem():
    hl = reg.get_hl()
    reg.set_a(mem.read_byte(reg.get_hl()))
    reg.dec_hl()
    op.cycles = 8    
def op_ldd_hlmem_a():
    hl = reg.get_hl() 
    mem.write_byte(reg.get_hl(), reg.get_a())
    reg.dec_hl()
    op.cycles = 8   
def op_ldi_a_hlmem(): 
    hl = reg.get_hl()
    reg.set_a(mem.read_byte(reg.get_hl()))
    reg.inc_hl()
    op.cycles = 8    
def op_ldi_hlmem_a():
    hl = reg.get_hl() 
    mem.write_byte(reg.get_hl(), reg.get_a())
    reg.inc_hl()
    op.cycles = 8
    
######################################################## OP LD (16-bit)###
def op_ld_rp_nn():
    rp = (op.code>>4)&0x03 #p
    nn = mem.read_word(reg.pc); reg.pc += 2
    reg.set_rp(rp, nn)
    op.cycles = 12
def op_ld_sp_hl():
    reg.set_sp(reg.get_hl())
    op.cycles = 8
def op_ldhl_sp_n():
    n = mem.read_byte(reg.pc); reg.pc += 1
    if(n > 127):
        n = n-256 # signed
    word = reg.sp + n
    if(word > 0xFFFF):
        word &= 0xFFFF
        dlog.print_error("Z80", "pc wrap in op_ldhl_sp_n (what is actual behavior?)")
    reg.set_hl(word)
    op.cycles = 12
def op_ld_nnmem_sp():
    nn = mem.read_word(reg.pc); reg.pc += 2
    mem.write_word(nn, reg.sp)    
    op.cycles = 20
    
######################################################## OP PUSH ###
def op_push_af():
    reg.sp -= 1; mem.write_byte(reg.sp, reg.a)
    reg.sp -= 1; mem.write_byte(reg.sp, reg.f)
    op.cycles = 16
def op_push_bc():
    reg.sp -= 1; mem.write_byte(reg.sp, reg.b)
    reg.sp -= 1; mem.write_byte(reg.sp, reg.c)
    op.cycles = 16
def op_push_de():
    reg.sp -= 1; mem.write_byte(reg.sp, reg.d)
    reg.sp -= 1; mem.write_byte(reg.sp, reg.e)
    op.cycles = 16
def op_push_hl():
    reg.sp -= 1; mem.write_byte(reg.sp, reg.h)
    reg.sp -= 1; mem.write_byte(reg.sp, reg.l)
    op.cycles = 16
    
######################################################## OP POP ###
def op_pop_af():
    reg.f = mem.read_byte(reg.sp); reg.sp += 1
    reg.a = mem.read_byte(reg.sp); reg.sp += 1
    op.cycles = 12
def op_pop_bc():
    reg.c = mem.read_byte(reg.sp); reg.sp += 1
    reg.b = mem.read_byte(reg.sp); reg.sp += 1
    op.cycles = 12
def op_pop_de():
    reg.e = mem.read_byte(reg.sp); reg.sp += 1
    reg.d = mem.read_byte(reg.sp); reg.sp += 1
    op.cycles = 12
def op_pop_hl():
    reg.l = mem.read_byte(reg.sp); reg.sp += 1
    reg.h = mem.read_byte(reg.sp); reg.sp += 1
    op.cycles = 12
    
######################################################## OP ADD (8-bit) ###
def op_add_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_add_a_x_helper(s2)
    op.cycles = 4
def op_add_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_add_a_x_helper(s2)
    op.cycles = 8
def op_add_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_add_a_x_helper(s2)
    op.cycles = 8
def op_add_a_x_helper(s2):
    s1 = reg.a
    res = s1+s2
    reg.reset_flags()
    if(res == 0):
        reg.set_flag_z()
    if(res > 0xFF):
        reg.set_flag_c()
    if((s1&0xf)+(s2&0xf) > 0xF):
        reg.set_flag_h()
    reg.a = res&0xFF
    
######################################################## OP ADC (8-bit) ###
def op_adc_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_adc_a_x_helper(s2)
    op.cycles = 4    
def op_adc_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_adc_a_x_helper(s2)
    op.cycles = 8
def op_adc_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_adc_a_x_helper(s2)
    op.cycles = 8
def op_adc_a_x_helper(s2):
    s1 = reg.a
    sC = reg.get_flag_c()
    res = s1+s2+sC
    reg.reset_flags()
    if(res == 0):
        reg.set_flag_z()
    if(res > 0xFF):
        reg.set_flag_c()
    if((s1&0xf)+(s2&0xf)+sC > 0xF):
        # TODO half carry might be wrong
        reg.set_flag_h()
    reg.a = res&0xFF
    
######################################################## OP SUB (8-bit) ###
def op_sub_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_sub_a_x_helper(s2)
    op.cycles = 4
def op_sub_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_sub_a_x_helper(s2)
    op.cycles = 8
def op_sub_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_sub_a_x_helper(s2)
    op.cycles = 8
def op_sub_a_x_helper(s2):
    s1 = reg.a
    res = s1-s2
    reg.reset_flags()
    reg.set_flag_n()
    if(res == 0):
        reg.set_flag_z()
    if(res < 0):
        # TODO carry might be wrong
        reg.set_flag_c()
    if((s1&0xf)-(s2&0xf) < 0):
        # TODO half carry might be wrong
        reg.set_flag_h()
    reg.a = res&0xFF
    
######################################################## OP SBC (8-bit) ###
def op_sbc_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_sbc_a_x_helper(s2)
    op.cycles = 4
def op_sbc_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_sbc_a_x_helper(s2)
    op.cycles = 8
def op_sbc_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_sbc_a_x_helper(s2)
    op.cycles = 8
def op_sbc_a_x_helper(s2):
    s1 = reg.a
    sC = reg.get_flag_c()
    res = s1-s2-sC
    reg.reset_flags()
    reg.set_flag_n()
    if(res == 0):
        reg.set_flag_z()
    if(res < 0):
        reg.set_flag_c()
    if((s1&0xf)-(s2&0xf)-sC < 0):
        # TODO half carry might be wrong
        reg.set_flag_h()
    reg.a = res&0xFF
    
######################################################## OP AND (8-bit) ###
def op_and_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_and_a_x_helper(s2)
    op.cycles = 4
def op_and_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_and_a_x_helper(s2)
    op.cycles = 8
def op_and_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_and_a_x_helper(s2)
    op.cycles = 8
def op_and_a_x_helper(s2):
    s1 = reg.a
    res = s1&s2
    reg.reset_flags()
    reg.set_flag_h()
    if(res == 0):
        res.set_flag_z()
    reg.a = res

######################################################## OP OR (8-bit) ###
def op_or_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_or_a_x_helper(s2)
    op.cycles = 4
def op_or_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_or_a_x_helper(s2)
    op.cycles = 8
def op_or_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_or_a_x_helper(s2)
    op.cycles = 8
def op_or_a_x_helper(s2):
    s1 = reg.a
    res = s1|s2
    reg.reset_flags()
    if(res == 0):
        res.set_flag_z()
    reg.a = res

######################################################## OP XOR (8-bit) ###
def op_xor_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_xor_a_x_helper(s2)
    op.cycles = 4
def op_xor_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_xor_a_x_helper(s2)
    op.cycles = 8
def op_xor_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_xor_a_x_helper(s2)
    op.cycles = 8
def op_xor_a_x_helper(s2):
    s1 = reg.a
    res = s1^s2
    reg.reset_flags()
    if(res == 0):
        res.set_flag_z()
    reg.a = res
    
######################################################## OP CP (8-bit) ###
def op_cp_a_r2():
    s2 = reg.get_r((op.code >> 0)&0x07) #z
    op_cp_a_x_helper(s2)
    op.cycles = 4
def op_cp_a_hlmem():
    s2 = mem.read_byte(reg.get_hl())
    op_cp_a_x_helper(s2)
    op.cycles = 8
def op_cp_a_n():
    s2 = mem.read_byte(reg.pc); reg.pc += 1
    op_cp_a_x_helper(s2)
    op.cycles = 8
def op_cp_a_x_helper(s2):
    s1 = reg.a
    res = s1-s2
    reg.reset_flags()
    reg.set_flag_n()
    if(res == 0):
        reg.set_flag_z()
    if(res < 0):
        reg.set_flag_c()
    if((s1&0xf)-(s2&0xf) < 0):
        # TODO half carry might be wrong
        reg.set_flag_h()
        
######################################################## OP INC (8-bit) ###
def op_inc_r1():
    r1 = (op.code >> 3)&0x07 # y
    s1 = reg.get_r(r1)
    res = (s1+1)&0xFF
    reg.set_r(r1, res)
    op_inc_x_helper(res)
    op.cycles = 4
def op_inc_hlmem():
    hl = reg.get_hl()
    s1 = mem.read_byte(hl)
    res = (s1+1)&0xFF
    mem.write_byte(hl, res)
    op_inc_x_helper(res)
    op.cycles = 12
def op_inc_x_helper(res):
    reg.reset_flag_n()
    if(res == 0):
        reg.set_flag_z()
    else:
        reg.reset_flag_z()
    if(res == 0x10):
        # TODO half carry might be wrong
        reg.set_flag_h()
    else:
        # TODO half carry might be wrong
        reg.reset_flag_h()
        
######################################################## OP DEC (8-bit) ###
def op_dec_r1():
    r1 = (op.code >> 3)&0x07 # y
    s1 = reg.get_r(r1)
    res = (s1-1)&0xFF
    reg.set_r(r1, res)
    op_dec_x_helper(res)
    op.cycles = 4
def op_dec_hlmem():
    hl = reg.get_hl()
    s1 = mem.read_byte(hl)
    res = (s1-1)&0xFF
    mem.write_byte(hl, res)
    op_dec_x_helper(res)
    op.cycles = 12
def op_dec_x_helper(res):
    reg.set_flag_n()
    if(res == 0):
        reg.set_flag_z()
    else:
        reg.reset_flag_z()
    if(res == 0x10):
        # TODO half carry might be wrong
        reg.set_flag_h()
    else:
        # TODO half carry might be wrong
        reg.reset_flag_h()
        
######################################################## OP ADD (16-bit) ###
def op_add_hl_rp():
    s1 = reg.get_hl()
    s2 = reg.get_rp((op.code>>4)&0x03) #p
    res = s1+s2
    reg.reset_flag_n()
    if(res > 0xFFFF):
        reg.set_flag_c()
    else:
        reg.reset_flag_c()
    if((s1&0xFFF)+(s2&0xFFF) > 0xFFF):
        # TODO half carry might be wrong
        reg.set_flag_h()
    else:
        # TODO half carry might be wrong
        reg.reset_flag_h()    
    reg.set_hl(res&0xFFFF)
    op.cycles = 8
def op_add_sp_n():
    # flags?
    # https://stackoverflow.com/questions/8868396/game-boy-what-constitutes-a-half-carry
    # ADD SP, e: H from bit 3, C from bit 7 (flags from low byte op)
    n = mem.read_byte(reg.pc); reg.pc += 1
    if(n > 127):
        # sub operation
        n = n-256 # signed
        res = reg.sp + n
        reg.reset_flags()
        if((reg.sp&0xFF)+n < 0):
            # TODO carry might be wrong
            reg.set_flag_c()       
        if((reg.sp&0xF)+(n&0xF) < 0):
            # TODO half carry might be wrong
            reg.set_flag_h()      
        reg.sp = res&0xFFFF
    else:
        # add operation
        res = reg.sp + n        
        reg.reset_flags()
        if((reg.sp&0xFF)+n > 0xFF):
            # TODO carry might be wrong
            reg.set_flag_c()    
        if((reg.sp&0xF)+(n&0xF) > 0xF):
            # TODO half carry might be wrong
            reg.set_flag_h()
        reg.sp = res&0xFFFF
    op.cycles = 16
    
######################################################## OP INC (16-bit) ###
def op_inc_rp():
    rp = (op.code>>4)&0x03 #p
    s1 = reg.get_rp(rp)
    reg.set_rp(rp, (s1+1)&0xFFFF)
    op.cycles = 8
    
######################################################## OP DEC (16-bit) ###
def op_dec_rp():
    rp = (op.code>>4)&0x03 #p
    s1 = reg.get_rp(rp)
    reg.set_rp(rp, (s1-1)&0xFFFF)
    op.cycles = 8
    
######################################################## OP XXX ###
def op_xxx():
    dlog.print_error("Z80", "invalid opcode " + hex(op.code) + " at " +  hex(reg.pc-1))

######################################################## OP MAP ###
op.map = [op_xxx]*256
op.map[0x7F] = [op_ld_r1_r2,    "LD", "A,A"]
op.map[0x78] = [op_ld_r1_r2,    "LD", "A,B"]
op.map[0x79] = [op_ld_r1_r2,    "LD", "A,C"]
op.map[0x7A] = [op_ld_r1_r2,    "LD", "A,D"]
op.map[0x7B] = [op_ld_r1_r2,    "LD", "A,E"]
op.map[0x7C] = [op_ld_r1_r2,    "LD", "A,H"]
op.map[0x7D] = [op_ld_r1_r2,    "LD", "A,L"]
op.map[0x47] = [op_ld_r1_r2,    "LD", "B,A"]
op.map[0x40] = [op_ld_r1_r2,    "LD", "B,B"]
op.map[0x41] = [op_ld_r1_r2,    "LD", "B,C"]
op.map[0x42] = [op_ld_r1_r2,    "LD", "B,D"]
op.map[0x43] = [op_ld_r1_r2,    "LD", "B,E"]
op.map[0x44] = [op_ld_r1_r2,    "LD", "B,H"]
op.map[0x45] = [op_ld_r1_r2,    "LD", "B,L"]
op.map[0x4F] = [op_ld_r1_r2,    "LD", "C,A"]
op.map[0x48] = [op_ld_r1_r2,    "LD", "C,B"]
op.map[0x49] = [op_ld_r1_r2,    "LD", "C,C"]
op.map[0x4A] = [op_ld_r1_r2,    "LD", "C,D"]
op.map[0x4B] = [op_ld_r1_r2,    "LD", "C,E"]
op.map[0x4C] = [op_ld_r1_r2,    "LD", "C,H"]
op.map[0x4D] = [op_ld_r1_r2,    "LD", "C,L"]
op.map[0x57] = [op_ld_r1_r2,    "LD", "D,A"]
op.map[0x50] = [op_ld_r1_r2,    "LD", "D,B"]
op.map[0x51] = [op_ld_r1_r2,    "LD", "D,C"]
op.map[0x52] = [op_ld_r1_r2,    "LD", "D,D"]
op.map[0x53] = [op_ld_r1_r2,    "LD", "D,E"]
op.map[0x54] = [op_ld_r1_r2,    "LD", "D,H"]
op.map[0x55] = [op_ld_r1_r2,    "LD", "D,L"]
op.map[0x5F] = [op_ld_r1_r2,    "LD", "E,A"]
op.map[0x58] = [op_ld_r1_r2,    "LD", "E,B"]
op.map[0x59] = [op_ld_r1_r2,    "LD", "E,C"]
op.map[0x5A] = [op_ld_r1_r2,    "LD", "E,D"]
op.map[0x5B] = [op_ld_r1_r2,    "LD", "E,E"]
op.map[0x5C] = [op_ld_r1_r2,    "LD", "E,H"]
op.map[0x5D] = [op_ld_r1_r2,    "LD", "E,L"]
op.map[0x67] = [op_ld_r1_r2,    "LD", "H,A"]
op.map[0x60] = [op_ld_r1_r2,    "LD", "H,B"]
op.map[0x61] = [op_ld_r1_r2,    "LD", "H,C"]
op.map[0x62] = [op_ld_r1_r2,    "LD", "H,D"]
op.map[0x63] = [op_ld_r1_r2,    "LD", "H,E"]
op.map[0x64] = [op_ld_r1_r2,    "LD", "H,H"]
op.map[0x65] = [op_ld_r1_r2,    "LD", "H,L"] 
op.map[0x6F] = [op_ld_r1_r2,    "LD", "L,A"]
op.map[0x68] = [op_ld_r1_r2,    "LD", "L,B"]
op.map[0x69] = [op_ld_r1_r2,    "LD", "L,C"]
op.map[0x6A] = [op_ld_r1_r2,    "LD", "L,D"]
op.map[0x6B] = [op_ld_r1_r2,    "LD", "L,E"]
op.map[0x6C] = [op_ld_r1_r2,    "LD", "L,H"]
op.map[0x6D] = [op_ld_r1_r2,    "LD", "L,L"]
op.map[0x3E] = [op_ld_r1_n,     "LD", "A,n"]
op.map[0x06] = [op_ld_r1_n,     "LD", "B,n"]
op.map[0x0E] = [op_ld_r1_n,     "LD", "C,n"]
op.map[0x16] = [op_ld_r1_n,     "LD", "D,n"]
op.map[0x1E] = [op_ld_r1_n,     "LD", "E,n"]
op.map[0x26] = [op_ld_r1_n,     "LD", "H,n"]
op.map[0x2E] = [op_ld_r1_n,     "LD", "L,n"]
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
op.map[0xF2] = [op_ld_a_ff00c,  "LD", "A,(0xFF00+C)"]
op.map[0xE2] = [op_ld_ff00c_a,  "LD", "(0xFF00+C),A"]
op.map[0xF0] = [op_ld_a_ff00n,  "LD", "A,(0xFF00+n)"]
op.map[0xE0] = [op_ld_ff00n_a,  "LD", "(0xFF00+n),A"]
op.map[0x3A] = [op_ldd_a_hlmem, "LD", "A,(HL-)"]
op.map[0x32] = [op_ldd_hlmem_a, "LD", "(HL-),A"]
op.map[0x2A] = [op_ldi_a_hlmem, "LD", "A,(HL+)"]
op.map[0x22] = [op_ldi_hlmem_a, "LD", "(HL+),A"]

op.map[0x01] = [op_ld_rp_nn,    "LD", "BC,nn"]
op.map[0x11] = [op_ld_rp_nn,    "LD", "DE,nn"]
op.map[0x21] = [op_ld_rp_nn,    "LD", "HL,nn"]
op.map[0x31] = [op_ld_rp_nn,    "LD", "SP,nn"]
op.map[0xF9] = [op_ld_sp_hl,    "LD", "SP,HL"]
op.map[0xF8] = [op_ldhl_sp_n,   "LD", "HL,SP+n"]
op.map[0x08] = [op_ld_nnmem_sp, "LD", "(nn),SP"]

op.map[0xF5] = [op_push_af,     "PUSH", "AF"]
op.map[0xC5] = [op_push_bc,     "PUSH", "BC"]
op.map[0xD5] = [op_push_de,     "PUSH", "DE"]
op.map[0xE5] = [op_push_hl,     "PUSH", "HL"]

op.map[0xF1] = [op_pop_af,      "POP", "AF"]
op.map[0xC1] = [op_pop_bc,      "POP", "BC"]
op.map[0xD1] = [op_pop_de,      "POP", "DE"]
op.map[0xE1] = [op_pop_hl,      "POP", "HL"]

op.map[0x87] = [op_add_a_r2,    "ADD", "A,A"]
op.map[0x80] = [op_add_a_r2,    "ADD", "A,B"]
op.map[0x81] = [op_add_a_r2,    "ADD", "A,C"]
op.map[0x82] = [op_add_a_r2,    "ADD", "A,D"]
op.map[0x83] = [op_add_a_r2,    "ADD", "A,E"]
op.map[0x84] = [op_add_a_r2,    "ADD", "A,H"]
op.map[0x85] = [op_add_a_r2,    "ADD", "A,L"]
op.map[0x86] = [op_add_a_hlmem, "ADD", "A,(HL)"]
op.map[0xC6] = [op_add_a_n,     "ADD", "A,n"]

op.map[0x8F] = [op_adc_a_r2,    "ADC", "A,A"]
op.map[0x88] = [op_adc_a_r2,    "ADC", "A,B"]
op.map[0x89] = [op_adc_a_r2,    "ADC", "A,C"]
op.map[0x8A] = [op_adc_a_r2,    "ADC", "A,D"]
op.map[0x8B] = [op_adc_a_r2,    "ADC", "A,E"]
op.map[0x8C] = [op_adc_a_r2,    "ADC", "A,H"]
op.map[0x8D] = [op_adc_a_r2,    "ADC", "A,L"]
op.map[0x8E] = [op_adc_a_hlmem, "ADC", "A,(HL)"]
op.map[0xCE] = [op_adc_a_n,     "ADC", "A,n"]

op.map[0x97] = [op_sub_a_r2,    "SUB", "A,A"]
op.map[0x90] = [op_sub_a_r2,    "SUB", "A,B"]
op.map[0x91] = [op_sub_a_r2,    "SUB", "A,C"]
op.map[0x92] = [op_sub_a_r2,    "SUB", "A,D"]
op.map[0x93] = [op_sub_a_r2,    "SUB", "A,E"]
op.map[0x94] = [op_sub_a_r2,    "SUB", "A,H"]
op.map[0x95] = [op_sub_a_r2,    "SUB", "A,L"]
op.map[0x96] = [op_sub_a_hlmem, "SUB", "A,(HL)"]
op.map[0xD6] = [op_sub_a_n,     "SUB", "A,n"]

op.map[0x9F] = [op_sbc_a_r2,    "SBC", "A,A"]
op.map[0x98] = [op_sbc_a_r2,    "SBC", "A,B"]
op.map[0x99] = [op_sbc_a_r2,    "SBC", "A,C"]
op.map[0x9A] = [op_sbc_a_r2,    "SBC", "A,D"]
op.map[0x9B] = [op_sbc_a_r2,    "SBC", "A,E"]
op.map[0x9C] = [op_sbc_a_r2,    "SBC", "A,H"]
op.map[0x9D] = [op_sbc_a_r2,    "SBC", "A,L"]
op.map[0x9E] = [op_sbc_a_hlmem, "SBC", "A,(HL)"]
op.map[0xDE] = [op_sbc_a_n,     "SBC", "A,n"]

op.map[0xA7] = [op_and_a_r2,    "AND", "A"]
op.map[0xA0] = [op_and_a_r2,    "AND", "B"]
op.map[0xA1] = [op_and_a_r2,    "AND", "C"]
op.map[0xA2] = [op_and_a_r2,    "AND", "D"]
op.map[0xA3] = [op_and_a_r2,    "AND", "E"]
op.map[0xA4] = [op_and_a_r2,    "AND", "H"]
op.map[0xA5] = [op_and_a_r2,    "AND", "L"]
op.map[0xA6] = [op_and_a_hlmem, "AND", "(HL)"]
op.map[0xE6] = [op_and_a_n,     "AND", "n"]

op.map[0xB7] = [op_or_a_r2,     "OR", "A"]
op.map[0xB0] = [op_or_a_r2,     "OR", "B"]
op.map[0xB1] = [op_or_a_r2,     "OR", "C"]
op.map[0xB2] = [op_or_a_r2,     "OR", "D"]
op.map[0xB3] = [op_or_a_r2,     "OR", "E"]
op.map[0xB4] = [op_or_a_r2,     "OR", "H"]
op.map[0xB5] = [op_or_a_r2,     "OR", "L"]
op.map[0xB6] = [op_or_a_hlmem,  "OR", "(HL)"]
op.map[0xF6] = [op_or_a_n,      "OR", "n"]

op.map[0xAF] = [op_xor_a_r2,    "XOR", "A"]
op.map[0xA8] = [op_xor_a_r2,    "XOR", "B"]
op.map[0xA9] = [op_xor_a_r2,    "XOR", "C"]
op.map[0xAA] = [op_xor_a_r2,    "XOR", "D"]
op.map[0xAB] = [op_xor_a_r2,    "XOR", "E"]
op.map[0xAC] = [op_xor_a_r2,    "XOR", "H"]
op.map[0xAD] = [op_xor_a_r2,    "XOR", "L"]
op.map[0xAE] = [op_xor_a_hlmem, "XOR", "(HL)"]
op.map[0xEE] = [op_xor_a_n,     "XOR", "n"]

op.map[0xBF] = [op_cp_a_r2,     "CP", "A"]
op.map[0xB8] = [op_cp_a_r2,     "CP", "B"]
op.map[0xB9] = [op_cp_a_r2,     "CP", "C"]
op.map[0xBA] = [op_cp_a_r2,     "CP", "D"]
op.map[0xBB] = [op_cp_a_r2,     "CP", "E"]
op.map[0xBC] = [op_cp_a_r2,     "CP", "H"]
op.map[0xBD] = [op_cp_a_r2,     "CP", "L"]
op.map[0xBE] = [op_cp_a_hlmem,  "CP", "(HL)"]
op.map[0xFE] = [op_cp_a_n,      "CP", "n"]

op.map[0x3C] = [op_inc_r1,      "INC", "A"]
op.map[0x04] = [op_inc_r1,      "INC", "B"]
op.map[0x0C] = [op_inc_r1,      "INC", "C"]
op.map[0x14] = [op_inc_r1,      "INC", "D"]
op.map[0x1C] = [op_inc_r1,      "INC", "E"]
op.map[0x24] = [op_inc_r1,      "INC", "H"]
op.map[0x2C] = [op_inc_r1,      "INC", "L"]
op.map[0x34] = [op_inc_hlmem,   "INC", "(HL)"]
    
op.map[0x3D] = [op_dec_r1,      "DEC", "A"]
op.map[0x05] = [op_dec_r1,      "DEC", "B"]
op.map[0x0D] = [op_dec_r1,      "DEC", "C"]
op.map[0x15] = [op_dec_r1,      "DEC", "D"]
op.map[0x1D] = [op_dec_r1,      "DEC", "E"]
op.map[0x25] = [op_dec_r1,      "DEC", "H"]
op.map[0x2D] = [op_dec_r1,      "DEC", "L"]
op.map[0x35] = [op_dec_hlmem,   "DEC", "(HL)"]

op.map[0x09] = [op_add_hl_rp,   "ADD", "HL,BC"]
op.map[0x19] = [op_add_hl_rp,   "ADD", "HL,DE"]
op.map[0x29] = [op_add_hl_rp,   "ADD", "HL,HL"]
op.map[0x39] = [op_add_hl_rp,   "ADD", "HL,SP"]
op.map[0xE8] = [op_add_sp_n,    "ADD", "SP,n"]

op.map[0x03] = [op_inc_rp,      "INC", "BC"]
op.map[0x13] = [op_inc_rp,      "INC", "DE"]
op.map[0x23] = [op_inc_rp,      "INC", "HL"]
op.map[0x33] = [op_inc_rp,      "INC", "SP"]

op.map[0x0B] = [op_dec_rp,      "DEC", "BC"]
op.map[0x1B] = [op_dec_rp,      "DEC", "DE"]
op.map[0x2B] = [op_dec_rp,      "DEC", "HL"]
op.map[0x3B] = [op_dec_rp,      "DEC", "SP"]








