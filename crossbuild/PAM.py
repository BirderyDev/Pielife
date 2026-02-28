import base64
from datetime import datetime

now = datetime.now()
curtime_formatted = f"{now.month}/{now.day}/{now.strftime('%y')} {now.strftime('%I:%M %p').lstrip('0')}"

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

pam_folder = "Pam account data (DO NOT SHARE)"
verison_number = 2
discord_link = "https://discord.gg/wAahM9r4CV"
github_repo = "https://github.com/SSCServicesGit/Pielife-SSC"

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

class Onelife:
    settings_folder = "settings"
    path_email = os.path.join(os.path.dirname(__file__), "settings", "email.ini")
    path_key = os.path.join(os.path.dirname(__file__), "settings", "accountKey.ini")
    server_ip = None
    server_port = None
    server_password = None

class Client:
    settings = os.path.join(pam_folder, "pam.cfg")
    accinfo = os.path.join(pam_folder, "accounts.txt")
    history = os.path.join(pam_folder, "history.log")
    private_key = "Pielife_unset_key"
    private_key_backup = None
    server_password = "testPassword"
    directory = None
    tag = None
    default_settings = (
        "executable = None\n"
        "server = bigserver2.onehouronelife.com\n"
        "port = 8005\n"
        "serverPassword = testPassword\n"
        f"privateKey = private_key_default\n"
        "clientTag = automata"
    )

class Special_Functions:
    @staticmethod

    def int_to_roman(num):
        values = [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I")
        ]

        result = ""

        for value, symbol in values:
            while num >= value:
                result += symbol
                num -= value

        return result

    def print_rgb(rgb, text=""):
        r, g, b = rgb
        print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")

    @staticmethod
    def encrypt(plaintext: str, key: str) -> str:
        encrypted_bytes = bytearray()
        key_bytes = key.encode()
        for i, char in enumerate(plaintext.encode()):
            encrypted_bytes.append(char ^ key_bytes[i % len(key_bytes)])
        return base64.b64encode(encrypted_bytes).decode()

    @staticmethod
    def decrypt(ciphertext: str, key: str) -> str:
        encrypted_bytes = base64.b64decode(ciphertext.encode())
        decrypted_bytes = bytearray()
        key_bytes = key.encode()
        for i, char in enumerate(encrypted_bytes):
            decrypted_bytes.append(char ^ key_bytes[i % len(key_bytes)])
        return decrypted_bytes.decode()

    @staticmethod
    def return_current_time():
        pass

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
                print("\nInvalid Option...")
                input("Press Enter...")
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
    
def set_vars():
    setvar = SFE(Client.settings)
    crypt = SFE(Client.accinfo)
    try:
        Onelife.server_ip = socket.gethostbyname(setvar.read_equality("server"))
        Onelife.server_port = int(setvar.read_equality("port"))
    except:
        print("Warning - Internet Info Invalid... Internet Spawn functions will not be functional")
        msvcrt.getch()
    
    # Ensure passwords and keys are set
    Client.directory = setvar.read_equality("executable")
    Client.tag = setvar.read_equality("clientTag")
    Client.server_password = setvar.read_equality("serverPassword") or "testPassword"
    Client.private_key = setvar.read_equality("privateKey") or "private_key_default"
    Client.private_key_backup = Client.private_key

    # Also sync to Onelife
    Onelife.server_password = Client.server_password

    try:
        total = crypt.total_lines()
        for i in range(1, total + 1):
            try:
                raw = crypt.read(i)
                if raw.startswith("CVXXVI"):
                    crypt.write(i, pack_key(raw))
            except:
                pass
    except:
        pass

def about():
    Special_Functions.print_rgb((255, 255, 255), f"Pielife Account Manager (PAM I{verison_number})\n")
    Special_Functions.print_rgb((255, 255, 255), "PAM is a program made by the mod developer Shady.")
    Special_Functions.print_rgb((255, 255, 255), "This program is meant to make the management of accounts eaiser for those who need its services.")
    Special_Functions.print_rgb((255, 255, 255), f"For more information please visit the offical discord server: {discord_link}")
    Special_Functions.print_rgb((255, 255, 255), f"For information on the opensource mod Pielife please, visit the github release page: {github_repo}")
    msvcrt.getch()

def history():
    history_file = SFE(Client.history)
    print("Account History 🗐\n")
    for i in range(1, history_file.total_lines() + 1):
        raw = history_file.read(i)
        try:
            Order, Email, Date = raw.split("//")
            print(f"{i}. Account: {Order}. {Email}")
            print(f"Date: {Date}\n")
            
        except:
            print(f"Corrupt history line {i}")
    msvcrt.getch()

def run_account(email, key):
    SFE(Onelife.path_email).write(1, email)
    SFE(Onelife.path_key).write(1, key)
    subprocess.Popen(Client.directory, shell=True)


