import requests
import json
import time
import random
from setproctitle import setproctitle
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse  # For decoding the URL-encoded initData

url = "https://notpx.app/api/v1"

# ACTIVITY
WAIT = 180 * 3
DELAY = 1

# IMAGE
WIDTH = 1000
HEIGHT = 1000
MAX_HEIGHT = 50

# Initialize colorama for colored output
init(autoreset=True)

setproctitle("notpixel")

# Definisikan self.colors untuk warna-warna yang digunakan saat pengecatan
self_colors = [
    "#3690ea", "#e46e6e", "#ffffff", "#be0039", "#6d001a",
    "#ffd635", "#ff9600", "#bf4300", "#7eed56", "#00cc78", "#00a368"
]

# Definisikan self.block untuk area blok piksel yang akan dicat
def ci(x, y):
    return (y * 1000) + x

self_block = {
    "#3690EA": [
        [ci(448, 595), ci(470, 595)], [ci(448, 594), ci(470, 594)], [ci(448, 593), ci(470, 593)],
        [ci(448, 592), ci(470, 592)], [ci(448, 591), ci(470, 591)], [ci(448, 590), ci(470, 590)],
        [ci(448, 589), ci(470, 589)], [ci(448, 588), ci(470, 588)], [ci(448, 587), ci(470, 587)],
        [ci(448, 586), ci(470, 586)], [ci(448, 585), ci(470, 585)], [ci(448, 584), ci(470, 584)],
        [ci(448, 583), ci(470, 583)], [ci(448, 582), ci(470, 582)], [ci(448, 581), ci(470, 581)],
        [ci(532, 593), ci(595, 593)], [ci(532, 592), ci(595, 592)], [ci(532, 591), ci(595, 591)],
        [ci(532, 590), ci(595, 590)], [ci(532, 589), ci(595, 589)], [ci(532, 588), ci(595, 588)],
        [ci(532, 587), ci(595, 587)], [ci(532, 586), ci(595, 586)], [ci(532, 585), ci(595, 585)],
        [ci(532, 584), ci(595, 584)], [ci(532, 583), ci(595, 583)], [ci(532, 582), ci(595, 582)],
        [ci(532, 581), ci(595, 581)], [ci(532, 580), ci(595, 580)], [ci(532, 579), ci(595, 579)],
        [ci(532, 578), ci(595, 578)], [ci(532, 577), ci(595, 577)], [ci(532, 576), ci(595, 576)],
        [ci(532, 575), ci(595, 575)], [ci(532, 574), ci(595, 574)], [ci(532, 573), ci(595, 573)],
        [ci(532, 572), ci(595, 572)], [ci(532, 571), ci(595, 571)]
    ]
}

# Function to log messages with timestamp in light grey color
def log_message(message, color=Style.RESET_ALL):
    current_time = datetime.now().strftime("[%H:%M:%S]")
    print(f"{Fore.LIGHTBLACK_EX}{current_time}{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")

