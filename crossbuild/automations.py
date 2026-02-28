
# BLOOMING ACCOUNT MANAGER!
import heapq
from datetime import datetime


now = datetime.now()
current_date = f"{now.month}/{now.day}/{now.strftime('%y')} {now.strftime('%I:%M %p').lstrip('0')}"



from collections import deque
import subprocess
import threading
import hashlib
import socket
import msvcrt
import queue
import heapq
import math
import hmac
import time
import zlib
import math
import sys
import os





client_storage = "Client Data (Do not share)"
console_color = (255, 0, 0)

class debug_:
    test_directory = os.path.join(client_storage, "test.test")

class menu:
    @staticmethod
    def display_title():
        print(f"\033[38;2;{console_color[0]};{console_color[1]};{console_color[2]}m", end="")
        print("[AT-14 🛦 ]")
        print("----------")

    states = {  
        "main menu": True,

        "about": False,
        "history": False,
        "client_config": False,
        "game_config": False,
        "automata": False,
        "display_all_accounts": False,
        "debugging_without_debugging": False,

        "add_accounts": False,
        "remove_accounts": False,
        "edit_accounts": False,
        "open_accounts": False,
        "cycle_accounts": False,

        "spawn_fast": False,
        "spawn_listed": False,

    }

# Function to help switch menus back and foward better
def toggle_menu(key):
    if not menu.states[key]:  
        for k in menu.states:
            menu.states[k] = False
        menu.states[key] = True
    else:  
        menu.states[key] = False
        menu.states["main menu"] = True

class client:
    game_executable = None

    server_ip = None
    server_port = None

    server_password = None
    client_tag = None

    debug_file = os.path.join(client_storage, "debug.txt")
    settings = os.path.join(client_storage, "settings.cfg")
    accinfo = os.path.join(client_storage, "accounts.txt")
    history = os.path.join(client_storage, "login_history.log")

    tick_sound_debug = os.path.join(client_storage, "tick.wav")
 
    default_config = """# Client Config

server = bigserver2.onehouronelife.com
serverPassword = testPassword
port = 8005

executable = None
clientTag = automata


# Don't touch the server password if you don't know what you're doing
# Also don't touch that clientTag unless you know what you're doing 


        """     
class nonclient():
    path_email = os.path.join(os.path.dirname(__file__), "settings", "email.ini")
    path_key = os.path.join(os.path.dirname(__file__), "settings", "accountKey.ini")

    fullscreen = os.path.join(os.path.dirname(__file__), "settings", "fullscreen.ini")
    skipFps = os.path.join(os.path.dirname(__file__), "settings", "skipFPSMeasure.ini")
    autoLogin = os.path.join(os.path.dirname(__file__), "settings", "autoLogIn.ini")
    voiceOfGod = os.path.join(os.path.dirname(__file__), "settings", "vogModeOn.ini")
    customServer = os.path.join(os.path.dirname(__file__), "settings", "customServerAddress.ini")
    serverPassword = os.path.join(os.path.dirname(__file__), "settings", "serverPassword.ini")


# Byte Handeling Functions

def receive_next_byte(sock:socket.socket) -> bytes|None:
  try:
    data = sock.recv(1)
    if data: 
        return data
    else: 
        return None 
  except BlockingIOError:
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
    if packet_bytes.startswith(b'CM'):
        cm_position = packet_bytes.find(b'CM')
        hashtag_position = packet_bytes.find(b'#', cm_position)
        result = packet_bytes[cm_position:hashtag_position + 1]
        header_decoded = result.decode('utf-8', errors='ignore')
        split_header = header_decoded.split()

        decompressed_size = int(split_header[1])
        compressed_size = int(split_header[2])

        compressed_data_start = hashtag_position + 1
        compressed_data_end = compressed_data_start + compressed_size

        compressed_message = receive_number_of_bytes(sock, compressed_size)
        decompressed_message = zlib.decompress(compressed_message).decode()

        return decompressed_message

    elif packet_bytes.startswith(b'MC'):
        mc_position = packet_bytes.find(b'MC')
        hashtag_position = packet_bytes.find(b'#', mc_position)
        result = packet_bytes[mc_position:hashtag_position + 1]
        header_decoded = result.decode('utf-8', errors='ignore')

        split_header = header_decoded.split()
        decompressed_size = int(split_header[5])
        compressed_size = int(split_header[6])

        compressed_data_start = hashtag_position + 1
        compressed_data_end = compressed_data_start + compressed_size


        mc_header = header_decoded


        compressed_message = receive_number_of_bytes(sock, compressed_size)
        decompressed_message = zlib.decompress(compressed_message).decode()

        return mc_header + decompressed_message

    else:
        return packet_bytes.decode()