def settings():
    settings_file = SFE(Client.settings)
    while True:
        os.system("cls")
        print("PAM Settings")
        print("------------")
        for i in range(1, settings_file.total_lines() + 1):
            print(f"{i}. {settings_file.read(i)}")
            print("------------------------")
        print("Enter the number of the setting you'd like to edit or type 'EXIT' to return.")
        
        uinput = input("> ").strip()
        if uinput.upper() == "EXIT":
            return
        
        try:
            index = int(uinput)
            if index < 1 or index > settings_file.total_lines():
                raise ValueError
        except ValueError:
            print("Invalid Number...")
            msvcrt.getch()
            continue

        old_line = settings_file.read(index)
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

        settings_file.write_equality(key, new_value)
        print("\nSetting updated...")
        set_vars()
        msvcrt.getch()

def onelife_settings():
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
            file_path = os.path.join(Onelife.settings_folder, f"{setting_name}.ini")
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
                file_path = os.path.join(Onelife.settings_folder, f"{name}.ini")
                SFE(file_path).write(1, settings_data[name])
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
        file_path = os.path.join(Onelife.settings_folder, f"{selected}.ini")
        current_value = settings_data[selected]
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                current_value = f.read().strip()
        print(f"Current value: {selected} = {current_value}")
        new_value = input("New value: ").strip()
        if new_value:
            SFE(file_path).write(1, new_value)

def unpack_key(value):
    try:
        return Special_Functions.decrypt(value, Client.private_key)
    except:
        return value

def pack_key(value):
    return Special_Functions.encrypt(value, Client.private_key)

def display_keys():
    account_file = SFE(Client.accinfo)
    for i in range(1, account_file.total_lines() + 1):
        current = account_file.read(i)
        try:
            current = unpack_key(current)
            parts = current.split("//")
            if len(parts) < 4:
                raise
            proofsum, name, email, key = parts
        except:
            print(f"Corrupt account at line {i}")
            continue
        print(f"{i}. Account Name: {'N/A' if name.upper() == 'NONE' else name}")
        print(f"Email: {email}")
        print(f"Key: {key}\n")
    msvcrt.getch()

def display_emails():
    account_file = SFE(Client.accinfo)
    for i in range(1, account_file.total_lines() + 1):
        current = account_file.read(i)
        try:
            current = unpack_key(current)
            parts = current.split("//")
            if len(parts) < 4:
                raise
            proofsum, name, email, key = parts
        except:
            print(f"{i} CorruptLine")
            continue
        print(f"{i} {email if name.upper() == 'NONE' else name}")

def add_accounts():
    print("[Add Accounts + ]:")
    display_emails()
    print("\nType 'None' to leave nameless.")
    name = input("\nNAME > ")
    if name.upper() == "EXIT":
        return "return"
    if name.upper() == "None":
        name = name.upper()
    email = input("\n[Acc Email] > ")
    key = input("\n[Acc Key] > ")
    assembly = f"CVXXVI//{name}//{email}//{key}".strip()
    SFE(Client.accinfo).write("L", pack_key(assembly))

def delete_accounts():
    Account = SFE(Client.accinfo)
    print("\033[38;2;255;0;0m", end="")
    print("[Remove Accounts - ]")
    print("----------------------")
    print("\033[38;2;166;0;0m", end="")
    display_emails()
    try:
        userInput = input("\n> ")
        if userInput.upper() == "EXIT":
            return "return"
        numberValue = int(userInput)
    except:
        print("Invalid Input...")
        msvcrt.getch()
        return
    if numberValue < 1 or numberValue > Account.total_lines():
        print("Not a valid account")
        msvcrt.getch()
        return
    print(f"Are you sure you want to delete account {numberValue}? [Y/N]")
    userInput = input("\n> ")
    if userInput.lower() == "y":
        Account.delete(numberValue)
        print(f"Account {numberValue} deleted.")
        msvcrt.getch()
    else:
        print("Deletion cancelled.")
        msvcrt.getch()
        return


