import base64
import traceback
import subprocess
import threading
import hashlib
import socket
import msvcrt
import hmac
import time
import zlib
import math
import requests
import re
import random
import os

from datetime import datetime
from itertools import zip_longest
from collections import deque
from typing import Optional
now = datetime.now()
curtime_formatted = f"{now.month}/{now.day}/{now.strftime('%y')} {now.strftime('%I:%M %p').lstrip('0')}"




default_color=(255,55,55)

terminal_name = "Birdery's Distributor Terminal"
folder_name = "Terminal Data (Sensitive)"
version = "1.0"

def set_rgb(rgb=(255, 255, 255)):
    r, g, b = rgb
    print(f"\033[38;2;{r};{g};{b}m", end="")
set_rgb(default_color)

def print_as_rgb(*args, rgb=(255, 255, 255), sep=" ", end="\n"):
    text = sep.join(map(str, args))
    r, g, b = rgb
    colored = f"\033[38;2;{r};{g};{b}m{text}\033[0m"
    print(colored, end=end)
    set_rgb(default_color)

def HMAC_SHA1(key, message):
    hmac_object = hmac.new(key.encode(), message.encode(), hashlib.sha1)
    return hmac_object.hexdigest()

class FileBuilder:
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
            return len(self.lines) + 1

    def _resolve_line_number(self, line_number, for_write=False):
        if isinstance(line_number, str) and line_number.upper() == "L":
            return self.total_lines()
        if isinstance(line_number, int):
            return line_number
        return None

    def read(self, line_number):
        with self.lock:
            line_number = self._resolve_line_number(line_number)
            if isinstance(line_number, int) and 1 <= line_number < self.total_lines():
                return self.lines[line_number - 1].rstrip("\n")
            return None

    def write(self, line_number, value):
        with self.lock:
            line_number = self._resolve_line_number(line_number, for_write=True)
            if not isinstance(line_number, int) or line_number < 1:
                return self
            while len(self.lines) < line_number:
                self.lines.append("\n")
            self.lines[line_number - 1] = value.rstrip("\n") + "\n"
            if self.autosave:
                self.save()
        return self

    def delete(self, line_number):
        with self.lock:
            line_number = self._resolve_line_number(line_number)
            if isinstance(line_number, int) and 1 <= line_number < self.total_lines():
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
            open(self.filepath, "w", encoding="utf-8").close()
            self.lines = []
        return self

class MenuBuilder:
    def __init__(self, 
                 main_menu=False, 
                 options=None, 
                 title=None, 
                 placement=None,
                 parent=None,
                 replacement_display=None,
                 color=(255, 255, 255)):  
        
        self.parent = parent
        self.options = options or {}
        self.main_menu = main_menu
        self.title = title
        self.placement = placement
        self.result = None
        self.replacement_display = replacement_display
        self.color = color 

    def menu(self):
        while True:

            if self.replacement_display:
                if callable(self.replacement_display):
                    self.replacement_display(self)
                else:
                    print_as_rgb(self.replacement_display, rgb=self.color)
                uinput = input("\033[38;2;180;180;180m> \033[0m").strip().lower()
            else:
                if self.title:
                    print_as_rgb(self.title, rgb=self.color)
                
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
                            line = "  ".join(line_parts)
                            print_as_rgb(line, rgb=self.color)
                else:
                    for key_name in keys:
                        option_key = self.options[key_name].get("Key", "")
                        print_as_rgb(f"[{option_key.upper()}] {key_name}", rgb=self.color)

                uinput = input("\033[38;2;180;180;180m> \033[0m").strip().lower()

            chosen_option = None
            for name, data in self.options.items():
                key = data.get("Key", "")
                if key.lower() == uinput:
                    chosen_option = data
                    break

            if not chosen_option:
                print_as_rgb("\nInvalid Option...", rgb=(255, 80, 80))
                msvcrt.getch()
                os.system("cls")
                continue

            func = chosen_option["Function"]
            single_run = chosen_option.get("Single Run", False)

            if single_run:
                os.system("cls")
                result = func()
                os.system("cls")
                if result == "exit":
                    return "exit" if self.main_menu else "back"
            else:
                while True:
                    os.system("cls")
                    self.result = func()
                    os.system("cls")
                    if self.result == "return":
                        break
                    if self.result == "exit":
                        return "exit" if self.main_menu else "back"

    def eInput(self, text="> "):
        prompt_colored = f"\033[38;2;180;180;180m{text}\033[0m"
        uinput = input(prompt_colored)
        if uinput.lower() == "exit":
            self.result = "return"
            os.system("cls")
            return "return"
        return uinput

Filesaves = {
    "Dirs": {
        "Settings": os.path.join(folder_name, "Settings.cfg"),
        "Accounts": os.path.join(folder_name, "Accounts.txt"),
        "History": os.path.join(folder_name, "History.txt"),
        "Executables": os.path.join(folder_name, "Executables.txt"),
        "Ohol": {"email ini": os.path.join(os.path.dirname(__file__),"settings", "email.ini"), 
                 "key ini": os.path.join(os.path.dirname(__file__), "settings", "accountKey.ini")
                } 
            },

    "Links": {"Reflector": "https://onehouronelife.com/reflector/server.php?action=report",
              "Ticket": "https://onehouronelife.com/ticketServer/server.php?action=show_downloads&ticket_id=",
              "Fitness": "https://onehouronelife.com/fitnessServer/server.php?action=",
              "Curses": "http://onehouronelife.com/curseServer/server.php?action="
            },

    "Settings": {"default_executable":None, "client":None, "password":None,"server_password":None,"server_ip":None, "port":None,},
    "Memory": {"General": {"Password Copy": None, "Server Name": None},"Executables": [], "Accounts": []} # Store executables in a list for the for function, give it its own file if not done so already 
    # What if updating memory could just be put into a single callable function, one that makes it so you dont gotta generate each time
    # But instead just update

}

def encrypt(plaintext: str, key: str) -> str:
    encrypted_bytes = bytearray()
    key_bytes = key.encode()
    for i, char in enumerate(plaintext.encode()):
        encrypted_bytes.append(char ^ key_bytes[i % len(key_bytes)])
    return base64.b64encode(encrypted_bytes).decode()

def decrypt(ciphertext: str, key: str) -> str:
    encrypted_bytes = base64.b64decode(ciphertext.encode())
    decrypted_bytes = bytearray()
    key_bytes = key.encode()
    for i, char in enumerate(encrypted_bytes):
        decrypted_bytes.append(char ^ key_bytes[i % len(key_bytes)])
    return decrypted_bytes.decode()

def run_game(exe):
    subprocess.Popen(exe, shell=True)

