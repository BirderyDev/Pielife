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

automata_folder = "automata_data"
ERRORMSG = "error"

class switchtype:
    numswitch = True

    about = False
    history = False
    settings_client = False
    settings_onelife = False
    bot_test = False

    add_accounts = False
    remove_accounts = False
    edit_accounts = False
    select_accounts = False
    cycle_accounts = False

    fast_spawn = False
    spawn_any = False
    detect_accounts = False
    quick_kill = False
    kill_many = False

    lock_account = False

class client:
    #paths
    settings = os.path.join(automata_folder, "settings.cfg")
    accinfo = os.path.join(automata_folder, "accounts.txt")
    history = os.path.join(automata_folder, "history.log")

    # Large File Varibles
    default_settings = """
executable = None
server = bigserver2.onehouronelife.com
port = 8005
serverPassword = testPassword
clientTag = automata
    """

    # Varibles
    
    directory = None
    tag = None

    # Functions

    
    @staticmethod
    def title():
        print("\033[38;2;251;255;209m", end="")
        print("[ Щ☭ ITERATION 11 AUTOMATA ]\n")

class onelife:

    # Paths
    path_email = os.path.join(os.path.dirname(__file__), "settings", "email.ini")
    path_key = os.path.join(os.path.dirname(__file__), "settings", "accountKey.ini")

    fullscreen = os.path.join(os.path.dirname(__file__), "settings", "fullscreen.ini")
    skipFps = os.path.join(os.path.dirname(__file__), "settings", "skipFPSMeasure.ini")
    autoLogin = os.path.join(os.path.dirname(__file__), "settings", "autoLogIn.ini")
    voiceOfGod = os.path.join(os.path.dirname(__file__), "settings", "vogModeOn.ini")
    customServer = os.path.join(os.path.dirname(__file__), "settings", "customServerAddress.ini")
    serverPassword = os.path.join(os.path.dirname(__file__), "settings", "serverPassword.ini")

    # Varibles
    server_ip = None
    server_port = None

    server_password = None


    


# Byte Handeling Functions
def get_next_byte(sock:socket.socket) -> bytes|None:
  try:
    data = sock.recv(1)
    if data: 
        return data
    else: 
        return None 
  except BlockingIOError:
    return None
def get_number_of_bytes(sock: socket.socket, n: int) -> bytes:
    """
    Get a specific number of bytes from the socket.
    This function will block until the specified number of bytes is received.
    """
    sock.setblocking(True) # Ensure blocking, since we want to wait for the bytes
    data = bytes()
    while len(data) < n: # While we don't have enough bytes
        byte = get_next_byte(sock)
        if byte is None:
            raise ConnectionError("Socket closed before receiving all bytes")
        data += byte
    sock.setblocking(False) # Restore non-blocking mode
    return data
def handle_packet(sock: socket.socket, packet_bytes: bytes) -> str:
    """
    Handle a packet received from the socket.
    This function processes packet data and preserves headers,
    but removes the '#' from the decompressed MC message only.
    """

    if packet_bytes.startswith(b'CM') or packet_bytes.startswith(b'MC'):
        if packet_bytes.startswith(b'CM'):
            cm_position = packet_bytes.find(b'CM')
        else:
            cm_position = packet_bytes.find(b'MC')

        hashtag_position = packet_bytes.find(b'#', cm_position)
        header_bytes = packet_bytes[cm_position:hashtag_position + 1]
        header_decoded = header_bytes.decode('utf-8', errors='ignore')
        split_header = header_decoded.split()

        if packet_bytes.startswith(b'CM'):
            decompressed_size = int(split_header[1])
            compressed_size = int(split_header[2])
        else:  # 'MC'
            decompressed_size = int(split_header[5])
            compressed_size = int(split_header[6])

        # Calculate data bounds
        compressed_data_start = hashtag_position + 1
        compressed_data_end = compressed_data_start + compressed_size

        # Read full compressed message
        compressed_message = get_number_of_bytes(sock, compressed_size)
        decompressed_message = zlib.decompress(compressed_message).decode()

        # Return with header and hashtag included in header but not in message
        return header_decoded + decompressed_message

    else:
        return packet_bytes.decode()

# File Reading Functions
def total_lines(directory):
    try:
        with open(directory, "r") as file:
            lines = file.readlines()
            return len(lines)
    except FileNotFoundError:
        return 0
    except Exception:
        print(ERRORMSG)
        return 0
def read_line(line_number, directory):
    try:
        with open(directory, "r") as file:
            lines = file.readlines()

        if 0 < line_number <= len(lines):
            return lines[line_number - 1].rstrip("\n")
        else:
            return ERRORMSG
    except FileNotFoundError:
        return ERRORMSG
def write_line(line_number, directory, value):
    try:
        with open(directory, "r") as file:
            lines = file.readlines()

        lines = [line if line.endswith("\n") else line + "\n" for line in lines]

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
    else:
        print("Invalid line number.")

    with open(directory, "w") as file:
        file.writelines(lines)
def locateLine(value, directory):
    indexNum = 1
    while True:
        if indexNum > total_lines(directory):
            return ERRORMSG

        fileValue = read_line(indexNum, directory)
        if value in fileValue:
            return indexNum
        else:
            indexNum += 1
            continue

# Logic Reading Functions
def read_logic(value, directory):  # Returns True/False based on file contents
    indexNum = 1

    while indexNum <= total_lines(directory):
        line = read_line(indexNum, directory)

        if value in line and "=" in line:
            try:
                base, equality = [x.strip() for x in line.split("=", 1)]
                if base == value:
                    return equality == "True"
            except ValueError:
                pass  # Skip malformed line

        indexNum += 1

    return False  # Not found — default to False
def reverse_logic(value, directory):  # Polarizes the logic
    switchValue = read_logic(value, directory)
    location = locateLine(value, directory)

    if location == ERRORMSG:
        return ERRORMSG

    textValue = read_line(location, directory)
    if textValue == ERRORMSG or "=" not in textValue:
        return ERRORMSG

    try:
        Base, Equality = [x.strip() for x in textValue.split("=", 1)]
    except ValueError:
        return ERRORMSG

    newEquality = "False" if switchValue else "True"
    write_line(location, directory, f"{Base} = {newEquality}")
def read_equality(value, directory):  # Reads Equalities``
    location = locateLine(value, directory)

    if not isinstance(location, int) or location == ERRORMSG:
        return ERRORMSG

    rawValue = read_line(location, directory)
    if rawValue == ERRORMSG or "=" not in rawValue:
        return ERRORMSG

    try:
        Base, Equality = rawValue.split("=", 1)
        if Base.strip() == value:
            return Equality.strip()
    except ValueError:
        return ERRORMSG

    return ERRORMSG
def write_equality(value, directory, replacementValue):  # Writes Equalities
    location = locateLine(value, directory)

    if not isinstance(location, int) or location == ERRORMSG:
        return

    rawValue = read_line(location, directory)
    if rawValue == ERRORMSG or "=" not in rawValue:
        return

    try:
        Base, _ = rawValue.split("=", 1)
        write_line(location, directory, f"{Base.strip()} = {replacementValue.strip()}")
    except ValueError:
        return

def HMAC_SHA1(key, message):
    hmac_object = hmac.new(key.encode(), message.encode(), hashlib.sha1)
    return hmac_object.hexdigest()

def run_program():
    if not os.path.exists(automata_folder):
        os.makedirs(automata_folder)
    
        write_line(1, client.settings, client.default_settings)
        open(client.history, 'w').close()
        open(client.accinfo, 'w').close()

        user_input = input("Paste in your game client's directory > ")
        write_equality("executable", client.settings, user_input)
    

    client.directory = read_equality("executable", client.settings)
    onelife.server_password = read_equality("serverPassword", client.settings)
    client.tag = read_equality("clientTag", client.settings)
try:
    onelife.server_ip = socket.gethostbyname(read_equality("server", client.settings))
    onelife.server_port = int(read_equality("port", client.settings))
except:
    print("Warning - Internet Info Invalid... Internet Spawn functions will not be functional")
    msvcrt.getch()

# CONFIG

def about():
    print("Automata Iteration 10")
    print("A program designed by Shady...")
    print("Do not share this program if it was gifted to you.")
    msvcrt.getch()
    switchtype.numswitch = True
    switchtype.about = False
    return

def display_emails():

    index = 1

    while index <= total_lines(client.accinfo):
        accinfo = read_line(index, client.accinfo)
        if accinfo == ERRORMSG:
            return

        try:
            name, email, key = accinfo.split("//")
        except ValueError:
            print(f"Account {index} is illformatted.")
            msvcrt.getch()
            index += 1
            continue


        if name.lower() == "none":
            print(f"{index} - {email} ")
        else:
            print(f"{index} - {name} ")


        index += 1

