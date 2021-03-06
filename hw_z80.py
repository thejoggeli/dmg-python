import util_dlog as dlog
import util_gbmath as gbmath
import hw_mem as mem

OPCODE_INFO_SIZE = 0
OPCODE_INFO_NAME = 1
OPCODE_INFO_PARAMS = 2

CLOCK_FREQUENCY = 4194304 # in hz
CYCLE_DURATION = 1.0/CLOCK_FREQUENCY # in seconds

class OP:
    
    # current opcode
    cycles = 0
    prefix = 0
    code = 0
    address = 0
    
    # opcode map
    map = None
    
    def code_str(self, spacer = ""):    
        if(self.prefix == 0x00):
            return "00{0:0{1}X}".format(self.code, 2)
        else:
            return("{0:0{1}X}".format(self.prefix, 2) + spacer + 
                   "{0:0{1}X}".format(self.code, 2))
    
    def is_prefix(self, byte):
        if(byte == 0xCB or byte == 0xDD or byte == 0xED or byte == 0xFD):
            return True
        return False
    
    def get_opcode_info(self, prefix, opcode):
        if(prefix == 0x00):
            return op_map_nopref[opcode][1]
        if(prefix == 0xCB):
            return op_map_cbpref[opcode][1]
        if(prefix == 0xDD):
            dlog.print_error("Z80", "0xDD prefix not implemented")
            return "not implemented"
        if(prefix == 0xED):
            dlog.print_error("Z80", "0xED prefix not implemented")
            return "not implemented"
        if(prefix == 0xFD):
            dlog.print_error("Z80", "0xFD prefix not implemented")
            return "not implemented"
            
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
        
    def set_flag_z_to(self, val):
        if(val):
            self.f |= 0x80
        else:
            self.f &= 0x7F
    def set_flag_n_to(self, val):
        if(val):
            self.f |= 0x40
        else:
            self.f &= 0xBF
    def set_flag_h_to(self, val):
        if(val):
            self.f |= 0x20
        else:
            self.f &= 0xDF
    def set_flag_c_to(self, val):
        if(val):
            self.f |= 0x10
        else:
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
                
class State:
    instruction_location = 0
    time_passed = 0
    cycles_delta = 0
    halted = False
    halt_bug = False
    stopped = False
    interrupt_master_enable = 0
    interrupt_master_enable_skip_one_cycle = 0
    
op    = None
reg   = None
state = None

def init():
    global op, reg, state
    op = OP()
    reg = RegisterSet()
    state = State()
    pass
    
def update():      
    
    # print current cpu state
    if(dlog.enable.z80):
        print_state()
    
    state.instruction_location = reg.pc
        
    if(state.stopped):  
        if(dlog.enable.z80):  
            dlog.print_msg("Z80", "STOP", cat="stop_mode")
        joypad = mem.read_byte(0xFF00)
        if(joypad&0x0F != 0xF):
            if(dlog.enable.z80):
                dlog.print_msg("Z80", "Leaving STOP mode", cat="stop_mode")
            state.stopped = False
        state.cycles_delta = 4
    else:        
        interrupted = False        
        if(state.interrupt_master_enable):
            if(state.interrupt_master_enable_skip_one_cycle):
                state.interrupt_master_enable_skip_one_cycle = 0
            else:
                # check if interrupt
                if_flags = mem.read_byte(0xFF0F)
                ie_flags = mem.read_byte(0xFFFF)
                masked = if_flags&ie_flags
                if(masked > 0):
                    state.interrupt_master_enable = 0    
                    interrupt_cycles = 0
                    if(state.halted):
                        state.halted = False
                        if(dlog.enable.z80):
                            dlog.print_msg("Z80", "Leaving HALT mode with IME=1", cat="halt_mode")
                        interrupt_cycles = 24
                    else:                    
                        interrupt_cycles = 20  
                    # push pc on stack 
                    reg.sp -= 2; mem.write_word(reg.sp, reg.pc)              
                    # jump to vector
                    if(masked&0x01):
                        # vertical blank             
                        mem.write_byte(0xFF0F, if_flags&0x1E) # reset bit 0
                        if(dlog.enable.z80):
                            dlog.print_msg("Z80", "Interrupt: V-Blank", cat="interrupt") 
                        reg.pc = 0x0040
                    elif(masked&0x02):
                        # LCD STAT
                        mem.write_byte(0xFF0F, if_flags&0x1D) # reset bit 1
                        if(dlog.enable.z80):
                            dlog.print_msg("Z80", "Interrupt: LCD STAT", cat="interrupt")
                        reg.pc = 0x0048
                    elif(masked&0x04):
                        # timer
                        mem.write_byte(0xFF0F, if_flags&0x1B) # reset bit 2
                        if(dlog.enable.z80):
                            dlog.print_msg("Z80", "Interrupt: Timer", cat="interrupt")
                        reg.pc = 0x0050
                    elif(masked&0x08):
                        # timer
                        mem.write_byte(0xFF0F, if_flags&0x17) # reset bit 3
                        if(dlog.enable.z80):
                            dlog.print_msg("Z80", "Interrupt: Serial", cat="interrupt")
                        reg.pc = 0x0058
                    elif(masked&0x10):
                        # joypad
                        mem.write_byte(0xFF0F, if_flags&0x0F) # reset bit 4
                        if(dlog.enable.z80):
                            dlog.print_msg("Z80", "Interrupt: Joypad", cat="interrupt")
                        reg.pc = 0x0060
                    else:
                        dlog.print_error(
                            "Z80", 
                            "invalid interrupt: " +
                            "IE=" + "%{0:0{1}b}".format(ie_flags,8) +
                            " and " + 
                            "IF=" + "%{0:0{1}b}".format(if_flags,8)
                        )
                    interrupted = True
                    state.cycles_delta = interrupt_cycles
                   #state.cycles_total += interrupt_cycles
                   
        if(not interrupted):        
            if(state.halted):
                if(dlog.enable.z80):
                    dlog.print_msg("Z80", "HALT", cat="halt_mode")            
                if_flags = mem.read_byte_silent(0xFF0F)
                ie_flags = mem.read_byte_silent(0xFFFF)
                if(if_flags&ie_flags&0x1F > 0):
                    if(dlog.enable.z80):
                        dlog.print_msg("Z80", "Leaving HALT mode with IME=0", cat="halt_mode")
                    state.halted = False
                state.cycles_delta = 4
            else:
                # fetch op code
                op.address = reg.pc
                byte = mem.read_byte(reg.pc); reg.pc += 1
                if(state.halt_bug):
                    reg.pc -= 1
                    state.halt_bug = False
                if(byte == 0xCB):
                    op.prefix = 0xCB
                    op.code = mem.read_byte(reg.pc); reg.pc += 1
                    op.map = op_map_cbpref
                elif(byte == 0xDD):
                    dlog.print_error("Z80", "0xDD prefix not implemented")
                    op.prefix = 0x00
                    op.code = 0x00
                    op.map = None
                elif(byte == 0xED):
                    dlog.print_error("Z80", "0xED prefix not implemented")
                    op.prefix = 0x00
                    op.code = 0x00
                    op.map = None    
                elif(byte == 0xFD):
                    dlog.print_error("Z80", "0xFD prefix not implemented")
                    op.prefix = 0x00
                    op.code = 0x00
                    op.map = None    
                else:
                    op.prefix = 0x00
                    op.code = byte
                    op.map = op_map_nopref        
                # wrap pc
                if(reg.pc > 0xFFFF):
                    reg.pc &= 0xFFFF
                    dlog.print_error("Z80", "pc wrap in execute (what is actual behavior?)")        
                # print opcode
                if(dlog.enable.z80):
                    print_op()        
                # execute opcode
                op.map[op.code][0]()
                state.cycles_delta = op.cycles
               #state.cycles_total += op.cycles
               
    if(dlog.enable.z80):
        print_endst()
    
    # state
    state.time_passed += state.cycles_delta * CYCLE_DURATION
    
def print_state():
    ie_byte = mem.read_byte_silent(0xFFFF)
    if_byte = mem.read_byte_silent(0xFF0F)
    dlog.print_msg(
        "Z80",         
        "IME=" + 
        str(state.interrupt_master_enable) + "/" + 
        str(state.interrupt_master_enable_skip_one_cycle) + "\t" + 
        "IE=" + "{0:0{1}b}".format((ie_byte>>4)&0xF,4) + "_"  +
                "{0:0{1}b}".format((ie_byte>>0)&0xF,4) + "\t" + 
        "IF=" + "{0:0{1}b}".format((if_byte>>4)&0xF,4) + "_"  +
                "{0:0{1}b}".format((if_byte>>0)&0xF,4) + "\t",
        cat="interrupt"
    )
    dlog.print_msg(
        "Z80",
        "PC=" + "0x{0:0{1}X}".format(reg.pc, 4) + "\t" +
        "B="  + "0x{0:0{1}X}".format(reg.b, 2) + "\t" +
        "D="  + "0x{0:0{1}X}".format(reg.d, 2) + "\t" +
        "H="  + "0x{0:0{1}X}".format(reg.h, 2) + "\t" +
        "A="  + "0x{0:0{1}X}".format(reg.a, 2) + "\t" +
        "Z N H C",
        cat="registers"
    )
    dlog.print_msg(
        "Z80",
        "SP=" + "0x{0:0{1}X}".format(reg.sp, 4) + "\t" +
        "C="  + "0x{0:0{1}X}".format(reg.c, 2) + "\t" +
        "E="  + "0x{0:0{1}X}".format(reg.e, 2) + "\t" +
        "L="  + "0x{0:0{1}X}".format(reg.l, 2) + "\t" +
        "F="  + "0x{0:0{1}X}".format(reg.f, 2) + "\t" +
        str(reg.get_flag_z()) + " " +
        str(reg.get_flag_n()) + " " +
        str(reg.get_flag_h()) + " " +
        str(reg.get_flag_c()),
        cat="registers"
    )
    
def print_endst():
    dlog.print_msg(
        "Z80",
        "Cycles="+str(state.cycles_delta) + "\t" +
        "Time="+"{0:.3f}".format(round(state.time_passed, 3),3),
        cat="z80_endst"
    )
    