def update_file_info(histlog=None): # Have this update everything from accounts to history, it'll make things eaiser
    if not os.path.exists(folder_name):
        fbSettings = FileBuilder(Filesaves["Dirs"]["Settings"])

        print("Before you start create a password for security purposes.\n" \
        "You can change this password any time in settings.")
        password = input("> "); os.system("cls")
        
        print("Now copy and paste a default executable for your client's launcher to use.")
        executable = input("> "); os.system("cls")


        os.makedirs(folder_name)
        
        open(Filesaves["Dirs"]["Accounts"], 'w').close()
        open(Filesaves["Dirs"]["Executables"], 'w').close()
        open(Filesaves["Dirs"]["History"], 'w').close()
        open(Filesaves["Dirs"]["Settings"], 'w').close()
        fbSettings.write(1, f"default_executable = {executable}\n" \
        "client = client_piterminal\n" \
        f"password = {password}\n" \
        "server_password = testPassword\n" \
        "server_ip = bigserver2.onehouronelife.com\n" \
        "port = 8005")

    def internet_check():
        fbSettings = FileBuilder(Filesaves["Dirs"]["Settings"])
        server_password = fbSettings.read_equality("server_password")
        server_ip = fbSettings.read_equality("server_ip")
        port = fbSettings.read_equality("port")

        Filesaves["Settings"]["server_password"] = fbSettings.read_equality("server_password")
        if server_password != "testPassword":
            os.system("cls")
            print("Abnormal Server Password Detected")
            input("Press enter key to continue..")
            os.system("cls")
        try:
            Filesaves["Settings"]["server_ip"] = socket.gethostbyname(server_ip)
        except:
            os.system("cls")
            print(f"Internet error detected: {server_ip} is not a valid server address")
            input("Press enter key to continue..")
        try:
            Filesaves["Settings"]["port"] = int(fbSettings.read_equality("port"))
        except:
            os.system("cls")
            print(f"Internet error detected: {port} is not a valid number for a port.")
            input("Press enter key to continue..")
    internet_check()



    ####
    fbSettings = FileBuilder(Filesaves["Dirs"]["Settings"])
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    fbHistory = FileBuilder(Filesaves["Dirs"]["History"])
    fbDirecotries = FileBuilder(Filesaves["Dirs"]["Executables"])
     # Internet check above does the job of the three other file's detections for convenience
    def account_update():
        # Accounts
        Filesaves["Memory"]["Accounts"].clear()
        for i in range(1, fbAccounts.total_lines()): # We are 0 based
            Filesaves["Memory"]["Accounts"].append(fbAccounts.read(i)) #allows accounts to be list printed
    account_update()
    
    # Settings
    Filesaves["Memory"]["General"]["Server Name"] = fbSettings.read_equality("server_ip")
    Filesaves["Settings"]["default_executable"] = fbSettings.read_equality("default_executable")
    Filesaves["Settings"]["client"] = fbSettings.read_equality("client")
    Filesaves["Settings"]["password"] = fbSettings.read_equality("password")

    # Encryption Password Exchange
    if not Filesaves["Memory"]["General"]["Password Copy"]:
        Filesaves["Memory"]["General"]["Password Copy"] = Filesaves["Settings"]["password"]
        pass
    if (Filesaves["Memory"]["General"]["Password Copy"] != Filesaves["Settings"]["password"]):
        for i, account in enumerate(Filesaves["Memory"]["Accounts"]):
            decrypted = decrypt(account, Filesaves["Memory"]["General"]["Password Copy"])
            parts = decrypted.split("//")
            if len(parts) == 3:
                name, email, key = parts
                fbAccounts.write(i+1, encrypt(f"{name}//{email}//{key}", Filesaves["Settings"]["password"]))
        Filesaves["Memory"]["General"]["Password Copy"] = Filesaves["Settings"]["password"]
    
    
    # Executables
    for i in range(1, fbDirecotries.total_lines()): # We are 0 based
        Filesaves["Memory"]["Executables"].append(fbAccounts.read(i)) #allows exes to be list printed, less important though...?
        # This feature might be removed entirely keep note...

    badlist = []
    for i, account in enumerate(Filesaves["Memory"]["Accounts"]):
        try:
            decrypt(account, Filesaves["Settings"]["password"])
        except:
            badlist.append(i)
    for unencrypted in badlist:
        encrypted = encrypt(Filesaves["Memory"]["Accounts"][unencrypted], Filesaves["Settings"]["password"])
        fbAccounts.write(unencrypted+1, encrypted)
    account_update()

    if(histlog): # For history each runner has to submit their entry before running: could be account, could be email, it dont care.
        fbHistory.write(fbHistory.total_lines(), f"{curtime_formatted}//{histlog}")
        
def client_settings(): # Forgot how it works, just ported it to this version.
    fbSettings = FileBuilder(Filesaves["Dirs"]["Settings"])
    while True:
        os.system("cls")
        print("Client Settings")
        print("---------------")
        for i in range(1, fbSettings.total_lines()):
            print(f"{i}. {fbSettings.read(i)}")
            print("------------------------")
        print("Enter the number of the setting you'd like to edit or type 'EXIT' to return.")
        
        uinput = input("> ").strip()
        if uinput.upper() == "EXIT":
            return "return"
        
        try:
            index = int(uinput)
            if index < 1 or index > fbSettings.total_lines():
                raise ValueError
        except ValueError:
            print("Invalid Number...")
            msvcrt.getch()
            continue

        old_line = fbSettings.read(index)
        if "=" in old_line:
            key, current_value = old_line.split("=", 1)
            key = key.strip()
            current_value = current_value.strip()
        else:
            key = old_line.strip()
            current_value = ""

        os.system("cls")
        print(f"Editing: '{key} = {current_value}'")
        print("Enter new value or type 'EXIT' to cancel:")
        new_value = input("> ").strip()
        if new_value.upper() == "EXIT":
            continue

        fbSettings.write_equality(key, new_value)

        update_file_info()
        print("\nSetting updated...")
        msvcrt.getch()

def onelife_settings(): # Same with this one, we just gonna go with it
    settings_data = {
        "vogModeOn":"1","useSteamUpdate":"1","useLifeTokenServer":"1","useFitnessServer":"1","upLeftDownRightKeys":"wasd",
        "tutorialDone":"0","targetFrameRate":"60","useCustomServer":"0","soundSampleRate":"44100","soundEffectsOff":"0",
        "soundEffectsLoudness":"1.0","skipFPSMeasure":"1","serverPassword":"testPassword","recordGame":"0",
        "recordAudioLengthInSeconds":"130","recordAudio":"0","reportWildBugToUser":"0","outputAllFrames":"0",
        "mouseSpeed":"1.0","musicOff":"0","musicLoudness":"1.0","mapPullStartY":"-100","mapPullStartX":"-100",
        "mapPullMode":"0","mapPullEndY":"100","mapPullEndX":"100","loginSuccess":"1","keepPastRecordings":"20",
        "halfFrameRate":"0","fullscreen":"0","forceBigPointer":"0","emotDuration":"10","eKeyForRightClick":"0",
        "enableSpeedControlKeys":"0","enableLiveTriggers":"0","compressExports":"1","checkReviewSpelling":"1",
        "blendOutputFramePairs":"1","blendOutputFrameFraction":"0","borderlessHeightAdjust":"1","borderless":"0",
        "ahapSkipDataUpdate":"0","autoLogIn":"0","screenWidth":"1280","screenHeight":"720"
    }
    flat_list = list(settings_data.keys())
    while True:
        os.system("cls")
        print("Settings Onelife 🌣\n")
        for idx, setting_name in enumerate(flat_list, 1):
            file_path = os.path.join("settings", f"{setting_name}.ini")
            value = settings_data[setting_name]
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    value = f.read().strip()
            print(f"{idx}. {setting_name} = {value}")
        print("\nType a number or setting name.\nType 'Reset' to reset settings.\nType 'Exit' to return.")
        uinput = input("> ").strip()
        if uinput.upper() == "EXIT":
            return
        if uinput.upper() == "RESET":
            for name in flat_list:
                file_path = os.path.join("settings", f"{name}.ini")
                FileBuilder(file_path).write(1, settings_data[name])
            print("All settings reset..")
            msvcrt.getch()
            continue
        selected = None
        if uinput.isdigit():
            idx = int(uinput)-1
            if 0 <= idx < len(flat_list):
                selected = flat_list[idx]
        else:
            for name in flat_list:
                if name.lower() == uinput.lower():
                    selected = name
                    break
        if not selected:
            print("Invalid setting..")
            msvcrt.getch()
            continue
        file_path = os.path.join("settings", f"{selected}.ini")
        current_value = settings_data[selected]
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                current_value = f.read().strip()
        print(f"Current value: {selected} = {current_value}")
        new_value = input("New value: ").strip()
        if new_value:
            FileBuilder(file_path).write(1, new_value)

