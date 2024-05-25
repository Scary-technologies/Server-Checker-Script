# اسکریپت بررسی سرور

این اسکریپت پایتون، یک لیست از آدرس‌های سرور را از یک فایل می‌خواند، دسترسی‌پذیری آن‌ها را بررسی می‌کند و سرورهای کارا را در یک فایل خروجی می‌نویسد. این اسکریپت از کتابخانه `requests` برای ارسال درخواست‌های HTTP و `concurrent.futures.ThreadPoolExecutor` برای انجام این بررسی‌ها به صورت همزمان استفاده می‌کند.

## نیازمندی‌ها

- پایتون 3.x
- کتابخانه `requests`

می‌توانید کتابخانه `requests` را با استفاده از pip نصب کنید:

```sh
pip install requests
```

## فایل‌ها

- `servers.txt`: فایلی که لیست سرورها را برای بررسی در خود دارد. هر خط باید به فرم `ip:port` باشد.
- `results.txt`: فایل خروجی که سرورهای کارا در آن نوشته می‌شوند.

## توضیح اسکریپت

### 1. وارد کردن کتابخانه‌ها

اسکریپت با وارد کردن کتابخانه‌های لازم شروع می‌شود:

```python
import requests
from concurrent.futures import ThreadPoolExecutor
```

### 2. تعریف تابع `check_server`

تابع `check_server` یک آدرس سرور را می‌گیرد، آن را به آی‌پی و پورت تقسیم می‌کند، URL را می‌سازد و سعی می‌کند یک درخواست HTTP GET به سرور ارسال کند. اگر سرور با کد وضعیت 200 پاسخ دهد، آن سرور به عنوان سرور کارا در نظر گرفته می‌شود:

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

### 3. خواندن لیست سرورها از فایل

اسکریپت لیست سرورها را از فایل `servers.txt` می‌خواند و فاصله‌های اضافی را حذف می‌کند:

```python
with open('servers.txt', 'r') as file:
    servers = file.readlines()

servers = [server.strip() for server in servers]
```

### 4. استفاده از `ThreadPoolExecutor` برای بررسی همزمان سرورها

اسکریپت از `ThreadPoolExecutor` برای بررسی همزمان چندین سرور استفاده می‌کند که فرآیند را سریع‌تر می‌کند:

```python
working_servers = []

with ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_server, servers)
```

### 5. جمع‌آوری سرورهای کارا

اسکریپت سرورهای کارا را جمع‌آوری کرده و به لیست `working_servers` اضافه می‌کند:

```python
for result in results:
    if result:
        working_servers.append(result)
```

### 6. نوشتن سرورهای کارا به فایل خروجی

در نهایت، اسکریپت سرورهای کارا را در فایل `results.txt` می‌نویسد:

```python
with open('results.txt', 'w') as file:
    for server in working_servers:
        file.write(server + '\n')

print("Finished checking servers. Results saved to results.txt.")
```

## اجرای اسکریپت

1. فایل `servers.txt` خود را با لیست سرورها به فرم `ip:port` آماده کنید، هر سرور در یک خط.
2. اسکریپت را اجرا کنید:

```sh
python check_servers.py
```

اسکریپت هر سرور را بررسی کرده و سرورهای کارا را در `results.txt` ذخیره می‌کند.

## مثال `servers.txt`

```
192.168.1.1:8080
192.168.1.2:8080
192.168.1.3:8080
```

این اسکریپت برای بررسی دسترسی‌پذیری یک لیست از سرورها به سرعت و کارایی بالا مفید است.