def handle_messages():
    pass

def is_connected(sock: socket.socket) -> bool:
    try:
        sock.send(b'')
        return True
    except socket.error:
        return False
# Encryption 

def HMAC_SHA1(key, message):
    hmac_object = hmac.new(key.encode(), message.encode(), hashlib.sha1)
    return hmac_object.hexdigest()

# Fun 
def print_rgb(r, g, b, text=""):
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m", end="")
    
def overwrite(text: str):
    sys.stdout.write('\r' + text)
    sys.stdout.flush()

def print_lined(value):
    print(f"{value}\n{'-' * len(value)}")

# File Reading Functions

def total_lines(directory):

    try:
        with open(directory, "r") as file:
            lines = file.readlines()
            return len(lines)
    except:
        return 0
def read_line(line_number, directory):
    line_number = int(line_number)
    try:
        with open(directory, "r") as file:
            lines = file.readlines()

        if 0 < line_number <= len(lines):
            return lines[line_number - 1].rstrip("\n")
        else:
            return None
    except:
        return None
def write_line(line_number, directory, value):
    line_number = int(line_number)
    try:
        with open(directory, "r") as file:
            lines = file.readlines()

        lines = [line if line.endswith("\n") else line + "\n" for line in lines] # makes total sense if you think about it (It's an index)

        while len(lines) < line_number:
            lines.append("\n")

        lines[line_number - 1] = value + "\n" if not value.endswith("\n") else value

        with open(directory, "w") as file:
            file.writelines(lines)

    except:

        lines = ["\n"] * (line_number - 1)
        lines.append(value if value.endswith("\n") else value + "\n")

        with open(directory, "w") as file:
            file.writelines(lines)
def delete_line(line_number, directory):

    line_number = int(line_number)

    with open(directory, "r") as file:
        lines = file.readlines()
        
    lines = [line for line in lines if line.strip()]

    if 0 < line_number <= len(lines):
        del lines[line_number - 1]

    with open(directory, "w") as file:
        file.writelines(lines)
def locate_line(value, directory, inValue=False):
    for index in range(1, total_lines(directory) + 1):
        line = read_line(index, directory)
        if not line:
            continue

        if inValue:

            words = line.split()  
            for word in words:
                if value in word:
                    return index
        else:
            if value in line:
                return index

    return None


# Logic Reading Functions

def read_logic(value, directory, equalizer="="):  
    # Returns True/False based on whether the line contains value = True
    for index in range(1, total_lines(directory) + 1):
        line = read_line(index, directory)
        if not line or equalizer not in line:
            continue
        try:
            base, equality = [x.strip() for x in line.split(equalizer, 1)]
            if base == value:
                return equality == "True"
        except ValueError:
            continue
    return False
def reverse_logic(value, directory, equalizer="="):  
    # Flips a boolean value at a line
    location = locate_line(value, directory)
    if location is None or not isinstance(location, int):
        return

    text_value = read_line(location, directory)
    if text_value is None or equalizer not in text_value:
        return

    try:
        base, equality = [x.strip() for x in text_value.split(equalizer, 1)]
        if base != value:
            return
    except ValueError:
        return

    new_equality = "False" if equality == "True" else "True"
    write_line(location, directory, f"{base} {equalizer} {new_equality}")
def read_equality(value, directory, equalizer="="):  
    # Reads and returns the value associated with key `value`
    location = locate_line(value, directory)
    if location is None or not isinstance(location, int):
        return None

    raw_value = read_line(location, directory)
    if not raw_value or equalizer not in raw_value:
        return None

    try:
        base, equality = raw_value.split(equalizer, 1)
        if base.strip() == value:
            return equality.strip()
    except ValueError:
        return None
    return None
def write_equality(value, directory, replacement_value, equalizer="="):  
    # Writes a new value to a key
    location = locate_line(value, directory)
    if location is None or not isinstance(location, int):
        return

    raw_value = read_line(location, directory)
    if not raw_value or equalizer not in raw_value:
        return

    try:
        base, _ = [x.strip() for x in raw_value.split(equalizer, 1)]
        if base != value:
            return
        replacement_value = str(replacement_value).strip()
        write_line(location, directory, f"{base} {equalizer} {replacement_value}")
    except Exception:
        return
 