def display_history():
    fbHistory = FileBuilder(Filesaves["Dirs"]["History"])
    for i in range(1, fbHistory.total_lines()): # We are 0 base
        try:
            time, entry = fbHistory.read(i).split("//")
            print(f"{i}. {time}: {entry}")   
        except:
            print(f"{i}. Corrupt Log") 

def display_emails(specific=None):
    update_file_info()
    
    if specific is not None:
        try:
            raw = decrypt(Filesaves["Memory"]["Accounts"][specific-1], Filesaves["Settings"]["password"])
            name, email, key = raw.split("//")
            cleaned_name = (name or "").strip()
            ident = cleaned_name if cleaned_name and cleaned_name.lower() != "none" else email.strip()
            print(f"{specific:3d} │ {ident}")
        except:
            print(f"{specific:3d} │ Corrupt or non-existent account")
        return

    for i, account in enumerate(Filesaves["Memory"]["Accounts"], 1):
        try:
            raw = decrypt(account, Filesaves["Settings"]["password"])
            name, email, key = raw.split("//")
            cleaned_name = (name or "").strip()
            ident = cleaned_name if cleaned_name and cleaned_name.lower() != "none" else email.strip()
            print(f"{i:3d} │ {ident}")
        except:
            print(f"{i:3d} │ Corrupt Account")

def display_emails_keys():
    set_rgb(default_color)
    update_file_info()
    
    for i, account in enumerate(Filesaves["Memory"]["Accounts"], 1):
        try:
            raw = decrypt(account, Filesaves["Settings"]["password"])
            name, email, key = raw.split("//")
            
            cleaned_name = (name or "").strip()
            display_name = "N/A" if cleaned_name.lower() == "none" or not cleaned_name else cleaned_name
            
            print(f"{i:3d} │ Name : {display_name}")
            print(f"    │ Email: {email}")
            print(f"    │ Key  : {key}")
            print("    ├─────────────────────────────────────────")
        except:
            print(f"{i:3d} │ Corrupt Account")
            print("    ├─────────────────────────────────────────")

def display_all_accounts():
    print("     All Accounts")
    print("    ├───────────────────────────────────")
    display_emails_keys()
    msvcrt.getch()
    return
    
def About():
    set_rgb(default_color)
    print("This is terminal by Birdery")
    print("Possible distribution in the future.")
    print("Possibility: Miniscule")
    msvcrt.getch()

def History():
    set_rgb(default_color)
    print("History Of Account Use")
    print("───────────────────────")
    display_history()
    msvcrt.getch()

def Debug():
    # set_rgb(default_color)
    # print("DEBUG INFORMATION")
    # print("------------------")
    # print(Filesaves["Memory"]["General"]["Server Name"])
    # display_emails(specific=3)
    # print(Filesaves["Settings"]["default_executable"])
    # print(Filesaves["Settings"]["client"])
    # print(Filesaves["Settings"]["password"])
    # print(Filesaves["Settings"]["server_password"])
    # print(Filesaves["Settings"]["server_ip"])
    # print(Filesaves["Settings"]["port"])
    # msvcrt.getch()
    # # run_game(Filesaves["Settings"]["default_executable"])
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    
    print("DEBUGGING")
    print("-------------------")
    display_emails()
    try: 
        number = input("> ")
        if number.upper() == "EXIT":
            return "return"
        number = int(number)
        if number < 1 or number > fbAccounts.total_lines():
            print("Attempted to select a non-existant account..")
            msvcrt.getch()
            return
    except:
        print("The characters you have tried to enter do not qualify as a valid number.")
        msvcrt.getch()
        return  
    
    raw = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"])
    name, email, key = raw.split("//")
    account_tuple = (name, email, key)
    
    Account = Inclient(account_tuple, casecode="account locking")
    thread = threading.Thread(target=Account.client_engine, daemon=True)
    thread.start()
    thread.join()

    if Account.casecode == "ERROR":
        print("Connection Closed Due To Crash")
        msvcrt.getch()
    if Account.casecode == "REJECTED":
        print(f"Account {number}: [{name if name else email}] rejected by server.")
        msvcrt.getch()
    if "SPAWNCARD" in Account.casecode:
        os.system("cls")
        print(Account.casecode[1])
        update_file_info(histlog = f"quickspawn: {name if name else email}")
        msvcrt.getch()
    return

def add_accounts():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    print("Account Adding")
    print("───────────────")
    display_emails()
    print("\n[Type [None] for no name]")
    name = input("[Account Name] > ")
    if(name.upper() == "EXIT"):
        return "return"
    email = input("[Email] > ")
    if(email.upper() == "EXIT"):
        return "return"
    key = input("[Account Key] > ")
    if(key.upper() == "EXIT"):
        return "return"
    account = encrypt(f"{name}//{email}//{key}", Filesaves["Settings"]["password"])# from now on all account related things will use account for the sum string
    fbAccounts.write(fbAccounts.total_lines(), account)
    update_file_info()

def delete_accounts():
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    set_rgb((255,0,0))
    print("Account Deleteing")

    print("----------------")
    display_emails()
    try: 
        number = input("> ")
        if number.upper() == "EXIT":
            return "return"
        number = int(number)
        if number < 1 or number > fbAccounts.total_lines():
            print("Attempted to delete a non-existant account..")
            msvcrt.getch()
            return
    except:
        print("The characters you have tried to enter do not qualify as a valid number.")
        msvcrt.getch()
        return  

    print(f"Delete account {number}? [y/n]")
    choice = input("> ")
    if choice.upper() == "Y":
        fbAccounts.delete(number)
        print(f"Account {number} deleted.")
        msvcrt.getch()
    elif choice.upper() == "N":
        msvcrt.getch()
        print("deletion cancelled sucessfully")
    update_file_info()
    return

def edit_accounts():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    print("Account Editor")
    print("---------------")
    display_emails()
    try: 
        number = input("> ")
        if number.upper() == "EXIT":
            return "return"
        number = int(number)
        if number < 1 or number > fbAccounts.total_lines():
            print("Attempted to select a non-existant account..")
            msvcrt.getch()
            return
    except:
        print("The characters you have tried to enter do not qualify as a valid number.")
        msvcrt.getch()
        return          
    raw = decrypt(fbAccounts.read(number), Filesaves["Settings"]["password"])
    name, email, key = raw.split("//")

    while(True):
        os.system("cls")

        update_file_info()
        raw = decrypt(fbAccounts.read(number), Filesaves["Settings"]["password"])
        name, email, key = raw.split("//")

        print(f"Account: {name if name else email}")
        print("Choose a feature to edit.\n")

        print(f"1. Name: {name}")
        print(f"2. Email: {email}")
        print(f"3. Key: {key}\n")

        try: 
            choice = input("> ")
            if choice.upper() == "EXIT":
                return # double exit
            choice = int(choice)
            if choice < 1 or choice > 3:
                print("Attempted to select an out of range number..")
                msvcrt.getch()
                continue
        except:
            print("The characters you have tried to enter do not qualify as a valid number.")
            msvcrt.getch()
            continue
        if choice == 1:
            print("\nEnter your account's new name")
            new_name = input("> ")
            if new_name.upper() == "EXIT":
                continue
            fbAccounts.write(number, encrypt(f"{new_name}//{email}//{key}", Filesaves["Settings"]["password"]))
            print(f"\nSucessfully Changed {name}->{new_name}")
            msvcrt.getch()
        elif choice == 2:
            print("\nEnter your account's new email")
            new_email = input("> ")
            fbAccounts.write(number, encrypt(f"{name}//{new_email}//{key}", Filesaves["Settings"]["password"]))
            if new_email.upper() == "EXIT":
                continue
            print(f"\nSucessfully Changed {email}->{new_email}")
            msvcrt.getch()
        elif choice == 3:
            print("\nEnter your account's new key")
            new_key = input("> ")
            if new_key.upper() == "EXIT":
                continue
            fbAccounts.write(number, encrypt(f"{name}//{email}//{new_key}", Filesaves["Settings"]["password"]))
            print(f"\nSucessfully Changed {key}->{new_key}")
            msvcrt.getch()