def display_keys():
    index = 1

    while index <= total_lines(client.accinfo):
        accinfo = read_line(index, client.accinfo)
        if accinfo == ERRORMSG:
            return

        try:
            name, email, key = accinfo.split("//")
        except ValueError:
            print(f"Account {index} is illformatted.")
            msvcrt.getch()
            index += 1
            continue


        print(f"{index}. {name}")
        print(f"⁜  {email}")
        print(f"⚿  {key}\n")

        index += 1

def display_history():
    index = 1
    total = total_lines(client.history)
    print("Account History:\n")

    while index <= total:
        raw = read_line(index, client.history)
        try:
            accnum, date, email = raw.split("//")
            print(f"Identification: {email}")
            print(f"Account Number: {accnum}")
            print(f"Date Used: {date}\n")
        except:
            pass
        index += 1
    if total == 0:
        print("[Use some accounts to get an account history]")
    msvcrt.getch()
    switchtype.numswitch = True
    switchtype.history = False
def writeHistory(acc_number, current_time, acc_name):
    openSpace = total_lines(client.history) + 1
    value = f"{acc_number}//{current_time}//{acc_name}"
    write_line(openSpace, client.history, value)
    os.system(f'title {acc_name}')

def client_settings_config():

    print("[EDIT CLIENT SETTINGS]:\n")

    for index in range(1, total_lines(client.settings) + 1):
        data = read_line(index, client.settings)
        if "=" in data:
            print(f"{data}\n")

    uInput = input("\nValue > ").strip()

    if uInput.lower() == "exit":
        switchtype.numswitch = True
        switchtype.settings_client = False
        return

    configuration = uInput
    try:

        equality = read_equality(configuration, client.settings)
        
        if equality.lower() == "true" or equality.lower() == "false":
            reverse_logic(configuration, client.settings)
        else:
            os.system("cls")
            new_value = input(f"New Value For {configuration}\n> ").strip()

            if new_value.lower() == "exit":
                switchtype.numswitch = True
                switchtype.settings_client = False
                return
            
            write_equality(configuration, client.settings, new_value)
            
            client.directory = read_equality("executable", client.settings)
            onelife.server_password = read_equality("serverPassword", client.settings)
            client.tag = read_equality("clientTag", client.settings)
            try:
                onelife.server_ip = socket.gethostbyname(read_equality("server", client.settings))
                onelife.port = int(read_equality("port", client.settings))
            except:
                os.system("cls")
                print("Internet Info is invalid but reguardless program will proceed...")
                msvcrt.getch()
                pass

    except:
        print("Invalid Input")

def onelife_settings_config():
    try:
        fullscreen = read_line(1, onelife.fullscreen)
        auto_login = read_line(1, onelife.autoLogin)
        vog = read_line(1, onelife.voiceOfGod)
        skipfpscheck = read_line(1, onelife.skipFps)
    except:
        print("Setting directories changed or corrupted!")
        msvcrt.getch()
        switchtype.numswitch = True
        switchtype.settings_onelife = False
        return

    while True:
        client.title()

        print(f"1. fullscreen: {fullscreen}")
        print(f"2. auto login: {auto_login}")
        print(f"3. voice of god: {vog}")
        print(f"4. skip FPS check: {skipfpscheck}")


        userInput = input("> ").strip().lower()

        if userInput == "exit":
            switchtype.numswitch = True
            switchtype.settings_onelife = False
            return

        if userInput == "1":
            fullscreen = "1" if fullscreen == "0" else "0"
            write_line(1, onelife.fullscreen, fullscreen)

        elif userInput == "2":
            auto_login = "1" if auto_login == "0" else "0"
            write_line(1, onelife.autoLogin, auto_login)

        elif userInput == "3":
            vog = "1" if vog == "0" else "0"
            write_line(1, onelife.voiceOfGod, vog)

        elif userInput == "4":
            skipfpscheck = "1" if skipfpscheck == "0" else "0"
            write_line(1, onelife.skipFps, skipfpscheck)

        else:
            print("Invalid Input")
            msvcrt.getch()
        return

# ACCOUNT MANAGER
def add_accounts():
    print("[ADDING ACCOUNTS ✚ ]:\n")
    display_emails()

    name = input("\n[Acc Name ('None' for None)] > ")
    if name.lower() == "exit":
        switchtype.numswitch = True
        switchtype.add_accounts = False
        return

    email = input("\n[Acc Email] > ")
    if email.lower() == "exit":
        switchtype.numswitch = True
        switchtype.add_accounts = False
        return

    key = input("\n[Acc Key] > ")
    if key.lower() == "exit":
        switchtype.numswitch = True
        switchtype.add_accounts = False
        return

    assembly = f"{name}//{email}//{key}".strip()

    latest_line = total_lines(client.accinfo) + 1
    
    write_line(latest_line, client.accinfo, assembly)

def remove_accounts():
    print("\033[38;2;255;0;0m", end="")
    print("[REMOVING ACCOUNTS ✘]")
    print("----------------------")
    print("\033[38;2;166;0;0m", end="")
    display_emails()
    try:
        userInput = input("\n> ")
        if userInput == "Exit" or userInput == "exit" or userInput == "EXIT":
            switchtype.numswitch = True
            switchtype.remove_accounts = False
            return
        numberValue = int(userInput)
    except:
        print("Invalid Input...")
        msvcrt.getch()
        return

    if numberValue > total_lines(client.accinfo):
        print("Not a valid account")
        msvcrt.getch()
        return

    print(f"Are you sure you want to delete account {numberValue} ? [Y/N]")
    userInput = input("\n> ")
    if userInput.lower() == "y":
        delete_line(numberValue, client.accinfo)
    else:
        return

def edit_accounts():
    print("[EDITING ACCOUNTS]:\n")
    display_emails()

    try:
        userInput = input("\n> ")
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.edit_accounts = False
            return

        numberValue = int(userInput)
    except ValueError:
        print("Invalid Input")
        msvcrt.getch()
        return

    if numberValue > total_lines(client.accinfo):
        print("Invalid Account Number")
        msvcrt.getch()
        return

    while True:
        os.system("cls")

        rawAccountData = read_line(numberValue, client.accinfo)
        try:
            name, email, key = rawAccountData.strip().split("//")
        except ValueError:
            print("Corrupt account data.")
            msvcrt.getch()
            return

        print("What do you want to edit? '[Type exit' to exit]\n")
        print("1. Name")
        print("2. Email")
        print("3. Key\n")

        print(f"Acc Name: {name}")
        print(f"Acc Email: {email}")
        print(f"Acc Key: {key}\n")

        userInput = input("\n> ").lower()

        if userInput == "exit":
            switchtype.numswitch = True
            switchtype.edit_accounts = False
            return

        if userInput in ["1", "2", "3"]:
            fields = {"1": "Name", "2": "Email", "3": "Key"}
            new_value = input(f"New Account {fields[userInput]}: ")

            print("Are you sure? [y/n]")
            confirm = input("> ").lower()

            if confirm != "y":
                continue
            
            if userInput == "1":
                name = new_value
            elif userInput == "2":
                email = new_value
            elif userInput == "3":
                key = new_value

            try:
                fullAccountDetails = f"{name}//{email}//{key}"
                write_line(numberValue, client.accinfo, fullAccountDetails)
            except Exception as e:
                print("Failed to write to accounts:", e)
                msvcrt.getch()
                continue
        else:
            print("Invalid Option")
            msvcrt.getch()

# MANUAL
def select_account():
    print("[SELECTING ACCOUNTS ▼ ]:\n")
    display_emails()

    try:
        userInput = input("\n  > ")
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.select_accounts = False
            return

        numberValue = int(userInput)
    except:
        print("Not a valid input")
        msvcrt.getch()
        return

    if numberValue < 1 or numberValue > total_lines(client.accinfo):
        print("Invalid Account Number")
        msvcrt.getch()
        return

    accountInfo = read_line(numberValue, client.accinfo)
    name, email, key = accountInfo.split("//")

    write_line(1, onelife.path_email, email)
    write_line(1, onelife.path_key, key)

    try:
        subprocess.Popen(client.directory, shell=True)
        if name.lower() == None:
            writeHistory(numberValue, curtime_formatted, email)
        else:

            writeHistory(numberValue, curtime_formatted, name)
            return
    except:
        print(f"Failed to run directory: {client.directory} - invalid ???")
        msvcrt.getch()
        switchtype.numswitch = True
        switchtype.select_accounts = False
        return