# Logging Function
def read_account_data():
    index = 1
    while index <= total_lines(client.accinfo):
        accinfo = read_line(index, client.accinfo)
        if accinfo == None:
            return

        try:
            name, email, key = accinfo.split("//")
        except:
            print(f"{index} illformatted.")
            index += 1
            continue

        if name.lower() == "none":
            print(f"{index} ፠ {email} ")
        else:
            print(f"{index} ፠ {name} ")

        index += 1
    
def read_account_full():
    index = 1
    while index <= total_lines(client.accinfo):
        accinfo = read_line(index, client.accinfo)
        if accinfo == None:
            return

        try:
            name, email, key = accinfo.split("//")
        except:
            print(f"Account {index} is illformatted.")
            index += 1
            continue
            
        print(f"{index}. {name}")
        print(f"፠ {email}")
        print(f"⚿  {key}\n")

        index += 1

def read_history():
    total = total_lines(client.history)

    if total == 0:
        print("[You have no account history]")
        return

    for i in range(1, total + 1):
        history_info = read_line(i, client.history)
        if history_info is None or history_info.strip() == "":
            continue  
        try:
            account_number, date, identification = history_info.split("//")
            print(f"Identification: {identification}")
            print(f"Date Used: {date}")
            print(f"Account Number: {account_number}\n")
        except:
            continue

def write_history(account_number, date, identification):
    available_space = total_lines(client.history) + 1
    value = f"{account_number}//{date}//{identification}"
    write_line(available_space, client.history, value)
    os.system(f'title {identification}')

# Important
def set_client_vars():
    client.game_executable = read_equality("executable", client.settings)
    client.server_password = read_equality("serverPassword", client.settings)
    client.client_tag = read_equality("clientTag", client.settings)

    if client.server_password != "testPassword":
        os.system("cls")
        print(f"[Warning]: Server password has been altered from (testPassword) to ({client.server_password})\n")
        print("Offical servers do not use this password...(Press any key to continue)")
        msvcrt.getch()
        os.system("cls")

    try:
        client.server_ip = socket.gethostbyname(read_equality("server", client.settings))
        client.server_port = int(read_equality("port", client.settings))
    except:
        os.system("cls")
        print("The server/port you've entered into your settings is invalid\nTry again to use internet functions (go to [3x])...", end="")
        msvcrt.getch()
        os.system("cls")


# Non-utility

def about():
    print_lined("Automata Iteration 12 𝕮")
    print("Dependencies: None")
    msvcrt.getch()
    toggle_menu("about"); return

def history():
    print_lined("[ACCOUNT USAGE HISTORY]")
    read_history()
    msvcrt.getch()
    toggle_menu("history"); return

def client_settings(): 
    def display_settings():
        i = 0
        while (i := i + 1) <= total_lines(client.settings):
            line = read_line(i, client.settings)
            if "=" in line:
                print(line)
                
    print_lined("[CLIENT SETTINGS]")
    display_settings()
    
    print("\nEnter the setting you want to edit")
    setting = input("\n> ")
    
    if setting.lower() == "exit":
        toggle_menu("client_config"); return
    else:
        os.system("cls")
        print_lined(f"Editing value for {setting.upper()}")
        display_settings()
        value = input("> ")
        write_equality(setting,client.settings ,value)
        set_client_vars(); return
        
def game_settings(): 
    def invert_setting(setting_directory):
        value = read_line(1, setting_directory)

        if value == '1':
            write_line(1, setting_directory, '0')
        else:
            write_line(1, setting_directory, '1')         

    print_lined("[ONELIFE SETTINGS]")
    print(f"1. Skip-Fps Check: {'✓' if read_line(1, nonclient.skipFps) == '1' else '✗'}")
    print(f"2. Voice Of God: {'✓' if read_line(1, nonclient.voiceOfGod) == '1' else '✗'}")
    print(f"3. Fullscreen: {'✓' if read_line(1, nonclient.fullscreen) == '1' else '✗'}")
    print(f"4. Auto-Login: {'✓' if read_line(1, nonclient.autoLogin) == '1' else '✗'}")

    setting = input("\n> ")

    if setting.lower() == "exit":
        toggle_menu("game_config");return

    if setting in ["1", "2", "3", "4"]:
        if setting == "1":
            invert_setting(nonclient.skipFps)
        elif setting == "2":
            invert_setting(nonclient.voiceOfGod)
        elif setting == "3":
            invert_setting(nonclient.fullscreen)
        elif setting == "4":
            invert_setting(nonclient.autoLogin)

    else:
        print("Invalid Setting..")
        msvcrt.getch()
        return

