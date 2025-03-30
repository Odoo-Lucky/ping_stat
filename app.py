from flask import Flask, render_template, jsonify, request
import threading
import subprocess
import platform
import time
import datetime
import numpy as np

app = Flask(__name__)

target_domain = "bista-maulik-jbc-supply.odoo.com"
is_windows = platform.system().lower() == "windows"

aggregated_ping_results = []      
aggregated_time_points = []       
overall_ping_results = []  
start_time = time.time()
start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%H:%M:%S")
stop_flag = False 

interval_duration = 3    
moving_window_intervals = 3 

def ping_loop():
    global stop_flag, aggregated_ping_results, aggregated_time_points, overall_ping_results, start_time
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
                    pass
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
        aggregated_time_points.append(int(time.time() - start_time))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    if overall_ping_results:
        overall_avg = np.nanmean(overall_ping_results)
        overall_max = np.nanmax(overall_ping_results)
        overall_min = np.nanmin(overall_ping_results)
    else:
        overall_avg = overall_max = overall_min = 0.0

    data = {
        "time_points": aggregated_time_points,
        "ping_results": aggregated_ping_results,
        "overall_avg": overall_avg,
        "overall_max": overall_max,
        "overall_min": overall_min,
        "start_time": start_time_str,
        "elapsed": int(time.time() - start_time)
    }
    return jsonify(data)

@app.route("/stop", methods=["POST"])
def stop():
    global stop_flag
    stop_flag = True
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    threading.Thread(target=ping_loop, daemon=True).start()
    app.run(debug=True)
