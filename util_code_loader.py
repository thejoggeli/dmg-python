import hw_mem as mem
import hw_z80 as z80
import util_dlog as dlog
    
def load_binary_file(file):
    bytes = None
    with open(file, "rb") as fh:    
        bytes = bytearray(fh.read())
    return bytes

def load_into_memory(bytes, offset=0):
    for byte in bytes:
        mem.write_byte(offset, byte)
        offset += 1

def print_code(bytes, start_index=None, end_index=None):
    if(start_index == None):
        start_index = 0
    if(end_index == None):
        end_index = len(bytes)
    i = start_index
    line = 0
    while(i < end_index):  
        
        prefix = 0x00
        opcode = 0x00        
        params_offset = 1
        
        if(z80.op.is_prefix(bytes[i])):
            prefix = bytes[i]
            opcode = bytes[i+1]
            params_offset = 2
        else:
            prefix = 0x00
            opcode = bytes[i]
            
        info = z80.op.get_opcode_info(prefix, opcode)
        size = info[z80.OPCODE_INFO_SIZE]
        
        msg = ""
        msg += "{0:0{1}d}".format(line, 4) + ":" + "0x{0:0{1}X}".format(i,4) + ":" + str(size) + "\t"
        msg += "0x{0:0{1}X}".format(prefix, 2) + "{0:0{1}X}".format(opcode, 2) + "\t"
        msg += info[z80.OPCODE_INFO_NAME] + "\t"
        msg += info[z80.OPCODE_INFO_PARAMS]
        
        for j in range(i+params_offset, i+size):
            msg += "\t" + "0x{0:0{1}X}".format(bytes[j], 2)
        
        dlog.print_msg("CLD", msg)
        
        i += size
        line += 1
        
        
def decode_instruction_to_string(addr, with_addr=True, insert_params=True, justify=True):
    prefix = 0x00
    opcode = 0x00        
    params_offset = 1
    
    if(z80.op.is_prefix(mem.read_byte_silent(addr))):
        prefix = mem.read_byte_silent(addr)
        opcode = mem.read_byte_silent(addr+1)
        params_offset = 2
    else:
        prefix = 0x00
        opcode = mem.read_byte_silent(addr)
        
    info = z80.op.get_opcode_info(prefix, opcode)
    size = info[z80.OPCODE_INFO_SIZE]
    
    msg = ""
    if(with_addr):
        msg += "0x{0:0{1}X}".format(addr,4) + ": "
    if(justify):
        msg += info[z80.OPCODE_INFO_NAME].ljust(5)
    else:
        msg += info[z80.OPCODE_INFO_NAME] + " "
    
    if(insert_params):
        params = info[z80.OPCODE_INFO_PARAMS]        
        if(params.find("nn") != -1):
            word = mem.read_word_silent(addr+params_offset)
            word_str = "0x{0:0{1}X}".format(word,4)
            params = params.replace("nn", word_str)
        elif(params.find("n") != -1):
            byte = mem.read_byte_silent(addr+params_offset)
            byte_str = "0x{0:0{1}X}".format(byte,2)
            params = params.replace("n", byte_str)
        msg += params    
    else:
        msg += info[z80.OPCODE_INFO_PARAMS]
        for j in range(addr+params_offset, addr+size):
            msg += " " + "0x{0:0{1}X}".format(mem.read_byte_silent(j), 2)
    
    return msg
