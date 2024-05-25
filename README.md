# Server Checker Script

This Python script reads a list of server addresses from a file, checks their availability, and writes the working servers to an output file. It utilizes the `requests` library to make HTTP requests and `concurrent.futures.ThreadPoolExecutor` to perform these checks concurrently for improved efficiency.

## Requirements

- Python 3.x
- `requests` library

You can install the `requests` library using pip:

```sh
pip install requests
```

## Files

- `servers.txt`: A file containing the list of servers to check. Each line should be in the format `ip:port`.
- `results.txt`: The output file where the working servers will be written.

## Script Explanation

### 1. Importing Libraries

The script starts by importing the necessary libraries:

```python
import requests
from concurrent.futures import ThreadPoolExecutor
```

### 2. Defining the `check_server` Function

The `check_server` function takes a server address, splits it into IP and port, constructs the URL, and tries to send an HTTP GET request to the server. If the server responds with status code 200, it considers the server as working:

```python
def check_server(server):
    ip, port = server.split(':')
    url = f"http://{ip}:{port}"
    print(f'Checking Proxy {ip} : {port}....\n')
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            print(ip, port, ' Done ')
            return server
    except requests.exceptions.RequestException:
        return None
    return None
```

### 3. Reading Server List from File

The script reads the list of servers from `servers.txt` and strips any extra whitespace:

```python
with open('servers.txt', 'r') as file:
    servers = file.readlines()

servers = [server.strip() for server in servers]
```

### 4. Using `ThreadPoolExecutor` to Check Servers Concurrently

The script uses `ThreadPoolExecutor` to check multiple servers simultaneously, which speeds up the process:

```python
working_servers = []

with ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_server, servers)
```

### 5. Collecting Working Servers

The script collects the servers that are working and appends them to the `working_servers` list:

```python
for result in results:
    if result:
        working_servers.append(result)
```

### 6. Writing Working Servers to Output File

Finally, the script writes the working servers to `results.txt`:

```python
with open('results.txt', 'w') as file:
    for server in working_servers:
        file.write(server + '\n')

print("Finished checking servers. Results saved to results.txt.")
```

## Running the Script

1. Prepare your `servers.txt` file with a list of servers in the format `ip:port`, each on a new line.
2. Run the script:

```sh
python check_servers.py
```

The script will check each server and save the working servers to `results.txt`.

## Example `servers.txt`

```
192.168.1.1:8080
192.168.1.2:8080
192.168.1.3:8080
```

This script is useful for checking the availability of a list of servers quickly and efficiently.