def cycle_accounts():
    total = total_lines(client.accinfo)
    print("[CYCLING ↻ ]\n")
    display_emails()

    userInput = input("\n[Start] > ").strip()
    if userInput.lower() == "exit":
        switchtype.numswitch = True
        switchtype.cycle_accounts = False
        return
    try:
        startNum = int(userInput)
    except:
        print("Invalid Input")
        msvcrt.getch()
        return

    if startNum >= total or startNum <= 0:
        print("Invalid Number For Starting Sequence...")
        msvcrt.getch()
        return

    userInput = input("\n[End] > ").strip()
    if userInput.lower() == "exit":
        return
    try:
        endNum = int(userInput)
    except:
        print("Invalid Input")
        msvcrt.getch()
        return

    if endNum < startNum or endNum > total:
        print("Invalid Number For EndNum Sequence...")
        msvcrt.getch()
        return

    currentNum = startNum
    start = True

    while currentNum <= endNum:
        if not start:
            time.sleep(4)

        accountInfo = read_line(currentNum, client.accinfo)
        name, email, key = accountInfo.split("//")

        write_line(1, onelife.path_email, email)
        write_line(1, onelife.path_key, key)

        try:
            subprocess.Popen(client.directory, shell=True)
        except:
            print("Invalid game directory, edit it in the main menu...")
            msvcrt.getch()
            switchtype.numswitch = True
            switchtype.cycle_accounts = False
            return

        start = False
        currentNum += 1

    return

class automata:
    @staticmethod
    def fetch_object_name(object_id):
        file_path = os.path.join("objects", f"{object_id}.txt")
        
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                if len(lines) < 2:  
                    return None 
                line = lines[1]
                name = read_line(2, file_path)
                return name
        except FileNotFoundError:
            return None
        
    @staticmethod
    def fetch_curse_token(data_stream):
        CX_SPLIT = data_stream.split()
        if "1#" in CX_SPLIT:
            return 1
        elif "0#" in CX_SPLIT:
            return 0
              
    @staticmethod
    def fetch_race(object_id):
        if object_id in [19, 350, 1007]:
            return "WHITEF"
        if object_id in [352, 347, 1008]:
            return "WHITEM"

        if object_id in [1628, 2462]:
            return "GINGERF"
        if object_id in [3081, 3080, 2403]:
            return "GINGERM"

        if object_id in [351, 353, 1009]:
            return "BROWNF"
        if object_id in [354, 355, 1010]:
            return "BROWNM"

        if object_id in [2404, 2464]:
            return "BLACKF"
        if object_id in [1629, 3078, 3079]:
            return "BLACKM"

        return "UNKNOWN"
    


    @staticmethod
    def strip_data(data, indices_to_remove, split_by=None):
        if isinstance(data, str):
            if split_by is None:
                data = data.split()  # splits on all whitespace by default
            else:
                data = data.split(split_by)

        for i in sorted(indices_to_remove, reverse=True):
            if 0 <= i < len(data):
                data.pop(i)

        return data
    
    @staticmethod
    def collision_check(array2d):  # Returns a 2D array with collision info
        collision_map = []
        for i in range(len(array2d)):  # Loop over rows
            row_collision = []
            for j in range(len(array2d[i])):  # Loop over columns
                # Uncomment below if you want to pause for each tile input
                # msvcrt.getch()
                
                tile, overlay, object_id_str = array2d[i][j].split(":")
                object_id = int(object_id_str)  # Convert and store as int
                
                file_path = os.path.join("objects", f"{object_id}.txt")
                try:
                    with open(file_path, "r") as f:
                        line_data = f.readlines()
                except FileNotFoundError:
                    # If file not found, assume no collision (blocksWalking=0)
                    row_collision.append(f"{object_id}//0")
                    continue
                
                # Check lines for collision info
                if any("blocksWalking=0" in line for line in line_data):
                    row_collision.append(f"{object_id}//0")
                elif any("blocksWalking=1" in line for line in line_data):
                    row_collision.append(f"{object_id}//1")
                else:
                    # Default to blocking if key is unknown
                    row_collision.append(f"{object_id}//1")
            collision_map.append(row_collision)
        
        return collision_map
    

# BOT TESTING
def bot_testing():
    class conditionals:
        pass
    class records:
        bot_registered_players = []

        player_updates = []
        player_names = []
        restricted_biomes = []

    class map_data:
        mapchunk = []
        collison_map = []
        
        chunksizeX = None
        chunksizeY = None
        mx = None
        my = None

    class player:
        relative_location = (0,0)
        steps_taken = 2

        birth_location = None

        race = None
        gender = None

        uID = None
        motheruID = None

        mother_name = None
        family_name = None

    tutorial_number = 0

    while True:
        print("Choose a mode ▼")
        print("1. Main")
        print("2. Tutorial 1")
        print("3. Tutorial 2")

        userInput = input("> ")
        if userInput == "1":    
            os.system("cls")
            break
        elif userInput == "2":
            tutorial_number = 1
            os.system("cls")
            break
        elif userInput == "3":
            tutorial_number = 2
            os.system("cls")
            break
        elif userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.bot_test = False
            return
        else:
            print("Invalid Input")
            msvcrt.getch()
            os.system("cls")

    print("[Fast Spawn]:\n")
    display_emails()

    try:
        userInput = input("\n  > ")
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.bot_test = False
            return

        numberValue = int(userInput)
    except:
        print("Not a valid input")
        msvcrt.getch()
        return
    if numberValue < 1 or numberValue > total_lines(client.accinfo):
        print("Invalid Account Number")
        msvcrt.getch()
        return
    try:
        accountInfo = read_line(numberValue, client.accinfo)
        name, email, key = accountInfo.split("//")
    except:
        print("Corrupted or invalid account line format.")
        msvcrt.getch()
        return

    key = key.replace("-", "")

    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((onelife.server_ip,onelife.server_port))
    except Exception:
        print("Failed to connect to server")
        msvcrt.getch()
        return

    client_sock.setblocking(False)

    # The Bot Engine
    packet_buffer = bytes()

    while True:
        #
        new_byte = get_next_byte(client_sock)

        while new_byte is not None:
            packet_buffer += new_byte
            if new_byte == b'#':

                data_stream = handle_packet(client_sock, packet_buffer)
                packet_buffer = bytes() 
                print(data_stream)
                if "MC" in data_stream: 
                    MC_CUT = automata.strip_data(data_stream, [0, 5, 6]) 

                    map_data.chunksizeX = int(MC_CUT[0])
                    map_data.chunksizeY = int(MC_CUT[1])
                    map_data.mx = int(MC_CUT[2])
                    map_data.my = int(MC_CUT[3])

                    expected_len = map_data.chunksizeX * map_data.chunksizeY

  
                    chunk_data = MC_CUT[4:] 
                    if len(chunk_data) > expected_len:
                        data_stream = chunk_data[expected_len:]  
                        chunk_data = chunk_data[:expected_len]  
                    else:
                        continue

                    chunk_data[0] = chunk_data[0].replace("#", "").strip()
                    map_data.mapchunk = automata.build2d_array(chunk_data, map_data.chunksizeX, map_data.chunksizeY)
                    map_data.collison_map = automata.collision_check(map_data.mapchunk)


                # Record Takers
                if "NM" in data_stream:
                    records.player_names.extend(data_stream.split())
                if "PU" in data_stream:
                    records.player_updates.extend(data_stream.split())
                if "BB" in data_stream:
                    records.restricted_biomes.extend(data_stream.split())

                
                # Login Protocols
                if "SN" in data_stream:
                    SN_SPLIT = data_stream.split()
                    server_secret = SN_SPLIT[2]
                    password_hash = HMAC_SHA1(onelife.server_password, server_secret)
                    key_hash = HMAC_SHA1(key, server_secret)
                    message = f"LOGIN client_{client.tag} {email} {password_hash} {key_hash} {tutorial_number}#"
                    client_sock.sendall(message.encode())

                elif "ACCEPTED" in data_stream:
                    print(f"{email.upper()} ACCEPTED AS BOT")

                    client_sock.sendall("MOTH 0 0 #".encode())
                elif "REJECTED" in data_stream:
                    os.system("cls")
                    print(f"{email} REJECTED")
                    msvcrt.getch()
                    return
                elif "NO_LIFE_TOKENS" in data_stream:
                    os.system("cls")
                    print(f"{email} NO LIFE TOKENS")
                    msvcrt.getch()
                    return
        
                # Donkey Town Status Fetcher
                if player.birth_location is None and "CX" in data_stream:
                    CXTokens = automata.fetch_curse_token(data_stream)
                    if CXTokens > 0:
                       player.birth_location = "MAINLAND" 

                    else:
                        player.birth_location = "DONKEYTOWN"

                # Player Profile Fetcher
                if player.uID is None and "PS" in data_stream:
                    data_stream = data_stream.replace("PS", "").replace("#", "").strip()
                    PS_SPLIT = data_stream.split()

                    if len(PS_SPLIT) == 10:  # Normal Case
                        try:
                            int(PS_SPLIT[6])  # MOTHER PID

                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[6]
                            player.mother_name = PS_SPLIT[3]
                            player.family_name = PS_SPLIT[4]

                        except:
                            pass

                    elif len(PS_SPLIT) == 9:  # No Last Name
                        try:
                            int(PS_SPLIT[5])  # MOTHER PID

                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[5]
                            player.mother_name = PS_SPLIT[3]

                        except:
                            pass

                    elif len(PS_SPLIT) == 8:  # No Name
                        try:
                            int(PS_SPLIT[4])  # MOTHER PID

                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[4]

                        except:
                            pass

                    if "NO MOTHER" in data_stream:
                        player.uID = PS_SPLIT[0]  # PID

                    if player.uID:
                        player.uID = player.uID.replace("/0", "").strip()

                    if player.family_name is None:
                        player.family_name = "NONE"

                # Race Detection
                if records.player_updates and player.uID and not player.race:
                    if str(player.uID) in records.player_updates:
                        idx = records.player_updates.index(str(player.uID))
                        if idx + 1 < len(records.player_updates):
                            
                            race_code = automata.fetch_race(int(records.player_updates[idx + 1]))
                            
                            if race_code.endswith("F"):
                                player.gender = "FEMALE"
                            elif race_code.endswith("M"):
                                player.gender = "MALE"
                            else:
                                player.gender = "UNKNOWN"

                            if race_code.startswith("WHITE"):
                                player.race = "WHITE"
                            elif race_code.startswith("GINGER"):
                                player.race = "GINGER"
                            elif race_code.startswith("BROWN"):
                                player.race = "BROWN"
                            elif race_code.startswith("BLACK"):
                                player.race = "BLACK"
                            else:
                                player.race = "UNKNOWN"
                                    
                if player.gender and player.birth_location and player.uID: # Main for bot
                    pass
        #                
            new_byte = get_next_byte(client_sock)