def edit_accounts():
    Account = SFE(Client.accinfo)
    while True:
        os.system("cls")
        print("[EDIT ACCOUNTS]\n")
        for i in range(1, Account.total_lines() + 1):
            try:
                current = unpack_key(Account.read(i))
                parts = current.split("//")
                if len(parts) < 4:
                    print(f"{i}. Corrupt account")
                    continue
                proofsum, name, email, key = parts
                print(f"{i}. {email if name.upper() == 'NONE' else name}")
            except:
                print(f"{i}. Corrupt account")
        print("\nSelect account number to edit (or type 'exit'):")
        userInput = input("> ").strip()
        if userInput.lower() == "exit":
            return "return"
        try:
            numberValue = int(userInput)
        except:
            print("Invalid input.")
            msvcrt.getch()
            continue
        if numberValue < 1 or numberValue > Account.total_lines():
            print("Invalid account number.")
            msvcrt.getch()
            continue
        rawAccountData = unpack_key(Account.read(numberValue))
        try:
            parts = rawAccountData.strip().split("//")
            if len(parts) < 4:
                raise
            proofsum, name, email, key = parts
        except:
            print("Corrupt account data.")
            msvcrt.getch()
            continue
        while True:
            os.system("cls")
            print(f"[Editing Account {numberValue}]\n")
            print(f"1. Name : {name}")
            print(f"2. Email: {email}")
            print(f"3. Key  : {key}")
            print("\nSelect field to edit (or type 'exit'):")
            userInput = input("> ").strip().lower()
            if userInput.upper() == "EXIT":
                break
            fields = {"1": "Name", "2": "Email", "3": "Key"}
            if userInput not in fields:
                print("Invalid option.")
                msvcrt.getch()
                continue
            new_value = input(f"New {fields[userInput]}: ").strip()
            confirm = input("Confirm changes? [y/n]: ").lower()
            if confirm != "y":
                continue
            if userInput == "1":
                name = new_value
            elif userInput == "2":
                email = new_value
            elif userInput == "3":
                key = new_value
            try:
                fullAccountDetails = f"CVXXVI//{name}//{email}//{key}"
                Account.write(numberValue, pack_key(fullAccountDetails))
                print("Account updated successfully!")
                msvcrt.getch()
            except:
                print("Failed to write account:")
                msvcrt.getch()

def write_to_history(order, name):  
    history = SFE(Client.history)
    value = f"{order}//{name}//{curtime_formatted}"
    history.write("L", value)
    os.system(f'title {name}')

def select_accounts():
    Account = SFE(Client.accinfo)
    print("[Selecting Accounts @]:\n")
    display_emails()

    try:
        userInput = input("\n> ")

        if userInput.upper() == "EXIT":
            return "return"
        
        userInput = int(userInput)

    except:
        print("Invalid..")
        msvcrt.getch()
        return
    if userInput < 1 or userInput > Account.total_lines():
        print("Invalid...")
        msvcrt.getch()
        return
    
    accountInfo = Account.read(userInput)
    accountInfo = unpack_key(accountInfo)
    try:
        parts = accountInfo.split("//")
        if len(parts) < 4:
            raise
        proofsum, name, email, key = parts
    except:
        print("Corrupt account data")
        msvcrt.getch()
        return
    


    try:
        run_account(email, key)
        write_to_history(userInput, name if name else email)
    except:
        print(f"Failed to launch..")
        msvcrt.getch()
        return "return"

def cycle_accounts():
    Account = SFE(Client.accinfo)

    print("[Select a cycle mode]")
    print("1. Line, Example: [Start: 1 -> End: 6]")
    print("2. Set, Example: [2, 3, 5]")
    
    mode = input("> ").strip()
    if mode.upper() == "EXIT":
        return "return"

    try:
        mode = int(mode)
    except:
        print("Invalid...")
        msvcrt.getch()
        return

    if mode not in (1, 2):
        print("Invalid...")
        msvcrt.getch()
        return

    print("\n[Spawn Accounts ↻]:\n")
    display_emails()

    if mode == 1:
        try:
            start = input("\nCycle Start > ").strip()
            if start.upper() == "EXIT":
                return "return"
            start = int(start)

            end = input("Cycle End > ").strip()
            if end.upper() == "EXIT":
                return "return"
            end = int(end)

            if start < 1 or start > Account.total_lines():
                print("You can't start with this number!")
                msvcrt.getch()
                return
            if end < start or end > Account.total_lines():
                print("You can't end with this number!")
                msvcrt.getch()
                return
        except:
            print("Must be a number!")
            msvcrt.getch()
            return

        selected_ids = list(range(start, end + 1))

    else:
        print("\nEnter Set: x, x, x, etc.. (Set can repeat)")
        raw = input("> ")

        try:
            selected_ids = []
            for part in raw.split(","):
                num = int(part.strip())
                if 1 <= num <= Account.total_lines():
                    selected_ids.append(num)
        except:
            print("Invalid format likely..")
            msvcrt.getch()
            return

    first_run = True

    for i in selected_ids:
        if not first_run:
            time.sleep(4)
        else:
            first_run = False

        if msvcrt.kbhit():
            if msvcrt.getch() == b'\r':
                print("\n[Cycle stopped by you.]")
                msvcrt.getch()
                return

        accountInfo = Account.read(i)
        accountInfo = unpack_key(accountInfo)

        try:
            parts = accountInfo.split("//")
            if len(parts) < 4:
                print(f"Corrupt account data - Account {i}")
                continue

            proofsum, name, email, key = parts
            key = key.replace("-", "")
        except:
            print(f"Corrupt account data - Account {i}")
            continue

        run_account(email, key)

    if mode == 1:
        write_to_history(i, name if name else email)
    else:
        write_to_history(selected_ids, name if name else email)

    msvcrt.getch()