def print_op():    
    info = op.get_opcode_info(op.prefix, op.code)
    size = info[OPCODE_INFO_SIZE]
    msg = ""
    msg += "op_decode --> "
   #msg += "0x{0:0{1}X}".format(op.prefix, 2) + "{0:0{1}X}".format(op.code, 2) + "\t"
    if(op.prefix):
        msg += "{0:0{1}X}".format(op.prefix, 2) + " "
    msg += info[OPCODE_INFO_NAME] + " "
    msg += info[OPCODE_INFO_PARAMS]
    dlog.print_msg("Z80", msg)
    
def print_instruction_set():
    
    opcode2 = 128

    for opcode in range(0, 128):
    
        msg = ""
        
        info = op.get_opcode_info(0x00, opcode)
        msg += "0x{0:0{1}X}".format(0x00, 2) + "{0:0{1}X}".format(opcode, 2) + "  "
        msg += info[OPCODE_INFO_NAME].ljust(5, " ")
        msg += info[OPCODE_INFO_PARAMS].ljust(10, " ")
        
        info = op.get_opcode_info(0x00, opcode2)
        msg += "0x{0:0{1}X}".format(0x00, 2) + "{0:0{1}X}".format(opcode2, 2) + "  "
        msg += info[OPCODE_INFO_NAME].ljust(5, " ")
        msg += info[OPCODE_INFO_PARAMS].ljust(10, " ")
        
        info = op.get_opcode_info(0xCB, opcode)        
        msg += "0x{0:0{1}X}".format(0xCB, 2) + "{0:0{1}X}".format(opcode, 2) + "  "
        msg += info[OPCODE_INFO_NAME].ljust(5, " ")
        msg += info[OPCODE_INFO_PARAMS].ljust(10, " ")
        
        info = op.get_opcode_info(0xCB, opcode2)        
        msg += "0x{0:0{1}X}".format(0xCB, 2) + "{0:0{1}X}".format(opcode2, 2) + "  "
        msg += info[OPCODE_INFO_NAME].ljust(5, " ")
        msg += info[OPCODE_INFO_PARAMS].ljust(10, " ")
        
        opcode2 += 1
                
        print(msg)
    
def exit():
    pass

### OP LD (8-bit)###################################################################
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
    nn = mem.read_word(reg.pc); reg.pc += 2
    reg.set_a(mem.read_byte(nn))
    op.cycles = 16
def op_ld_bcmem_a():
    mem.write_byte(reg.get_bc(), reg.get_a())
    op.cycles = 8    
def op_ld_demem_a():
    mem.write_byte(reg.get_de(), reg.get_a())
    op.cycles = 8    
def op_ld_nnmem_a():
    nn = mem.read_word(reg.pc); reg.pc += 2
    mem.write_byte(nn, reg.get_a())    
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
    
### OP LD (16-bit)##################################################################
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
    n = gbmath.signed_byte(n)
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
    
### OP PUSH ########################################################################
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
    
### OP POP ###
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
    
### OP ADD (8-bit) #################################################################
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
    result = s1+s2
    reg.reset_flags()
    if(result > 0xFF):
        reg.set_flag_c()
    result &= 0xFF
    if(result == 0):
        reg.set_flag_z()
    if((s1&0xf)+(s2&0xf) > 0xF):
        reg.set_flag_h()
    reg.a = result
    
### OP ADC (8-bit) #################################################################
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
    result = s1+s2+sC
    reg.reset_flags()
    if(result > 0xFF):
        reg.set_flag_c()
    result &= 0xFF
    if(result == 0):
        reg.set_flag_z()
    if((s1&0xf)+(s2&0xf)+sC > 0xF):
        # TODO half carry might be wrong
        reg.set_flag_h()
    reg.a = result
    
### OP SUB (8-bit) #################################################################
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
    result = s1-s2
    reg.reset_flags()
    reg.set_flag_n()
    if(result < 0):
        # TODO carry might be wrong
        reg.set_flag_c()
    result &= 0xFF
    if(result == 0):
        reg.set_flag_z()
    if((s1&0xf)-(s2&0xf) < 0):
        # TODO half carry might be wrong
        reg.set_flag_h()
    reg.a = result
    
### OP SBC (8-bit) #################################################################
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
    result = s1-s2-sC
    reg.reset_flags()
    reg.set_flag_n()
    if(result < 0):
        reg.set_flag_c()
    result &= 0xFF
    if(result == 0):
        reg.set_flag_z()
    if((s1&0xf)-(s2&0xf)-sC < 0):
        # TODO half carry might be wrong
        reg.set_flag_h()
    reg.a = result
    
### OP AND (8-bit) #################################################################
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
    result = s1&s2
    reg.reset_flags()
    reg.set_flag_h()
    if(result == 0):
        reg.set_flag_z()
    reg.a = result

### OP OR (8-bit) ##################################################################
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
    result = s1|s2
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    reg.a = result

### OP XOR (8-bit) #################################################################
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
    result = s1^s2
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    reg.a = result
    
### OP CP (8-bit) ##################################################################
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
    result = s1-s2
    reg.reset_flags()
    reg.set_flag_n()
    if(result == 0):
        reg.set_flag_z()
    if(result < 0):
        reg.set_flag_c()
    if((s1&0xf)-(s2&0xf) < 0):
        # TODO half carry might be wrong
        reg.set_flag_h()
        
### OP INC (8-bit) #################################################################
def op_inc_r1():
    r1 = (op.code >> 3)&0x07 # y
    s1 = reg.get_r(r1)
    result = (s1+1)&0xFF
    reg.set_r(r1, result)
    op_inc_x_helper(result)
    op.cycles = 4
def op_inc_hlmem():
    hl = reg.get_hl()
    s1 = mem.read_byte(hl)
    result = (s1+1)&0xFF
    mem.write_byte(hl, result)
    op_inc_x_helper(result)
    op.cycles = 12
def op_inc_x_helper(result):
    reg.reset_flag_n()
    if(result == 0):
        reg.set_flag_z()
    else:
        reg.reset_flag_z()
    if(result == 0x10):
        # TODO half carry might be wrong
        reg.set_flag_h()
    else:
        # TODO half carry might be wrong
        reg.reset_flag_h()
        
### OP DEC (8-bit) #################################################################
def op_dec_r1():
    r1 = (op.code >> 3)&0x07 # y
    s1 = reg.get_r(r1)
    result = (s1-1)&0xFF
    reg.set_r(r1, result)
    op_dec_x_helper(result)
    op.cycles = 4
def op_dec_hlmem():
    hl = reg.get_hl()
    s1 = mem.read_byte(hl)
    result = (s1-1)&0xFF
    mem.write_byte(hl, result)
    op_dec_x_helper(result)
    op.cycles = 12
def op_dec_x_helper(result):
    reg.set_flag_n()
    if(result == 0):
        reg.set_flag_z()
    else:
        reg.reset_flag_z()
    if(result == 0x10):
        # TODO half carry might be wrong
        reg.set_flag_h()
    else:
        # TODO half carry might be wrong
        reg.reset_flag_h()
        
### OP ADD (16-bit) ###
def op_add_hl_rp():
    s1 = reg.get_hl()
    s2 = reg.get_rp((op.code>>4)&0x03) #p
    result = s1+s2
    reg.reset_flag_n()
    if(result > 0xFFFF):
        reg.set_flag_c()
    else:
        reg.reset_flag_c()
    if((s1&0xFFF)+(s2&0xFFF) > 0xFFF):
        # TODO half carry might be wrong
        # 0xFFF? really?
        reg.set_flag_h()
    else:
        # TODO half carry might be wrong
        reg.reset_flag_h()    
    reg.set_hl(result&0xFFFF)
    op.cycles = 8
def op_add_sp_n():
    # flags?
    # https://stackoverflow.com/questions/8868396/game-boy-what-constitutes-a-half-carry
    # ADD SP, e: H from bit 3, C from bit 7 (flags from low byte op)
    n = mem.read_byte(reg.pc); reg.pc += 1
    if(n > 127):
        # sub operation
        n = n-256 # signed
        result = reg.sp + n
        reg.reset_flags()
        if((reg.sp&0xFF)+n < 0):
            # TODO carry might be wrong
            reg.set_flag_c()       
        if((reg.sp&0xF)+(n&0xF) < 0):
            # TODO half carry might be wrong
            reg.set_flag_h()      
        reg.sp = result&0xFFFF
    else:
        # add operation
        result = reg.sp + n        
        reg.reset_flags()
        if((reg.sp&0xFF)+n > 0xFF):
            # TODO carry might be wrong
            reg.set_flag_c()    
        if((reg.sp&0xF)+(n&0xF) > 0xF):
            # TODO half carry might be wrong
            reg.set_flag_h()
        reg.sp = result&0xFFFF
    op.cycles = 16
    
### OP INC (16-bit) ################################################################
def op_inc_rp():
    rp = (op.code>>4)&0x03 #p
    s1 = reg.get_rp(rp)
    reg.set_rp(rp, (s1+1)&0xFFFF)
    op.cycles = 8
    
### OP DEC (16-bit) ################################################################
def op_dec_rp():
    rp = (op.code>>4)&0x03 #p
    s1 = reg.get_rp(rp)
    reg.set_rp(rp, (s1-1)&0xFFFF)
    op.cycles = 8
    
### OP SWAP ########################################################################
def op_swap_r():
    r = (op.code >> 0)&0x07 #z
    s1 = reg.get_r(r)
    result = ((s1&0x0F)<<4)|((s1&0xF0)>>4)
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    reg.set_r(r, result)
    op.cycles = 8
def op_swap_hlmem():
    hl = reg.get_hl()
    s1 = mem.read_byte(hl)
    result = ((s1&0x0F)<<4)|((s1&0xF0)>>4)
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    mem.write_byte(hl, result)
    op.cycles = 16
    
### OP DAA #########################################################################
def op_daa():
    # https://stackoverflow.com/questions/8119577/z80-daa-instruction
    # TODO might be wrong?
    t = 0
    A = reg.a
    H = reg.get_flag_h()
    C = reg.get_flag_c()
    N = reg.get_flag_n()
    if(H or ((A & 0xF) > 9)):
         t += 1
    if(C or (A > 0x99)):   
        t += 2
        C = 1
    if (N and not H):
        H=0
    else:
        if (N and H):
            H = (((A & 0x0F)) < 6)
        else:
            H = ((A & 0x0F) >= 0x0A)   
    if(t==1):
            A += 0xFA if N else 0x06 # -6:6    
    elif(t==2):
            A += 0xA0 if N else 0x60 # -0x60:0x60    
    elif(t==3):
            A += 0x9A if N else 0x66 # -0x66:0x66
    reg.a = A
    reg.set_flag_h_to(H)
    reg.set_flag_h_to(C)
    reg.set_flag_h_to(not A)
    reg.set_flag_h_to(N)
    op.cycles = 4
    dlog.print_warning("Z80", "op_daa might be wrong?")
    
