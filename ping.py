import subprocess
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import platform
import time
from datetime import datetime, timedelta
import numpy as np  

target_domain = "https://bista-maulik-jbc-supply.odoo.com/"
ping_count = 0
is_windows = platform.system().lower() == "windows"
ping_results = []      
time_points = []       
stop_flag = False 
failed_pings = 0      

def stop(event):
    global stop_flag
    stop_flag = True

start_time = time.time()
start_time_str = datetime.fromtimestamp(start_time).strftime("%H:%M:%S")

fig, ax = plt.subplots(figsize=(12, 6))
plt.subplots_adjust(bottom=0.30) 
line, = ax.plot([], [], marker='o', linestyle='-', linewidth=2, markersize=6)
ax.set_title(f'Ping Response Times to {target_domain}')
ax.set_xlabel('Elapsed Time')
ax.set_ylabel('Response Time (ms)')
ax.grid(True)  

summary_text = ax.text(0.02, 0.95, "", transform=ax.transAxes,
                        verticalalignment='top',
                        bbox=dict(facecolor='white', alpha=0.8))

button_ax = plt.axes([0.81, 0.05, 0.15, 0.075])
stop_button = Button(button_ax, 'Stop')
stop_button.on_clicked(stop)

max_points = 100

while not stop_flag:
    ping_count += 1
    current_time = time.time()
    elapsed = current_time - start_time

    if is_windows:
        response = subprocess.run(["ping", "-n", "1", target_domain],
                                  capture_output=True, text=True)
    else:
        response = subprocess.run(["ping", "-c", "1", target_domain],
                                  capture_output=True, text=True)
    
    output = response.stdout
    print(f"Ping output for iteration {ping_count}:\n{output}")
    
    success = False
    if "time=" in output:
        try:
            if is_windows:
                time_value = output.split("time=")[1].split("ms")[0].strip()
            else:
                time_value = output.split("time=")[-1].split(" ms")[0]
            ping_time = float(time_value)
            ping_results.append(ping_time)
            success = True
        except ValueError:
            print(f"Error: Could not convert time value for ping {ping_count}")
    else:
        print(f"Error: No time data found for ping {ping_count}")
    
    if not success:
        failed_pings += 1
        ping_results.append(np.nan)
    
    time_points.append(elapsed)
    
    display_time = time_points[-max_points:]
    display_pings = ping_results[-max_points:]
    
    line.set_data(display_time, display_pings)
    ax.relim()
    ax.autoscale_view()

    valid_pings = [p for p in ping_results if not np.isnan(p)]
    if valid_pings:
        avg_time = sum(valid_pings) / len(valid_pings)
        max_time = max(valid_pings)
        min_time = min(valid_pings)
    else:
        avg_time = max_time = min_time = 0.0

    success_pct = (len(valid_pings) / ping_count) * 100

    elapsed_str = str(timedelta(seconds=int(elapsed)))
    
    summary_text.set_text(
        f"Start Time: {start_time_str}\n"
        f"Elapsed Time: {elapsed_str}\n"
        f"Avg Response: {avg_time:.1f} ms\n"
        f"Max Response: {max_time:.1f} ms\n"
        f"Min Response: {min_time:.1f} ms\n"
        f"Success Rate: {success_pct:.1f}%"
    )
    
    plt.draw()
    plt.pause(0.1)
    time.sleep(1)

plt.show()