def duplicate_detector():
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    set_rgb((0,0,255))
    print("Welcome to duplicate cleaner")
    known_keys = []
    duplicate_keys = []
    for i, account in enumerate(Filesaves["Memory"]["Accounts"]): #i+1 for use in file device
        name, email, key = decrypt(account, Filesaves["Settings"]["password"]).split("//")
        if(key) in known_keys:
            duplicate_keys.append(i+1) # Processed for file already
        else:
            known_keys.append(key)
    if(duplicate_keys):
        print("Duplicates Detected: Delete? [y/n]")
        choice = input("> ")
        if choice.upper() == "Y":
            for num in sorted(duplicate_keys, reverse=True):
                fbAccounts.delete(num)
            print("Duplicate Accounts Deleted Sucessfully!")
            msvcrt.getch()
        elif choice.upper() == "N":
            return
    else:
        print("Found no duplicate keys!")
        msvcrt.getch()
        return
    update_file_info()
   
def active_account_detector():
    set_rgb(default_color)
    
    os.system("cls")
    print("Valid Account Detector")
    print("──────────────────────")
    print("Start Detection [y/n]")
    
    choice = input("> ").strip()
    if choice.upper() == "EXIT":
        return "return"

    if choice.upper() == "Y":
        os.system("cls")
        print("Valid Account Detector")
        print("──────────────────────")
        for i, account in enumerate(Filesaves["Memory"]["Accounts"]):
            if msvcrt.kbhit():
                if msvcrt.getch() == b'\r':
                    print("\n[Ended Prematurely]")
                    msvcrt.getch()
                    return
            
            name, email, key = decrypt(account, Filesaves["Settings"]["password"]).split("//")
            url = f"https://onehouronelife.com/ticketServer/server.php?action=show_downloads&ticket_id={key}"

            try:
                server_response = requests.get(url, timeout=1)
                server_response.raise_for_status()
                response_text = server_response.text.strip()

                if "Your ticket number was not found" in response_text:
                    print(f"{i+1}. {name if name else email}: [Disabled]")
                else:
                    print(f"{i+1}. {name if name else email}: [Active]")
            except:
                print(f"{i+1}. {name if name else email}: Request Failed [Unknown]")

        msvcrt.getch()
    elif choice.upper() == "N":
        return

def gene_score_checker():
    set_rgb(default_color)  # assuming you have this function for color
    
    os.system("cls")
    print("Gene Score Detector")
    print("──────────────────────────────")
    print("Start Detection [y/n]")
    
    choice = input("> ").strip().upper()
    if choice == "EXIT":
        return "return"
    if choice != "Y":
        return
    
    os.system("cls")
    print("Gene Score (Fitness) Detector")
    print("──────────────────────────────")
    print("Checking accounts...\n")
    
    base_url = Filesaves["Links"]["Fitness"]  # should be "https://onehouronelife.com/fitnessServer/server.php?action="
    # If not, hardcode: base_url = "https://onehouronelife.com/fitnessServer/server.php"
    
    for i, account_enc in enumerate(Filesaves["Memory"]["Accounts"]):
        if msvcrt.kbhit():
            if msvcrt.getch() == b'\r':
                print("\n[Detection stopped]")
                msvcrt.getch()
                return
        
        try:
            # Decrypt stored account line (format: name//email//key)
            decrypted = decrypt(account_enc, Filesaves["Settings"]["password"])
            parts = decrypted.split("//")
            name = parts[0].strip() if len(parts) > 0 else ""
            email = parts[1].strip() if len(parts) > 1 else ""
            key = parts[2].strip() if len(parts) > 2 else ""
            
            if not email or not key:
                print(f"{i+1}. {name or email}: [Invalid stored data]")
                continue
            
            ticket_id = key.replace("-", "").upper()
            
            # Step 1: Get next valid client sequence number
            seq_url = f"{base_url}get_client_sequence_number&email={email}"
            seq_response = requests.get(seq_url, timeout=5).text.strip()
            
            if not seq_response.endswith("OK"):
                print(f"{i+1}. {name or email}: [Sequence denied] {seq_response}")
                continue
            
            sequence_number = seq_response.split()[0].strip()
            
            # Step 2: Compute hash_value = HMAC-SHA1(ticket_id, sequence_number)
            hash_obj = hmac.new(
                ticket_id.encode('utf-8'),
                sequence_number.encode('utf-8'),
                hashlib.sha1
            )
            hash_value = hash_obj.hexdigest()
            
            # Step 3: Get the actual gene score
            score_params = {
                "action": "get_client_score",
                "email": email,
                "sequence_number": sequence_number,
                "hash_value": hash_value
            }
            score_response = requests.get("https://onehouronelife.com/fitnessServer/server.php", 
                                        params=score_params, 
                                        timeout=6).text.strip()
            
            if score_response.endswith("OK") and "DENIED" not in score_response.upper():
                lines = score_response.splitlines()
                if len(lines) >= 3:
                    leaderboard_name = lines[0].strip()
                    score = lines[1].strip()
                    rank = lines[2].strip()
                    
                    display = f"Score: {score}  Rank: {rank}"
                    if leaderboard_name:
                        display += f"  ({leaderboard_name})"
                    print(f"{i+1}. {name or email}: [Active] {display}")
                else:
                    print(f"{i+1}. {name or email}: [Active] (incomplete response)")
            else:
                print(f"{i+1}. {name or email}: [No score / Denied] {score_response[:60]}...")
                
        except Exception as e:
            print(f"{i+1}. {name or email}: [Error] {str(e)[:80]}")
    
    print("\nFinished checking all accounts.")
    print("Press any key to continue...")
    msvcrt.getch()

def read_server_reflector():
    set_rgb(default_color)
    
    print("Loading Reflector...")
    url = Filesaves["Links"]["Reflector"]
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        content = re.sub(r"<br\s*/?>", "\n", response.text)
        os.system("cls")
        print("Server Reflector")
        print("────────────────")
        print(content.strip())
        print("────────────────")
        
    except requests.RequestException as e:
        print(f"Error fetching server reflector: {e}")
    
    msvcrt.getch()

def select_account():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    
    os.system("cls")
    print("     Select Account")
    print("    ────────────────")
    display_emails()
    print()
    
    try: 
        number = input("> ")
        if number.upper() == "EXIT":
            return "return"
        number = int(number)
        if number < 1 or number > fbAccounts.total_lines():
            print("Attempted to select a non-existant account..")
            msvcrt.getch()
            return
    except:
        print("The characters you have tried to enter do not qualify as a valid number.")
        msvcrt.getch()
        return  
    
    name, email, key = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"]).split("//")
    FileBuilder(Filesaves["Dirs"]["Ohol"]["email ini"]).write(1, email)
    FileBuilder(Filesaves["Dirs"]["Ohol"]["key ini"]).write(1, key)
    time.sleep(1)
    run_game(Filesaves["Settings"]["default_executable"])
    update_file_info(histlog=f"{name if name else email}")

