import subprocess
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import platform
import time
from datetime import datetime

target_domain = "www.google.com"
ping_count = 0
is_windows = platform.system().lower() == "windows"
ping_results = []
stop_flag = False 

def stop(event):
    global stop_flag
    stop_flag = True

start_time = time.time()
start_time_str = datetime.fromtimestamp(start_time).strftime("%H:%M:%S")

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25) 
line, = ax.plot([], [], marker='o')
ax.set_title(f'Ping Response Times to {target_domain}')
ax.set_xlabel('Ping Count')
ax.set_ylabel('Response Time (ms)')

timer_text = ax.text(0.02, 0.95, f"Start Time: {start_time_str}\nElapsed Time: 0.0 s",
                     transform=ax.transAxes, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

button_ax = plt.axes([0.81, 0.05, 0.1, 0.075])
stop_button = Button(button_ax, 'Stop')
stop_button.on_clicked(stop)

while not stop_flag:
    ping_count += 1
    
    if is_windows:
        response = subprocess.run(["ping", "-n", "1", target_domain], capture_output=True, text=True)
    else:
        response = subprocess.run(["ping", "-c", "1", target_domain], capture_output=True, text=True)
    
    output = response.stdout
    print(f"Ping output for iteration {ping_count}:\n{output}")
    
    if "time=" in output:
        try:
            if is_windows:
                time_value = output.split("time=")[1].split("ms")[0].strip()
            else:
                time_value = output.split("time=")[-1].split(" ms")[0]
            ping_results.append(float(time_value))
        except ValueError:
            print(f"Error: Could not convert time value for ping {ping_count}")
    else:
        print(f"Error: No time data found for ping {ping_count}")
    
    line.set_data(range(len(ping_results)), ping_results)
    ax.relim()          
    ax.autoscale_view() 
    
    elapsed = time.time() - start_time
    timer_text.set_text(f"Start Time: {start_time_str}\nElapsed Time: {elapsed:.1f} s")
    
    plt.draw()
    plt.pause(0.1)     
    time.sleep(1)       
    
plt.show()
