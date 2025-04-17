import subprocess
import platform
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates

targets = [
    ("Gateway",   "192.168.10.1"),
    ("Odoo.sh",   "odoo.sh"),
    ("Microsoft", "www.microsoft.com")
]
colors = ["tab:blue", "tab:green", "tab:red"]

SMOOTH_WINDOW = 5
SLIDING_WINDOW = datetime.timedelta(minutes=10)

is_windows = platform.system().lower() == "windows"

datetime_points = []
ping_results = {name: [] for name, _ in targets}

start_time = time.time()
start_dt = datetime.datetime.now()
start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
safe_start = start_str.replace(":", "-").replace(" ", "_")
csv_filename = f"ping_log_{safe_start}.csv"

with open(csv_filename, "w") as f:
    header = "current_datetime,elapsed_time," + ",".join(name for name, _ in targets)
    f.write(header + "\n")


def ping_once(host):
    """Ping the host once, return round-trip time in ms (or np.nan)."""
    cmd = ["ping", "-n", "1", host] if is_windows else ["ping", "-c", "1", host]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout
    if "time=" in out:
        try:
            if is_windows:
                val = out.split("time=")[1].split("ms")[0].strip()
            else:
                val = out.split("time=")[-1].split(" ms")[0]
            return float(val)
        except ValueError:
            return np.nan
    return np.nan


fig, ax = plt.subplots()
fig.subplots_adjust(right=0.75) 

def update(frame):
    now = datetime.datetime.now()
    elapsed = time.time() - start_time
    datetime_points.append(now)

    row = []
    for name, host in targets:
        t = ping_once(host)
        ping_results[name].append(t)
        row.append(f"{t:.2f}")

    with open(csv_filename, "a") as f:
        line = (
            f"{now.strftime('%Y-%m-%d %H:%M:%S')},"
            f"{elapsed:.2f},"
            + ",".join(row)
            + "\n"
        )
        f.write(line)

    ax.clear()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.set_title("Ping Response Times")
    ax.set_xlabel("Time")
    ax.set_ylabel("Response Time (ms)")
    ax.grid(True, linestyle='--', alpha=0.4)

    # plot each series: raw + rolling average
    for (name, _), color in zip(targets, colors):
        data = np.array(ping_results[name])

        ax.plot(
            datetime_points,
            data,
            linewidth=1,
            alpha=0.3,
            color=color,
            marker='o',
            markevery=10
        )

        if len(data) >= SMOOTH_WINDOW:
            smooth = np.convolve(
                data,
                np.ones(SMOOTH_WINDOW) / SMOOTH_WINDOW,
                mode='valid'
            )
            xs = datetime_points[SMOOTH_WINDOW - 1:]
            ax.plot(
                xs,
                smooth,
                linewidth=2.5,
                alpha=0.9,
                label=f"{name} ({SMOOTH_WINDOW}-pt avg)",
                color=color
            )

    if now - start_dt < SLIDING_WINDOW:
        # initial period: show from start_dt forward
        ax.set_xlim(start_dt, start_dt + SLIDING_WINDOW)
    else:
        ax.set_xlim(now - SLIDING_WINDOW, now)

    ax.margins(x=0)

    ax.legend(loc='upper left', fontsize='small')

    summary_lines = [
        f"{name} avg: {np.nanmean(ping_results[name]):.1f} ms"
        for name, _ in targets
    ]
    summary_text = (
        f"Start: {start_str}\n"
        f"Now:   {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        + "\n".join(summary_lines)
    )
    fig.text(
        0.78, 0.5,
        summary_text,
        va='center',
        ha='left',
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    )


def on_key(event):
    if event.key == 'q':
        end_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(csv_filename, "a") as f:
            f.write(f"END,{end_str}\n")
        ani.event_source.stop()
        plt.close(fig)
        print("Stopped by user; log closed.")


fig.canvas.mpl_connect('key_press_event', on_key)
ani = animation.FuncAnimation(fig, update, interval=3000)
plt.show()