def select_multiple_accounts():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])

    while True:
        os.system("cls")
        print("Select Number Scheme")
        print("─────────────────────")
        print("1. Cycle: [x -> y]")
        print("2. Select: [1, 3, 9, 2]")
        print()
        
        choice = input("> ")
        mode = 2

        if choice.upper() == "EXIT":
            return "return"

        try:
            choice = int(choice)
        except:
            print("The characters you have tried to enter do not qualify as a valid number.")
            msvcrt.getch()
            os.system("cls")
            continue

        if choice == 1:
            mode = 1
            break

        if choice > 2 or choice < 1:
            print("The numbers you are trying to enter are invalid for this case.")
            msvcrt.getch()
            os.system("cls")
            continue

        break

    while True:
        os.system("cls")
        print("     Select Multiple Accounts")
        print("    ───────────────────────────")
        display_emails()
        print()

        selected = []

        if mode == 1:
            try:
                start = input("[Starting Number] > ")
                end = input("[Ending Number] > ")

                if start.upper() == "EXIT" or end.upper() == "EXIT":
                    return "return"

                start = int(start)
                end = int(end)

            except:
                print("The characters you have tried to enter do not qualify as a valid number.")
                msvcrt.getch()
                os.system("cls")
                continue

            if start < 1 or end > fbAccounts.total_lines() or end < start:
                print("Invalid by a scope issue.")
                msvcrt.getch()
                os.system("cls")
                continue

            selected = list(range(start, end + 1))

        else:
            try:
                raw = input("> ")

                if raw.upper() == "EXIT":
                    return "return"

                selected = [int(x.strip()) for x in raw.split(",")]

            except:
                print("The characters you have tried to enter do not qualify as a valid number.")
                msvcrt.getch()
                os.system("cls")
                continue

            for number in selected:
                if number < 1 or number > fbAccounts.total_lines():
                    print("Attempted to access a non-existant account.")
                    msvcrt.getch()
                    return

        first = True

        for number in selected:

            if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                print("\n[Ended Prematurely]")
                if mode == 1:
                    update_file_info(histlog=f"{start} -> {number}")
                else:
                    update_file_info(histlog=number)
                break

            if not first:
                time.sleep(3)

            name, email, key = decrypt(
                Filesaves["Memory"]["Accounts"][number-1],
                Filesaves["Settings"]["password"]
            ).split("//")

            FileBuilder(Filesaves["Dirs"]["Ohol"]["email ini"]).write(1, email)
            FileBuilder(Filesaves["Dirs"]["Ohol"]["key ini"]).write(1, key)

            run_game(Filesaves["Settings"]["default_executable"])

            first = False
        
        if mode == 1:
            update_file_info(histlog=f"{start} -> {end}")
        else:
            update_file_info(histlog=selected)
        break

class StreamParser:
    def __init__(self):
        self.buffer = b""

    def feed(self, data: bytes):
        self.buffer += data

    def get_messages(self):
        messages = []

        while True:
            if not self.buffer:
                break

            hashtag_pos = self.buffer.find(b"#")
            if hashtag_pos == -1:
                break  

            header_block = self.buffer[:hashtag_pos+1]
            header_text = header_block.decode("utf-8", errors="ignore")

            if header_text.startswith("CM"):
                parts = header_text.split()
                if len(parts) < 3:
                    break

                compressed_size = int(parts[2])
                total_needed = hashtag_pos + 1 + compressed_size

                if len(self.buffer) < total_needed:
                    break 
                compressed_data = self.buffer[hashtag_pos+1:total_needed]
                decompressed = zlib.decompress(compressed_data).decode()

                messages.append(decompressed)

                self.buffer = self.buffer[total_needed:]
                continue

            elif header_text.startswith("MC"):
                parts = header_text.split()
                if len(parts) < 7:
                    break

                compressed_size = int(parts[6])
                total_needed = hashtag_pos + 1 + compressed_size

                if len(self.buffer) < total_needed:
                    break

                compressed_data = self.buffer[hashtag_pos+1:total_needed]
                decompressed = zlib.decompress(compressed_data)

                full_message = header_text + decompressed.decode()
                messages.append(full_message)

                self.buffer = self.buffer[total_needed:]
                continue

            
            else:
                message = header_text[:-1]  # remove #
                messages.append(message)
                self.buffer = self.buffer[hashtag_pos+1:]
                continue

        return messages

def quickspawn_account():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    
    os.system("cls")
    print("     Quickspawn Accounts")
    print("    ──────────────────────")
    display_emails()
    print()
    
    try: 
        number = input("> ")
        if number.upper() == "EXIT":
            return "return"
        number = int(number)
        if number < 1 or number > fbAccounts.total_lines():
            print("Attempted to select a non-existant account..")
            msvcrt.getch()
            return
    except:
        print("The characters you have tried to enter do not qualify as a valid number.")
        msvcrt.getch()
        return  
    
    raw = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"])
    name, email, key = raw.split("//")
    account_tuple = (name, email, key)
    
    Account = Inclient(account_tuple, casecode="quickspawn")
    thread = threading.Thread(target=Account.client_engine, daemon=True)
    thread.start()
    thread.join()

    if Account.casecode == "ERROR":
        print("Connection Closed Due To Crash")
        msvcrt.getch()
    if Account.casecode == "REJECTED":
        print(f"Account {number}: [{name if name else email}] rejected by server.")
        msvcrt.getch()
    if "SPAWNCARD" in Account.casecode:
        os.system("cls")
        print(Account.casecode[1])
        update_file_info(histlog = f"quickspawn: {name if name else email}")
        msvcrt.getch()
    return