class Locker:
    def __init__(self, email, key, name=None, server_ip=None, serverPort=None,
                 server_password=None, tutorial=1, login_only=True, Lockmode=True):
        self.email = email
        self.key = key
        self.server_ip = server_ip or Onelife.server_ip
        self.serverPort = serverPort or Onelife.server_port
        self.server_password = server_password or Onelife.server_password
        self.tutorial = tutorial
        self.login_only = login_only
        self.name = name
        self.Lockmode = Lockmode

        # Start the account thread
        self.thread = threading.Thread(target=self.account, daemon=True)
        self.thread.start()

    def account(self):
        TIMEOUT = 5

        while self.Lockmode:  # Outer reconnect loop
            try:

                # Initialize variables
                login_value = 0
                known_players = {}
                Accepted = False
                GOAL = "None"
                SELF_ID = None
                MOTHER = None
                SELF_NAME = None
                self.Donkeytown = "No"
                last_received = time.time()

                # Connect to server
                try:
                    acc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    acc_socket.connect((self.server_ip, self.serverPort))
                except:
                    print(f"[{self.email}] Failed to connect to server, terminating account session..")
                    msvcrt.getch()
                    return

                acc_socket.setblocking(False)
                buffer = bytes()

                while self.Lockmode:  # Inner loop for reading bytes
                    # Check for timeout
                    if time.time() - last_received > TIMEOUT:
                        raise ConnectionError("Server stopped sending messages (timeout)")

                    new_byte = receive_next_byte(acc_socket)
                    if new_byte is False:
                        raise ConnectionError("Disconnected from server")

                    while new_byte:
                        buffer += new_byte

                        if new_byte == b'#':
                            msg = format_packet(acc_socket, buffer).replace("#", "")

                            msg_split = msg.split()
                            msg_linesplit = msg.splitlines()
                            header = msg_split[0]
                            del msg_linesplit[0]
                            del msg_split[0]

                            last_received = time.time()

                            if header == "SN":
                                Secret = msg_split[1]
                                Hash = HMAC_SHA1(self.server_password, Secret)
                                Keyhash = HMAC_SHA1(self.key, Secret)
                                Login = f"LOGIN client_{Client.tag} {self.email} {Hash} {Keyhash} {self.tutorial}#"
                                acc_socket.sendall(Login.encode())

                            elif header == "REJECTED":
                                self.Lockmode = False
                                
                            
                            elif header == "NO_LIFE_TOKENS":
                                self.Lockmode = False

                            elif header == "SD":
                                self.Lockmode = False
                            elif header == "SHUTDOWN":
                                self.Lockmode = False

                            buffer = bytes()

                        new_byte = receive_next_byte(acc_socket)

            except:
                if self.Lockmode:
                    time.sleep(2)
                    continue
                else:
                    return