# AUTOMATA

def fast_spawn():
    class conditionals:
        pass

    class records:
        player_updates = []
        player_names = []

    class player:
        birth_location = None

        race = None
        gender = None

        uID = None
        motheruID = None

        mother_name = None
        family_name = None

    tutorial_number = 0

    while True:
        print("Choose a mode ▼")
        print("1. Main")
        print("2. Tutorial 1")
        print("3. Tutorial 2")

        userInput = input("> ")
        if userInput == "1":
            os.system("cls")
            break
        elif userInput == "2":
            tutorial_number = 1
            os.system("cls")
            break
        elif userInput == "3":
            tutorial_number = 2
            os.system("cls")
            break
        elif userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.fast_spawn = False
            return
        else:
            print("Invalid Input")
            msvcrt.getch()
            os.system("cls")

    print("[Fast Spawn]:\n")
    display_emails()

    try:
        userInput = input("\n  > ")
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.fast_spawn = False
            return

        numberValue = int(userInput)
    except:
        print("Not a valid input")
        msvcrt.getch()
        return
    if numberValue < 1 or numberValue > total_lines(client.accinfo):
        print("Invalid Account Number")
        msvcrt.getch()
        return
    try:
        accountInfo = read_line(numberValue, client.accinfo)
        name, email, key = accountInfo.split("//")
    except:
        print("Corrupted or invalid account line format.")
        msvcrt.getch()
        return

    key = key.replace("-", "")

    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((onelife.server_ip,onelife.server_port))
    except Exception:
        print("Failed to connect to server")
        msvcrt.getch()
        return

    client_sock.setblocking(False)

    # The Bot Engine
    packet_buffer = bytes()

    while True:
        #
        new_byte = get_next_byte(client_sock)

        while new_byte is not None:
            packet_buffer += new_byte
            if new_byte == b'#':

                data_stream = handle_packet(client_sock, packet_buffer)
                packet_buffer = bytes() 

                # Record Takers
                if "NM" in data_stream:
                    records.player_names.extend(data_stream.split())
                if "PU" in data_stream:
                    records.player_updates.extend(data_stream.split())

                # Login Protocols
                if "SN" in data_stream:
                    SN_SPLIT = data_stream.split()
                    server_secret = SN_SPLIT[2]
                    password_hash = HMAC_SHA1(onelife.server_password, server_secret)
                    key_hash = HMAC_SHA1(key, server_secret)
                    message = f"LOGIN client_{client.tag} {email} {password_hash} {key_hash} {tutorial_number}#"
                    client_sock.sendall(message.encode())

                elif "ACCEPTED" in data_stream:
                    client_sock.sendall("MOTH 0 0 #".encode())
                elif "REJECTED" in data_stream:
                    os.system("cls")
                    print(f"{email} REJECTED")
                    msvcrt.getch()
                    return
                elif "NO_LIFE_TOKENS" in data_stream:
                    os.system("cls")
                    print(f"{email} NO LIFE TOKENS")
                    msvcrt.getch()
                    return
        
                # Donkey Town Status Fetcher
                if player.birth_location is None and "CX" in data_stream:
                    CXTokens = automata.fetch_curse_token(data_stream)
                    if CXTokens > 0:
                       player.birth_location = "MAINLAND" 

                    else:
                        player.birth_location = "DONKEYTOWN"

                # Player Profile Fetcher
                if player.uID is None and "PS" in data_stream:
                    data_stream = data_stream.replace("PS", "").replace("#", "").strip()
                    PS_SPLIT = data_stream.split()

                    if len(PS_SPLIT) == 10:  # Normal Case
                        try:
                            int(PS_SPLIT[6])  # MOTHER PID

                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[6]
                            player.mother_name = PS_SPLIT[3]
                            player.family_name = PS_SPLIT[4]

                        except:
                            pass

                    elif len(PS_SPLIT) == 9:  # No Last Name
                        try:
                            int(PS_SPLIT[5])  # MOTHER PID

                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[5]
                            player.mother_name = PS_SPLIT[3]

                        except:
                            pass

                    elif len(PS_SPLIT) == 8:  # No Name
                        try:
                            int(PS_SPLIT[4])  # MOTHER PID

                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[4]

                        except:
                            pass

                    if "NO MOTHER" in data_stream:
                        player.uID = PS_SPLIT[0]  # PID

                    if player.uID:
                        player.uID = player.uID.replace("/0", "").strip()

                    if player.family_name is None:
                        player.family_name = "NONE"


                # Race Detection
                if records.player_updates and player.uID and not player.race:
                    if str(player.uID) in records.player_updates:
                        idx = records.player_updates.index(str(player.uID))
                        if idx + 1 < len(records.player_updates):
                            
                            race_code = automata.fetch_race(int(records.player_updates[idx + 1]))
                            
                            if race_code.endswith("F"):
                                player.gender = "FEMALE"
                            elif race_code.endswith("M"):
                                player.gender = "MALE"
                            else:
                                player.gender = "UNKNOWN"

                            if race_code.startswith("WHITE"):
                                player.race = "WHITE"
                            elif race_code.startswith("GINGER"):
                                player.race = "GINGER"
                            elif race_code.startswith("BROWN"):
                                player.race = "BROWN"
                            elif race_code.startswith("BLACK"):
                                player.race = "BLACK"
                            else:
                                player.race = "UNKNOWN"
                                    
                if player.gender and player.birth_location and player.uID:
                    
                    if name.lower() == None:
                        writeHistory(numberValue, curtime_formatted, email)
                    else:
                        writeHistory(numberValue, curtime_formatted, name)
                    os.system("cls")
                    print(f"Location ?!: {player.birth_location}")
                    print("--------------------------------------------")
                    print(f"Family: {player.family_name}")
                    print(f"Gender: {player.gender}")
                    print(f"Race: {player.race}")

                    msvcrt.getch()
                    return
        #                
            new_byte = get_next_byte(client_sock)