def quickspawn_multiple():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])

    while True:
        os.system("cls")
        print("Select Number Scheme")
        print("─────────────────────")
        print("0. No Tutorial")
        print("1. Tutorial 1")
        print("2. Tutorial 2")
        print()
        
        choice = input("> ")
        tutorial = 0

        if choice.upper() == "EXIT":
            return "return"

        try:
            choice = int(choice)
        except:
            print("The characters you have tried to enter do not qualify as a valid number.")
            msvcrt.getch()
            os.system("cls")
            continue
        if choice in (0, 1, 2):
            tutorial = choice
        else:
            print("The numbers you are trying to enter are invalid for this case.")
            msvcrt.getch()
            os.system("cls")
            continue

        break
    os.system("cls")
    while True:
        os.system("cls")
        print("Select Number Scheme")
        print("─────────────────────")
        print("1. Cycle: [x -> y]")
        print("2. Select: [1, 3, 9, 2]")
        print()
        
        choice = input("> ")
        mode = 2

        if choice.upper() == "EXIT":
            return "return"

        try:
            choice = int(choice)
        except:
            print("The characters you have tried to enter do not qualify as a valid number.")
            msvcrt.getch()
            os.system("cls")
            continue
        
        if choice in (1,2):
            mode = choice
        else:
            print("The numbers you are trying to enter are invalid for this case.")
            msvcrt.getch()
            os.system("cls")
            continue
           

        break

    while True:
        os.system("cls")
        print("     Quickspawn Multiple Accounts")
        print("    ──────────────────────────────")
        display_emails()
        print()

        selected = []

        if mode == 1:
            try:
                start = input("[Starting Number] > ")

                if start.upper() == "EXIT":
                    return "return"
                end = input("[Ending Number] > ")

                if end.upper() == "EXIT":
                    return "return"

                start = int(start)
                end = int(end)

            except:
                print("The characters you have tried to enter do not qualify as a valid number.")
                msvcrt.getch()
                os.system("cls")
                continue

            if start < 1 or end > fbAccounts.total_lines() or end < start:
                print("Invalid by a scope issue.")
                msvcrt.getch()
                os.system("cls")
                continue

            selected = list(range(start, end + 1))

        else:
            try:
                raw = input("> ")

                if raw.upper() == "EXIT":
                    return "return"

                selected = [int(x.strip()) for x in raw.split(",")]

            except:
                print("The characters you have tried to enter do not qualify as a valid number.")
                msvcrt.getch()
                os.system("cls")
                continue

            for number in selected:
                if number < 1 or number > fbAccounts.total_lines():
                    print("Attempted to access a non-existant account.")
                    msvcrt.getch()
                    return

        first = True
        os.system("cls")
        
        for number in selected:

            if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                print("\n[Ended Prematurely]")
                if mode == 1:
                    update_file_info(histlog=f"{start} -> {number}")
                else:
                    update_file_info(histlog=number)
                break

            if not first:
                time.sleep(3)

            raw = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"])
            name, email, key = raw.split("//")
            account_tuple = (name, email, key)
            
            Account = Inclient(account_tuple, casecode="quickspawn", tutorial=tutorial)
            thread = threading.Thread(target=Account.client_engine, daemon=True)
            thread.start()
            thread.join()

            if Account.casecode == "ERROR":
                print(f"{number}. {name if name else email} Closed Due To Crash")
                

            if Account.casecode == "REJECTED":
                print(f"Account {number}: [{name if name else email}] rejected by server.")
            

            if "SPAWNCARD" in Account.casecode:
                print(f"Account Number: {number}")
                print(f"{Account.casecode[1]}\n")

            first = False
        
        if mode == 1:
            update_file_info(histlog=f"{start} -> {end}")
        else:
            update_file_info(histlog=selected)
        
        print("[End Of Running]")
        print("────────────────")
        msvcrt.getch()
        break

def detect_donkeytown():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    
    while True:
        os.system("cls")
        print("Choose Scan Mode")
        print("───────────────────────────")
        print("1. Attempt Mainland Spawn")
        print("2. Attempt Donkeytown Spawn")
        print()
        
        choice = input("> ")
        donkeytown = True

        if choice.upper() == "EXIT":
            return "return"

        try:
            choice = int(choice)
        except:
            print("The characters you have tried to enter do not qualify as a valid number.")
            msvcrt.getch()
            os.system("cls")
            continue

        if choice == 1:
            donkeytown = False
            break

        if choice > 2 or choice < 1:
            print("The numbers you are trying to enter are invalid for this case.")
            msvcrt.getch()
            os.system("cls")
            continue
        break
    
    while True:
        os.system("cls")
        print("Select Number Scheme")
        print("─────────────────────")
        print("1. Cycle: [x -> y]")
        print("2. Select: [1, 3, 9, 2]")
        print()
        
        choice = input("> ")
        mode = 2

        if choice.upper() == "EXIT":
            return "return"

        try:
            choice = int(choice)
        except:
            print("The characters you have tried to enter do not qualify as a valid number.")
            msvcrt.getch()
            os.system("cls")
            continue

        if choice == 1:
            mode = 1
            break

        if choice > 2 or choice < 1:
            print("The numbers you are trying to enter are invalid for this case.")
            msvcrt.getch()
            os.system("cls")
            continue

        break

    while True:
        os.system("cls")
        print("    Detect For Donkeytown")
        print("   ────────────────────────")
        display_emails()
        print()

        selected = []

        if mode == 1:
            try:
                start = input("[Starting Number] > ")
                end = input("[Ending Number] > ")

                if start.upper() == "EXIT" or end.upper() == "EXIT":
                    return "return"

                start = int(start)
                end = int(end)

            except:
                print("The characters you have tried to enter do not qualify as a valid number.")
                msvcrt.getch()
                os.system("cls")
                continue

            if start < 1 or end > fbAccounts.total_lines() or end < start:
                print("Invalid by a scope issue.")
                msvcrt.getch()
                os.system("cls")
                continue

            selected = list(range(start, end + 1))

        else:
            try:
                raw = input("> ")

                if raw.upper() == "EXIT":
                    return "return"

                selected = [int(x.strip()) for x in raw.split(",")]

            except:
                print("The characters you have tried to enter do not qualify as a valid number.")
                msvcrt.getch()
                os.system("cls")
                continue

            for number in selected:
                if number < 1 or number > fbAccounts.total_lines():
                    print("Attempted to access a non-existant account.")
                    msvcrt.getch()
                    return

        first = True
        os.system("cls")
        
        for number in selected:

            if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                print("\n[Ended Prematurely]")
                if mode == 1:
                    update_file_info(histlog=f"{start} -> {number}")
                else:
                    update_file_info(histlog=number)
                return

            if not first:
                time.sleep(3)

            raw = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"])
            name, email, key = raw.split("//")
            account_tuple = (name, email, key)
            
            Account = Inclient(account_tuple, casecode="quickspawn")
            thread = threading.Thread(target=Account.client_engine, daemon=True)
            thread.start()
            thread.join()

            if Account.casecode == "ERROR":
                print(f"{number}. {name if name else email} Closed Due To Crash")
                msvcrt.getch()
                break
            if Account.casecode == "REJECTED":
                print(f"Account {number}: [{name if name else email}] rejected by server.")
                msvcrt.getch()
                break
            if "SPAWNCARD" in Account.casecode:
                print(f"Account Number: {number}")
                print(f"{Account.casecode[1]}\n")
                if "DONKEYTOWN" in Account.casecode[1]:
                    if donkeytown:
                        name, email, key = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"]).split("//")
                        FileBuilder(Filesaves["Dirs"]["Ohol"]["email ini"]).write(1, email)
                        FileBuilder(Filesaves["Dirs"]["Ohol"]["key ini"]).write(1, key)
                        run_game(Filesaves["Settings"]["default_executable"])
                        break
                else:
                    if donkeytown == False:
                        name, email, key = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"]).split("//")
                        FileBuilder(Filesaves["Dirs"]["Ohol"]["email ini"]).write(1, email)
                        FileBuilder(Filesaves["Dirs"]["Ohol"]["key ini"]).write(1, key)
                        run_game(Filesaves["Settings"]["default_executable"])
                        break
            
            first = False
        
        if mode == 1:
            update_file_info(histlog=f"{start} -> {end}")
        else:
            update_file_info(histlog=selected)
        
        print("[End Of Running]")
        print("────────────────")
        msvcrt.getch()
        break

