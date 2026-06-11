# Operating Systems (CSCI 340)
# Summer 2026
# Assignment2 - Process Monitor
# Rayan Nibir
# Used Google Gemini (Disclosure as asked)

import OutputUtil as ou
import time
import psutil
import pandas as pd
import matplotlib.pyplot as plt


def list_processes(sort_by="mem_pct", ascending=False):
    proc_list = []
    for proc in psutil.process_iter():
        try:
            name = proc.name()
            pid = proc.pid
            ppid = proc.ppid()
            status = proc.status()
            username = proc.username()
            mem_pct = round(proc.memory_percent(), 2)
            cpu_time = round(proc.cpu_times()[0], 2)  # [0] extracts user-mode CPU execution time specifically

            proc_list.append([pid, ppid, name, status, username, mem_pct, cpu_time])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignore transient system processes that terminate or restrict read access during iteration
            pass

    columns = ["pid", "ppid", "name", "status", "username", "mem_pct", "cpu_time"]
    df = pd.DataFrame(proc_list, columns=columns)
    return df.sort_values(by=sort_by, ascending=ascending)


def run_process_monitor(interval_in_seconds=5, metric_to_track="mem_pct"):
    print(f"Starting Process Monitor. Refreshing every {interval_in_seconds} seconds...")
    print("Press Ctrl+C in the terminal to stop at any time.\n")

    title_text = "System Process Report"
    instructions_text = "Operating Systems (CSCI 340) <br> Assignment 2 - Process Monitor <br> Run Focus: Memory Percent Utilization"

    headers = ["PID", "PPID", "Process Name", "Status", "User", "Memory %", "CPU Time (s)"]
    types = ["N", "N", "S", "S", "S", "N", "N"]  # N/S maps columns as Numeric or String for sorting script hooks
    alignments = ["c", "c", "l", "c", "l", "r", "r"]  # maps columns to center, left, or right text alignment

    prev_time = time.time()

    try:
        while True:
            curr_time = time.time()

            if curr_time - prev_time >= interval_in_seconds:
                df_procs = list_processes(sort_by=metric_to_track, ascending=False)

                # Convert the Pandas DataFrame subset to a native nested list format required by add_stats
                raw_data_rows = df_procs.head(15).values.tolist()

                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n================= SNAPSHOT: {timestamp} =================")
                print(df_procs.head(15).to_string(index=False))

                # Appends computed stats directly to the bottom of raw_data_rows for columns 5 and 6
                ou.add_stats(raw_data_rows, stat_cols=[5, 6], stat_idx=2, dec=2, bold=True)

                # Packs information into a structural tuple list expected by write_html_file_new
                my_tables_package = [("Top System Resource Consumers", headers, types, alignments, raw_data_rows)]

                ou.write_html_file_new(
                    file_name="Assignment02.html",
                    my_title=title_text,
                    my_instructions=instructions_text,
                    my_tables=my_tables_package,
                    open_file=False,
                    style_file="mystyle.css"
                )

                plot_top_processes(df_procs, metric=metric_to_track, top_n=10)

                print(f"--> Files successfully generated at {timestamp}.\n")
                prev_time = time.time()

            # Prevent high-frequency CPU consumption when idling between intervals
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExecution terminated.")


def plot_top_processes(df, metric="mem_pct", top_n=10):
    # Slice the top 10 items, then invert the order using .iloc[::-1] so highest consumer plots at the top row
    top_chart_data = df.head(top_n).iloc[::-1]
    plt.figure(figsize=(10, 5))

    if metric == "mem_pct":
        plt.barh(top_chart_data["name"], top_chart_data["mem_pct"], color="#8E44AD", edgecolor="#1C2833")
        plt.xlabel("Memory Footprint Percentage (%)")
        plt.title(f"Top {top_n} Active Processes by Memory Allocation")
    else:
        plt.barh(top_chart_data["name"], top_chart_data["cpu_time"], color="#BDC3C7", edgecolor="#1C2833")
        plt.xlabel("Cumulative CPU Time (Seconds)")
        plt.title(f"Top {top_n} Active Processes by Execution Time")

    plt.ylabel("Process Name")
    plt.tight_layout()  # Trims excess whitespace around axis strings to keep process labels readable
    plt.savefig("Assignment02.png")
    plt.close()


def main():
    run_process_monitor(interval_in_seconds=5, metric_to_track="mem_pct")


if __name__ == "__main__":
    main()