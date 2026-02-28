import base64
from datetime import datetime
now = datetime.now()
current_time = f"{now.month}/{now.day}/{now.strftime('%y')} {now.strftime('%I:%M %p').lstrip('0')}"
from collections import deque
import subprocess
import threading
import hashlib
import socket
import msvcrt
import hmac
import time
import zlib
import math
import os

workspace_folder = "ScurvyData (contains accounts)"

paths = {
"oh-email": os.path.join(os.path.dirname(__file__), "settings", "email.ini"),
"oh-key": os.path.join(os.path.dirname(__file__), "settings", "accountKey.ini"),
"svy-settings": os.path.join(workspace_folder, "scurvy.cfg"),
"svy-accounts": os.path.join(workspace_folder, "accounts.txt"),
"svy-history": os.path.join(workspace_folder, "history.txt"),
}

svy_data = {
"cfg_default": """\
exe = None
server = bigserver2.onehouronelife.com
port = 8005
---------------------------------------
scurvy_key = None
client_tag = None
""",
"client_tag": None,
"scurvy_key": None,
"exe": None,
"server": None,
"port": None,
"client_tag": None,
}

rgb = (255, 197, 145); r, g, b = rgb; print(f"\033[38;2;{r};{g};{b}m", end="")

client_title = """\
███████  ██████ ██    ██ ██████  ██    ██ ██    ██ 
██      ██      ██    ██ ██   ██ ██    ██  ██  ██  
███████ ██      ██    ██ ██████  ██    ██   ████   
     ██ ██      ██    ██ ██   ██  ██  ██     ██    
███████  ██████  ██████  ██   ██   ████      ██  

               🜋 Version XXII 🜋     
               -----------------                   
"""
manual_text = f"""{client_title}
[I] Information     [H] History     [S] Settings
"""



class Menu:
    def __init__(self, 
                 main_menu=False, 
                 options=None, 
                 title=None, 
                 placement=None,
                 parent=None,
                 replacement_display=None):
        
        self.parent = parent
        self.options = options or {}
        self.main_menu = main_menu
        self.title = title
        self.placement = placement
        self.result = None
        self.replacement_display = replacement_display

    def menu(self):
        while True:
            os.system("cls" if os.name == 'nt' else "clear")
            
            if self.replacement_display:
                if callable(self.replacement_display):
                    self.replacement_display(self)
                else:
                    print(self.replacement_display)
                uinput = input("> ").strip().lower()
            else:
                if self.title:
                    print(self.title)
                
                keys = list(self.options.keys())
                
                if self.placement:
                    columns, rows = self.placement
                    count = 0
                    for _ in range(rows):
                        line_parts = []
                        for _ in range(columns):
                            if count < len(keys):
                                key_name = keys[count]
                                option_key = self.options[key_name].get("Key", "")
                                line_parts.append(f"[{option_key.upper()}] {key_name}")
                                count += 1
                        if line_parts:
                            line = "  ".join(line_parts).ljust(25 * len(line_parts))
                            print(line)
                else:
                    for key_name in keys:
                        option_key = self.options[key_name].get("Key", "")
                        print(f"[{option_key.upper()}] {key_name}")

                uinput = input("> ").strip().lower()

            chosen_option = None
            for name, data in self.options.items():
                key = data.get("Key", "")
                if key.lower() == uinput:
                    chosen_option = data
                    break

            if not chosen_option:
                print("\nOption Not Found...",end="")
                msvcrt.getch()
                continue

            func = chosen_option["Function"]
            single_run = chosen_option.get("Single Run", False)

            if single_run:
                os.system("cls" if os.name == 'nt' else "clear")
                result = func()
                if result == "exit":
                    return "exit" if self.main_menu else "back"
            else:
                while True:
                    os.system("cls" if os.name == 'nt' else "clear")
                    self.result = func()
                    if self.result == "return":
                        break
                    if self.result == "exit":
                        return "exit" if self.main_menu else "back"

    def eInput(self, text="> "):
        uinput = input(text)
        if uinput.lower() == "exit":
            self.result = "return"
            return "return"
        return uinput
   