class PAM_Automated_Account:
    def __init__(self, email, key, name=None, server_ip=None, serverPort=None,
                 server_password=None, tutorial=0, login_only=False,filter_donkey=0, Family_filter=None, acc=None):
        self.email = email
        self.key = key
        self.server_ip = server_ip or Onelife.server_ip
        self.serverPort = serverPort or Onelife.server_port
        self.server_password = server_password or Onelife.server_password
        self.tutorial = tutorial
        self.login_only = login_only
        self.name = name
        self.MOTHER_FAMILY = None
        self.Donkeytown = "No"
        self.spawncard = None
        self.filter_donkey = filter_donkey
        self.Family_filter = Family_filter
        self.acc=acc

        # Immediately process the account
        self.flag = self.account()

    def account(self):

        login_value = 0
        SELF_ID = None
        SELF_PID = None
        SELF_AGE = None


        # Connect to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.serverPort))
        s.setblocking(False)
        buffer = bytes()
        once = False # ONCE CODE!!!!!!!
        while True:     
            new_byte = receive_next_byte(s)
            if new_byte is False:
                break
            while new_byte:
                buffer += new_byte
                if new_byte == b'#':
                    msg = format_packet(s, buffer).replace("#", "")
                    if not "MC" in msg.split()[0]:
                        msg = msg.replace("#", "")

                    msg_split = msg.split()
                    msg_linesplit = msg.splitlines()
                    header = msg_split[0]
                    del msg_split[0]
                    del msg_linesplit[0]

                    if header == "SN":
                        Secret = msg_split[1]
                        Hash = HMAC_SHA1(self.server_password, Secret)
                        Keyhash = HMAC_SHA1(self.key, Secret)
                        Login = f"LOGIN client_{Client.tag} {self.email} {Hash} {Keyhash} {self.tutorial}#"

                        s.sendall(Login.encode())

                    elif header == "ACCEPTED":
                        pass

                    if once == True: # ONCE TRIGGER!!!!!
                        NAME = "GOWRI BENAVIDES"
                        NAME = NAME.upper()
                        s.sendall(f"SAY 0 0 CURSE {NAME}#".encode())
                        once = True

                    elif header in ["REJECTED", "NO_LIFE_TOKENS", "SD"]:
                        return  

                    elif header == "PU" and not SELF_ID:
                        if self.login_only:
                            s.sendall("MOTH 0 0#".encode())
                        SELF_ID = msg_linesplit[-1].split()[0]
                        SELF_PID = msg_linesplit[-1].split()[1]
                        SELF_AGE = msg_linesplit[-1].split()[16]
                        login_value += 1
                    
                    if header == "CX" and "1#" in msg_split:
                        self.Donkeytown = "No"
                    if header == "CS":
                        self.Donkeytown = "Yes"

                    elif header == "PS" and self.login_only and SELF_ID:
                        if SELF_ID.split()[0] == msg_split[0].replace("/0", ""):
                            MOTHER = " ".join(msg_split[1:])
                            login_value += 1
                            mother_parts = MOTHER.strip().split()
                            MOTHER_PID = None
                            for i, part in enumerate(mother_parts):
                                if part.isdigit():
                                    MOTHER_PID = part
                                    pid_index = i
                                    break
                            if MOTHER_PID is not None:
                                name_parts = mother_parts[2:pid_index]
                                if len(name_parts) >= 2:
                                    self.MOTHER_FAMILY = name_parts[1]
                                elif len(name_parts) == 1:
                                    self.MOTHER_FAMILY = name_parts[0]
                            else:
                                self.MOTHER_FAMILY = "NONE"

                    # Generate spawncard when ready
                    if self.login_only and login_value == 2:
                        obj_id = int(SELF_PID)
                        if obj_id in [19, 350, 1007]:
                            race_gender = "WHITEF"
                        elif obj_id in [352, 347, 1008]:
                            race_gender = "WHITEM"
                        elif obj_id in [1628, 2462]:
                            race_gender = "GINGERF"
                        elif obj_id in [3081, 3080, 2403]:
                            race_gender = "GINGERM"
                        elif obj_id in [351, 353, 1009]:
                            race_gender = "BROWNF"
                        elif obj_id in [354, 355, 1010]:
                            race_gender = "BROWNM"
                        elif obj_id in [2404, 2464]:
                            race_gender = "BLACKF"
                        elif obj_id in [1629, 3078, 3079]:
                            race_gender = "BLACKM"
                        else:
                            race_gender = "UNKNOWN"

                        if race_gender != "UNKNOWN":
                            race = race_gender[:-1]
                            gender = "FEMALE" if race_gender.endswith("F") else "MALE"
                        else:
                            race = "UNKNOWN"
                            gender = "UNKNOWN"

                        self.spawncard = (
                            f"{self.email if not self.name or self.name.strip().lower() == 'none' else self.name}\n"
                            "=======================\n"
                            f"PERSONAL ID: {SELF_ID}\n"
                            f"DONKEYTOWN?: {self.Donkeytown.upper()}\n"
                            f"FAMILY NAME: {self.MOTHER_FAMILY}\n"
                            f"RACE: {race}\n"
                            f"SEX: {gender}\n"
                            f"AGE: {SELF_AGE}"
                        )
   
                        if self.filter_donkey == 0:
                            return

                        elif self.filter_donkey == 1:  # DT only
                            if self.Donkeytown == "Yes":  # DT → ok
                                run_account(self.email, self.key)
                                return "Done"
                            else:  # Mainland → kill
                                s.sendall("DIE 0 0#".encode())
                                return

                        elif self.filter_donkey == 2:  # Mainland only
                            if self.Donkeytown == "No":  # Mainland → ok
                                run_account(self.email, self.key)
                                return "Done"
                            else:  # DT → kill
                                s.sendall("DIE 0 0#".encode())
                                return
                    buffer = bytes()
                new_byte = receive_next_byte(s)

def quick_spawn():
    Account = SFE(Client.accinfo)
    print("[SELECTING ACCOUNTS ▼]:\n")
    display_emails()
    try:
        userInput = input("\n> ").strip()
        if userInput.upper() == "EXIT":
            return "return"
        userInput = int(userInput)
    except:
        print("Not a valid input")
        msvcrt.getch()
        return
    if userInput < 1 or userInput > Account.total_lines():
        print("Invalid Account Number")
        msvcrt.getch()
        return
    accountInfo = Account.read(userInput)
    accountInfo = unpack_key(accountInfo)
    try:
        parts = accountInfo.split("//")
        if len(parts) < 4:
            raise
        proofsum, name, email, key = parts
        key = key.replace("-", "")
    except:
        print("Corrupt account data")
        msvcrt.getch()
        return

    Spawn = PAM_Automated_Account(email, key, name=name, login_only=True)
    while True:
        try:
            os.system("cls")
            print(f"{userInput}. {Spawn.spawncard}")
            write_to_history(userInput, name if name else email)
            print("> ")
            msvcrt.getch()
            return
        except:
            continue