def terminate_account():
    packet_buffer = bytes()
    

   
    client.tag
    onelife.server_password

    tutorial_number = 0

    twincode = "automata_rebirth"

    print("[INSTAKILL ➴ ]:\n")


    display_emails()

    try:
        userInput = input("\n  > ")
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.quick_kill = False
            return

        numberValue = int(userInput)
    except:
        print("Not a valid input")
        msvcrt.getch()
        return

    if numberValue < 1 or numberValue > total_lines(client.accinfo):
        print("Invalid Account Number")
        msvcrt.getch()
        return

    accountInfo = read_line(numberValue, client.accinfo)
    name, email, key = accountInfo.split("//")
    key = key.replace("-","")

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((onelife.server_ip, onelife.server_port))

    except:
        print("Failed to connect to server_ip") 
        msvcrt.getch()
        return


    client_socket.setblocking(False)
    # Main
    while True:
        new_byte = get_next_byte(client_socket)
        while new_byte is not None:
            packet_buffer += new_byte
            if new_byte == b'#':
                data_stream = handle_packet(client_socket, packet_buffer)

                # Start Login Protocol
                if "SN" in data_stream: 
                    SN_SPLIT = data_stream.split()
                    server_secret = SN_SPLIT[2]

                    password_hash = HMAC_SHA1(onelife.server_password, server_secret)
                    key_hash = HMAC_SHA1(key, server_secret)
                    twincode_hash = HMAC_SHA1(twincode, server_secret)


                    message = f"RLOGIN client_{client.tag} {email} {password_hash} {key_hash} {tutorial_number} {twincode_hash} 1#"
                    client_socket.sendall(message.encode())

                if "ACCEPTED" in data_stream:
                    os.system("cls")
                    time.sleep(1)
                    client_socket.sendall("DIE 0 0#".encode())
                    print("ACCOUNT SUCESSFULLY KILLED")
                    msvcrt.getch()
                    return
                elif "REJECTED" in data_stream:
                    os.system("cls")
                    print("ACCOUNT REJECTED")
                    msvcrt.getch()
                    return
                elif "NO_LIFE_TOKENS" in data_stream:
                    os.system("cls")
                    print("NO LIFE TOKENS")
                    msvcrt.getch()
                    return      
                        

                packet_buffer = bytes()
            new_byte = get_next_byte(client_socket)

def spawn_many():
    class conditionals:
        pass

    class records:
        player_updates = []
        player_names = []

    class player:
        birth_location = None
        race = None
        gender = None
        uID = None
        motheruID = None
        mother_name = None
        family_name = None

    tutorial_number = 0
    packet_buffer = bytes()

    while True:
        print("1. Spawn Normally")
        print("2. Tutorial 1")
        print("3. Tutorial 2\n")
        uInput = input("> ")

        if uInput == "1":
            os.system("cls")
            break
        elif uInput == "2":
            tutorial_number = 1
            os.system("cls")
            break
        elif uInput == "3":
            tutorial_number = 2
            os.system("cls")
            break
        elif userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.spawn_any = False            
            return
            
        else: 
            os.system("cls")
    print("[Spawn Many ⤔ ]:\n")
    display_emails()

    try:
        userInput = input("\n[Start] > ").strip()
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.spawn_any = False
            return
        start_index = int(userInput)
    except ValueError:
        print("Invalid Input")
        msvcrt.getch()
        return

    if start_index < 1 or start_index > total_lines(client.accinfo):
        print("Range Error")    
        msvcrt.getch()
        return
    try:
        userInput = input("[End] > ").strip()
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.spawn_any = False
            return
        end_index = int(userInput)
    except ValueError:
        print("Invalid input..")
        msvcrt.getch()
        return
    if end_index < start_index or end_index > total_lines(client.accinfo):
        print("Range Error")
        msvcrt.getch()
        return

    for i in range(start_index, end_index + 1):
        records.player_updates = []
        records.player_names = []

        player.birth_location = None
        player.race = None
        player.gender = None
        player.uID = None
        player.motheruID = None
        player.mother_name = None
        player.family_name = None

        name, email, key = read_line(i, client.accinfo).split("//")
        key = key.replace("-", "")

        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((onelife.server_ip, onelife.server_port))
            client_sock.setblocking(False)
        except Exception:
            print("Failed to connect to server")
            msvcrt.getch()
            return

        while True:
            if msvcrt.kbhit():
                if msvcrt.getch() == b'\r':
                    print("\n[Scan stopped by user]")
                    msvcrt.getch()
                    return

            new_byte = get_next_byte(client_sock)
            if new_byte is None:
                continue

            packet_buffer += new_byte

            if new_byte == b'#':
                data_stream = handle_packet(client_sock, packet_buffer)
                packet_buffer = bytes()

                # Record Takers
                if "NM" in data_stream:
                    records.player_names.extend(data_stream.split())
                if "PU" in data_stream:
                    records.player_updates.extend(data_stream.split())

                # Login
                if "SN" in data_stream:
                    server_secret = data_stream.split()[2]
                    password_hash = HMAC_SHA1(onelife.server_password, server_secret)
                    key_hash = HMAC_SHA1(key, server_secret)
                    login_message = f"LOGIN client_{client.tag} {email} {password_hash} {key_hash} {tutorial_number}#"
                    client_sock.sendall(login_message.encode())

                elif "ACCEPTED" in data_stream:
                    time.sleep(1)
                    client_sock.sendall("MOTH 0 0#".encode())

                elif "REJECTED" in data_stream:
                    os.system("cls")
                    print(f"{email} REJECTED")
                    msvcrt.getch()
                    break

                elif "NO_LIFE_TOKENS" in data_stream:
                    os.system("cls")
                    print(f"{email} NO LIFE TOKENS")
                    msvcrt.getch()
                    break   
                
                # Curse Status Fetcher
                if "CX" in data_stream and player.birth_location is None:
                    CXTokens = automata.fetch_curse_token(data_stream)
                    if CXTokens > 0:
                        player.birth_location = "MAINLAND"
                    else:
                        player.birth_location = "DONKEYTOWN"

                # Birth Info Fetcher
                if "PS" in data_stream and player.uID is None:
                    stream = data_stream.replace("PS", "").replace("#", "").strip()
                    split = stream.split()

                    try:
                        if len(split) == 10:
                            int(split[6])
                            player.uID = split[0]
                            player.motheruID = split[6]
                            player.mother_name = split[3]
                            player.family_name = split[4]
                        elif len(split) == 9:
                            int(split[5])
                            player.uID = split[0]
                            player.motheruID = split[5]
                            player.mother_name = split[3]
                        elif len(split) == 8:
                            int(split[4])
                            player.uID = split[0]
                            player.motheruID = split[4]
                        elif "NO MOTHER" in data_stream:
                            player.uID = split[0]
                    except:
                        pass

                    if player.uID:
                        player.uID = player.uID.replace("/0", "").strip()
                    if player.family_name is None:
                        player.family_name = "NONE"

                # Player Race Finder
                if records.player_updates and player.uID and not player.race:
                    if str(player.uID) in records.player_updates:
                        idx = records.player_updates.index(str(player.uID))
                        if idx + 1 < len(records.player_updates):
                            race_code = automata.fetch_race(int(records.player_updates[idx + 1]))
                            if race_code.endswith("F"):
                                player.gender = "FEMALE"
                            elif race_code.endswith("M"):
                                player.gender = "MALE"
                            else:
                                player.gender = "UNKNOWN"

                            if race_code.startswith("WHITE"):
                                player.race = "WHITE"
                            elif race_code.startswith("GINGER"):
                                player.race = "GINGER"
                            elif race_code.startswith("BROWN"):
                                player.race = "BROWN"
                            elif race_code.startswith("BLACK"):
                                player.race = "BLACK"
                            else:
                                player.race = "UNKNOWN"

                # Spawn Info Card 
                if player.gender and player.birth_location and player.uID:
                    print(f"\n{i}. {email}")
                    print(f"Location {'(TUTORIAL) ' if tutorial_number != 0 else ''}?!: {player.birth_location}")
                    print(f"Family: {player.family_name}")  
                    print(f"Gender: {player.gender}")
                    print(f"Race: {player.race}")
                    msvcrt.getch()
                    break

    print("\n[Done]")
    writeHistory(f"{start_index}-{i}", curtime_formatted, f"{start_index}-{i}")
    msvcrt.getch()