### OP CPL #########################################################################
def op_cpl():
    reg.set_flag_n()
    reg.set_flag_h()
    reg.a = (~reg.a)&0xFF
    op.cycles = 4
    
### OP CCF #########################################################################
def op_ccf():
    reg.reset_flag_n()
    reg.reset_flag_h()
    if(reg.get_flag_c()):
        reg.reset_flag_c()
    else:
        reg.set_flag_c()
    op.cycles = 4
    
### OP SCF #########################################################################
def op_scf():
    reg.reset_flag_n()
    reg.reset_flag_h()
    reg.set_flag_c()
    op.cycles = 4
    
### OP NOP #########################################################################
def op_nop():
    op.cycles = 4
    
### OP HALT ########################################################################
def op_halt():
    # The instruction immediately following the
    # HALT instruction is "skipped" when interrupts are
    # disabled (DI) on the GB,GBP, and SGB. As a result,
    # always put a NOP after the HALT instruction. This
    # instruction skipping doesn't occur when interrupts
    # are enabled (EI).
    # Source: GBCPUman.pdf
    # TODO implement HALT bug
    if_flags = mem.read_byte_silent(0xFF0F)
    ie_flags = mem.read_byte_silent(0xFFFF)
    if(state.interrupt_master_enable == 1):
        if(dlog.enable.z80):
            dlog.print_msg("Z80", "Entering HALT with IME=1", cat="halt_mode")    
        state.halted = True
    else:
        if(if_flags&ie_flags&0x1F == 0):        
            if(dlog.enable.z80):
                dlog.print_msg("Z80", "Entering HALT mode with IME=0", cat="halt_mode")    
            state.halted = True
        else:
            if(dlog.enable.z80):
                dlog.print_msg("Z80", "HALT bug", cat="halt_mode")
            state.halt_bug = True      
    op.cycles = 4
    
### OP STOP ########################################################################
def op_stop():
    state.stopped = True
    if(dlog.enable.z80):
        dlog.print_msg("Z80", "Entering STOP mode", cat="stop_mode")
    # Skip one byte because
    # https://stackoverflow.com/questions/41353869/length-of-instruction-ld-a-c-in-gameboy-z80-processor
    # There is a hardware bug on Gameboy Classic that causes 
    # the instruction following a STOP to be skipped.
    # TODO implement STOP bug
    op.cycles = 4
    
### OP DI ##########################################################################
def op_di():
    state.interrupt_master_enable = 0
    op.cycles = 4
    
### OP EI ##########################################################################
def op_ei():
    state.interrupt_master_enable = 1
    state.interrupt_master_enable_skip_one_cycle = 1
    op.cycles = 4
    
### OP RLC #########################################################################   
def op_rlc_a():
    s = reg.a    
    result = op_rlc_x_helper(s)
    reg.a = result
    op.cycles = 4
def op_rlc_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r)
    result = op_rlc_x_helper(s)
    reg.set_r(r, result)
    op.cycles = 8
def op_rlc_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    result = op_rlc_x_helper(s)
    mem.write_byte(hl, result)
    op.cycles = 16
def op_rlc_x_helper(s):
    result = ((s<<1)&0xFF)|((s&0x80)>>7)
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    if(s&0x80):
        reg.set_flag_c()
    return result
    
### OP RL ##########################################################################
def op_rl_a():
    s = reg.a    
    result = op_rl_x_helper(s)
    reg.a = result
    op.cycles = 4
def op_rl_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r)
    result = op_rl_x_helper(s)
    reg.set_r(r, result)
    op.cycles = 8
def op_rl_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    result = op_rl_x_helper(s)
    mem.write_byte(hl, result)
    op.cycles = 16
def op_rl_x_helper(s):
    result = ((s<<1)&0xFF)|(reg.get_flag_c())
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    if(s&0x80):
        reg.set_flag_c()
    return result
    
### OP RRC #########################################################################
def op_rrc_a():
    s = reg.a    
    result = op_rrc_x_helper(s)
    reg.a = result
    op.cycles = 4
def op_rrc_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r)
    result = op_rrc_x_helper(s)
    reg.set_r(r, result)
    op.cycles = 8
def op_rrc_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    result = op_rrc_x_helper(s)
    mem.write_byte(hl, result)
    op.cycles = 16
def op_rrc_x_helper(s):
    result = (s>>1)|((s&0x01)<<7)
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    if(s&0x01):
        reg.set_flag_c()
    return result
    
### OP RR ##########################################################################
def op_rr_a():
    s = reg.a    
    result = op_rr_x_helper(s)
    reg.a = result
    op.cycles = 4
def op_rr_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r)
    result = op_rr_x_helper(s)
    reg.set_r(r, result)
    op.cycles = 8
def op_rr_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    result = op_rr_x_helper(s)
    mem.write_byte(hl, result)
    op.cycles = 16
def op_rr_x_helper(s):
    result = (s>>1)|(reg.get_flag_c()<<7)
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()
    if(s&0x01):
        reg.set_flag_c()
    return result
    
### OP SLA #########################################################################
def op_sla_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r)
    result = op_sla_x_helper(s)
    reg.set_r(r, result)
    op.cycles = 8
def op_sla_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    result = op_sla_x_helper(s)
    mem.write_byte(hl, result)
    op.cycles = 16
def op_sla_x_helper(s):
    result = (s<<1)&0xFE
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()     
    if(s&0x80):
        reg.set_flag_c()   
    return result

### OP SRA ########################################################################
def op_sra_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r)
    result = op_sra_x_helper(s)
    reg.set_r(r, result)
    op.cycles = 8
def op_sra_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    result = op_sra_x_helper(s)
    mem.write_byte(hl, result)
    op.cycles = 16
def op_sra_x_helper(s):
    result = (s&0x80)|((s>>1)&0x7F)
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()     
    if(s&0x01):
        reg.set_flag_c()   
    return result

### OP SRL ########################################################################
def op_srl_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r)
    result = op_srl_x_helper(s)
    reg.set_r(r, result)
    op.cycles = 8
def op_srl_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    result = op_srl_x_helper(s)
    mem.write_byte(hl, result)
    op.cycles = 16
def op_srl_x_helper(s):
    result = ((s>>1)&0x7F)
    reg.reset_flags()
    if(result == 0):
        reg.set_flag_z()     
    if(s&0x01):
        reg.set_flag_c()   
    return result
    
### OP BIT #########################################################################
def op_bit_r():
    s = reg.get_r((op.code >> 0)&0x07) #z
    b = (op.code >> 3)&0x07 #y
    op_bit_x_helper(s,b)
    op.cycles = 8
def op_bit_hlmem():
    s = mem.read_byte(reg.get_hl())
    b = (op.code >> 3)&0x07 #y
    op_bit_x_helper(s,b)
    op.cycles = 16
def op_bit_x_helper(s,b):
    if(s&(0x01<<b)==0):
        reg.set_flag_z()
    else:
        reg.reset_flag_z()
    reg.reset_flag_n()
    reg.set_flag_h()
    
### OP SET #########################################################################
def op_set_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r) 
    b = (op.code >> 3)&0x07 #y
    reg.set_r(r, s|(0x01<<b))
    op.cycles = 8
def op_set_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    b = (op.code >> 3)&0x07 #y
    mem.write_byte(hl, s|(0x01<<b))
    op.cycles = 16
    
### OP RES #########################################################################
def op_res_r():
    r = (op.code >> 0)&0x07 #z
    s = reg.get_r(r) 
    b = (op.code >> 3)&0x07 #y
    reg.set_r(r, s&(~(0x01<<b)))
    op.cycles = 8
def op_res_hlmem():
    hl = reg.get_hl()
    s = mem.read_byte(hl)
    b = (op.code >> 3)&0x07 #y
    mem.write_byte(hl, s&(~(0x01<<b)))
    op.cycles = 16

### OP JP ##########################################################################
def op_jp_nn():
    reg.pc = mem.read_word(reg.pc)
    op.cycles = 12
def op_jp_nz_nn():
    if(not reg.get_flag_z()):
        reg.pc = mem.read_word(reg.pc)
    else:
        reg.pc += 2
    op.cycles = 12
def op_jp_z_nn():
    if(reg.get_flag_z()):
        reg.pc = mem.read_word(reg.pc)
    else:
        reg.pc += 2
    op.cycles = 12
def op_jp_nc_nn():
    if(not reg.get_flag_c()):
        reg.pc = mem.read_word(reg.pc)
    else:
        reg.pc += 2
    op.cycles = 12
def op_jp_c_nn():
    if(reg.get_flag_c()):
        reg.pc = mem.read_word(reg.pc)
    else:
        reg.pc += 2
    op.cycles = 12
def op_jp_hl():
    reg.pc = reg.get_hl()
    op.cycles = 4
    
### OP JR ##########################################################################
def op_jr_n():
    n = mem.read_byte(reg.pc);
    n = gbmath.signed_byte(n)
    reg.pc = reg.pc+n+1
    op.cycles = 8
def op_jr_nz_n():
    if(not reg.get_flag_z()):    
        n = mem.read_byte(reg.pc);
        n = gbmath.signed_byte(n)
        reg.pc = reg.pc+n+1
    else:
        reg.pc += 1
    op.cycles = 8
def op_jr_z_n():
    if(reg.get_flag_z()):    
        n = mem.read_byte(reg.pc);
        n = gbmath.signed_byte(n)
        reg.pc = reg.pc+n+1
    else:
        reg.pc += 1
    op.cycles = 8
def op_jr_nc_n():
    if(not reg.get_flag_c()):    
        n = mem.read_byte(reg.pc);
        n = gbmath.signed_byte(n)
        reg.pc = reg.pc+n+1
    else:
        reg.pc += 1
    op.cycles = 8