def display_all_accounts():
    print_lined("[ACCOUNT HANGER]")
    read_account_full()
    msvcrt.getch()
    toggle_menu("display_all_accounts"); return

# Account-utility

def add_accounts():
    print_lined("[ADDING ACCOUNTS]")
    read_account_data()
    print("\nType None for no name")

    name = input("\nAccount Name > ")
    if name.lower() == "exit":
        toggle_menu("add_accounts"); return    
    
    email = input("\nAccount Email > ")
    if email.lower() == "exit":
        toggle_menu("add_accounts"); return   
     
    key = input("\nAccount Key > ")
    if key.lower() == "exit":
        toggle_menu("add_accounts"); return   
    
    account_str = f"{name}//{email}//{key}"

    write_line(total_lines(client.accinfo) + 1, client.accinfo, account_str); return

def remove_accounts():
    print("\033[38;2;255;0;0m", end="")
    print_lined("[REMOVING ACCOUNTS]")
    read_account_data()

    account_number = input("\n> ")
    
    try:
        if account_number.lower() == "exit":
            toggle_menu("remove_accounts"); return    
        else:
            number_value = int(account_number)
        
        if number_value > total_lines(client.accinfo) or number_value < 0:
            print("Invalid Account Number.."); msvcrt.getch(); return

        os.system("cls")
        name, email, key = read_line(number_value, client.accinfo).split("//")

        print_lined(f"Delete Account {(email if name.lower() == 'none' else name)} - {account_number} [y/n]")

        user_choice = input("> ")

        if user_choice.lower() == "y":
            delete_line(account_number,client.accinfo)
        else:
            return
    except:
        print("Invalid Input.."); msvcrt.getch(); return

def edit_accounts():
    print_lined("[EDITING ACCOUNTS]") 
    read_account_data()
    print("\nEdit an account")

    account_number = input("\n> ")
    try:
        if account_number.lower() == "exit":
            toggle_menu("edit_accounts"); return    
        else:    
            number_value = int(account_number)
        
        if number_value > total_lines(client.accinfo) or number_value < 0:
            print("Invalid Account Number.."); msvcrt.getch(); return
        
        os.system("cls")
        name, email, key = read_line(number_value, client.accinfo).split("//")

        while True:
            print_lined(f"{(email if name.lower() == 'none' else name)}")
            print(f"1. Account name: {name}")
            print(f"2. Account email: {email.upper()}")
            print(f"3. Account key: {key.upper()}")
            
            choice = input("\n> ")
            
            if choice == "1":
                name = input("[New Name] > ")
            elif choice == "2":
                email = input("[New Email] > ")
            elif choice == "3":
                key = input("[New Key] > ")
            elif choice == "exit":
                toggle_menu("edit_accounts"); return             
            else:
                print("Invalid Choice"); msvcrt.getch(); os.system("cls"); continue
            
            if name.lower() == "exit" or email.lower() == "exit" or key.lower() == "exit":
                toggle_menu("edit_accounts"); return
            else:
                account_str = f"{name}//{email}//{key}"
                write_line(account_number, client.accinfo, account_str)
                os.system("cls"); continue
    except:
        print("Invalid Input..")
        msvcrt.getch(); return
    
# Account Usage (Basic)

def open_accounts(): # learn threads here
    print_lined("[SELECTING ACCOUNTS]")
    read_account_data()

    def launch_account(email, key, number_value): 
        write_line(1, nonclient.path_email, email); write_line(1, nonclient.path_key, key)
        try:
            subprocess.Popen(client.game_executable, shell=True)
        except:
            pass

    account_number = input("\n> ")   
    try:
        if account_number.lower() == "exit":
            toggle_menu("open_accounts"); return    
        else:
            number_value = int(account_number)
        
        if number_value > total_lines(client.accinfo) or number_value < 0:
            print("Invalid Account Number.."); msvcrt.getch(); return

        name, email, key = read_line(number_value, client.accinfo).split("//")
        threading.Thread(target=launch_account, args=(email, key, number_value)).start()
        write_history(f"{account_number}", current_date, f"{(email if name.lower() == 'none' else name)}")
    except:
        print("Invalid Input.."); msvcrt.getch(); return

