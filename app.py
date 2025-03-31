import subprocess
import platform
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates

target_domain = "bista-maulik-jbc-supply.odoo.com"
is_windows = platform.system().lower() == "windows"

datetime_points = [] 
ping_results = []

start_time = time.time()
start_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
safe_start_str = start_time_str.replace(":", "-").replace(" ", "_")
csv_filename = f"ping_log_{safe_start_str}.csv"

log_file = open(csv_filename, "w")
log_file.write("current_datetime,elapsed_time,ping_time\n")

def ping_once():
    if is_windows:
        cmd = ["ping", "-n", "1", target_domain]
    else:
        cmd = ["ping", "-c", "1", target_domain]
    response = subprocess.run(cmd, capture_output=True, text=True)
    output = response.stdout
    if "time=" in output:
        try:
            if is_windows:
                time_value = output.split("time=")[1].split("ms")[0].strip()
            else:
                time_value = output.split("time=")[-1].split(" ms")[0]
            return float(time_value)
        except ValueError:
            return np.nan
    return np.nan

def update(frame):
    global log_file
    current_elapsed = time.time() - start_time
    current_datetime = datetime.datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    ping_time = ping_once()
    datetime_points.append(current_datetime)  
    ping_results.append(ping_time)
    
    log_file.write(f"{current_datetime_str},{current_elapsed:.2f},{ping_time}\n")
    log_file.flush()
    
    ax.clear()
    ax.plot(datetime_points, ping_results, marker="o")
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()
    
    ax.set_title("Ping Response Times")
    ax.set_xlabel("Date & Time")
    ax.set_ylabel("Response Time (ms)")
    
    valid_pings = [x for x in ping_results if not np.isnan(x)]
    if valid_pings:
        overall_avg = np.mean(valid_pings)
        highest = max(valid_pings)
        lowest = min(valid_pings)
    else:
        overall_avg = highest = lowest = np.nan
    
    summary_text = (f"Start Time: {start_time_str}\n"
                    f"Current Time: {current_datetime_str}\n"
                    f"Avg: {overall_avg:.1f} ms\n"
                    f"High: {highest:.1f} ms\n"
                    f"Low: {lowest:.1f} ms")
    ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, verticalalignment='top')

def on_key(event):
    global log_file
    if event.key == 'q':
        end_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"END,{end_time_str}\n")
        log_file.close()
        ani.event_source.stop()
        print("Animation stopped by user. Log file closed.")

fig, ax = plt.subplots()
fig.canvas.mpl_connect('key_press_event', on_key)
ani = animation.FuncAnimation(fig, update, interval=3000)
plt.show()