def op_jr_c_n():
    if(reg.get_flag_c()):    
        n = mem.read_byte(reg.pc);
        n = gbmath.signed_byte(n)
        reg.pc = reg.pc+n+1
    else:
        reg.pc += 1
    op.cycles = 8

### OP CALL ########################################################################
def op_call_nn():
    nn = mem.read_word(reg.pc); reg.pc += 2
    reg.sp -= 2; mem.write_word(reg.sp, reg.pc)
    reg.pc = nn
    op.cycles = 12
def op_call_nz_nn():
    if(not reg.get_flag_z()): 
        nn = mem.read_word(reg.pc); reg.pc += 2
        reg.sp -= 2; mem.write_word(reg.sp, reg.pc)
        reg.pc = nn
    else:
        reg.pc += 2
    op.cycles = 12
def op_call_z_nn():
    if(reg.get_flag_z()): 
        nn = mem.read_word(reg.pc); reg.pc += 2
        reg.sp -= 2; mem.write_word(reg.sp, reg.pc)
        reg.pc = nn
    else:
        reg.pc += 2
    op.cycles = 12
def op_call_nc_nn():
    if(not reg.get_flag_c()): 
        nn = mem.read_word(reg.pc); reg.pc += 2
        reg.sp -= 2; mem.write_word(reg.sp, reg.pc)
        reg.pc = nn
    else:
        reg.pc += 2
    op.cycles = 12
def op_call_c_nn():
    if(reg.get_flag_c()): 
        nn = mem.read_word(reg.pc); reg.pc += 2
        reg.sp -= 2; mem.write_word(reg.sp, reg.pc)
        reg.pc = nn
    else:
        reg.pc += 2
    op.cycles = 12

### OP RST #########################################################################
def op_rst_n():
    reg.sp -= 2; mem.write_word(reg.sp, reg.pc)
    reg.pc = op.code&0x38
    op.cycles = 32

### OP RET #########################################################################
def op_ret():
    reg.pc = mem.read_word(reg.sp)
    reg.sp += 2
    op.cycles = 8
def op_ret_nz():
    if(not reg.get_flag_z()): 
        reg.pc = mem.read_word(reg.sp)
        reg.sp += 2
    op.cycles = 8
def op_ret_z():
    if(reg.get_flag_z()): 
        reg.pc = mem.read_word(reg.sp)
        reg.sp += 2
    op.cycles = 8
def op_ret_nc():
    if(not reg.get_flag_c()): 
        reg.pc = mem.read_word(reg.sp)
        reg.sp += 2
    op.cycles = 8
def op_ret_c():
    if(reg.get_flag_c()): 
        reg.pc = mem.read_word(reg.sp)
        reg.sp += 2
    op.cycles = 8
    
### OP RET #########################################################################
def op_reti():
    reg.pc = mem.read_word(reg.sp)
    reg.sp += 2
    op.cycles = 8
    state.interrupt_master_enable = 1
    state.interrupt_master_enable_skip_one_cycle = 0
    
### OP XXX #########################################################################
def op_xxx():
    op.cycles = 4
    dlog.print_error("Z80", "invalid opcode " + hex(op.code) + " at " +  hex(reg.pc-1))
        