# 777
def cycle_through_accounts(): 
    print_lined("[CYCLING ACCOUNTS]")
    read_account_data()

    try:
        account_number = input("\n(x y) > ")   
        if account_number.lower() == "exit":    
            toggle_menu("cycle_accounts")
            return    
        else:
            start, end = account_number.split(" ")
            start = int(start.strip())
            end = int(end.strip())

        total = total_lines(client.accinfo)
        if start < 1 or end > total or start > end:
            print("Invalid Account Number..")
            msvcrt.getch()
            return

        print("")
        for i in range(start, end + 1):
            if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                print("\n[cycle ended prematurely]")
                msvcrt.getch()
                return

            if i != start:
                time.sleep(3.5)

            try:
                accountInfo = read_line(i, client.accinfo)
                name, email, key = accountInfo.split("//")
                write_line(1, nonclient.path_email, email)
                write_line(1, nonclient.path_key, key)

                print(f"Launching: {(email if name.lower() == 'none' else name)}")
                subprocess.Popen(client.game_executable, shell=True)

            except:
                continue

        print("[End]", end="")
        msvcrt.getch()
        write_history(f"{start}-{end}", current_date, f"{start}-{end}")

    except:
        print("Invalid Input.. [Must be a number to a number ex. 1 10]")
        msvcrt.getch()
        return

class Protocols:
# Cleared
    def login(socket, email, key, tutorial_number, server_output, twincode=None, twin_amount=None, reborn=False):
            try:
                if twincode:
                    SN_SPLIT = server_output.split()
                    server_secret = SN_SPLIT[2]
                    twincode_hash = HMAC_SHA1(twincode, server_secret)
                    password_hash = HMAC_SHA1(client.server_password, server_secret); key_hash = HMAC_SHA1(key, server_secret)
                    message = f"{'R' if reborn else ''}LOGIN client_{client.client_tag} {email} {password_hash} {key_hash} {tutorial_number} {twincode_hash} {twin_amount}#"
                    socket.sendall(message.encode())   
                else:
                    SN_SPLIT = server_output.split()
                    server_secret = SN_SPLIT[2]
                    password_hash = HMAC_SHA1(client.server_password, server_secret); key_hash = HMAC_SHA1(key, server_secret)
                    message = f"{'R' if reborn else ''}LOGIN client_{client.client_tag} {email} {password_hash} {key_hash} {tutorial_number}#"
                    socket.sendall(message.encode())   
            except:
                return Exception

    def fetch_curse_token(server_output): # 'CX' on login   
        try:
            CX_SPLIT = server_output.split()
            if "0#" in CX_SPLIT:
                return 0
            elif"1#":
                return 1
            else:
                return None
        except:
            pass    
        pass

    def fetch_birth_data(server_output): #  moth 'PS'
        automation_pid = None
        motherID = None
        
        mother_name = None
        family_name = None

        server_output = server_output.replace("PS", "").replace("#", "").strip()
        PS_SPLIT = server_output.split()

        if len(PS_SPLIT) == 10:  # Normal Case
            try:
                int(PS_SPLIT[6])  # MOTHER PID

                automation_pid = PS_SPLIT[0]
                motherID = PS_SPLIT[6]
                mother_name = PS_SPLIT[3]
                family_name = PS_SPLIT[4]

            except:
                pass

        elif len(PS_SPLIT) == 9:  # No Last Name
            try:
                int(PS_SPLIT[5])  # MOTHER PID

                automation_pid = PS_SPLIT[0]
                motherID = PS_SPLIT[5]
                mother_name = PS_SPLIT[3]

            except:
                pass

        elif len(PS_SPLIT) == 8:  # No Name
            try:
                int(PS_SPLIT[4])  # MOTHER PID

                automation_pid = PS_SPLIT[0]
                motherID = PS_SPLIT[4]

            except:
                pass

        if "NO MOTHER" in server_output:
            automation_pid = PS_SPLIT[0]  # PID

        if automation_pid:
            automation_pid = automation_pid.replace("/0", "").strip()

        if family_name is None:
            family_name = "NONE"
        return automation_pid, motherID, mother_name, family_name
    
    def fetch_id_pu_status(pID, player_updates):
        for player_update in player_updates:
            parts = player_update.split()
            if parts[0] == pID:
                keys = [
                    "p_id", "po_id", "facing", "action", "action_target_x", "action_target_y",
                    "o_id", "o_origin_valid", "o_origin_x", "o_origin_y", "o_transition_source_id",
                    "heat", "done_moving_seqNum", "force", "x", "y", "age", "age_r",
                    "move_speed", "clothing_set", "just_ate", "last_ate_id", "responsible_id",
                    "held_yum", "held_learned"
                ]
                return dict(zip(keys, parts))
        return None

    def fetch_id_name(pID, player_names):
        first_name = None
        last_name = None
        for player_name in player_names:
            parts = player_name.split()
            if len(parts) >= 3 and pID == parts[0]:
                first_name = parts[1]
                last_name = parts[2]
                break  # Stop after finding the first match
        return first_name, last_name



