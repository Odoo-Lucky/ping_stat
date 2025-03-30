import subprocess
import matplotlib.pyplot as plt
import platform
import time 

target_domain = "www.google.com" 
ping_count = 0

is_windows = platform.system().lower() == "windows"

ping_results = []

while True:
    ping_count += 1
    
    if is_windows:
        response = subprocess.run(["ping", "-n", "1", target_domain], capture_output=True, text=True)
    else:
        response = subprocess.run(["ping", "-c", "1", target_domain], capture_output=True, text=True)
    
    output = response.stdout
    print(f"Ping output for iteration {ping_count}: {output}") 

    if is_windows:
        if "time=" in output:
            time_value = output.split("time=")[1].split("ms")[0].strip()
            try:
                ping_results.append(float(time_value))
            except ValueError:
                print(f"Error: Could not convert time value for ping {ping_count}")
        else:
            print(f"Error: No time data found for ping {ping_count}")
    else:
        if "time=" in output:
            time_value = output.split("time=")[-1].split(" ms")[0]
            try:
                ping_results.append(float(time_value))
            except ValueError:
                print(f"Error: Could not convert time value for ping {ping_count}")
        else:
            print(f"Error: No time data found for ping {ping_count}")
    
    if ping_count % 10 == 0 and ping_results: 
        plt.clf() 
        plt.plot(ping_results, marker='o')
        plt.title(f'Ping Response Times to {target_domain}')
        plt.xlabel('Ping Count')
        plt.ylabel('Response Time (ms)')
        plt.draw()
        plt.pause(0.1) 
    
    time.sleep(1) 
