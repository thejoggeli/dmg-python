import time

start_time = 0
current_time = 0
last_time = 0
since_start = 0
delta_time = 0

fps = 0
fps_counter = 0
last_fps_time = 0
    
def start():
    global start_time, current_time, last_time, last_fps_time
    start_time = time.time()
    current_time = start_time
    last_time = start_time
    last_fps_time = start_time

def update():
    global current_time, last_time, delta_time, since_start
    global last_fps_time, fps, fps_counter
    
    last_time = current_time
    current_time = time.time()
    delta_time = current_time-last_time
    since_start = current_time-start_time 
    
    fps_counter += 1
    if(current_time-last_fps_time >= 1.0):
        fps = fps_counter
        fps_counter = 0
        last_fps_time = current_time