# threading.Thread(target=play_tick_sfx, daemon=True).start() 

class Automation:
    def __init__(self, email, key, name=None, tutorial_number=0, rebirth=False, twincode=None, twin_count=None,
                  identification=None, run_as_thread=False, auto_reconnect=False):
        args = locals()
        args.pop('self')
        for name, value in args.items():
            setattr(self, name, value)

        self.spawncard = None

        self.status = {
            "Online*": threading.Event(),
            "Online": False, 

            "Rejected*": threading.Event(),
            "Rejected": False,

        }
        self.start_central_processor()

    def central_processor(self):

        packet_buffer = bytes()

        self.command_queue = queue.Queue()
        self.queue_in_play = False

        while not self._stop_flag:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((client.server_ip, client.server_port))
            except:
                print("failed connection")
                if not self._stop_flag:
                    msvcrt.getch()
                return

            if not is_connected(self.socket):
                if not self.auto_reconnect or self._stop_flag:
                    break
                else:
                    continue  

            self.map_chunk_new = []
            self.map_chunk_total = []
            self.homelands = []
            self.bad_biomes = []
            self.cravings = []
            self.player_message_catche = []
            self.global_message_catche = []
            self.player_curse_catche = []
            self.players_out_of_range = []
            self.fliped_players = []
            self.babies_wiggling = []
            self.player_updates = []
            self.player_lineage = []
            self.player_names = []
            self.player_moves = []
            self.player_emot = []
            self.locations = []
            self.map_change = []
            self.food_change = []
            self.heat_change = []
            self.apocalypse = False
            self.dying_players = []
            self.healed_players = []
            self.ghost_players = []
            self.posse_joiners = []
            self.monument_calls = []
            self.player_graves = []
            self.grave_moves = []
            self.old_graves = []
            self.owner_list = []
            self.following = []
            self.exiled = []
            self.valley_spacing = []
            self.cursed_players = []
            self.curse_tokens = None
            self.curse_score_changes = []
            self.flight_dests = []
            self.vog_updates = []
            self.photo_signatures = []
            self.war_report = []
            self.rocket_ride = []
            self.rocket_account = []



            while not self._stop_flag:
                if not is_connected(self.socket):
                    break
                    
                new_byte = receive_next_byte(self.socket)
                while new_byte is not None and not self._stop_flag:
                    packet_buffer += new_byte
                    
                    if new_byte == b'#':

                        ss = format_packet(self.socket, packet_buffer)
                        ss_split = ss.split()
                        header = ss_split[0]
                        print(ss)
                        if (self.status["Online"] == False):
                            if "SN" == header:
                                Protocols.login(self.socket, self.email, self.key, self.tutorial_number,
                                ss, self.rebirth, self.twin_count, self.twincode)
                            elif "SD" == header:
                                self.status["Rejected"] = True
                                self.status["Rejected*"].set()
                                break
                            elif "SHUTDOWN" == header:
                                self.status["Rejected"] = True
                                self.status["Rejected*"].set()
                                break
                            elif "SERVER_FULL" == header:
                                self.status["Rejected"] = True
                                self.status["Rejected*"].set()
                                break
                            elif "ACCEPTED" == header:

                                os.system("cls")

                                self.status["Online"] = True
                                self.status["Online*"].set()
                            elif "REJECTED" == header:
                                self.status["Rejected"] = True
                                self.status["Rejected*"].set()
                                break
                            elif "NO_LIFE_TOKENS" == header:
                                self.status["Rejected"] = True
                                self.status["Rejected*"].set()
                                break
                                
                        if (self.status["Online"]):
                            if header == "MC":
                                del ss_split[0]; del ss_split[4]; del ss_split[4]

                                csizeX = int(ss_split[0])
                                csizeY = int(ss_split[1])
                                tlx = int(ss_split[2])
                                tly = int(ss_split[3])

                                expected_len = csizeX * csizeY
                                chunkdata = ss_split[4:]
                                
                                if len(chunkdata) > expected_len:
                                    ss = chunkdata[expected_len:]
                                    ss_split = ss.split()
                                    header = ss_split[0]
                                    chunkdata = chunkdata[:expected_len]
                                    chunkdata[0] = chunkdata[0].replace("#", "").strip()

                                

                            elif header == "MX":
                                pass  # MAP_CHANGE
                            elif header == "PU": # start
                                pass  # PLAYER_UPDATE
                            elif header == "PM":
                                pass  # PLAYER_MOVES_START
                            elif header == "PO":
                                pass  # PLAYER_OUT_OF_RANGE
                            elif header == "BW":
                                pass  # BABY_WIGGLE
                            elif header == "PS":
                                pass  # PLAYER_SAYS
                            elif header == "LS":
                                pass  # LOCATION_SAYS
                            elif header == "PE":
                                pass  # PLAYER_EMOT
                            elif header == "FX":
                                pass  # FOOD_CHANGE
                            elif header == "HX":
                                pass  # HEAT_CHANGE
                            elif header == "LN":
                                pass  # LINEAGE
                            elif header == "CU":
                                pass  # CURSED
                            elif header == "CX":
                                pass  # CURSE_TOKEN_CHANGE
                            elif header == "CS":
                                pass  # CURSE_SCORE
                            elif header == "NM":
                                pass  # NAMES
                            elif header == "AP":
                                pass  # APOCALYPSE
                            elif header == "AD":
                                pass  # APOCALYPSE_DONE
                            elif header == "DY":
                                pass  # DYING
                            elif header == "HE":
                                pass  # HEALED
                            elif header == "PJ":
                                pass  # POSSE_JOIN
                            elif header == "MN":
                                pass  # MONUMENT_CALL
                            elif header == "GV":
                                pass  # GRAVE
                            elif header == "GM":
                                pass  # GRAVE_MOVE
                            elif header == "GO":
                                pass  # GRAVE_OLD
                            elif header == "OW":
                                pass  # OWNER
                            elif header == "FW":
                                pass  # FOLLOWING
                            elif header == "EX":
                                pass  # EXILED
                            elif header == "VS":
                                pass  # VALLEY_SPACING
                            elif header == "FD":
                                pass  # FLIGHT_DEST
                            elif header == "BB":
                                pass  # BAD_BIOMES
                            elif header == "VU":
                                pass  # VOG_UPDATE
                            elif header == "PH":
                                pass  # PHOTO_SIGNATURE
                            elif header == "PONG":
                                pass  # PONG
                            elif header == "SHUTDOWN":
                                pass  # SHUTDOWN
                            elif header == "SERVER_FULL":
                                pass  # SERVER_FULL
                            elif header == "SN":
                                pass  # SEQUENCE_NUMBER
                            elif header == "ACCEPTED":
                                pass  # ACCEPTED
                            elif header == "REJECTED":
                                pass  # REJECTED
                            elif header == "NO_LIFE_TOKENS":
                                pass  # NO_LIFE_TOKENS
                            elif header == "SD":
                                pass  # FORCED_SHUTDOWN
                            elif header == "MS":
                                pass  # GLOBAL_MESSAGE
                            elif header == "WR":
                                pass  # WAR_REPORT
                            elif header == "LR":
                                pass  # LEARNED_TOOL_REPORT
                            elif header == "TE":
                                pass  # TOOL_EXPERTS
                            elif header == "TS":
                                pass  # TOOL_SLOTS
                            elif header == "HL":
                                pass  # HOMELAND
                            elif header == "FL":
                                pass  # FLIP
                            elif header == "CR":
                                pass  # CRAVING
                            elif header == "GH":
                                pass  # GHOST
                            elif header == "RR":
                                pass  # ROCKET_RIDE
                            elif header == "RA":
                                pass  # ROCKET_ACCOUNT
                            else:
                                pass 
                            
                            def tick(self): # Main for bots
                                pass

                                        
                            tick(self)

                        packet_buffer = bytes()
                    new_byte = receive_next_byte(self.socket)
                if self._stop_flag:
                    break
            if not self.auto_reconnect:
                break
            break
                  
    def start_central_processor(self):
        self._stop_flag = False  # reset stop flag when starting
        if self.run_as_thread:
            if not hasattr(self, 'central_processor_thread') or not self.central_processor_thread.is_alive():
                self.central_processor_thread = threading.Thread(target=self.central_processor)
                self.central_processor_thread.daemon = True
                self.central_processor_thread.start()
        else:
            self.central_processor()

    def stop_central_processor(self):
        self.status["Online*"].wait()
        self._stop_flag = True
        if self.run_as_thread:
            if hasattr(self, 'central_processor_thread') and self.central_processor_thread.is_alive():
                self.central_processor_thread.join(timeout=5)  # timeout to avoid hanging
                if self.central_processor_thread.is_alive():
                    print("Warning: central_processor_thread did not stop within timeout.")

