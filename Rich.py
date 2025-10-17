import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
from datetime import datetime
import time
import threading
import json
import os
from urllib.parse import urlparse

console = Console()

CONFIG_URL = "https://raw.githubusercontent.com/Scary-technologies/Server-Checker-Script/refs/heads/main/Server.txt"
DEFAULT_PORT = 80
TIMEOUT = 3
MAX_WORKERS = 150
MAX_SHOW = 15
CACHE_FILE = "error_cache.json"

def normalize_server_line(line):
    line = line.strip()
    if not line:
        return None
    if line.startswith("http://") or line.startswith("https://"):
        parsed = urlparse(line)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if host:
            return f"{host}:{port}"
        return None
    if ":" in line:
        host, port = line.split(":", 1)
        host = host.strip()
        port = port.strip()
        if not port.isdigit():
            return None
        return f"{host}:{int(port)}"
    return f"{line}:{DEFAULT_PORT}"

def load_error_cache():
    """بارگذاری لیست سرورهای خطادار از فایل کش"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('error_servers', []))
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load cache: {e}[/yellow]")
    return set()

def save_error_cache(error_servers):
    """ذخیره لیست سرورهای خطادار در فایل کش"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'error_servers': list(error_servers),
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save cache: {e}[/yellow]")

def fetch_server_list():
    try:
        with requests.Session() as s:
            r = s.get(CONFIG_URL, timeout=30)
            r.raise_for_status()
            server_list_url = r.text.strip().splitlines()[0].strip()
            r2 = s.get(server_list_url, timeout=30)
            r2.raise_for_status()
            lines = [normalize_server_line(l) for l in r2.text.splitlines()]
            servers = [srv for srv in lines if srv]
            return servers
    except Exception as e:
        console.print(f"[red]Error fetching server list: {e}[/red]")
        return None

def remove_duplicates(servers):
    """حذف آیتم‌های تکراری و حفظ ترتیب اولین رخداد"""
    seen = set()
    unique = []
    duplicates = []
    
    for srv in servers:
        if srv not in seen:
            seen.add(srv)
            unique.append(srv)
        else:
            duplicates.append(srv)
    
    return unique, duplicates

def check_server(session, server):
    try:
        ip, port = server.split(":")
        url = f"http://{ip}:{port}"
        resp = session.get(url, timeout=TIMEOUT)
        if resp.status_code == 200:
            return server, True, None
        return server, False, f"status {resp.status_code}"
    except requests.RequestException as e:
        return server, False, str(e)
    except Exception as e:
        return server, False, str(e)

def build_layout(active_list, errors_list, skipped_count, progress, total, total_original, duplicates_count):
    info_text = (
        f"Original servers: {total_original}\n"
        f"Duplicates removed: {duplicates_count}\n"
        f"Skipped (cached errors): {skipped_count}\n"
        f"Total to check: {total}\n"
        f"Progress updates in real-time"
    )
    info = Panel(Text(info_text, justify="left"), title="Info", border_style="cyan")
    
    active_text = "\n".join(active_list[-MAX_SHOW:]) if active_list else "[dim]No active servers yet[/dim]"
    if len(active_list) > MAX_SHOW:
        active_text = f"... +{len(active_list)-MAX_SHOW} more\n" + active_text
    active_panel = Panel(Text(active_text, justify="left"), title=f"Active ({len(active_list)})", border_style="green")

    errors_preview = "\n".join(f"{s} -> {e}" for s, e in errors_list[-MAX_SHOW:]) if errors_list else "[dim]No errors yet[/dim]"
    if len(errors_list) > MAX_SHOW:
        errors_preview = f"... +{len(errors_list)-MAX_SHOW} more\n" + errors_preview
    errors_panel = Panel(Text(errors_preview, justify="left"), title=f"New Errors ({len(errors_list)})", border_style="red")

    return Group(info, active_panel, errors_panel, progress)

