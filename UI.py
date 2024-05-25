import requests
import concurrent.futures
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

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
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        return []

def check_servers():
    def thread_function():
        server_list = fetch_servers(server_list_url)
        available_servers = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            future_to_server = {executor.submit(check_server, server): server for server in server_list}
            for future in concurrent.futures.as_completed(future_to_server):
                result = future.result()
                if result:
                    available_servers.append(result)

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
root.title("Server Checker")
root.geometry("220x400")
root.resizable(False, False)

server_list_url = "https://raw.githubusercontent.com/Scary-technologies/Server-Checker-Script/main/servers.txt"

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

title_label = ttk.Label(frame, text="Server Checker", font=("Helvetica", 18))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

check_button = ttk.Button(frame, text="Check Servers", command=check_servers)
check_button.grid(row=1, column=0, columnspan=2, pady=10)

status_label = ttk.Label(frame, text="", font=("Helvetica", 12))
status_label.grid(row=2, column=0, columnspan=2, pady=10)

columns = ("Server",)
result_table = ttk.Treeview(frame, columns=columns, show="headings")
result_table.heading("Server", text="Available Servers")
result_table.grid(row=3, column=0, columnspan=2, pady=10)

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=result_table.yview)
result_table.configure(yscroll=scrollbar.set)
scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))

root.mainloop()