def automata():

    print("[Automata I-12 - Gen - 1]")
    read_account_data()

    try:
        account_number = input("\n> ")

        if account_number.lower() == "exit":
            toggle_menu("automata")
            return
        else:
            number_value = int(account_number)

        if number_value > total_lines(client.accinfo) or number_value < 0:
            print("Invalid Account Number..")
            msvcrt.getch()
            return

        name, email, key = read_line(number_value, client.accinfo).split("//")
        key = key.replace("-", "")
    except:
        print("Invalid Input..")
        msvcrt.getch()
        return

    account = Automation(email, key, name = name, auto_reconnect=False, run_as_thread=False) 

def debug_without_debugging():
    uinput = input("Object Name > ")
    os.system("cls")
    try: 
        pass
    except:
        print("Object Not Found Error")
    msvcrt.getch()
    
# menu handlers
def menu_handler():
    menu.display_title()

    print("Utility ⚑\n")

    print("1x. About 🕮                   2x. History 🕮               3x. Client Settings </>")
    print("4x. Clear History ✗           5x. Game Settings </>       6x. Automata 𑁍")
    print("7x. Full Account Display 🕮    8x. DWD 𖢥\n")

    uinput = input("\n> ")

    if uinput.lower() == "exit":
        os.system("cls")
        exit()
    elif uinput == "1x":
        toggle_menu("about"); return
    elif uinput == "2x":
        toggle_menu("history"); return
    elif uinput == "3x":
        toggle_menu("client_config"); return
    elif uinput == "4x":
        open(client.history, 'w').close(); return
    elif uinput == "5x":
        toggle_menu("game_config")
    elif uinput == "6x":
        toggle_menu("automata")
    elif uinput == "7x":
        toggle_menu("display_all_accounts")
    elif uinput == "8x":
        toggle_menu("debugging_without_debugging")
    else:
        print("Invalid Input..")
        msvcrt.getch(); return
        
