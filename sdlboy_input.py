import sdl2
import sdlboy_console

class Keys:
    is_down = {}
    on_down = {}
    on_up   = {}
keys = Keys()

def init():
    pass

def handle_key_down(event):
    key = event.key.keysym.sym
    keys.on_up  [key] = False
    keys.on_down[key] = True
    keys.is_down[key] = True
    #print("Key pressed: " + str(key))
    
def handle_key_up(event):
    key = event.key.keysym.sym
    keys.on_up  [key] = True
    keys.on_down[key] = False
    keys.is_down[key] = False

def clear_on_keys():
    for i in keys.on_down:        
        keys.on_down[i] = False
    for i in keys.on_up:        
        keys.on_up[i] = False    

def is_key_down(key):  
    if(key not in keys.is_down):
        return False
    return keys.is_down[key]

def on_key_down(key):
    if(key not in keys.on_down):
        return False
    return keys.on_down[key]

def on_key_up(key):
    if(key not in keys.on_up):
        return False
    return keys.on_up[key]


    
    


