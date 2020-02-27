import mem
import z80
import dlog

instructions = []

def add_instruction(bytes):
    global instructions, code_lines
    instructions.append(bytes)

def load_into_memory(offset):
    global instructions, code_lines
    for instr in instructions:
        for byte in instr:
            mem.write_byte(offset, byte)
            offset += 1            

def print_code_lines():
    global instructions, code_lines    
    for i in range(0, len(instructions)):
        bytes = instructions[i]
        dlog.print_msg(
            "CLD", 
            "Line " + "{0:0{1}X}".format(i, 5) + "\t" + 
            z80.op.bytes_to_str(bytes)
        )