# Function to initialize a requests session with retry logic
def get_session_with_retries(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Create a session with retry logic
session = get_session_with_retries()

# Function to get the color of a pixel from the server
def get_color(pixel, header):
    try:
        response = session.get(f"{url}/image/get/{str(pixel)}", headers=header, timeout=10)
        if response.status_code == 401:
            return -1
        return response.json()['pixel']['color']
    except KeyError:
        return "#000000"
    except requests.exceptions.Timeout:
        log_message("Request timed out", Fore.RED)
        return "#000000"
    except requests.exceptions.ConnectionError as e:
        log_message(f"Connection error: {e}", Fore.RED)
        return "#000000"
    except requests.exceptions.RequestException as e:
        log_message(f"Request failed: {e}", Fore.RED)
        return "#000000"

# Function to claim resources from the server
def claim(header):
    log_message("BOT LAGI NGEGAMBAR", Fore.CYAN)
    try:
        session.get(f"{url}/mining/claim", headers=header, timeout=10)
    except requests.exceptions.RequestException as e:
        log_message(f"GAGAL COK: {e}", Fore.RED)

# Function to calculate pixel index based on x, y position
def get_pixel(x, y):
    return y * 1000 + x + 1

# Function to get x, y position from pixel index
def get_pos(pixel, size_x):
    return pixel % size_x, pixel // size_x

# Function to get pixel index based on canvas position
def get_canvas_pos(x, y):
    return get_pixel(start_x + x - 1, start_y + y - 1)

# Starting coordinates
start_x = 920
start_y = 386

# Main function to perform the painting process
def main(auth, account):
    headers = {'authorization': auth}

    try:
        # Claim resources dan ambil balance awal
        claim(headers)
        response = session.get(f"{url}/mining/status", headers=headers, timeout=10)
        balance = response.json().get("userBalance", 0)  # Balance awal
        log_message(f"balance: {balance:.2f}", Fore.CYAN)

        # Inisialisasi total poin
        total_points = 0

        # Mengecat setiap piksel di blok yang sudah didefinisikan
        for color, blocks in self_block.items():
            for block in blocks:
                time.sleep(0.05 + random.uniform(0.01, 0.1))
                try:
                    # Mengambil ID pixel dan menghubungkan dengan warna yang benar
                    pixel_id = block[0]
                    new_color = color  # Menggunakan warna dari self_block
                    data = {"pixelId": pixel_id, "newColor": new_color}
                    
                    # Melakukan request pengecatan
                    response = session.post(f"{url}/repaint/start", json=data, headers=headers, timeout=10)
                    
                    # Periksa status response
                    if response.status_code == 400:
                        log_message("Abis bensin", Fore.RED)
                        break
                    if response.status_code == 401:
                        log_message("Unauthorized", Fore.RED)
                        break

                    # Hitung poin yang didapat dari pengecatan
                    new_balance = response.json().get("balance", 0)
                    inc = new_balance - balance  # Poin yang didapat dari pengecatan ini
                    balance = new_balance  # Update balance

                    # Hanya tampilkan poin yang didapat dari pengecatan, bukan balance besar
                    if inc > 0:
                        log_message(f"Paint: {pixel_id}, color: {new_color}, reward: +{inc:.2f} points", Fore.GREEN)
                    else:
                        log_message(f"Paint: {pixel_id}, color: {new_color}, reward: 0 points", Fore.YELLOW)

                    # Tambahkan poin ke total poin
                    total_points += inc

                except requests.exceptions.RequestException as e:
                    log_message(f"Failed to paint: {e}", Fore.RED)
                    break

        # Tampilkan total poin yang didapat di akhir sesi
        log_message(f"Total points yang didapat: {total_points:.2f} points", Fore.MAGENTA)

    except requests.exceptions.RequestException as e:
        log_message(f"Network error in account {account}: {e}", Fore.RED)

# Process accounts and manage sleep logic
def process_accounts(accounts):
    for account in accounts:
        username = extract_username_from_initdata(account)
        log_message(f"--- NOTPIXELTOT PAKE QUERYTOD: {username} ---", Fore.BLUE)
        main(account, account)

# Function to extract the username from the URL-encoded init data
def extract_username_from_initdata(init_data):
    decoded_data = urllib.parse.unquote(init_data)
    
    username_start = decoded_data.find('"username":"') + len('"username":"')
    username_end = decoded_data.find('"', username_start)
    
    if username_start != -1 and username_end != -1:
        return decoded_data[username_start:username_end]
    
    return "Unknown"

# Function to load accounts from data.txt
def load_accounts_from_file(filename):
    with open(filename, 'r') as file:
        accounts = [f"initData {line.strip()}" for line in file if line.strip()]
    return accounts

if __name__ == "__main__":
    accounts = load_accounts_from_file('data.txt')
    process_accounts(accounts)