class SFE:
    def __init__(self, filepath, autosave=True):
        self.filepath = filepath
        self.autosave = autosave
        self.lock = threading.RLock()
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.lines = [line.rstrip("\n") + "\n" for line in f.readlines()]
        except FileNotFoundError:
            self.lines = []

    def save(self):
        with self.lock:
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.writelines(self.lines)
        return self

    def total_lines(self):
        with self.lock:
            return len(self.lines)

    def read(self, line_number):
        with self.lock:
            if isinstance(line_number, str) and line_number.upper() == "L":
                line_number = self.total_lines()
            if 1 <= line_number <= self.total_lines():
                return self.lines[line_number - 1].rstrip("\n")
            return None

    def write(self, line_number, value):
        with self.lock:
            if isinstance(line_number, str) and line_number.upper() == "L":
                line_number = self.total_lines() + 1
            while len(self.lines) < line_number:
                self.lines.append("\n")
            self.lines[line_number - 1] = value.rstrip("\n") + "\n"
            if self.autosave:
                self.save()
        return self

    def delete(self, line_number):
        with self.lock:
            if 1 <= line_number <= self.total_lines():
                del self.lines[line_number - 1]
                if self.autosave:
                    self.save()
        return self

    def locate(self, key, equalizer="="):
        with self.lock:
            for index, line in enumerate(self.lines, start=1):
                if equalizer in line:
                    base = line.split(equalizer, 1)[0].strip()
                    if base.lower() == key.lower():
                        return index
            return None

    def read_equality(self, key, equalizer="="):
        with self.lock:
            idx = self.locate(key, equalizer)
            if idx:
                base, value = self.lines[idx - 1].split(equalizer, 1)
                return value.strip()
            return None

    def write_equality(self, key, replacement_value, equalizer="="):
        replacement_value = str(replacement_value).strip()
        with self.lock:
            idx = self.locate(key, equalizer)
            if idx:
                base, _ = self.lines[idx - 1].split(equalizer, 1)
                self.lines[idx - 1] = f"{base.strip()} {equalizer} {replacement_value}\n"
            else:
                self.lines.append(f"{key} {equalizer} {replacement_value}\n")
            if self.autosave:
                self.save()
        return self

    def reverse_logic(self, key, equalizer="="):
        with self.lock:
            idx = self.locate(key, equalizer)
            if idx:
                base, value = self.lines[idx - 1].split(equalizer, 1)
                new_value = "False" if value.strip().lower() == "true" else "True"
                self.lines[idx - 1] = f"{base.strip()} {equalizer} {new_value}\n"
                if self.autosave:
                    self.save()
        return self

    def make(self):
        with self.lock:
            open(self.filepath, 'w').close()
    
def run_account(email, key):
    SFE(paths["oh-email"]).write(1, email)
    SFE(paths["oh-key"]).write(1, key)
    subprocess.Popen(svy_data["exe"], shell=True)

def about():
    print(" > About \n")
    print(" 🜋     Welcome to Scurvy, an external client.")
    print(" 🜋     All of the features are clearly listed in the main menu section, feel free to explore.\n")
    print(" 🜋     Contributors: Shady")
    msvcrt.getch()

def display_history():
    history = SFE(paths["svy-history"])
    print("> Account History\n")
    for i in range(1, history.total_lines() + 1):
        raw = history.read(i)
        try:
            Order, Email, Date = raw.split("//")
            print(f" 🜋     Account {Order}: {Email}")
            print(f" 🜋     Date: {Date}\n")
            
        except:
            print(f"Corrupt history line {i}")
    msvcrt.getch()



def start():
    # Menu Area
    mm=Menu(
        main_menu=True,
        options={    
            "INFO": {"Function": about, "Single Run": True, "Key": "I"}, 
            "HIST": {"Function": display_history, "Single Run": True, "Key": "H"}, 

        },
        replacement_display=manual_text
    )
    # Running Area
    os.system(f'title Scurvy')
    
    if not os.path.exists(workspace_folder):
        os.makedirs(workspace_folder)

    mm.menu()

start()