def spawn_multiples():
    Account = SFE(Client.accinfo)

    print("[Select a cycle mode]")
    print("1. Line, Example: [Start: 1 -> End: 6]")
    print("2. Set, Example: [2, 3, 5]")
    
    mode = input("> ").strip()
    if mode.upper() == "EXIT":
        return "return"

    try:
        mode = int(mode)
    except:
        print("Invalid...")
        msvcrt.getch()
        return

    if mode not in (1, 2):
        print("Invalid...")
        msvcrt.getch()
        return

    tutorial = 0
    os.system("cls")
    print("Tutorial?")
    print("0. No")
    print("1. Tut1")
    print("2. Tut2")
    
    tutorial = input("> ").strip()
    if tutorial.upper() == "EXIT":
        return "return"

    try:
        tutorial = int(tutorial)
    except:
        print("Invalid...")
        msvcrt.getch()
        return

    if tutorial not in (0, 1, 2):
        print("Invalid...")
        msvcrt.getch()
        return

    print("\n[Spawn Accounts ↻]:\n")
    display_emails()

    # -------- MODE 1: RANGE -------- #
    if mode == 1:
        try:
            start = input("\nCycle Start > ").strip()
            if start.upper() == "EXIT":
                return "return"
            start = int(start)

            end = input("Cycle End > ").strip()
            if end.upper() == "EXIT":
                return "return"
            end = int(end)

            if start < 1 or start > Account.total_lines():
                print("You can't start with this number!")
                msvcrt.getch()
                return
            if end < start or end > Account.total_lines():
                print("You can't end with this number!")
                msvcrt.getch()
                return
        except:
            print("Must be a number!")
            msvcrt.getch()
            return

        selected_ids = list(range(start, end + 1))


    else:
        print("\nEnter Set: x, x, x, etc.. (Set can repeat)")
        raw = input("> ")

        try:
            selected_ids = []
            for part in raw.split(","):
                num = int(part.strip())
                if 1 <= num <= Account.total_lines():
                    selected_ids.append(num)
        except:
            print("Invalid format likely..")
            msvcrt.getch()
            return

    os.system("cls")
    for i in selected_ids:
        if msvcrt.kbhit():
                        if msvcrt.getch() == b'\r':
                            print("\n[Cycle stopped by you.]")
                            msvcrt.getch()
                            return

        accountInfo = Account.read(i)
        accountInfo = unpack_key(accountInfo)

        try:
            parts = accountInfo.split("//")
            if len(parts) < 4:
                print(f"Corrupt account data - Account {i}")
                continue

            proofsum, name, email, key = parts
            key = key.replace("-", "")
        except:
            print(f"Corrupt account data - Account {i}")
            continue

        Spawn = PAM_Automated_Account(email, key, name=name, login_only=True, tutorial=tutorial,acc=i)

        
        print(f"{i}. {Spawn.spawncard}")
        
        print("> ")
    if(mode == 1):
        write_to_history(i, name if name else email)
    else:
        write_to_history(selected_ids, name if name else email)
    msvcrt.getch()
        




    return

def lock_accounts():
    Account = SFE(Client.accinfo)  
    local_bank = {}
    input_buffer = ""

    while True:

        os.system('cls' if os.name == 'nt' else 'clear')
        print("[LOCKING MENU] (must remain open)\n")

 
        for i in range(1, Account.total_lines() + 1):
            current = Account.read(i)
            try:
                current = unpack_key(current)
                parts = current.split("//")
                if len(parts) < 4:
                    raise
                proofsum, name, email, keystr = parts
            except:
                print(f"{i} Corrupt Line")
                continue

            display_name = email if name.upper() == "NONE" else name
            lock_status = "[LOCKED]" if email in local_bank and local_bank[email].Lockmode else "[UNLOCKED]"
            print(f"{i} {display_name} {lock_status}")

        print(f"\n> {input_buffer}", end="", flush=True)


        while msvcrt.kbhit():
            char = msvcrt.getch()
            if char == b'\r':
                userInput = input_buffer.strip()
                input_buffer = ""
                if userInput.upper() == "EXIT":
               
                    for acc in local_bank.values():
                        acc.Lockmode = False
                    return
                if not userInput.isdigit():
                    break
                index = int(userInput)
                if index < 1 or index > Account.total_lines():
                    break

            
                accountInfo = Account.read(index)
                accountInfo = unpack_key(accountInfo)
                parts = accountInfo.split("//")
                if len(parts) < 4:
                    break
                proofsum, name, email, keystr = parts
                keystr = keystr.replace("-", "")

                if email in local_bank:
                    acc_obj = local_bank[email]
                    acc_obj.Lockmode = not acc_obj.Lockmode  
                else:
                    acc_obj = Locker(email, keystr, name=name, Lockmode=True)
                    local_bank[email] = acc_obj
            elif char == b'\x08':  # Backspace
                input_buffer = input_buffer[:-1]
            else:
                try:
                    input_buffer += char.decode("utf-8")
                except:
                    pass

        time.sleep(.5)  

