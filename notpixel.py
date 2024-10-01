import requests
import random
import time
import os
import threading
from colorama import Fore, Style, init, Back
from datetime import datetime

init(autoreset=True)

COLOR_COMBOS = [
    (Fore.RED),
    (Fore.GREEN),
    (Fore.YELLOW),
    (Fore.BLUE),
    (Fore.MAGENTA),
    (Fore.CYAN),
]

color_index = 0
print_lock = threading.Lock() 

def load_account():
    if os.path.exists('accounts.txt'):
        with open('accounts.txt', 'r') as file:
            return file.read().strip()
    else:
        query_id = input("Enter your queryId: ")
        with open('data.txt', 'w') as file:
            file.write(query_id)
        return query_id

queryId = load_account()
API_URL = "https://notpx.app/api/v1"

class NotPx:
    def __init__(self, queryId) -> None:
        self.queryId = queryId
        self.session = requests.Session()
        self.__update_headers()

    def __update_headers(self):
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'initData {self.queryId}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36',
        }

    def request(self, method, end_point, key_check, data=None):
        try:
            response = self.session.request(method,
                                            f"{API_URL}{end_point}",
                                            json=data,
                                            timeout=5)
            if response.status_code == 200:
                if key_check in response.text:
                    return response.json()
                else:
                    print_colored_log(f"Key check unsuccessful in the response.")
                    return None
            else:
                print_colored_log(f"Error: Authentication error or another problem. Status Code: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            print_colored_log(f"Connection error. Sleeping for 5 seconds...")
            time.sleep(5)
        except requests.exceptions.Timeout:
            print_colored_log(f"Timeout error. Sleeping for 5 seconds...")
            time.sleep(5)

    def claim_mining(self):
        response = self.request("get", "/mining/claim", "claimed")
        if response:
            return response.get('claimed', 0)
        else:
            return 0

    def account_status(self):
        return self.request("get", "/mining/status", "speedPerSecond")

    def auto_paint_pixel(self):
        colors = ["#FFFFFF", "#000000", "#00CC78", "#BE0039"]
        random_pixel = (random.randint(100, 990) * 1000) + random.randint(100, 990)
        data = {"pixelId": random_pixel, "newColor": random.choice(colors)}
        response = self.request("post", "/repaint/start", "balance", data)
        if response:
            return response.get('balance', 0)
        else:
            return 0

NotPxClient = NotPx(queryId)

def banner():
    print(Fore.CYAN + Style.BRIGHT + r"""

 /$$   /$$  /$$$$$$  /$$$$$$$$ /$$$$$$$  /$$$$$$ /$$   /$$ /$$$$$$$$ /$$      
| $$$ | $$ /$$__  $$|__  $$__/| $$__  $$|_  $$_/| $$  / $$| $$_____/| $$      
| $$$$| $$| $$  \ $$   | $$   | $$  \ $$  | $$  |  $$/ $$/| $$      | $$      
| $$ $$ $$| $$  | $$   | $$   | $$$$$$$/  | $$   \  $$$$/ | $$$$$   | $$      
| $$  $$$$| $$  | $$   | $$   | $$____/   | $$    >$$  $$ | $$__/   | $$      
| $$\  $$$| $$  | $$   | $$   | $$        | $$   /$$/\  $$| $$      | $$      
| $$ \  $$|  $$$$$$/   | $$   | $$       /$$$$$$| $$  \ $$| $$$$$$$$| $$$$$$$$
|__/  \__/ \______/    |__/   |__/      |______/|__/  |__/|________/|________/
            
            """ + Style.RESET_ALL)
    
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored_log(message):
    global color_index
    with print_lock:
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        fore_color = COLOR_COMBOS[color_index % len(COLOR_COMBOS)]
        print(f"{fore_color}[{timestamp}] {message}{Style.RESET_ALL}")
        color_index += 1

def painter():
    print_colored_log("Start Auto-paint.")
    while True:
        try:
            charges = NotPxClient.account_status()
            if not charges or charges.get('charges', 0) <= 0:
                print_colored_log("No charges available. Wait for 10 minutes...")
                time.sleep(600)
                continue

            for i in range(charges['charges']):
                balance = NotPxClient.auto_paint_pixel()
                print_colored_log(f"1 Pixel Success painted | User balance: {balance}")
                time.sleep(random.randint(1, 6))
        except Exception as e:
            print_colored_log(f"Error in painter: {e}. Sleeping...")
            time.sleep(5)

def mine_claimer():
    print_colored_log("Start Auto-claiming mining rewards.")
    while True:
        try:
            acc_data = NotPxClient.account_status()
            if acc_data:
                from_start = acc_data.get('fromStart', 0)
                speed_per_second = acc_data.get('speedPerSecond', 0)
                if from_start * speed_per_second > 2:
                    claimed_count = NotPxClient.claim_mining()
                    print_colored_log(f"Claimed {claimed_count} NotPx Tokens.")
            print_colored_log("Miner Wait for 1 hour...")
            time.sleep(3600)
        except Exception as e:
            print_colored_log(f"Error in mining: {e}. Sleeping...")
            time.sleep(5)

# Start script
if __name__ == "__main__":
    clear_console()
    banner()
    threading.Thread(target=painter).start()
    mine_claimer()