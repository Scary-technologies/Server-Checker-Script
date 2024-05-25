import requests
from concurrent.futures import ThreadPoolExecutor

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

# خواندن لیست سرورها از فایل
with open('servers.txt', 'r') as file:
    servers = file.readlines()

# پاک کردن فاصله‌های اضافی
servers = [server.strip() for server in servers]

# استفاده از ThreadPoolExecutor برای بررسی همزمان سرورها
working_servers = []

with ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_server, servers)

# جمع‌آوری سرورهای کارا
for result in results:
    if result:
        working_servers.append(result)

# نوشتن سرورهای کارا به فایل نتایج
with open('results.txt', 'w') as file:
    for server in working_servers:
        file.write(server + '\n')

print("Finished checking servers. Results saved to results.txt.")
