

EVENT_SCANLINE_CHANGE = 0
EVENT_VIDEORAM_CHANGE = 1
EVENT_SPRITEMEM_CHANGE = 2

class Glob:
    map = {}
glob = Glob()

def subscribe(event, function):
    if event not in glob.map:
        glob.map[event] = []
    glob.map[event].append(function)

def unsubscribe(event, object, function):
    if event in glob.map:
        glob.map[event].remove(function)

def fire(event, data):
    if event in glob.map:
        functions = glob.map[event]
        for function in functions:
            function(data)
