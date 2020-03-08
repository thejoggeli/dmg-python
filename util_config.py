import json

config = None
enable_log = False

def load():
    global config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            if(enable_log):
                print_all()
                print("[CFG] loaded")
    except Exception as e:
        if(enable_log):
            print("[CFG] load failed")
            print(e)
    if(config == None):
        config = {}

def get(key, defval):
    if key in config:
        return config[key]
    return defval

def set(key, val):
    if(config != None):
        config[key] = val
        if(enable_log):
            print("[CFG] " +str(key)+"="+str(val))

def save():
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4)
            if(enable_log):
                print("[CFG] saved")
    except Exception as e:
        if(enable_log):
            print("[CFG] tsave failed")
            print(e)
            
def print_all():
    for key in config:
        print("[CFG] " + key + "=" + str(config[key]))