# run client
def run_client(debug=False):

    os.system(f'title AUTOMATIONS')
    set_client_vars()

    if not os.path.exists(client_storage):
        os.makedirs(client_storage)
        open(client.history, 'w').close()
        open(client.accinfo, 'w').close()
        write_line(0, client.settings, client.default_config)


        print_lined("Paste in your game client's directory")
        user_input = input("\n> ")
        write_equality("executable", client.settings, user_input)

        os.system("cls")
        print_lined("Please enter in your server ip...")

        client.server_ip = input("\n> ")

        os.system("cls")
        print("Please enter your port")

        client.server_port = input("\n> ")

    # Main for client 
    while True and debug:
        print("You are in debug mode 𖢥")
        read_account_data()
        msvcrt.getch()
        os.system("cls")

    while True and not debug:
        if menu.states["main menu"]:
            os.system("cls")
            menu_handler()
        elif menu.states["about"]:
            os.system("cls")
            about()
        elif menu.states["history"]:
            os.system("cls")
            history()
        elif menu.states["client_config"]:
            os.system("cls")
            client_settings()
        elif menu.states["game_config"]:
            os.system("cls")
            game_settings()
        elif menu.states["automata"]:
            os.system("cls")
            automata()
        elif menu.states["display_all_accounts"]:
            os.system("cls")
            display_all_accounts() 
        elif menu.states["debugging_without_debugging"]:
            os.system("cls")
            debug_without_debugging()
        
# main for menu
while(True):
    run_client(debug=False)
    os.system("cls")