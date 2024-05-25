مطمئناً، در اینجا یک فایل README به دو زبان فارسی و انگلیسی برای اسکریپت شما قرار داده شده است:

```markdown
# Server Checker Script

This Python script reads a list of server addresses from a file, checks their availability, and writes the working servers to an output file. It uses the `requests` library to make HTTP requests and `concurrent.futures.ThreadPoolExecutor` to perform these checks concurrently for improved efficiency.

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

1. **Reading Server List from File**: The script reads the list of servers from `servers.txt` and strips any extra whitespace.
2. **Using `ThreadPoolExecutor` to Check Servers Concurrently**: The script uses `ThreadPoolExecutor` to check multiple servers simultaneously, which speeds up the process.
3. **Collecting Working Servers**: The script collects the servers that are working and appends them to the `working_servers` list.
4. **Writing Working Servers to Output File**: Finally, the script writes the working servers to `results.txt`.

## Usage

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

---

# اسکریپت بررسی سرور

این اسکریپت پایتون لیست سرورهای مشخص شده در فایل `servers.txt` را بررسی می‌کند و سرورهای فعال را در فایل `results.txt` ذخیره می‌کند. از کتابخانه `requests` برای ارسال درخواست‌های HTTP و `ThreadPoolExecutor` برای انجام همزمان بررسی‌ها استفاده می‌شود.

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

1. **خواندن لیست سرورها از فایل**: اسکریپت لیست سرورها را از فایل `servers.txt` می‌خواند و فاصله‌های اضافی را حذف می‌کند.
2. **استفاده از `ThreadPoolExecutor` برای بررسی همزمان سرورها**: اسکریپت از `ThreadPoolExecutor` برای بررسی همزمان چندین سرور استفاده می‌کند که فرآیند را سریع‌تر می‌کند.
3. **جمع‌آوری سرورهای کارا**: اسکریپت سرورهای کارا را جمع‌آوری کرده و به لیست `working_servers` اضافه می‌کند.
4. **نوشتن سرورهای کارا به فایل خروجی**: در نهایت، اسکریپت سرورهای کارا را در فایل `results.txt` می‌نویسد.

## استفاده

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
```

این فایل README به کاربران هر دو زبان فارسی و انگلیسی توضیحات لازم برای استفاده از اسکریپت را ارائه می‌دهد.
