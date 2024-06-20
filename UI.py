import requests
import concurrent.futures
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import certifi
# Add your GitHub URLs here
github_urls = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/Scary-technologies/Server-Checker-Script/main/servers.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt"
    # Add more URLs as needed
]

# This will hold the mapping from display text to actual URLs
url_mapping = {}

def fetch_server_info(url):
    response = requests.get(url, verify=certifi.where())
    if response.status_code == 200:
        servers = response.text.splitlines()
        return url.split('/')[-1], len(servers)
    return url.split('/')[-1], 0

def populate_combobox():
    for url in github_urls:
        filename, server_count = fetch_server_info(url)
        display_text = f"{filename} - {server_count} servers"
        url_mapping[display_text] = url
        url_combobox['values'] = list(url_mapping.keys())

def check_server(server):
    try:
        ip, port = server.split(':')
        url = f'http://{ip}:{port}'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return server
    except requests.RequestException:
        return None

def fetch_servers(url):
    response = requests.get(url, verify=certifi.where())
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        return []

def check_servers():
    def thread_function():
        selected_display_text = url_combobox.get()
        selected_url = url_mapping.get(selected_display_text, "")
        if not selected_url:
            return
        
        server_list = fetch_servers(selected_url)
        available_servers = []
        total_servers = len(server_list)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            future_to_server = {executor.submit(check_server, server): server for server in server_list}
            for i, future in enumerate(concurrent.futures.as_completed(future_to_server)):
                result = future.result()
                if result:
                    available_servers.append(result)
                
                def update_progress():
                    progress_bar['value'] = ((i + 1) / total_servers) * 100
                    progress_label.config(text=f"Checked {i + 1} of {total_servers} servers")

                root.after(0, update_progress)

        def update_ui():
            for row in result_table.get_children():
                result_table.delete(row)

            if available_servers:
                status_label.config(text=f"Available servers ({len(available_servers)})", foreground='green')
                for server in available_servers:
                    result_table.insert('', tk.END, values=(server,))
            else:
                status_label.config(text="No available servers found", foreground='red')

            with open("available_servers.txt", "w") as file:
                for server in available_servers:
                    file.write(server + "\n")

        root.after(0, update_ui)

    status_label.config(text="Checking servers...", foreground='black')
    thread = Thread(target=thread_function)
    thread.start()

# Setup GUI
root = tk.Tk()
root.title("Server Checker Pr-M:)")
root.geometry("300x500")
root.resizable(False, False)

frame = ttk.Frame(root, padding="5")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

title_label = ttk.Label(frame, text="Server Checker", font=("Helvetica", 18))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Combobox for GitHub URLs
url_label = ttk.Label(frame, text="Select Server List:", font=("Helvetica", 12))
url_label.grid(row=1, column=0, pady=5)

url_combobox = ttk.Combobox(frame, state="readonly")
url_combobox.grid(row=1, column=1, pady=5)

check_button = ttk.Button(frame, text="Check Servers", command=check_servers)
check_button.grid(row=2, column=0, columnspan=2, pady=10)

status_label = ttk.Label(frame, text="", font=("Helvetica", 12))
status_label.grid(row=3, column=0, columnspan=2, pady=10)

progress_bar = ttk.Progressbar(frame, orient='horizontal', mode='determinate', length=280)
progress_bar.grid(row=4, column=0, columnspan=2, pady=10)

progress_label = ttk.Label(frame, text="Progress: 0%", font=("Helvetica", 10))
progress_label.grid(row=5, column=0, columnspan=2, pady=10)

columns = ("Server",)
result_table = ttk.Treeview(frame, columns=columns, show="headings")
result_table.heading("Server", text="Available Servers")
result_table.grid(row=6, column=0, columnspan=2, pady=10)

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=result_table.yview)
result_table.configure(yscroll=scrollbar.set)
scrollbar.grid(row=6, column=2, sticky=(tk.N, tk.S))

# Populate the combobox with URLs
populate_combobox()

root.mainloop()