def detect_dt():
    Account = SFE(Client.accinfo)

    print("[Select a cycle mode]")
    print("1. Line, Example: [Start: 1 -> End: 6]")
    print("2. Set, Example: [2, 3, 5]")
    
    mode = input("> ").strip()
    if mode.upper() == "EXIT":
        return "return"

    try:
        mode = int(mode)
    except:
        print("Invalid...")
        msvcrt.getch()
        return

    if mode not in (1, 2):
        print("Invalid...")
        msvcrt.getch()
        return

    os.system("cls")

    num = 0
    while True:
        print("[DT or Mainland spawn?]")
        print("1. DT")
        print("2. Mainland")
        uinput = input("> ").strip()
        if uinput.upper() == "EXIT":
            return "return"

        if uinput == "1":
            num = 1
            break
        if uinput == "2":
            num = 2
            break
        
        print("invalid number..")
        msvcrt.getch()
        os.system("cls")

    os.system("cls")

    print("\n[Spawn Accounts ↻]:\n")
    display_emails()


    if mode == 1:
        try:
            start = input("\nCycle Start > ").strip()
            if start.upper() == "EXIT":
                return "return"
            start = int(start)

            end = input("Cycle End > ").strip()
            if end.upper() == "EXIT":
                return "return"
            end = int(end)

            if start < 1 or start > Account.total_lines():
                print("You can't start with this number!")
                msvcrt.getch()
                return

            if end < start or end > Account.total_lines():
                print("You can't end with this number!")
                msvcrt.getch()
                return

        except:
            print("Must be a number!")
            msvcrt.getch()
            return

        selected_ids = list(range(start, end + 1))

    else:
        print("\nEnter Set: x, x, x, etc.. (Set can repeat)")
        raw = input("> ")

        try:
            selected_ids = []
            for part in raw.split(","):
                n = int(part.strip())
                if 1 <= n <= Account.total_lines():
                    selected_ids.append(n)
        except:
            print("Invalid format likely..")
            msvcrt.getch()
            return

    os.system("cls")
    display_emails()

    first_run = True

    for i in selected_ids:

        # Brake between cycles
        if not first_run:
            time.sleep(4)
        first_run = False

        # Manual stop
        if msvcrt.kbhit():
            if msvcrt.getch() == b'\r':
                print("\n[Cycle stopped by you.]")
                msvcrt.getch()
                return

        # Load account
        accountInfo = Account.read(i)
        accountInfo = unpack_key(accountInfo)

        try:
            parts = accountInfo.split("//")
            if len(parts) < 4:
                print(f"Corrupt account data - Account {i}")
                continue

            proofsum, name, email, key = parts
            key = key.replace("-", "")
        except:
            print(f"Corrupt account data - Account {i}")
            continue

        Spawn = PAM_Automated_Account(
            email, key, name=name,
            login_only=True,
            filter_donkey=num
        )

        print(f"\n{i}. {Spawn.spawncard}")

        if Spawn.flag == "Done":
            break


    if mode == 1:
        write_to_history(i, name if name else email)
    else:
        write_to_history(selected_ids, name if name else email)

    print("\n[Cycle Done]")
    msvcrt.getch()
    return

def duplicate_deleter():
    start = input("Welcome to duplicate deleter.\nType [Y/N] to start...\n> ")
    if start.upper() == "Y":

        account_file = SFE(Client.accinfo)
        seen_keys = set()
        lines_to_remove = []

        for i in range(1, account_file.total_lines() + 1):
            try:
                parts = unpack_key(account_file.read(i)).split("//")
                if len(parts) < 4:
                    raise ValueError
                proofsum, name, email, key = parts
            except:
                print(f"Corrupt account at line {i}")
                continue

            if key in seen_keys:
                print(f"Removed {email} for having a duplicate key")
                lines_to_remove.append(i)
            else:
                seen_keys.add(key)

        for line_number in reversed(lines_to_remove):
            account_file.delete(line_number)

        msvcrt.getch()
    else:
        print("None Found")
        msvcrt.getch()
        return "return"

def receive_next_byte(sock:socket.socket) -> bytes|None:
    try:
        data = sock.recv(1)
        if data:
            return data
        else:
            return None
    except BlockingIOError:
        return None
    except:
        return None

def receive_number_of_bytes(sock: socket.socket, n: int) -> bytes:
    sock.setblocking(True)
    data = bytes()
    while len(data) < n:
        byte = receive_next_byte(sock)
        if byte is None:
            raise ConnectionError("Socket closed error")
        data += byte
    sock.setblocking(False)
    return data



