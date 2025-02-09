import sys
import time
import threading
import itertools
import os
import platform
import shutil
from contextlib import contextmanager
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
import humanize
from termcolor import colored

class LoadingAnimation:
    def __init__(self, desc="Loading...", color="cyan"):
        self.desc = desc
        self.color = color
        self.done = False
        self.thread = None

    def animate(self):
        for c in itertools.cycle(['⢿', '⣻', '⣽', '⣾', '⣷', '⣯', '⣟', '⡿']):
            if self.done:
                break
            sys.stdout.write(f'\r{colored(self.desc, self.color)} {c}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(self.desc) + 2) + '\r')

    def start(self):
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        self.done = True
        if self.thread is not None:
            self.thread.join()

class ProgressBar:
    def __init__(self, total, prefix='Progress:', suffix='Complete', decimals=1, length=50, fill='█', color='cyan'):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.color = color

    def update(self, iteration):
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (iteration / float(self.total)))
        filled_length = int(self.length * iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        print(f'\r{self.prefix} |{colored(bar, self.color)}| {percent}% {self.suffix}', end='\r')
        if iteration == self.total:
            print()

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header(text, color="yellow", width=50):
    print(colored("=" * width, color))
    print(colored(text.center(width), color))
    print(colored("=" * width, color))

def input_with_prompt(prompt, color="cyan"):
    return input(colored(f"{prompt}: ", color))

def print_table(headers, data, color="cyan"):
    """Print formatted table with data"""
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Print headers
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(colored(header_line, color))
    print(colored("-" * len(header_line), color))

    # Print data
    for row in data:
        row_str = " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths))
        print(colored(row_str, "white"))

def format_bytes(bytes):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024

def setup_terminal():
    """Setup terminal for both Windows and Linux"""
    if platform.system() == 'Windows':
        try:
            import colorama
            colorama.init()
        except ImportError:
            pass
    # For Linux, no special setup needed as ANSI colors are supported by default

def get_terminal_size():
    """Get terminal size in a cross-platform way"""
    return shutil.get_terminal_size()

@contextmanager
def create_spinner(message):
    """Create a spinner with the given message"""
    console = Console()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description=message, total=None)
        yield progress
        progress.update(task, completed=True)

@contextmanager
def create_progress_bar():
    """Create a progress bar"""
    console = Console()
    with Progress(console=console) as progress:
        yield progress

def format_table_rich(headers, rows, style="default"):
    """Format data as a table"""
    from rich.table import Table
    table = Table(show_header=True, header_style="bold blue")
    
    for header in headers:
        table.add_column(header)
    
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    
    return table

def format_size(size_bytes):
    """Format size in bytes to human readable format"""
    return humanize.naturalsize(size_bytes)

def format_time(seconds):
    """Format time in seconds to human readable format"""
    return humanize.naturaldelta(seconds)

def is_root():
    """Check if the script is running with root/admin privileges"""
    if platform.system() == 'Windows':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:
        return os.geteuid() == 0  # For Linux/Unix

def get_config_dir():
    """Get the appropriate config directory for the platform"""
    if platform.system() == 'Windows':
        return os.path.join(os.getenv('APPDATA'), 'NetTrackr')
    else:
        return os.path.join(os.path.expanduser('~'), '.config', 'nettrackr')

def get_data_dir():
    """Get the appropriate data directory for the platform"""
    if platform.system() == 'Windows':
        return os.path.join(os.getenv('LOCALAPPDATA'), 'NetTrackr')
    else:
        return os.path.join(os.path.expanduser('~'), '.local', 'share', 'nettrackr')

def get_cache_dir():
    """Get the appropriate cache directory for the platform"""
    if platform.system() == 'Windows':
        return os.path.join(os.getenv('LOCALAPPDATA'), 'NetTrackr', 'Cache')
    else:
        return os.path.join(os.path.expanduser('~'), '.cache', 'nettrackr')