def account_locking():
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    set_rgb(default_color)
    statuses = []
    controllers = {}
    display_lock = threading.Lock()

    for line_num in range(1, fbAccounts.total_lines() + 1):
        line = fbAccounts.read(line_num)
        if not line:
            continue
        raw = decrypt(line, Filesaves["Settings"]["password"])
        if not raw:
            continue
        try:
            name, email, key = raw.split("//")
            cleaned_name = (name or "").strip()
            if cleaned_name.lower() == "none" or not cleaned_name:
                ident = email.strip() if email and email.strip() else f"Acc{line_num}"
            else:
                ident = cleaned_name
        except:
            continue
        statuses.append(f"{ident}//Open")

    def redraw():
        with display_lock:
            os.system("cls" if os.name == "nt" else "clear")
            print("  ACCOUNT LOCKER")
            print("─" *55)
            for i, entry in enumerate(statuses, 1):
                ident, st = entry.split("//", 1)
                print(f"{i:3d} │ {ident:<40}  {st}")
            print("─" * 55)

    def start_locking(num: int):
        if num < 1 or num > len(statuses):
            return

        idx = num - 1
        ident, old = statuses[idx].split("//", 1)
        if old != "Open":
            return

        statuses[idx] = f"{ident}//Starting…"
        redraw()

        line = fbAccounts.read(num)
        if not line:
            statuses[idx] = f"{ident}//No data"
            redraw()
            return

        raw = decrypt(line, Filesaves["Settings"]["password"])
        if not raw:
            statuses[idx] = f"{ident}//Decrypt fail"
            redraw()
            return

        try:
            name, email, key = raw.split("//")
            cleaned_name = (name or "").strip()
            if cleaned_name.lower() == "none" or not cleaned_name:
                ident = email.strip() if email and email.strip() else f"Acc{num}"
            else:
                ident = cleaned_name
        except:
            statuses[idx] = f"{ident}//Parse error"
            redraw()
            return

        client = Inclient((name, email, key), tutorial=2)
        client.casecode = "account locking"

        stop_ev = threading.Event()

        def runner():
            final = "Disconnected"
            try:
                client.client_engine()
            except Exception:
                traceback.print_exc()
                final = "Engine crash"

            if client.casecode == "DIED":
                final = "Died"
            elif client.casecode == "REJECTED":
                final = "Rejected"
            elif client.casecode == "ERROR":
                final = "Error"
            elif stop_ev.is_set():
                final = "Stopped"

            with display_lock:
                statuses[idx] = f"{ident}//{final}"
                redraw()

        th = threading.Thread(target=runner, daemon=True)
        th.start()

        controllers[num] = {
            "thread": th,
            "stop": stop_ev,
            "client": client
        }

        statuses[idx] = f"{ident}//Locked"
        redraw()

    def stop_locking(num: int):
        if num not in controllers:
            return

        ident, _ = statuses[num - 1].split("//", 1)
        statuses[num - 1] = f"{ident}//Stopping…"
        redraw()

        ctrl = controllers.pop(num)
        ctrl["stop"].set()
        ctrl["thread"].join(timeout=8.0)

        statuses[num - 1] = f"{ident}//Open"
        redraw()

    def toggle(num: int):
        if num < 1 or num > len(statuses):
            return
        ident, state = statuses[num - 1].split("//", 1)

        if state == "Open":
            start_locking(num)
        elif state in ("Locked", "Starting…"):
            stop_locking(num)

    redraw()

    while True:
        try:
            raw = input("> ").strip()
            cmd = raw.upper()

            if cmd in ("EXIT", "QUIT"):
                for n in list(controllers.keys()):
                    stop_locking(n)
                time.sleep(0.4)
                print("\nAll lockers stopped.")
                return "return"

            if cmd in ("R", "REFRESH"):
                redraw()
                continue

            try:
                num = int(raw)
                toggle(num)
            except ValueError:
                redraw()

        except KeyboardInterrupt:
            print("\nInterrupted — cleaning up…")
            for n in list(controllers.keys()):
                stop_locking(n)
            time.sleep(0.6)
            return "interrupted"

        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(1)
            redraw()

class Inclient: # Always run as thread for consistancy
    update_file_info()
    def __init__(self, account_tuple, tutorial=0, casecode=None): # encrypted account contains name, email, key and is valuable in many cases for this function.
        self.account_tuple = account_tuple
        self.tutorial = tutorial
        self.casecode = casecode
        self.name, self.email, self.key = account_tuple
        self.key = self.key.replace("-","")
        # Threading
        self.stop_event = threading.Event()

    def client_engine(self):
        while True:
            # Memory
            self.Memory = {"MOTH CMD": {"p_id": None, "m_id": None, "m_name": None, "f_name": None}, "Player Count":None}
            self.OurLiveObject = {"CX": {"Tokens": None, "Excess": 0}, 
                        "PU": {"p_id": None, "po_id": None, "facing": None, "action": None, "action_target_x": None, "action_target_y": None, "o_id": None, "o_origin_valid": None,\
                        "o_origin_x": None, "o_origin_y": None, "o_transition_source_id": None, "heat": None, "done_moving_seqNum": None, "force": None, "x": None, "y": None, "age": None, "age_r": None, \
                        "move_speed": None, "clothing_set": None, "just_ate": None, "last_ate_id": None, "responsible_id": None, "held_yum": None, "held_learned": None},
                        "RACE & SEX": None,
                        }
                                
            # Memory
            ceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ceSocket.connect((Filesaves["Settings"]["server_ip"], Filesaves["Settings"]["port"]))
            ceSocket.setblocking(False)
            parser = StreamParser()


            while not self.stop_event.is_set():
                try:
                    

                    data = ceSocket.recv(4096)
                    if not data:
                        break

                    parser.feed(data)

                    for msg in parser.get_messages():
                        msg = msg.replace("#", "")
                        msg_split = msg.split()
                        msg_linesplit = msg.splitlines()

                        if not msg_split:
                            continue

                        header = msg_split[0]
                        del msg_split[0]
                        if msg_linesplit:
                            del msg_linesplit[0]

                        if header == "SN":
                            self.Memory["Player Count"] = msg_split[0]
                            Secret = msg_split[1]
                            Hash = HMAC_SHA1(Filesaves["Settings"]["server_password"], Secret)
                            Keyhash = HMAC_SHA1(self.key, Secret)
                            Login = f"LOGIN {Filesaves['Settings']['client']} {self.email} {Hash} {Keyhash} {self.tutorial}#"
                            ceSocket.sendall(Login.encode())

                        elif header == "ACCEPTED":
                            ceSocket.sendall("MOTH 0 0#".encode())

                        elif header in ("REJECTED", "NO_LIFE_TOKENS", "SHUTDOWN"):
                            self.casecode = "REJECTED"
                            print("Rejected")
                            msvcrt.getch()
                            self.stop_event.set()
                            break
                
                        # Messages In Order Of Recive
                        if header == "PU":
                            if not (self.OurLiveObject["PU"]["po_id"]): 
                                for field, value in zip(self.OurLiveObject["PU"], msg_linesplit[-1].split()):
                                    self.OurLiveObject["PU"][field] = value 
                                gender_id = int(self.OurLiveObject["PU"]["po_id"])
                                if gender_id in [19, 350, 1007]:
                                    race_gender = "White Female"
                                elif gender_id in [352, 347, 1008]:
                                    race_gender = "White Male"
                                elif gender_id in [1628, 2462]:
                                    race_gender = "Ginger Female"
                                elif gender_id in [3081, 3080, 2403]:
                                    race_gender = "Ginger Male"
                                elif gender_id in [351, 353, 1009]:
                                    race_gender = "Brown Female"
                                elif gender_id in [354, 355, 1010]:
                                    race_gender = "Brown Male"
                                elif gender_id in [2404, 2464]:
                                    race_gender = "Black Female"
                                elif gender_id in [1629, 3078, 3079]:
                                    race_gender = "Black Male"
                                elif gender_id in [3201]:
                                    race_gender = "Jason Developer"
                                else:
                                    race_gender = "Unknown Unknown"

                                self.OurLiveObject["RACE & SEX"] = race_gender
                        if header == "CS":
                            self.OurLiveObject["CX"]["Excess"] = int(msg_split[0])

                        if header == "CX":
                            self.OurLiveObject["CX"]["Tokens"] = int(msg_split[0])

                            
                        if header == "PS":
                            if "MOTHER" in msg and "/0" in msg:
                                if len(msg_split) == 10: # Fullstock
                                    self.Memory["MOTH CMD"]["p_id"] = msg_split[0]
                                    self.Memory["MOTH CMD"]["m_id"] = msg_split[6]
                                    self.Memory["MOTH CMD"]["m_name"] = msg_split[3]
                                    self.Memory["MOTH CMD"]["f_name"] = msg_split[4]
                                if len(msg_split) == 9: # No Last Name
                                    self.Memory["MOTH CMD"]["p_id"] = msg_split[0]
                                    self.Memory["MOTH CMD"]["m_id"] = msg_split[5]
                                    self.Memory["MOTH CMD"]["m_name"] = msg_split[3]
                                if len(msg_split) == 8: # No Name
                                    self.Memory["MOTH CMD"]["p_id"] = msg_split[0]
                                    self.Memory["MOTH CMD"]["m_id"] = msg_split[4]
                                if "NO MOTHER" in msg:
                                    self.Memory["MOTH CMD"]["p_id"] = msg_split[0]  
                                self.Memory["MOTH CMD"]["p_id"] = self.Memory["MOTH CMD"]["p_id"].replace("/0", "").strip()

                    if self.casecode == "account locking":
                        if (self.OurLiveObject["PU"]["po_id"]):
                            agedeci = float(self.OurLiveObject["PU"]["age"])
                            if agedeci <= 1.99:
                                ceSocket.sendall("/DIE".encode())
                    
                    if(self.casecode == "quickspawn"):
                        if(self.Memory["MOTH CMD"]["p_id"] and self.OurLiveObject["PU"]["po_id"] and self.OurLiveObject['CX']['Excess'] != None):
                            server_name = Filesaves["Memory"]["General"]["Server Name"].capitalize()
                            player_count = self.Memory["Player Count"]
                            race, sex = self.OurLiveObject["RACE & SEX"].split()


                            self.casecode = ["SPAWNCARD",f"{server_name} [{player_count}]\n"
                                            f"{self.name if self.name else self.email}\n"
                                            f"{'─' * len(server_name)}{'─'*len(player_count)}───\n"
                                            f"Person ID: {self.Memory["MOTH CMD"]["p_id"]}\n"
                                            f"Location: {'DONKEYTOWN' if self.OurLiveObject['CX']['Excess'] > 0 else 'MAINLAND'}\n"
                                            f"Family: {self.Memory["MOTH CMD"]["f_name"]}\n"  
                                            f"Age: {self.OurLiveObject["PU"]["age"]}\n"
                                            f"Race: {race}\n"
                                            f"Gender: {sex}"
                                            ]
                            self.stop_event.set()
                            break
                except BlockingIOError:
                    continue
                except Exception as e:
                    print("Full Error Traceback:")
                    traceback.print_exc()
                    msvcrt.getch()
                    self.casecode = "ERROR"
                    break
            if not self.casecode == "account locking":
                ceSocket.close()
                return

    def stop_flag(self):
        self.stop_event.set()