def terminate_many():
    twincode = "automata_rebirth"

    class conditionals:
        pass

    class records:
        player_updates = []
        player_names = []

    class player:
        birth_location = None
        race = None
        gender = None
        uID = None
        motheruID = None
        mother_name = None
        family_name = None

    tutorial_number = 0
    packet_buffer = bytes()


    print("[Kill Many ➴ ]:\n")
    display_emails()

    try:
        userInput = input("\n[Start] > ").strip()
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.kill_many = False
            return
        start_index = int(userInput)
    except ValueError:
        print("Invalid Input")
        msvcrt.getch()
        return

    if start_index < 1 or start_index > total_lines(client.accinfo):
        print("Range Error")
        msvcrt.getch()
        return
    try:
        userInput = input("[End] > ").strip()
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.kill_many = False
            return
        end_index = int(userInput)
    except ValueError:
        print("Invalid input..")
        msvcrt.getch()
        return
    if end_index < start_index or end_index > total_lines(client.accinfo):
        print("Range Error")
        msvcrt.getch()
        return

    for i in range(start_index, end_index + 1):
        records.player_updates = []
        records.player_names = []

        player.birth_location = None
        player.race = None
        player.gender = None
        player.uID = None
        player.motheruID = None
        player.mother_name = None
        player.family_name = None

        name, email, key = read_line(i, client.accinfo).split("//")
        key = key.replace("-", "")

        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((onelife.server_ip, onelife.server_port))
            client_sock.setblocking(False)
        except Exception:
            print("Failed to connect to server")
            msvcrt.getch()
            return

        while True:
            if msvcrt.kbhit():
                if msvcrt.getch() == b'\r':
                    print("\n[Scan stopped by user]")
                    msvcrt.getch()
                    return

            new_byte = get_next_byte(client_sock)
            if new_byte is None:
                continue

            packet_buffer += new_byte

            if new_byte == b'#':
                data_stream = handle_packet(client_sock, packet_buffer)
                packet_buffer = bytes()

                # Record Takers
                if "NM" in data_stream:
                    records.player_names.extend(data_stream.split())
                if "PU" in data_stream:
                    records.player_updates.extend(data_stream.split())

                # Login
                if "SN" in data_stream:
                    server_secret = data_stream.split()[2]
                    twincode_hash = HMAC_SHA1(twincode, server_secret)
                    password_hash = HMAC_SHA1(onelife.server_password, server_secret)
                    key_hash = HMAC_SHA1(key, server_secret)
                    login_message = f"RLOGIN client_{client.tag} {email} {password_hash} {key_hash} {tutorial_number} {twincode_hash} 1#"
                    client_sock.sendall(login_message.encode())

                elif "ACCEPTED" in data_stream:
                    time.sleep(1)
                    client_sock.sendall("MOTH 0 0#".encode())

                elif "REJECTED" in data_stream:
                    os.system("cls")
                    print(f"{email} REJECTED")
                    msvcrt.getch()
                    break

                elif "NO_LIFE_TOKENS" in data_stream:
                    os.system("cls")
                    print(f"{email} NO LIFE TOKENS")
                    msvcrt.getch()
                    break
                
                # Curse Status Fetcher
                if "CX" in data_stream and player.birth_location is None:
                    CXTokens = automata.fetch_curse_token(data_stream)
                    if CXTokens > 0:
                        player.birth_location = "MAINLAND"
                    else:
                        player.birth_location = "DONKEYTOWN"

                # Birth Info Fetcher
                if "PS" in data_stream and player.uID is None:
                    stream = data_stream.replace("PS", "").replace("#", "").strip()
                    split = stream.split()

                    try:
                        if len(split) == 10:
                            int(split[6])
                            player.uID = split[0]
                            player.motheruID = split[6]
                            player.mother_name = split[3]
                            player.family_name = split[4]
                        elif len(split) == 9:
                            int(split[5])
                            player.uID = split[0]
                            player.motheruID = split[5]
                            player.mother_name = split[3]
                        elif len(split) == 8:
                            int(split[4])
                            player.uID = split[0]
                            player.motheruID = split[4]
                        elif "NO MOTHER" in data_stream:
                            player.uID = split[0]
                    except:
                        pass

                    if player.uID:
                        player.uID = player.uID.replace("/0", "").strip()
                    if player.family_name is None:
                        player.family_name = "NONE"

                # Player Race Finder
                if records.player_updates and player.uID and not player.race:
                    if str(player.uID) in records.player_updates:
                        idx = records.player_updates.index(str(player.uID))
                        if idx + 1 < len(records.player_updates):
                            race_code = automata.fetch_race(int(records.player_updates[idx + 1]))
                            if race_code.endswith("F"):
                                player.gender = "FEMALE"
                            elif race_code.endswith("M"):
                                player.gender = "MALE"
                            else:
                                player.gender = "UNKNOWN"

                            if race_code.startswith("WHITE"):
                                player.race = "WHITE"
                            elif race_code.startswith("GINGER"):
                                player.race = "GINGER"
                            elif race_code.startswith("BROWN"):
                                player.race = "BROWN"
                            elif race_code.startswith("BLACK"):
                                player.race = "BLACK"
                            else:
                                player.race = "UNKNOWN"

                # Spawn Info Card 
                if player.gender and player.birth_location and player.uID: 
                    print(f"\n{i}. {email}")
                    print(f"Rebirthed Location ?!: {player.birth_location}")
                    print(f"Rebirthed Family: {player.family_name}")
                    print(f"Rebirthed Gender: {player.gender}")
                    print(f"Rebirthed Race: {player.race}")
                    client_sock.sendall("DIE 0 0#".encode())                                        
                    print(f"Status: ACCOUNT SUCESSFULLY TERMINATED?!")
                    break

    print("\n[Done]")
    writeHistory(f"{start_index}-{end_index}", curtime_formatted, f"{start_index}-{end_index}")
    msvcrt.getch()

import os
import socket
import subprocess
import time
import msvcrt

from dataclasses import dataclass

@dataclass
class Conditionals:
    donkeytown_scan: bool = False
    keep_alive_on_wrong_spawn: bool = False

@dataclass
class Records:
    player_updates: list = None
    player_names: list = None

    def reset(self):
        self.player_updates = []
        self.player_names = []

@dataclass
class Player:
    birth_location: str = None
    race: str = None
    gender: str = None
    uID: str = None
    motheruID: str = None
    mother_name: str = None
    family_name: str = None

