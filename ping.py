import subprocess
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import platform
import time
from datetime import datetime, timedelta
import numpy as np  

target_domain = "bista-maulik-jbc-supply.odoo.com"
is_windows = platform.system().lower() == "windows"

aggregated_ping_results = []      
aggregated_time_points = []       

overall_ping_results = []  

stop_flag = False 

def stop(event):
    global stop_flag
    stop_flag = True

start_time = time.time()
start_time_str = datetime.fromtimestamp(start_time).strftime("%H:%M:%S")

fig, ax = plt.subplots(figsize=(12, 6))
plt.subplots_adjust(bottom=0.30) 
avg_line, = ax.plot([], [], color='red', linestyle='-', linewidth=2, label='Moving Avg')
ax.set_title(f'Ping Response Times to {target_domain}')
ax.set_xlabel('Elapsed Time (s)')
ax.set_ylabel('Response Time (ms)')
ax.grid(True)  
ax.legend(loc='upper right')

summary_text = ax.text(0.02, 0.95, "", transform=ax.transAxes,
                        verticalalignment='top',
                        bbox=dict(facecolor='white', alpha=0.8))

button_ax = plt.axes([0.81, 0.05, 0.15, 0.075])
stop_button = Button(button_ax, 'Stop')
stop_button.on_clicked(stop)

interval_duration = 3     
moving_window_intervals = 1  

while not stop_flag:
    interval_start = time.time()
    interval_pings = [] 
    
    while (time.time() - interval_start) < interval_duration and not stop_flag:
        if is_windows:
            response = subprocess.run(["ping", "-n", "1", target_domain],
                                      capture_output=True, text=True)
        else:
            response = subprocess.run(["ping", "-c", "1", target_domain],
                                      capture_output=True, text=True)
        output = response.stdout
        print(f"Ping output:\n{output}")
        
        success = False
        if "time=" in output:
            try:
                if is_windows:
                    time_value = output.split("time=")[1].split("ms")[0].strip()
                else:
                    time_value = output.split("time=")[-1].split(" ms")[0]
                ping_time = float(time_value)
                interval_pings.append(ping_time)
                overall_ping_results.append(ping_time)
                success = True
            except ValueError:
                print("Error converting ping time.")
        if not success:
            interval_pings.append(np.nan)
            overall_ping_results.append(np.nan)
        time.sleep(1) 

    valid_interval = [p for p in interval_pings if not np.isnan(p)]
    if valid_interval:
        interval_avg = sum(valid_interval) / len(valid_interval)
    else:
        interval_avg = np.nan
        
    aggregated_ping_results.append(interval_avg)
    aggregated_time_points.append(time.time() - start_time)
        
    if len(aggregated_ping_results) >= moving_window_intervals:
        moving_avgs = []
        moving_times = []
        for i in range(len(aggregated_ping_results) - moving_window_intervals + 1):
            window = aggregated_ping_results[i:i+moving_window_intervals]
            window_avg = np.nanmean(window)
            moving_avgs.append(window_avg)
            moving_times.append(aggregated_time_points[i + moving_window_intervals//2])
        avg_line.set_data(moving_times, moving_avgs)
    else:
        avg_line.set_data([], [])
    
    ax.relim()
    ax.autoscale_view()
    
    valid_overall = [p for p in overall_ping_results if not np.isnan(p)]
    if valid_overall:
        overall_avg = sum(valid_overall) / len(valid_overall)
        overall_max = max(valid_overall)
        overall_min = min(valid_overall)
    else:
        overall_avg = overall_max = overall_min = 0.0
    total_intervals = len(aggregated_ping_results)
    success_pct = (len(valid_overall) / (total_intervals * interval_duration)) * 100  
    elapsed_str = str(timedelta(seconds=int(time.time() - start_time)))
    
    summary_text.set_text(
        f"Start Time: {start_time_str}\n"
        f"Elapsed Time: {elapsed_str}\n"
        f"Overall Avg Response: {overall_avg:.1f} ms\n"
        f"Max Response: {overall_max:.1f} ms\n"
        f"Min Response: {overall_min:.1f} ms\n"
        f"Intervals: {total_intervals}\n"
        f"Success Rate: {success_pct:.1f}%"
    )
    
    plt.draw()
    plt.pause(0.1)

plt.show()