def main():
    console.clear()
    console.print(Panel.fit("Server Checker — Enhanced with Deduplication & Error Cache", border_style="blue"))

    # بارگذاری کش خطاها
    console.print("[cyan]Loading error cache...[/cyan]")
    error_cache = load_error_cache()
    if error_cache:
        console.print(f"[yellow]Found {len(error_cache)} cached error servers that will be skipped[/yellow]")

    # دریافت لیست سرورها
    console.print("[cyan]Fetching server list...[/cyan]")
    servers = fetch_server_list()
    if servers is None:
        return
    
    total_original = len(servers)
    if total_original == 0:
        console.print("[yellow]No servers to check.[/yellow]")
        return

    # حذف تکراری‌ها
    console.print("[cyan]Removing duplicates...[/cyan]")
    servers, duplicates = remove_duplicates(servers)
    duplicates_count = len(duplicates)
    
    if duplicates_count > 0:
        console.print(f"[yellow]Removed {duplicates_count} duplicate entries[/yellow]")

    # فیلتر کردن سرورهای خطادار قبلی
    servers_to_check = [s for s in servers if s not in error_cache]
    skipped_count = len(servers) - len(servers_to_check)
    
    if skipped_count > 0:
        console.print(f"[yellow]Skipped {skipped_count} servers from error cache[/yellow]")

    total = len(servers_to_check)
    if total == 0:
        console.print("[yellow]All servers are in error cache. Nothing to check.[/yellow]")
        return

    console.print(f"[green]Ready to check {total} servers...[/green]\n")
    time.sleep(1)

    active_servers = []
    new_errors = []
    new_error_set = set()
    lock = threading.Lock()
    start_time = time.time()

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True
    )
    task = progress.add_task("Checking servers...", total=total)

    with requests.Session() as session:
        with Live(build_layout(active_servers, new_errors, skipped_count, progress, total, total_original, duplicates_count), 
                  refresh_per_second=5, console=console) as live:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(check_server, session, s): s for s in servers_to_check}
                for future in as_completed(futures):
                    server = futures[future]
                    try:
                        srv, is_active, err = future.result()
                    except Exception as e:
                        srv, is_active, err = server, False, str(e)
                    
                    with lock:
                        if is_active:
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            active_servers.append(f"{timestamp}  {srv}")
                            console.log(f"[green]+ {srv} is active[/green]")
                        else:
                            new_errors.append((srv, err or "unknown"))
                            new_error_set.add(srv)
                            console.log(f"[red]- {srv} failed: {err}[/red]")
                        
                        progress.advance(task)
                        live.update(build_layout(active_servers, new_errors, skipped_count, progress, total, 
                                                total_original, duplicates_count))

    elapsed = time.time() - start_time

    # به‌روزرسانی کش خطاها
    updated_error_cache = error_cache.union(new_error_set)
    save_error_cache(updated_error_cache)
    console.print(f"[cyan]Updated error cache with {len(new_error_set)} new errors[/cyan]")

    console.print()
    console.print(Panel(
        f"[blue]Original servers: {total_original}[/blue]\n"
        f"[yellow]Duplicates removed: {duplicates_count}[/yellow]\n"
        f"[yellow]Skipped (cached): {skipped_count}[/yellow]\n"
        f"[green]Active servers: {len(active_servers)}[/green]\n"
        f"[red]New errors: {len(new_errors)}[/red]\n"
        f"[blue]Total checked: {total}[/blue]\n"
        f"[yellow]Time taken: {elapsed:.2f} seconds[/yellow]",
        title="[bold]Summary[/bold]",
        border_style="green"
    ))

    if active_servers:
        try:
            with open("results.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(active_servers))
            console.print(f"\n[green]Saved {len(active_servers)} active servers to results.txt[/green]")
        except Exception as e:
            console.print(f"[red]Failed to save results: {e}[/red]")

    console.print()
    console.print(Panel.fit(
        f"[bold green]Done![/bold green]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n"
        f"[yellow]Error cache stored in {CACHE_FILE}[/yellow]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