def detect_spawn():
    """
    Assumes these external functions/objects exist in your project:
      - display_emails()
      - read_line(index, path)
      - total_lines(path)
      - onelife (object with server_ip, server_port, server_password, path_email, path_key)
      - client (object with accinfo, tag, directory)
      - switchtype (object with numswitch, detect_accounts)
      - get_next_byte(sock) -> bytes or None
      - handle_packet(sock, packet_bytes) -> str (packet string)
      - automata.fetch_curse_token, automata.fetch_race
      - HMAC_SHA1(key, salt) -> str
      - write_line(pos, path, value)
      - writeHistory(range_str, time_str, note)
      - curtime_formatted (string)
    """

    conditionals = Conditionals()
    records = Records()
    player = Player()

    tutorial_number = 0
    # packet_buffer should be per-connection, set before each connection loop
    # packet_buffer = bytes()

    # --- First menu: choose scan type ---
    while True:
        print("1. Scan For Accounts Outside Of Donkeytown")
        print("2. Scan For Accounts In Donkeytown\n")
        uInput = input("> ").strip()
        if uInput == "1":
            os.system("cls")
            break
        if uInput == "2":
            conditionals.donkeytown_scan = True
            os.system("cls")
            break
        if uInput.lower() == "exit":
            # these objects should exist in your program
            switchtype.numswitch = True
            switchtype.detect_accounts = False
            return

    # --- Second menu: whether to keep alive on wrong spawn ---
    while True:
        print("1. [Kill on wrong spawn] - suggested ")
        print("2. Keep alive on wrong spawn")
        uInput = input("> ").strip()
        if uInput == "1":
            os.system("cls")
            # keep_alive_on_wrong_spawn defaults False
            break
        if uInput == "2":
            conditionals.keep_alive_on_wrong_spawn = True
            os.system("cls")
            break
        if uInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.detect_accounts = False
            return

    print("[Detect Working Accounts ᯤ ]:\n")
    display_emails()  # external UI helper - must exist

    # Get start index
    try:
        userInput = input("\n[Start] > ").strip()
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.detect_accounts = False
            return
        start_index = int(userInput)
    except ValueError:
        print("Invalid Input")
        msvcrt.getch()
        return

    if start_index < 1 or start_index > total_lines(client.accinfo):
        print("Range Error")
        msvcrt.getch()
        return

    # Get end index
    try:
        userInput = input("[End] > ").strip()
        if userInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.detect_accounts = False
            return
        end_index = int(userInput)
    except ValueError:
        print("Invalid input..")
        msvcrt.getch()
        return

    if end_index < start_index or end_index > total_lines(client.accinfo):
        print("Range Error")
        msvcrt.getch()
        return

    # Main loop over account lines
    for i in range(start_index, end_index + 1):
        # reset records and player for each account
        records.reset()
        player = Player()
        packet_buffer = bytes()

        # read line; expected format "name//email//key"
        try:
            line = read_line(i, client.accinfo)
            name, email, key = line.split("//")
        except Exception:
            print(f"Malformed line at {i}: {line!r}")
            continue

        key = key.replace("-", "").strip()

        # connect to server
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((onelife.server_ip, onelife.server_port))
            client_sock.setblocking(False)
        except Exception as e:
            print("Failed to connect to server:", e)
            msvcrt.getch()
            return

        # per-connection loop: read bytes and handle packets
        while True:
            # allow user to abort with Enter
            if msvcrt.kbhit():
                if msvcrt.getch() == b'\r':
                    print("\n[Scan stopped by user]")
                    msvcrt.getch()
                    return

            try:
                new_byte = get_next_byte(client_sock)
            except Exception:
                # If get_next_byte can raise, ignore and continue
                new_byte = None

            if new_byte is None:
                # don't busy-loop too fast
                time.sleep(0.01)
                continue

            packet_buffer += new_byte

            # Packet terminator '#' (keeps same semantics as original)
            if new_byte == b'#':
                try:
                    data_stream = handle_packet(client_sock, packet_buffer)
                except Exception:
                    # If packet handler fails, reset buffer and break connection loop
                    packet_buffer = bytes()
                    break

                packet_buffer = bytes()

                # Record takers - split and extend lists
                if "NM" in data_stream:
                    records.player_names.extend(data_stream.split())
                if "PU" in data_stream:
                    records.player_updates.extend(data_stream.split())

                # Login flow
                if "SN" in data_stream:
                    # expected that server_secret is in position 2
                    parts = data_stream.split()
                    if len(parts) >= 3:
                        server_secret = parts[2]
                        password_hash = HMAC_SHA1(onelife.server_password, server_secret)
                        key_hash = HMAC_SHA1(key, server_secret)
                        login_message = f"LOGIN client_{client.tag} {email} {password_hash} {key_hash} {tutorial_number}#"
                        try:
                            client_sock.sendall(login_message.encode())
                        except Exception:
                            pass

                elif "ACCEPTED" in data_stream:
                    time.sleep(1)
                    try:
                        client_sock.sendall("MOTH 0 0#".encode())
                    except Exception:
                        pass

                elif "REJECTED" in data_stream:
                    os.system("cls")
                    print(f"{email} REJECTED")
                    msvcrt.getch()
                    break

                elif "NO_LIFE_TOKENS" in data_stream:
                    os.system("cls")
                    print(f"{email} NO LIFE TOKENS")
                    msvcrt.getch()
                    break

                # Curse Status Fetcher
                if "CX" in data_stream and player.birth_location is None:
                    try:
                        CXTokens = automata.fetch_curse_token(data_stream)
                        if CXTokens > 0:
                            player.birth_location = "MAINLAND"
                        else:
                            player.birth_location = "DONKEYTOWN"
                    except Exception:
                        # If automata fails, leave birth_location None
                        pass

                # Birth Info Fetcher
                if "PS" in data_stream and player.uID is None:
                    stream = data_stream.replace("PS", "").replace("#", "").strip()
                    parts = stream.split()

                    try:
                        # try to parse different known lengths robustly
                        if len(parts) >= 7:
                            # common case: mother index at pos 6 (0-based)
                            # ensure that the index field is numeric where expected
                            int(parts[6])
                            player.uID = parts[0]
                            player.motheruID = parts[6]
                            # guard accesses that may not exist
                            if len(parts) > 3:
                                player.mother_name = parts[3]
                            if len(parts) > 4:
                                player.family_name = parts[4]
                        elif len(parts) == 6:
                            int(parts[5])
                            player.uID = parts[0]
                            player.motheruID = parts[5]
                            if len(parts) > 3:
                                player.mother_name = parts[3]
                        elif len(parts) == 5:
                            int(parts[4])
                            player.uID = parts[0]
                            player.motheruID = parts[4]
                        elif "NO MOTHER" in data_stream:
                            player.uID = parts[0]
                    except Exception:
                        # if parsing fails, ignore and continue
                        pass

                    if player.uID:
                        player.uID = player.uID.replace("/0", "").strip()
                    if player.family_name is None:
                        player.family_name = "NONE"

                # Player Race Finder (requires player_updates and uID)
                if records.player_updates and player.uID and not player.race:
                    # search for uID in the updates list (string compare)
                    uid_str = str(player.uID)
                    if uid_str in records.player_updates:
                        idx = records.player_updates.index(uid_str)
                        if idx + 1 < len(records.player_updates):
                            try:
                                race_code = automata.fetch_race(int(records.player_updates[idx + 1]))
                                if race_code.endswith("F"):
                                    player.gender = "FEMALE"
                                elif race_code.endswith("M"):
                                    player.gender = "MALE"
                                else:
                                    player.gender = "UNKNOWN"

                                if race_code.startswith("WHITE"):
                                    player.race = "WHITE"
                                elif race_code.startswith("GINGER"):
                                    player.race = "GINGER"
                                elif race_code.startswith("BROWN"):
                                    player.race = "BROWN"
                                elif race_code.startswith("BLACK"):
                                    player.race = "BLACK"
                                else:
                                    player.race = "UNKNOWN"
                            except Exception:
                                pass

                # Spawn Info Card: once we have gender, birth_location and uID
                if player.gender and player.birth_location and player.uID:
                    print(f"\n{i}. {email}")
                    print(f"Location ?!: {player.birth_location}")
                    print(f"Family: {player.family_name}")
                    print(f"Gender: {player.gender}")
                    print(f"Race: {player.race}")

                    match_condition = ((conditionals.donkeytown_scan and player.birth_location == "DONKEYTOWN")
                                       or (not conditionals.donkeytown_scan and player.birth_location == "MAINLAND"))

                    if match_condition:
                        # found desired account
                        write_line(1, onelife.path_email, email)
                        write_line(1, onelife.path_key, key)
                        # launch client
                        try:
                            subprocess.Popen(client.directory, shell=True)
                        except Exception:
                            pass
                        writeHistory(f"{start_index} - {i}", curtime_formatted, f"{start_index} - {i}")
                        print("[Done]")
                        msvcrt.getch()
                        # close socket gracefully
                        try:
                            client_sock.close()
                        except Exception:
                            pass
                        return
                    else:
                        # wrong spawn
                        time.sleep(1)
                        if not conditionals.keep_alive_on_wrong_spawn:
                            try:
                                client_sock.sendall("DIE 0 0#".encode())
                            except Exception:
                                pass
                        break  # break connection loop and move to next account

        # end while connection loop
        try:
            client_sock.close()
        except Exception:
            pass

    # finished scanning range
    print("\n[Done]")
    writeHistory(f"{start_index}-{i}", curtime_formatted, f"{start_index}-{i}")
    msvcrt.getch()