### OP MAP #########################################################################
op_map_nopref       = [None]*256
op_map_cbpref       = [None]*256
no_operation        = [op_xxx,          (1, "XXX", "")]
op_map_nopref[0x7F] = [op_ld_r1_r2,     (1, "LD", "A,A")]
op_map_nopref[0x78] = [op_ld_r1_r2,     (1, "LD", "A,B")]
op_map_nopref[0x79] = [op_ld_r1_r2,     (1, "LD", "A,C")]
op_map_nopref[0x7A] = [op_ld_r1_r2,     (1, "LD", "A,D")]
op_map_nopref[0x7B] = [op_ld_r1_r2,     (1, "LD", "A,E")]
op_map_nopref[0x7C] = [op_ld_r1_r2,     (1, "LD", "A,H")]
op_map_nopref[0x7D] = [op_ld_r1_r2,     (1, "LD", "A,L")]
op_map_nopref[0x47] = [op_ld_r1_r2,     (1, "LD", "B,A")]
op_map_nopref[0x40] = [op_ld_r1_r2,     (1, "LD", "B,B")]
op_map_nopref[0x41] = [op_ld_r1_r2,     (1, "LD", "B,C")]
op_map_nopref[0x42] = [op_ld_r1_r2,     (1, "LD", "B,D")]
op_map_nopref[0x43] = [op_ld_r1_r2,     (1, "LD", "B,E")]
op_map_nopref[0x44] = [op_ld_r1_r2,     (1, "LD", "B,H")]
op_map_nopref[0x45] = [op_ld_r1_r2,     (1, "LD", "B,L")]
op_map_nopref[0x4F] = [op_ld_r1_r2,     (1, "LD", "C,A")]
op_map_nopref[0x48] = [op_ld_r1_r2,     (1, "LD", "C,B")]
op_map_nopref[0x49] = [op_ld_r1_r2,     (1, "LD", "C,C")]
op_map_nopref[0x4A] = [op_ld_r1_r2,     (1, "LD", "C,D")]
op_map_nopref[0x4B] = [op_ld_r1_r2,     (1, "LD", "C,E")]
op_map_nopref[0x4C] = [op_ld_r1_r2,     (1, "LD", "C,H")]
op_map_nopref[0x4D] = [op_ld_r1_r2,     (1, "LD", "C,L")]
op_map_nopref[0x57] = [op_ld_r1_r2,     (1, "LD", "D,A")]
op_map_nopref[0x50] = [op_ld_r1_r2,     (1, "LD", "D,B")]
op_map_nopref[0x51] = [op_ld_r1_r2,     (1, "LD", "D,C")]
op_map_nopref[0x52] = [op_ld_r1_r2,     (1, "LD", "D,D")]
op_map_nopref[0x53] = [op_ld_r1_r2,     (1, "LD", "D,E")]
op_map_nopref[0x54] = [op_ld_r1_r2,     (1, "LD", "D,H")]
op_map_nopref[0x55] = [op_ld_r1_r2,     (1, "LD", "D,L")]
op_map_nopref[0x5F] = [op_ld_r1_r2,     (1, "LD", "E,A")]
op_map_nopref[0x58] = [op_ld_r1_r2,     (1, "LD", "E,B")]
op_map_nopref[0x59] = [op_ld_r1_r2,     (1, "LD", "E,C")]
op_map_nopref[0x5A] = [op_ld_r1_r2,     (1, "LD", "E,D")]
op_map_nopref[0x5B] = [op_ld_r1_r2,     (1, "LD", "E,E")]
op_map_nopref[0x5C] = [op_ld_r1_r2,     (1, "LD", "E,H")]
op_map_nopref[0x5D] = [op_ld_r1_r2,     (1, "LD", "E,L")]
op_map_nopref[0x67] = [op_ld_r1_r2,     (1, "LD", "H,A")]
op_map_nopref[0x60] = [op_ld_r1_r2,     (1, "LD", "H,B")]
op_map_nopref[0x61] = [op_ld_r1_r2,     (1, "LD", "H,C")]
op_map_nopref[0x62] = [op_ld_r1_r2,     (1, "LD", "H,D")]
op_map_nopref[0x63] = [op_ld_r1_r2,     (1, "LD", "H,E")]
op_map_nopref[0x64] = [op_ld_r1_r2,     (1, "LD", "H,H")]
op_map_nopref[0x65] = [op_ld_r1_r2,     (1, "LD", "H,L")] 
op_map_nopref[0x6F] = [op_ld_r1_r2,     (1, "LD", "L,A")]
op_map_nopref[0x68] = [op_ld_r1_r2,     (1, "LD", "L,B")]
op_map_nopref[0x69] = [op_ld_r1_r2,     (1, "LD", "L,C")]
op_map_nopref[0x6A] = [op_ld_r1_r2,     (1, "LD", "L,D")]
op_map_nopref[0x6B] = [op_ld_r1_r2,     (1, "LD", "L,E")]
op_map_nopref[0x6C] = [op_ld_r1_r2,     (1, "LD", "L,H")]
op_map_nopref[0x6D] = [op_ld_r1_r2,     (1, "LD", "L,L")]
op_map_nopref[0x3E] = [op_ld_r1_n,      (2, "LD", "A,n")]
op_map_nopref[0x06] = [op_ld_r1_n,      (2, "LD", "B,n")]
op_map_nopref[0x0E] = [op_ld_r1_n,      (2, "LD", "C,n")]
op_map_nopref[0x16] = [op_ld_r1_n,      (2, "LD", "D,n")]
op_map_nopref[0x1E] = [op_ld_r1_n,      (2, "LD", "E,n")]
op_map_nopref[0x26] = [op_ld_r1_n,      (2, "LD", "H,n")]
op_map_nopref[0x2E] = [op_ld_r1_n,      (2, "LD", "L,n")]
op_map_nopref[0xEA] = [op_ld_nnmem_a,   (3, "LD", "(nn),A")]
op_map_nopref[0x02] = [op_ld_bcmem_a,   (1, "LD", "(BC),A")]
op_map_nopref[0x12] = [op_ld_demem_a,   (1, "LD", "(DE),A")]
op_map_nopref[0x77] = [op_ld_hlmem_r2,  (1, "LD", "(HL),A")]
op_map_nopref[0x70] = [op_ld_hlmem_r2,  (1, "LD", "(HL),B")]
op_map_nopref[0x71] = [op_ld_hlmem_r2,  (1, "LD", "(HL),C")]
op_map_nopref[0x72] = [op_ld_hlmem_r2,  (1, "LD", "(HL),D")]
op_map_nopref[0x73] = [op_ld_hlmem_r2,  (1, "LD", "(HL),E")]
op_map_nopref[0x74] = [op_ld_hlmem_r2,  (1, "LD", "(HL),H")]
op_map_nopref[0x75] = [op_ld_hlmem_r2,  (1, "LD", "(HL),L")]
op_map_nopref[0x36] = [op_ld_hlmem_n,   (2, "LD", "(HL),n")]
op_map_nopref[0xFA] = [op_ld_a_nnmem,   (3, "LD", "A,(nn)")]
op_map_nopref[0x0A] = [op_ld_a_bcmem,   (1, "LD", "A,(BC)")]
op_map_nopref[0x1A] = [op_ld_a_demem,   (1, "LD", "A,(DE)")]
op_map_nopref[0x7E] = [op_ld_r1_hlmem,  (1, "LD", "A,(HL)")]
op_map_nopref[0x46] = [op_ld_r1_hlmem,  (1, "LD", "B,(HL)")]
op_map_nopref[0x4E] = [op_ld_r1_hlmem,  (1, "LD", "C,(HL)")]
op_map_nopref[0x56] = [op_ld_r1_hlmem,  (1, "LD", "D,(HL)")]
op_map_nopref[0x5E] = [op_ld_r1_hlmem,  (1, "LD", "E,(HL)")]
op_map_nopref[0x66] = [op_ld_r1_hlmem,  (1, "LD", "H,(HL)")]
op_map_nopref[0x6E] = [op_ld_r1_hlmem,  (1, "LD", "L,(HL)")]
op_map_nopref[0xF2] = [op_ld_a_ff00c,   (1, "LD", "A,(C)")]
op_map_nopref[0xE2] = [op_ld_ff00c_a,   (1, "LD", "(C),A")]
op_map_nopref[0xF0] = [op_ld_a_ff00n,   (2, "LDH", "A,(n)")]
op_map_nopref[0xE0] = [op_ld_ff00n_a,   (2, "LDH", "(n),A")]
op_map_nopref[0x3A] = [op_ldd_a_hlmem,  (1, "LD", "A,(HL-)")]
op_map_nopref[0x32] = [op_ldd_hlmem_a,  (1, "LD", "(HL-),A")]
op_map_nopref[0x2A] = [op_ldi_a_hlmem,  (1, "LD", "A,(HL+)")]
op_map_nopref[0x22] = [op_ldi_hlmem_a,  (1, "LD", "(HL+),A")]    
op_map_nopref[0x01] = [op_ld_rp_nn,     (3, "LD", "BC,nn")]
op_map_nopref[0x11] = [op_ld_rp_nn,     (3, "LD", "DE,nn")]
op_map_nopref[0x21] = [op_ld_rp_nn,     (3, "LD", "HL,nn")]
op_map_nopref[0x31] = [op_ld_rp_nn,     (3, "LD", "SP,nn")]
op_map_nopref[0xF9] = [op_ld_sp_hl,     (1, "LD", "SP,HL")]
op_map_nopref[0xF8] = [op_ldhl_sp_n,    (2, "LD", "HL,SP+n")]
op_map_nopref[0x08] = [op_ld_nnmem_sp,  (3, "LD", "(nn),SP")]    
op_map_nopref[0xF5] = [op_push_af,      (1, "PUSH", "AF")]
op_map_nopref[0xC5] = [op_push_bc,      (1, "PUSH", "BC")]
op_map_nopref[0xD5] = [op_push_de,      (1, "PUSH", "DE")]
op_map_nopref[0xE5] = [op_push_hl,      (1, "PUSH", "HL")]    
op_map_nopref[0xF1] = [op_pop_af,       (1, "POP", "AF")]
op_map_nopref[0xC1] = [op_pop_bc,       (1, "POP", "BC")]
op_map_nopref[0xD1] = [op_pop_de,       (1, "POP", "DE")]
op_map_nopref[0xE1] = [op_pop_hl,       (1, "POP", "HL")]    
op_map_nopref[0x87] = [op_add_a_r2,     (1, "ADD", "A,A")]
op_map_nopref[0x80] = [op_add_a_r2,     (1, "ADD", "A,B")]
op_map_nopref[0x81] = [op_add_a_r2,     (1, "ADD", "A,C")]
op_map_nopref[0x82] = [op_add_a_r2,     (1, "ADD", "A,D")]
op_map_nopref[0x83] = [op_add_a_r2,     (1, "ADD", "A,E")]
op_map_nopref[0x84] = [op_add_a_r2,     (1, "ADD", "A,H")]
op_map_nopref[0x85] = [op_add_a_r2,     (1, "ADD", "A,L")]
op_map_nopref[0x86] = [op_add_a_hlmem,  (1, "ADD", "A,(HL)")]
op_map_nopref[0xC6] = [op_add_a_n,      (2, "ADD", "A,n")]    
op_map_nopref[0x8F] = [op_adc_a_r2,     (1, "ADC", "A,A")]
op_map_nopref[0x88] = [op_adc_a_r2,     (1, "ADC", "A,B")]
op_map_nopref[0x89] = [op_adc_a_r2,     (1, "ADC", "A,C")]
op_map_nopref[0x8A] = [op_adc_a_r2,     (1, "ADC", "A,D")]
op_map_nopref[0x8B] = [op_adc_a_r2,     (1, "ADC", "A,E")]
op_map_nopref[0x8C] = [op_adc_a_r2,     (1, "ADC", "A,H")]
op_map_nopref[0x8D] = [op_adc_a_r2,     (1, "ADC", "A,L")]
op_map_nopref[0x8E] = [op_adc_a_hlmem,  (1, "ADC", "A,(HL)")]
op_map_nopref[0xCE] = [op_adc_a_n,      (2, "ADC", "A,n")]    
op_map_nopref[0x97] = [op_sub_a_r2,     (1, "SUB", "A,A")]
op_map_nopref[0x90] = [op_sub_a_r2,     (1, "SUB", "A,B")]
op_map_nopref[0x91] = [op_sub_a_r2,     (1, "SUB", "A,C")]
op_map_nopref[0x92] = [op_sub_a_r2,     (1, "SUB", "A,D")]
op_map_nopref[0x93] = [op_sub_a_r2,     (1, "SUB", "A,E")]
op_map_nopref[0x94] = [op_sub_a_r2,     (1, "SUB", "A,H")]
op_map_nopref[0x95] = [op_sub_a_r2,     (1, "SUB", "A,L")]
op_map_nopref[0x96] = [op_sub_a_hlmem,  (1, "SUB", "A,(HL)")]
op_map_nopref[0xD6] = [op_sub_a_n,      (2, "SUB", "A,n")]    
op_map_nopref[0x9F] = [op_sbc_a_r2,     (1, "SBC", "A,A")]
op_map_nopref[0x98] = [op_sbc_a_r2,     (1, "SBC", "A,B")]
op_map_nopref[0x99] = [op_sbc_a_r2,     (1, "SBC", "A,C")]
op_map_nopref[0x9A] = [op_sbc_a_r2,     (1, "SBC", "A,D")]
op_map_nopref[0x9B] = [op_sbc_a_r2,     (1, "SBC", "A,E")]
op_map_nopref[0x9C] = [op_sbc_a_r2,     (1, "SBC", "A,H")]
op_map_nopref[0x9D] = [op_sbc_a_r2,     (1, "SBC", "A,L")]
op_map_nopref[0x9E] = [op_sbc_a_hlmem,  (1, "SBC", "A,(HL)")]
op_map_nopref[0xDE] = [op_sbc_a_n,      (2, "SBC", "A,n")]    
op_map_nopref[0xA7] = [op_and_a_r2,     (1, "AND", "A")]
op_map_nopref[0xA0] = [op_and_a_r2,     (1, "AND", "B")]
op_map_nopref[0xA1] = [op_and_a_r2,     (1, "AND", "C")]
op_map_nopref[0xA2] = [op_and_a_r2,     (1, "AND", "D")]
op_map_nopref[0xA3] = [op_and_a_r2,     (1, "AND", "E")]
op_map_nopref[0xA4] = [op_and_a_r2,     (1, "AND", "H")]
op_map_nopref[0xA5] = [op_and_a_r2,     (1, "AND", "L")]
op_map_nopref[0xA6] = [op_and_a_hlmem,  (1, "AND", "(HL)")]
op_map_nopref[0xE6] = [op_and_a_n,      (2, "AND", "n")]    
op_map_nopref[0xB7] = [op_or_a_r2,      (1, "OR", "A")]
op_map_nopref[0xB0] = [op_or_a_r2,      (1, "OR", "B")]
op_map_nopref[0xB1] = [op_or_a_r2,      (1, "OR", "C")]
op_map_nopref[0xB2] = [op_or_a_r2,      (1, "OR", "D")]
op_map_nopref[0xB3] = [op_or_a_r2,      (1, "OR", "E")]
op_map_nopref[0xB4] = [op_or_a_r2,      (1, "OR", "H")]
op_map_nopref[0xB5] = [op_or_a_r2,      (1, "OR", "L")]
op_map_nopref[0xB6] = [op_or_a_hlmem,   (1, "OR", "(HL)")]
op_map_nopref[0xF6] = [op_or_a_n,       (2, "OR", "n")]    
op_map_nopref[0xAF] = [op_xor_a_r2,     (1, "XOR", "A")]
op_map_nopref[0xA8] = [op_xor_a_r2,     (1, "XOR", "B")]
op_map_nopref[0xA9] = [op_xor_a_r2,     (1, "XOR", "C")]
op_map_nopref[0xAA] = [op_xor_a_r2,     (1, "XOR", "D")]
op_map_nopref[0xAB] = [op_xor_a_r2,     (1, "XOR", "E")]
op_map_nopref[0xAC] = [op_xor_a_r2,     (1, "XOR", "H")]
op_map_nopref[0xAD] = [op_xor_a_r2,     (1, "XOR", "L")]
op_map_nopref[0xAE] = [op_xor_a_hlmem,  (1, "XOR", "(HL)")]
op_map_nopref[0xEE] = [op_xor_a_n,      (2, "XOR", "n")]    
op_map_nopref[0xBF] = [op_cp_a_r2,      (1, "CP", "A")]
op_map_nopref[0xB8] = [op_cp_a_r2,      (1, "CP", "B")]
op_map_nopref[0xB9] = [op_cp_a_r2,      (1, "CP", "C")]
op_map_nopref[0xBA] = [op_cp_a_r2,      (1, "CP", "D")]
op_map_nopref[0xBB] = [op_cp_a_r2,      (1, "CP", "E")]
op_map_nopref[0xBC] = [op_cp_a_r2,      (1, "CP", "H")]
op_map_nopref[0xBD] = [op_cp_a_r2,      (1, "CP", "L")]
op_map_nopref[0xBE] = [op_cp_a_hlmem,   (1, "CP", "(HL)")]
op_map_nopref[0xFE] = [op_cp_a_n,       (2, "CP", "n")]    
op_map_nopref[0x3C] = [op_inc_r1,       (1, "INC", "A")]
op_map_nopref[0x04] = [op_inc_r1,       (1, "INC", "B")]
op_map_nopref[0x0C] = [op_inc_r1,       (1, "INC", "C")]
op_map_nopref[0x14] = [op_inc_r1,       (1, "INC", "D")]
op_map_nopref[0x1C] = [op_inc_r1,       (1, "INC", "E")]
op_map_nopref[0x24] = [op_inc_r1,       (1, "INC", "H")]
op_map_nopref[0x2C] = [op_inc_r1,       (1, "INC", "L")]
op_map_nopref[0x34] = [op_inc_hlmem,    (1, "INC", "(HL)")]    
op_map_nopref[0x3D] = [op_dec_r1,       (1, "DEC", "A")]
op_map_nopref[0x05] = [op_dec_r1,       (1, "DEC", "B")]
op_map_nopref[0x0D] = [op_dec_r1,       (1, "DEC", "C")]
op_map_nopref[0x15] = [op_dec_r1,       (1, "DEC", "D")]
op_map_nopref[0x1D] = [op_dec_r1,       (1, "DEC", "E")]
op_map_nopref[0x25] = [op_dec_r1,       (1, "DEC", "H")]
op_map_nopref[0x2D] = [op_dec_r1,       (1, "DEC", "L")]
op_map_nopref[0x35] = [op_dec_hlmem,    (1, "DEC", "(HL)")]    
op_map_nopref[0x09] = [op_add_hl_rp,    (1, "ADD", "HL,BC")]
op_map_nopref[0x19] = [op_add_hl_rp,    (1, "ADD", "HL,DE")]
op_map_nopref[0x29] = [op_add_hl_rp,    (1, "ADD", "HL,HL")]
op_map_nopref[0x39] = [op_add_hl_rp,    (1, "ADD", "HL,SP")]
op_map_nopref[0xE8] = [op_add_sp_n,     (2, "ADD", "SP,n")]    
op_map_nopref[0x03] = [op_inc_rp,       (1, "INC", "BC")]
op_map_nopref[0x13] = [op_inc_rp,       (1, "INC", "DE")]
op_map_nopref[0x23] = [op_inc_rp,       (1, "INC", "HL")]
op_map_nopref[0x33] = [op_inc_rp,       (1, "INC", "SP")]    
op_map_nopref[0x0B] = [op_dec_rp,       (1, "DEC", "BC")]
op_map_nopref[0x1B] = [op_dec_rp,       (1, "DEC", "DE")]
op_map_nopref[0x2B] = [op_dec_rp,       (1, "DEC", "HL")]
op_map_nopref[0x3B] = [op_dec_rp,       (1, "DEC", "SP")]
op_map_nopref[0x27] = [op_daa,          (1, "DAA", "")]
op_map_nopref[0x2F] = [op_cpl,          (1, "CPL", "")]
op_map_nopref[0x3F] = [op_ccf,          (1, "CCF", "")]
op_map_nopref[0x37] = [op_scf,          (1, "SCF", "")]
op_map_nopref[0x00] = [op_nop,          (1, "NOP", "")]
op_map_nopref[0x76] = [op_halt,         (1, "HALT", "")]
op_map_nopref[0x10] = [op_stop,         (2, "STOP", "")]
op_map_nopref[0xF3] = [op_di,           (1, "DI", "")]
op_map_nopref[0xFB] = [op_ei,           (1, "EI", "")]
op_map_nopref[0x07] = [op_rlc_a,        (1, "RLCA", "")]
op_map_nopref[0x17] = [op_rl_a,         (1, "RLA", "")]
op_map_nopref[0x0F] = [op_rrc_a,        (1, "RRCA", "")]
op_map_nopref[0x1F] = [op_rr_a,         (1, "RRA", "")]
op_map_nopref[0x1F] = [op_rr_a,         (1, "RRA", "")]
op_map_nopref[0xC3] = [op_jp_nn,        (3, "JP", "nn")]
op_map_nopref[0xC2] = [op_jp_nz_nn,     (3, "JP", "NZ,nn")]
op_map_nopref[0xCA] = [op_jp_z_nn,      (3, "JP", "Z,nn")]
op_map_nopref[0xD2] = [op_jp_nc_nn,     (3, "JP", "NC,nn")]
op_map_nopref[0xDA] = [op_jp_c_nn,      (3, "JP", "C,nn")]
op_map_nopref[0xE9] = [op_jp_hl,        (1, "JP", "(HL)")]
op_map_nopref[0x18] = [op_jr_n,         (2, "JR", "n")]
op_map_nopref[0x20] = [op_jr_nz_n,      (2, "JR", "NZ,n")]
op_map_nopref[0x28] = [op_jr_z_n,       (2, "JR", "Z,n")]
op_map_nopref[0x30] = [op_jr_nc_n,      (2, "JR", "NC,n")]
op_map_nopref[0x38] = [op_jr_c_n,       (2, "JR", "C,n")]
op_map_nopref[0xCD] = [op_call_nn,      (3, "CALL", "nn")]
op_map_nopref[0xC4] = [op_call_nz_nn,   (3, "CALL", "NZ,nn")]
op_map_nopref[0xCC] = [op_call_z_nn,    (3, "CALL", "Z,nn")]
op_map_nopref[0xD4] = [op_call_nc_nn,   (3, "CALL", "NC,nn")]
op_map_nopref[0xDC] = [op_call_c_nn,    (3, "CALL", "C,nn")]
op_map_nopref[0xC9] = [op_ret,          (1, "RET", "")]
op_map_nopref[0xC0] = [op_ret_nz,       (3, "RET", "NZ,nn")]
op_map_nopref[0xC8] = [op_ret_z,        (3, "RET", "Z,nn")]
op_map_nopref[0xD0] = [op_ret_nc,       (3, "RET", "NC,nn")]
op_map_nopref[0xD8] = [op_ret_c,        (3, "RET", "C,nn")]
op_map_nopref[0xD9] = [op_reti,         (1, "RETI", "")]
op_map_nopref[0xC7] = [op_rst_n,        (1, "RST", "00H")]
op_map_nopref[0xCF] = [op_rst_n,        (1, "RST", "08H")]
op_map_nopref[0xD7] = [op_rst_n,        (1, "RST", "10H")]
op_map_nopref[0xDF] = [op_rst_n,        (1, "RST", "18H")]
op_map_nopref[0xE7] = [op_rst_n,        (1, "RST", "20H")]
op_map_nopref[0xEF] = [op_rst_n,        (1, "RST", "28H")]
op_map_nopref[0xF7] = [op_rst_n,        (1, "RST", "30H")]
op_map_nopref[0xFF] = [op_rst_n,        (1, "RST", "38H")]
op_map_cbpref[0x37] = [op_swap_r,       (2, "SWAP", "A")]
op_map_cbpref[0x30] = [op_swap_r,       (2, "SWAP", "B")]
op_map_cbpref[0x31] = [op_swap_r,       (2, "SWAP", "C")]
op_map_cbpref[0x32] = [op_swap_r,       (2, "SWAP", "D")]
op_map_cbpref[0x33] = [op_swap_r,       (2, "SWAP", "E")]
op_map_cbpref[0x34] = [op_swap_r,       (2, "SWAP", "H")]
op_map_cbpref[0x35] = [op_swap_r,       (2, "SWAP", "L")]
op_map_cbpref[0x36] = [op_swap_hlmem,   (2, "SWAP", "(HL)")]
op_map_cbpref[0x07] = [op_rlc_r,        (2, "RLC", "A")]
op_map_cbpref[0x00] = [op_rlc_r,        (2, "RLC", "B")]
op_map_cbpref[0x01] = [op_rlc_r,        (2, "RLC", "C")]
op_map_cbpref[0x02] = [op_rlc_r,        (2, "RLC", "D")]
op_map_cbpref[0x03] = [op_rlc_r,        (2, "RLC", "E")]
op_map_cbpref[0x04] = [op_rlc_r,        (2, "RLC", "H")]
op_map_cbpref[0x05] = [op_rlc_r,        (2, "RLC", "L")]
op_map_cbpref[0x06] = [op_rlc_hlmem,    (2, "RLC", "(HL)")]
op_map_cbpref[0x17] = [op_rl_r,         (2, "RL", "A")]
op_map_cbpref[0x10] = [op_rl_r,         (2, "RL", "B")]
op_map_cbpref[0x11] = [op_rl_r,         (2, "RL", "C")]
op_map_cbpref[0x12] = [op_rl_r,         (2, "RL", "D")]
op_map_cbpref[0x13] = [op_rl_r,         (2, "RL", "E")]
op_map_cbpref[0x14] = [op_rl_r,         (2, "RL", "H")]
op_map_cbpref[0x15] = [op_rl_r,         (2, "RL", "L")]
op_map_cbpref[0x16] = [op_rl_hlmem,     (2, "RL", "(HL)")]
op_map_cbpref[0x0F] = [op_rrc_r,        (2, "RRC", "A")]
op_map_cbpref[0x08] = [op_rrc_r,        (2, "RRC", "B")]
op_map_cbpref[0x09] = [op_rrc_r,        (2, "RRC", "C")]
op_map_cbpref[0x0A] = [op_rrc_r,        (2, "RRC", "D")]
op_map_cbpref[0x0B] = [op_rrc_r,        (2, "RRC", "E")]
op_map_cbpref[0x0C] = [op_rrc_r,        (2, "RRC", "H")]
op_map_cbpref[0x0D] = [op_rrc_r,        (2, "RRC", "L")]
op_map_cbpref[0x0E] = [op_rrc_hlmem,    (2, "RRC", "(HL)")]
op_map_cbpref[0x1F] = [op_rr_r,         (2, "RR", "A")]
op_map_cbpref[0x18] = [op_rr_r,         (2, "RR", "B")]
op_map_cbpref[0x19] = [op_rr_r,         (2, "RR", "C")]
op_map_cbpref[0x1A] = [op_rr_r,         (2, "RR", "D")]
op_map_cbpref[0x1B] = [op_rr_r,         (2, "RR", "E")]
op_map_cbpref[0x1C] = [op_rr_r,         (2, "RR", "H")]
op_map_cbpref[0x1D] = [op_rr_r,         (2, "RR", "L")]
op_map_cbpref[0x1E] = [op_rr_hlmem,     (2, "RR", "(HL)")]
op_map_cbpref[0x27] = [op_sla_r,        (2, "SLA", "A")]
op_map_cbpref[0x20] = [op_sla_r,        (2, "SLA", "B")]
op_map_cbpref[0x21] = [op_sla_r,        (2, "SLA", "C")]
op_map_cbpref[0x22] = [op_sla_r,        (2, "SLA", "D")]
op_map_cbpref[0x23] = [op_sla_r,        (2, "SLA", "E")]
op_map_cbpref[0x24] = [op_sla_r,        (2, "SLA", "H")]
op_map_cbpref[0x25] = [op_sla_r,        (2, "SLA", "L")]
op_map_cbpref[0x26] = [op_sla_hlmem,    (2, "SLA", "(HL)")]    
op_map_cbpref[0x2F] = [op_sra_r,        (2, "SRA", "A")]
op_map_cbpref[0x28] = [op_sra_r,        (2, "SRA", "B")]
op_map_cbpref[0x29] = [op_sra_r,        (2, "SRA", "C")]
op_map_cbpref[0x2A] = [op_sra_r,        (2, "SRA", "D")]
op_map_cbpref[0x2B] = [op_sra_r,        (2, "SRA", "E")]
op_map_cbpref[0x2C] = [op_sra_r,        (2, "SRA", "H")]
op_map_cbpref[0x2D] = [op_sra_r,        (2, "SRA", "L")]
op_map_cbpref[0x2E] = [op_sra_hlmem,    (2, "SRA", "(HL)")]    
op_map_cbpref[0x3F] = [op_srl_r,        (2, "SRL", "A")]
op_map_cbpref[0x38] = [op_srl_r,        (2, "SRL", "B")]
op_map_cbpref[0x39] = [op_srl_r,        (2, "SRL", "C")]
op_map_cbpref[0x3A] = [op_srl_r,        (2, "SRL", "D")]
op_map_cbpref[0x3B] = [op_srl_r,        (2, "SRL", "E")]
op_map_cbpref[0x3C] = [op_srl_r,        (2, "SRL", "H")]
op_map_cbpref[0x3D] = [op_srl_r,        (2, "SRL", "L")]
op_map_cbpref[0x3E] = [op_srl_hlmem,    (2, "SRL", "(HL)")]
op_map_cbpref[0x47] = [op_bit_r,        (2, "BIT", "0,A")]
op_map_cbpref[0x40] = [op_bit_r,        (2, "BIT", "0,B")]
op_map_cbpref[0x41] = [op_bit_r,        (2, "BIT", "0,C")]
op_map_cbpref[0x42] = [op_bit_r,        (2, "BIT", "0,D")]
op_map_cbpref[0x43] = [op_bit_r,        (2, "BIT", "0,E")]
op_map_cbpref[0x44] = [op_bit_r,        (2, "BIT", "0,H")]
op_map_cbpref[0x45] = [op_bit_r,        (2, "BIT", "0,L")]
op_map_cbpref[0x46] = [op_bit_hlmem,    (2, "BIT", "0,(HL)")]
op_map_cbpref[0x4F] = [op_bit_r,        (2, "BIT", "1,A")]
op_map_cbpref[0x48] = [op_bit_r,        (2, "BIT", "1,B")]
op_map_cbpref[0x49] = [op_bit_r,        (2, "BIT", "1,C")]
op_map_cbpref[0x4A] = [op_bit_r,        (2, "BIT", "1,D")]
op_map_cbpref[0x4B] = [op_bit_r,        (2, "BIT", "1,E")]
op_map_cbpref[0x4C] = [op_bit_r,        (2, "BIT", "1,H")]
op_map_cbpref[0x4D] = [op_bit_r,        (2, "BIT", "1,L")]
op_map_cbpref[0x4E] = [op_bit_hlmem,    (2, "BIT", "1,(HL)")]
op_map_cbpref[0x57] = [op_bit_r,        (2, "BIT", "2,A")]
op_map_cbpref[0x50] = [op_bit_r,        (2, "BIT", "2,B")]
op_map_cbpref[0x51] = [op_bit_r,        (2, "BIT", "2,C")]
op_map_cbpref[0x52] = [op_bit_r,        (2, "BIT", "2,D")]
op_map_cbpref[0x53] = [op_bit_r,        (2, "BIT", "2,E")]
op_map_cbpref[0x54] = [op_bit_r,        (2, "BIT", "2,H")]
op_map_cbpref[0x55] = [op_bit_r,        (2, "BIT", "2,L")]
op_map_cbpref[0x56] = [op_bit_hlmem,    (2, "BIT", "2,(HL)")]
op_map_cbpref[0x5F] = [op_bit_r,        (2, "BIT", "3,A")]
op_map_cbpref[0x58] = [op_bit_r,        (2, "BIT", "3,B")]
op_map_cbpref[0x59] = [op_bit_r,        (2, "BIT", "3,C")]
op_map_cbpref[0x5A] = [op_bit_r,        (2, "BIT", "3,D")]
op_map_cbpref[0x5B] = [op_bit_r,        (2, "BIT", "3,E")]
op_map_cbpref[0x5C] = [op_bit_r,        (2, "BIT", "3,H")]
op_map_cbpref[0x5D] = [op_bit_r,        (2, "BIT", "3,L")]
op_map_cbpref[0x5E] = [op_bit_hlmem,    (2, "BIT", "3,(HL)")]
op_map_cbpref[0x67] = [op_bit_r,        (2, "BIT", "4,A")]
op_map_cbpref[0x60] = [op_bit_r,        (2, "BIT", "4,B")]
op_map_cbpref[0x61] = [op_bit_r,        (2, "BIT", "4,C")]
op_map_cbpref[0x62] = [op_bit_r,        (2, "BIT", "4,D")]
op_map_cbpref[0x63] = [op_bit_r,        (2, "BIT", "4,E")]
op_map_cbpref[0x64] = [op_bit_r,        (2, "BIT", "4,H")]
op_map_cbpref[0x65] = [op_bit_r,        (2, "BIT", "4,L")]
op_map_cbpref[0x66] = [op_bit_hlmem,    (2, "BIT", "4,(HL)")]
op_map_cbpref[0x6F] = [op_bit_r,        (2, "BIT", "5,A")]
op_map_cbpref[0x68] = [op_bit_r,        (2, "BIT", "5,B")]
op_map_cbpref[0x69] = [op_bit_r,        (2, "BIT", "5,C")]
op_map_cbpref[0x6A] = [op_bit_r,        (2, "BIT", "5,D")]
op_map_cbpref[0x6B] = [op_bit_r,        (2, "BIT", "5,E")]
op_map_cbpref[0x6C] = [op_bit_r,        (2, "BIT", "5,H")]
op_map_cbpref[0x6D] = [op_bit_r,        (2, "BIT", "5,L")]
op_map_cbpref[0x6E] = [op_bit_hlmem,    (2, "BIT", "5,(HL)")]
op_map_cbpref[0x77] = [op_bit_r,        (2, "BIT", "6,A")]
op_map_cbpref[0x70] = [op_bit_r,        (2, "BIT", "6,B")]
op_map_cbpref[0x71] = [op_bit_r,        (2, "BIT", "6,C")]
op_map_cbpref[0x72] = [op_bit_r,        (2, "BIT", "6,D")]
op_map_cbpref[0x73] = [op_bit_r,        (2, "BIT", "6,E")]
op_map_cbpref[0x74] = [op_bit_r,        (2, "BIT", "6,H")]
op_map_cbpref[0x75] = [op_bit_r,        (2, "BIT", "6,L")]
op_map_cbpref[0x76] = [op_bit_hlmem,    (2, "BIT", "6,(HL)")]
op_map_cbpref[0x7F] = [op_bit_r,        (2, "BIT", "7,A")]
op_map_cbpref[0x78] = [op_bit_r,        (2, "BIT", "7,B")]
op_map_cbpref[0x79] = [op_bit_r,        (2, "BIT", "7,C")]
op_map_cbpref[0x7A] = [op_bit_r,        (2, "BIT", "7,D")]
op_map_cbpref[0x7B] = [op_bit_r,        (2, "BIT", "7,E")]
op_map_cbpref[0x7C] = [op_bit_r,        (2, "BIT", "7,H")]
op_map_cbpref[0x7D] = [op_bit_r,        (2, "BIT", "7,L")]
op_map_cbpref[0x7E] = [op_bit_hlmem,    (2, "BIT", "7,(HL)")]
op_map_cbpref[0xC7] = [op_set_r,        (2, "SET", "0,A")]
op_map_cbpref[0xC0] = [op_set_r,        (2, "SET", "0,B")]
op_map_cbpref[0xC1] = [op_set_r,        (2, "SET", "0,C")]
op_map_cbpref[0xC2] = [op_set_r,        (2, "SET", "0,D")]
op_map_cbpref[0xC3] = [op_set_r,        (2, "SET", "0,E")]
op_map_cbpref[0xC4] = [op_set_r,        (2, "SET", "0,H")]
op_map_cbpref[0xC5] = [op_set_r,        (2, "SET", "0,L")]
op_map_cbpref[0xC6] = [op_set_hlmem,    (2, "SET", "0,(HL)")]
op_map_cbpref[0xCF] = [op_set_r,        (2, "SET", "1,A")]
op_map_cbpref[0xC8] = [op_set_r,        (2, "SET", "1,B")]
op_map_cbpref[0xC9] = [op_set_r,        (2, "SET", "1,C")]
op_map_cbpref[0xCA] = [op_set_r,        (2, "SET", "1,D")]
op_map_cbpref[0xCB] = [op_set_r,        (2, "SET", "1,E")]
op_map_cbpref[0xCC] = [op_set_r,        (2, "SET", "1,H")]
op_map_cbpref[0xCD] = [op_set_r,        (2, "SET", "1,L")]
op_map_cbpref[0xCE] = [op_set_hlmem,    (2, "SET", "1,(HL)")]
op_map_cbpref[0xD7] = [op_set_r,        (2, "SET", "2,A")]
op_map_cbpref[0xD0] = [op_set_r,        (2, "SET", "2,B")]
op_map_cbpref[0xD1] = [op_set_r,        (2, "SET", "2,C")]
op_map_cbpref[0xD2] = [op_set_r,        (2, "SET", "2,D")]
op_map_cbpref[0xD3] = [op_set_r,        (2, "SET", "2,E")]
op_map_cbpref[0xD4] = [op_set_r,        (2, "SET", "2,H")]
op_map_cbpref[0xD5] = [op_set_r,        (2, "SET", "2,L")]
op_map_cbpref[0xD6] = [op_set_hlmem,    (2, "SET", "2,(HL)")]
op_map_cbpref[0xDF] = [op_set_r,        (2, "SET", "3,A")]
op_map_cbpref[0xD8] = [op_set_r,        (2, "SET", "3,B")]
op_map_cbpref[0xD9] = [op_set_r,        (2, "SET", "3,C")]
op_map_cbpref[0xDA] = [op_set_r,        (2, "SET", "3,D")]
op_map_cbpref[0xDB] = [op_set_r,        (2, "SET", "3,E")]
op_map_cbpref[0xDC] = [op_set_r,        (2, "SET", "3,H")]
op_map_cbpref[0xDD] = [op_set_r,        (2, "SET", "3,L")]
op_map_cbpref[0xDE] = [op_set_hlmem,    (2, "SET", "3,(HL)")]
op_map_cbpref[0xE7] = [op_set_r,        (2, "SET", "4,A")]
op_map_cbpref[0xE0] = [op_set_r,        (2, "SET", "4,B")]
op_map_cbpref[0xE1] = [op_set_r,        (2, "SET", "4,C")]
op_map_cbpref[0xE2] = [op_set_r,        (2, "SET", "4,D")]
op_map_cbpref[0xE3] = [op_set_r,        (2, "SET", "4,E")]
op_map_cbpref[0xE4] = [op_set_r,        (2, "SET", "4,H")]
op_map_cbpref[0xE5] = [op_set_r,        (2, "SET", "4,L")]
op_map_cbpref[0xE6] = [op_set_hlmem,    (2, "SET", "4,(HL)")]
op_map_cbpref[0xEF] = [op_set_r,        (2, "SET", "5,A")]
op_map_cbpref[0xE8] = [op_set_r,        (2, "SET", "5,B")]
op_map_cbpref[0xE9] = [op_set_r,        (2, "SET", "5,C")]
op_map_cbpref[0xEA] = [op_set_r,        (2, "SET", "5,D")]
op_map_cbpref[0xEB] = [op_set_r,        (2, "SET", "5,E")]
op_map_cbpref[0xEC] = [op_set_r,        (2, "SET", "5,H")]
op_map_cbpref[0xED] = [op_set_r,        (2, "SET", "5,L")]
op_map_cbpref[0xEE] = [op_set_hlmem,    (2, "SET", "5,(HL)")]
op_map_cbpref[0xF7] = [op_set_r,        (2, "SET", "6,A")]
op_map_cbpref[0xF0] = [op_set_r,        (2, "SET", "6,B")]
op_map_cbpref[0xF1] = [op_set_r,        (2, "SET", "6,C")]
op_map_cbpref[0xF2] = [op_set_r,        (2, "SET", "6,D")]
op_map_cbpref[0xF3] = [op_set_r,        (2, "SET", "6,E")]
op_map_cbpref[0xF4] = [op_set_r,        (2, "SET", "6,H")]
op_map_cbpref[0xF5] = [op_set_r,        (2, "SET", "6,L")]
op_map_cbpref[0xF6] = [op_set_hlmem,    (2, "SET", "6,(HL)")]
op_map_cbpref[0xFF] = [op_set_r,        (2, "SET", "7,A")]
op_map_cbpref[0xF8] = [op_set_r,        (2, "SET", "7,B")]
op_map_cbpref[0xF9] = [op_set_r,        (2, "SET", "7,C")]
op_map_cbpref[0xFA] = [op_set_r,        (2, "SET", "7,D")]
op_map_cbpref[0xFB] = [op_set_r,        (2, "SET", "7,E")]
op_map_cbpref[0xFC] = [op_set_r,        (2, "SET", "7,H")]
op_map_cbpref[0xFD] = [op_set_r,        (2, "SET", "7,L")]
op_map_cbpref[0xFE] = [op_set_hlmem,    (2, "SET", "7,(HL)")]
op_map_cbpref[0x87] = [op_res_r,        (2, "RES", "0,A")]
op_map_cbpref[0x80] = [op_res_r,        (2, "RES", "0,B")]
op_map_cbpref[0x81] = [op_res_r,        (2, "RES", "0,C")]
op_map_cbpref[0x82] = [op_res_r,        (2, "RES", "0,D")]
op_map_cbpref[0x83] = [op_res_r,        (2, "RES", "0,E")]
op_map_cbpref[0x84] = [op_res_r,        (2, "RES", "0,H")]
op_map_cbpref[0x85] = [op_res_r,        (2, "RES", "0,L")]
op_map_cbpref[0x86] = [op_res_hlmem,    (2, "RES", "0,(HL)")]
op_map_cbpref[0x8F] = [op_res_r,        (2, "RES", "1,A")]
op_map_cbpref[0x88] = [op_res_r,        (2, "RES", "1,B")]
op_map_cbpref[0x89] = [op_res_r,        (2, "RES", "1,C")]
op_map_cbpref[0x8A] = [op_res_r,        (2, "RES", "1,D")]
op_map_cbpref[0x8B] = [op_res_r,        (2, "RES", "1,E")]
op_map_cbpref[0x8C] = [op_res_r,        (2, "RES", "1,H")]
op_map_cbpref[0x8D] = [op_res_r,        (2, "RES", "1,L")]
op_map_cbpref[0x8E] = [op_res_hlmem,    (2, "RES", "1,(HL)")]
op_map_cbpref[0x97] = [op_res_r,        (2, "RES", "2,A")]
op_map_cbpref[0x90] = [op_res_r,        (2, "RES", "2,B")]
op_map_cbpref[0x91] = [op_res_r,        (2, "RES", "2,C")]
op_map_cbpref[0x92] = [op_res_r,        (2, "RES", "2,D")]
op_map_cbpref[0x93] = [op_res_r,        (2, "RES", "2,E")]
op_map_cbpref[0x94] = [op_res_r,        (2, "RES", "2,H")]
op_map_cbpref[0x95] = [op_res_r,        (2, "RES", "2,L")]
op_map_cbpref[0x96] = [op_res_hlmem,    (2, "RES", "2,(HL)")]
op_map_cbpref[0x9F] = [op_res_r,        (2, "RES", "3,A")]
op_map_cbpref[0x98] = [op_res_r,        (2, "RES", "3,B")]
op_map_cbpref[0x99] = [op_res_r,        (2, "RES", "3,C")]
op_map_cbpref[0x9A] = [op_res_r,        (2, "RES", "3,D")]
op_map_cbpref[0x9B] = [op_res_r,        (2, "RES", "3,E")]
op_map_cbpref[0x9C] = [op_res_r,        (2, "RES", "3,H")]
op_map_cbpref[0x9D] = [op_res_r,        (2, "RES", "3,L")]
op_map_cbpref[0x9E] = [op_res_hlmem,    (2, "RES", "3,(HL)")]
op_map_cbpref[0xA7] = [op_res_r,        (2, "RES", "4,A")]
op_map_cbpref[0xA0] = [op_res_r,        (2, "RES", "4,B")]
op_map_cbpref[0xA1] = [op_res_r,        (2, "RES", "4,C")]
op_map_cbpref[0xA2] = [op_res_r,        (2, "RES", "4,D")]
op_map_cbpref[0xA3] = [op_res_r,        (2, "RES", "4,E")]
op_map_cbpref[0xA4] = [op_res_r,        (2, "RES", "4,H")]
op_map_cbpref[0xA5] = [op_res_r,        (2, "RES", "4,L")]
op_map_cbpref[0xA6] = [op_res_hlmem,    (2, "RES", "4,(HL)")]
op_map_cbpref[0xAF] = [op_res_r,        (2, "RES", "5,A")]
op_map_cbpref[0xA8] = [op_res_r,        (2, "RES", "5,B")]
op_map_cbpref[0xA9] = [op_res_r,        (2, "RES", "5,C")]
op_map_cbpref[0xAA] = [op_res_r,        (2, "RES", "5,D")]
op_map_cbpref[0xAB] = [op_res_r,        (2, "RES", "5,E")]
op_map_cbpref[0xAC] = [op_res_r,        (2, "RES", "5,H")]
op_map_cbpref[0xAD] = [op_res_r,        (2, "RES", "5,L")]
op_map_cbpref[0xAE] = [op_res_hlmem,    (2, "RES", "5,(HL)")]
op_map_cbpref[0xB7] = [op_res_r,        (2, "RES", "6,A")]
op_map_cbpref[0xB0] = [op_res_r,        (2, "RES", "6,B")]
op_map_cbpref[0xB1] = [op_res_r,        (2, "RES", "6,C")]
op_map_cbpref[0xB2] = [op_res_r,        (2, "RES", "6,D")]
op_map_cbpref[0xB3] = [op_res_r,        (2, "RES", "6,E")]
op_map_cbpref[0xB4] = [op_res_r,        (2, "RES", "6,H")]
op_map_cbpref[0xB5] = [op_res_r,        (2, "RES", "6,L")]
op_map_cbpref[0xB6] = [op_res_hlmem,    (2, "RES", "6,(HL)")]
op_map_cbpref[0xBF] = [op_res_r,        (2, "RES", "7,A")]
op_map_cbpref[0xB8] = [op_res_r,        (2, "RES", "7,B")]
op_map_cbpref[0xB9] = [op_res_r,        (2, "RES", "7,C")]
op_map_cbpref[0xBA] = [op_res_r,        (2, "RES", "7,D")]
op_map_cbpref[0xBB] = [op_res_r,        (2, "RES", "7,E")]
op_map_cbpref[0xBC] = [op_res_r,        (2, "RES", "7,H")]
op_map_cbpref[0xBD] = [op_res_r,        (2, "RES", "7,L")]
op_map_cbpref[0xBE] = [op_res_hlmem,    (2, "RES", "7,(HL)")]

for i in range(0, 256):
    if(op_map_nopref[i] == None):
        op_map_nopref[i] = no_operation
    if(op_map_cbpref[i] == None):
        op_map_cbpref[i] = no_operation
        