def format_packet(sock: socket.socket, packet_bytes: bytes) -> str:
    try:
        if packet_bytes.startswith(b'CM'):
            cm_position = packet_bytes.find(b'CM')
            hashtag_position = packet_bytes.find(b'#', cm_position)
            result = packet_bytes[cm_position:hashtag_position + 1]
            header_decoded = result.decode('utf-8', errors='ignore')
            split_header = header_decoded.split()
            compressed_size = int(split_header[2])
            compressed_message = receive_number_of_bytes(sock, compressed_size)
            decompressed_message = zlib.decompress(compressed_message).decode()
            return decompressed_message
        elif packet_bytes.startswith(b'MC'):
            mc_position = packet_bytes.find(b'MC')
            hashtag_position = packet_bytes.find(b'#', mc_position)
            result = packet_bytes[mc_position:hashtag_position + 1]
            header_decoded = result.decode('utf-8', errors='ignore')
            split_header = header_decoded.split()
            compressed_size = int(split_header[6])
            compressed_message = receive_number_of_bytes(sock, compressed_size)
            decompressed_message = zlib.decompress(compressed_message).decode()
            return header_decoded + decompressed_message
        else:
            return packet_bytes.decode()
    except:
        try:
            return packet_bytes.decode(errors='ignore')
        except:
            return ""

def HMAC_SHA1(key, message):
    hmac_object = hmac.new(key.encode(), message.encode(), hashlib.sha1)
    return hmac_object.hexdigest()

def initalize():
    Title = f"PAM I{verison_number}"
    os.system(f'title {Title}')
    if not os.path.exists(pam_folder):
        os.makedirs(pam_folder)
        settings_file = SFE(Client.settings)
        for idx, line in enumerate(Client.default_settings.splitlines(), start=1):
            settings_file.write(idx, line)
        open(Client.history, 'w').close()
        open(Client.accinfo, 'w').close()
        print("What is your one hour one life client directory?")
        print("You can change this any time you want in S̲ettings.")
        uInput = input("> ")
        os.system("cls")
        print("Enter a security code for key encryption (This can be changed later)")
        uInput = input("> ")
        settings_file.write_equality("privateKey",uInput)
    set_vars()

    manual_text = f"""Main - PAM I{verison_number}

Utilities:

[A] About 𝒊   [S] PAM Settings 🌣    [S2] Onelife Settings
[?X] Display All Keys   [FLT] Clean Duplicates

History:

[H] History 🗐    [CLR] Clear History 🗐

Account Editing:

[1] Add Accounts +   [2] Remove Accounts -   [3] Edit Accounts #

Client Spawning:

[4] Select Accounts ▼   [5] Run Multiple ↻   [L] Launch Game

Remote Spawning:

[6] Spawn ⛟   [7] Spawn Multiple x   [8] Lock Accounts ⚷ 
[9] Detect DT 𖦏
"""
    main = Menu(
        main_menu=True,
        options={    
            "About 𝒊": {"Function": about, "Single Run": True, "Key": "A"},
            "PAM Settings 🌣": {"Function": settings, "Single Run": True, "Key": "S"},
            "Ohol Settings": {"Function": onelife_settings, "Single Run": True, "Key": "S2"},
            "History 🗐": {"Function": history, "Single Run": True, "Key": "H"},
            "Clear History 🗐": {"Function": lambda: open(Client.history, 'w').close(), "Single Run": True, "Key": "CLR"},
            "Display All Keys": {"Function": display_keys, "Single Run": True, "Key": "?X"},
            "Clean Duplicates\n\n": {"Function": duplicate_deleter, "Single Run": True, "Key": "FLT"},  
            "Add Accounts +": {"Function": add_accounts, "Single Run": False, "Key": "1"},           
            "Remove Accounts -": {"Function": delete_accounts, "Single Run": False, "Key": "2"},
            "Edit Accounts #\n\n\n": {"Function": edit_accounts, "Single Run": False, "Key": "3"},         
            "Select Accounts ▼": {"Function": select_accounts, "Single Run": False, "Key": "4"},     
            "Cycle Accounts ↻": {"Function": cycle_accounts, "Single Run": False, "Key": "5"},     
            "Launch Game\n\n\n": {"Function": lambda: subprocess.Popen(Client.directory, shell=True), "Single Run": True, "Key": "L"},
            "Clientless Spawn ⛟": {"Function": quick_spawn, "Single Run": False, "Key": "6"},  
            "Spawn Multiples ⛌": {"Function": spawn_multiples, "Single Run": False, "Key": "7"}, 
            "Lock Accounts": {"Function": lock_accounts, "Single Run": True, "Key": "8"},  
            "DETECT DT": {"Function": detect_dt, "Single Run": False, "Key": "9"},  

        },
        replacement_display=manual_text
    )


    main.menu()

initalize()