class Phexclient:
    def __init__(self, account_tuple):
        self.account_tuple = account_tuple
        self.name, self.email, self.key = account_tuple
        self.key = self.key.replace("-","")
        self.life_id = 1
        self.channel = Filesaves["Settings"][""]
    def phex_main():
        pass

def phex_global_chat():
    set_rgb(default_color)
    fbAccounts = FileBuilder(Filesaves["Dirs"]["Accounts"])
    
    os.system("cls")
    print("     Select Account")
    print("    ────────────────")
    display_emails()
    print()
    
    try: 
        number = input("> ")
        if number.upper() == "EXIT":
            return "return"
        number = int(number)
        if number < 1 or number > fbAccounts.total_lines():
            print("Attempted to select a non-existant account..")
            msvcrt.getch()
            return
    except:
        print("The characters you have tried to enter do not qualify as a valid number.")
        msvcrt.getch()
        return  
    
    name, email, key = decrypt(Filesaves["Memory"]["Accounts"][number-1], Filesaves["Settings"]["password"]).split("//")



def initialize():
    update_file_info() # most important piece
    os.system(f'title {terminal_name}')
    # Menu
    mbMain = MenuBuilder(
        main_menu=True,
        options={
            "DebugTest ?": {"Function": Debug, "Single Run": True, "Key": "DEBUG"},
            "About ?": {"Function": About, "Single Run": True, "Key": "A"},
            "History": {"Function": History, "Single Run": True, "Key": "H"},
            "Clear History 🗐": {"Function": lambda: open(Filesaves["Dirs"]["History"], 'w').close(), "Single Run": True, "Key": "CLR"},
            "Game Cfg": {"Function": client_settings, "Single Run": False, "Key": "CFG"},
            "Onelife Settings": {"Function": onelife_settings, "Single Run": False, "Key": "GS"},
            "Display_All": {"Function": display_all_accounts, "Single Run": True, "Key": "?X"}, 
            "Manually Update Info": {"Function": lambda: update_file_info(), "Single Run": True, "Key": "U"},
            "Add Accounts +": {"Function": add_accounts, "Single Run": False, "Key": "1"},           
            "Remove Accounts -": {"Function": delete_accounts, "Single Run": False, "Key": "2"},
            "Edit Accounts #": {"Function": edit_accounts, "Single Run": False, "Key": "3"},
            "Duplicate Detector": {"Function": duplicate_detector, "Single Run": True, "Key": "4"},
            "Valid Account Detector": {"Function": active_account_detector, "Single Run": True, "Key": "5"},
            "Check Server Reflector": {"Function": read_server_reflector, "Single Run": True, "Key": "SRV"},
            "Launch": {"Function": lambda: run_game(Filesaves["Settings"]["default_executable"]), "Single Run": True, "Key": "L"},
            "Select Accounts": {"Function": select_account, "Single Run": False, "Key": "6"},
            "Cycle Accounts": {"Function": select_multiple_accounts, "Single Run": False, "Key": "7"},
            "Quickspawn Accounts": {"Function": quickspawn_account, "Single Run": False, "Key": "8"},
            "Quickspawn Multiple": {"Function": quickspawn_multiple, "Single Run": False, "Key": "9"},
            "Detect For Donkeytown": {"Function": detect_donkeytown, "Single Run": False, "Key": "10"},
            "Account Locking Menu": {"Function": account_locking, "Single Run": False, "Key": "LK"},
            "Phex": {"Function": phex_global_chat, "Single Run": False, "Key": "PHEX"},
            "Genescore Checker": {"Function": gene_score_checker, "Single Run": False, "Key": "SCR"},
        },
        color=default_color,
        replacement_display = (
            f"{terminal_name} {version} [Accounts Total: {len(Filesaves['Memory']['Accounts'])}]\n"
            "────────────────────────────────────────────────────────────────────────\n"
            "Client Utilities:\n"
            "[A] About           [H] History             [CLR] Clear History\n"
            "[U] Update Info     [CFG] Client Config     [GS] Game Settings\n"
            "[?X] Display All Accounts\n\n"
            
            
            "Tools:\n"
            "[SRV] Check Server Reflector ᯤ    [SCR] Read Genescores\n\n"
            
            f"Account Manager:\n"
            "[1] Add Accounts                   [2] Delete Accounts\n"
            "[3] Edit Accounts                  [4] Duplicate Detector\n"
            "[5] Active Account Detector ᯤ     [LK] Lock Accounts ➴⚷\n\n"
            
            "Account Launcher:\n"
            "[L] Launch     [6] Select Accounts     [7] Cycle Accounts\n\n"
            
            "Automated Spawning:\n"
            "[8] Quick Spawn     [9] Quick Spawn Multiple    [10] Spawn Selector\n"
            "────────────────────────────────────────────────────────────────────────\n"
        )
    )
    mbMain.menu()
    



#init
initialize()
