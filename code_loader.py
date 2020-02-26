import mem
import z80
import dlog

instructions = []
code_lines = []

def add_instruction(bytes):
    global instructions, code_lines
    instructions.append(bytes)
    line = z80.op.name(bytes[0]) + "\t" + z80.op.params(bytes[0]) + "\t"
    for i in range(1, len(bytes)):  
        line += "\t" + "0x{0:0{1}X}".format(bytes[i], 2)
    code_lines.append(line)

def load_into_memory(offset):
    global instructions, code_lines
    for instr in instructions:
        for byte in instr:
            mem.write_byte(offset, byte)
            offset += 1            

def print_code_lines():
    global instructions, code_lines
    for i in range(0, len(code_lines)):
        dlog.print_msg(
            "CLD", 
            "Line " + "{0:0{1}X}".format(i, 5) + "\t" + 
            code_lines[i]
        )