def account_locking():
    import time  # For retry delays

    class Records:
        def __init__(self):
            self.player_updates = []
            self.player_names = []

    class Player:
        def __init__(self):
            self.birth_location = None
            self.race = None
            self.gender = None
            self.uID = None
            self.motheruID = None
            self.mother_name = None
            self.family_name = None

    tutorial_number = 2

    while True:
        print("1. Tutorial based locking")
        print("2. Non-Tutorial based locking")

        uInput = input("\n> ")

        if uInput == "1":
            os.system("cls")
            break
        elif uInput == "2":
            os.system("cls")
            tutorial_number = 0
            break
        elif uInput.lower() == "exit":
            switchtype.numswitch = True
            switchtype.lock_account = False
            return
        else:
            os.system("cls")
            print("Invalid Input")
            os.system("cls")
        uInput = input(">")

    print("[Lock Accounts]:\n")
    display_emails()

    user_input = input("\n  > ").strip()
    if user_input.lower() == "exit":
        switchtype.numswitch = True
        switchtype.fast_spawn = False
        return

    try:
        number_value = int(user_input)
    except ValueError:
        print("Not a valid input")
        msvcrt.getch()
        return

    if number_value < 1 or number_value > total_lines(client.accinfo):
        print("Invalid Account Number")
        msvcrt.getch()
        return

    try:
        account_info = read_line(number_value, client.accinfo)
        name, email, key = account_info.split("//")
    except Exception:
        print("Corrupted or invalid account line format.")
        msvcrt.getch()
        return

    key = key.replace("-", "")

    lock_cycles = 0

    while True:  # Outer loop to retry forever
        lock_cycles += 1
        os.system("cls")

        player = Player()
        records = Records()
        packet_buffer = b""

        # Attempt connection with retry on failure
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((onelife.server_ip, onelife.server_port))
            client_sock.setblocking(False)
        except Exception:
            print("Failed to connect to server, retrying in 5 seconds...")
            time.sleep(5)
            continue  # Retry outer loop

        while True:  # Inner loop to process packets
            # User abort check
            if msvcrt.kbhit():
                if msvcrt.getch() == b'\r':
                    print("\n[Scan ended by user]")
                    msvcrt.getch()
                    client_sock.close()
                    return

            try:
                data = client_sock.recv(1024)
                if not data:
                    print("Server closed connection, reconnecting...")
                    client_sock.close()
                    break  # break inner loop to reconnect
                packet_buffer += data
            except BlockingIOError:
                pass
            except Exception as e:
                print(f"Socket error: {e}, reconnecting...")
                client_sock.close()
                break  # break inner loop to reconnect

            while b'#' in packet_buffer:
                idx = packet_buffer.index(b'#')
                raw_packet = packet_buffer[:idx].decode(errors='ignore')
                packet_buffer = packet_buffer[idx+1:]

                data_stream = raw_packet.strip()
                if not data_stream:
                    continue

                if "NM" in data_stream:
                    records.player_names.extend(data_stream.split())
                if "PU" in data_stream:
                    records.player_updates.extend(data_stream.split())

                if "SN" in data_stream:
                    SN_SPLIT = data_stream.split()
                    if len(SN_SPLIT) > 2:
                        server_secret = SN_SPLIT[2]
                        password_hash = HMAC_SHA1(onelife.server_password, server_secret)
                        key_hash = HMAC_SHA1(key, server_secret)
                        message = f"LOGIN client_{client.tag} {email} {password_hash} {key_hash} {tutorial_number}#"
                        client_sock.sendall(message.encode())
                elif "ACCEPTED" in data_stream:
                    print(f"{email.upper()}")
                    print(f"LOCK CYCLE {lock_cycles}")
                    client_sock.sendall("MOTH 0 0 #".encode())
                elif "REJECTED" in data_stream:
                    os.system("cls")
                    print(f"{email} REJECTED")
                    msvcrt.getch()
                    client_sock.close()
                    return  # Fatal rejection - exit entirely
                elif "NO_LIFE_TOKENS" in data_stream:
                    os.system("cls")
                    print(f"{email} NO LIFE TOKENS")
                    msvcrt.getch()
                    client_sock.close()
                    return  # Fatal - exit entirely
                
                        
                if player.uID is None and "PS" in data_stream:
                    ps_data = data_stream.replace("PS", "").strip()
                    PS_SPLIT = ps_data.split()
                    try:
                        if len(PS_SPLIT) == 10 and PS_SPLIT[6].isdigit():
                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[6]
                            player.mother_name = PS_SPLIT[3]
                            player.family_name = PS_SPLIT[4]
                        elif len(PS_SPLIT) == 9 and PS_SPLIT[5].isdigit():
                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[5]
                            player.mother_name = PS_SPLIT[3]
                        elif len(PS_SPLIT) == 8 and PS_SPLIT[4].isdigit():
                            player.uID = PS_SPLIT[0]
                            player.motheruID = PS_SPLIT[4]
                    except Exception:
                        pass
                    if "NO MOTHER" in data_stream:
                        player.uID = PS_SPLIT[0]
                    if player.uID:
                        player.uID = player.uID.replace("/0", "").strip()
                    if not player.family_name:
                        player.family_name = "NONE"

                # If we have enough data to break lock cycle and reconnect
                if player.uID and ("PU" in records.player_updates or data_stream):
                    if "reason_" in data_stream and player.uID in data_stream:
                        client_sock.close()
                        break  # Break inner packet processing loop to reconnect

            else:
                # Continue reading more packets if no break
                continue
            # Inner packet processing loop break reached
            break



# MENU
def numswitch():
    client.title()
    
    print("Info/Configurations 🗐\n")

    print("1x. About 𝒊               2x. History 🕮")
    print("3x. Client Settings </>   4x. Clear History ✘")
    print("5x. Onelife Settings Ⅰ    6x. Automation Trailing ▼")
    print("7x. Account Key Info 𝒊\n")

    print("Account Management 🗐\n")
    print("1. Add ✚   2. Remove ✘   3. Edit @\n")

    print("Manual 모\n")
    print("4. Select ▼   5. Cycle ↻   L. Launch Game ▼\n")

    print("Automated 𖥞\n")
    print("6. Fast Spawn ⛟          7. Spawn Any 𝓐")
    print("8. Terminate Account ➴  9. Terminate Many ➴➴➴")
    print("10. Account Detection 𝓓\n")

    print("Security ⚷\n")
    print("11. Lock account ꗃ\n")
    
    uInput = input("> ")
    if uInput.lower() == "exit":
        exit()
    elif uInput == "1x": # Config
        switchtype.numswitch = False
        switchtype.about = True
    elif uInput == "2x":
        switchtype.numswitch = False
        switchtype.history = True
    elif uInput == "3x":
        switchtype.numswitch = False
        switchtype.settings_client = True
    elif uInput == "4x":
        open(client.history, 'w').close()
    elif uInput == "5x":
        switchtype.numswitch = False
        switchtype.settings_onelife = True
    elif uInput == "6x":
        switchtype.numswitch = False
        switchtype.bot_test = True
    elif uInput == "7x":
        os.system("cls")
        print("Your Account Hanger:\n")
        display_keys()
        msvcrt.getch()
    elif uInput == "1": # Account Manager
        switchtype.numswitch = False    
        switchtype.add_accounts = True
    elif uInput == "2":
        switchtype.numswitch = False
        switchtype.remove_accounts = True
    elif uInput == "3":
        switchtype.numswitch = False
        switchtype.edit_accounts = True
    elif uInput == "4":
        switchtype.numswitch = False
        switchtype.select_accounts = True
    elif uInput == "5": # Manual
        switchtype.numswitch = False
        switchtype.cycle_accounts = True    
    elif uInput.lower() == "l":
        subprocess.Popen(client.directory, shell=True)
    elif uInput == "6":
        switchtype.numswitch = False
        switchtype.fast_spawn = True
    elif uInput == "7":
        switchtype.numswitch = False
        switchtype.spawn_any = True
    elif uInput == "8":
        switchtype.numswitch = False
        switchtype.quick_kill = True        
    elif uInput == "9":
        switchtype.numswitch = False
        switchtype.kill_many = True   
    elif uInput == "10":
        switchtype.numswitch = False
        switchtype.detect_accounts = True      
    elif uInput == "11":
        switchtype.numswitch = False
        switchtype.lock_account = True   
    else:
        print("Invalid Input")
        msvcrt.getch()
# MAINLOOP
debug_mode = False
run_program()



while True:
    if not debug_mode:
        if switchtype.numswitch:
            os.system("cls")
            numswitch()
            pass
        elif switchtype.about:
            os.system("cls")
            about()
        elif switchtype.history:
            os.system("cls")
            display_history()
        elif switchtype.settings_client:
            os.system("cls")
            client_settings_config()
        elif switchtype.settings_onelife:
            os.system("cls")
            onelife_settings_config()
        elif switchtype.bot_test:
            os.system("cls")
            bot_testing()

        if switchtype.add_accounts:
            os.system("cls")
            add_accounts()
        elif switchtype.remove_accounts:
            os.system("cls")
            remove_accounts()
        elif switchtype.edit_accounts:
            os.system("cls")
            edit_accounts()

        if switchtype.select_accounts:
            os.system("cls")
            select_account()
        elif switchtype.cycle_accounts:
            os.system("cls")
            cycle_accounts()

        if switchtype.fast_spawn:
            os.system("cls")
            fast_spawn()
        if switchtype.quick_kill:
            os.system("cls")
            terminate_account()
        if switchtype.spawn_any:
            os.system("cls")
            spawn_many()
        if switchtype.kill_many:
            os.system("cls")
            terminate_many()
        if switchtype.detect_accounts:
            os.system("cls")
            detect_spawn()
        if switchtype.lock_account:
            os.system("cls")
            account_locking()

    else:
        bot_testing()
        msvcrt.getch()
        os.system("cls")
        pass    




"""
bot Engine Blueprint

while(True):
   new_byte = get_next_byte(sock)
   while new_byte is not None:
      packet_buffer += new_byte
      if(new_byte == b'#'):
          # Process the packet when we hit the end marker
          handle_packet(sock, packet_buffer)
          packet_buffer = bytes() # clear buffer for next packet
"""