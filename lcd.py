import z80
import dlog

class State:
    enabled = 1
    cycle_count = 0
state = State()

def init():
    pass

def update():
    state.cycle_count += z80.state.cycles_delta
    if(dlog.enable.lcd):
        print_state()
    
def print_state():
    dlog.print_msg(
        "LCD", 
        "lcdisplay" + "\t" +
        "Enabled=" + str(state.enabled) + "\t" + 
        "Cycles=" + str(state.cycle_count)
    )