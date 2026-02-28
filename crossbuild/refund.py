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

data_folder = "Refund Folder"
verison_number = 1


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
    def __init__(self, main_menu=False, options=None, title=None, placement=None,
                 rgb=None, title_rgb=None, parent=None, replacement_display=None):
        if parent:
            if rgb is None:
                rgb = parent.rgb
            if title_rgb is None:
                title_rgb = parent.title_rgb
        if rgb is None:
            rgb = (255, 255, 255)
        if title_rgb is None:
            title_rgb = rgb

        self.parent = parent
        self.options = options or {}
        self.main_menu = main_menu
        self.title = title
        self.placement = placement
        self.rgb = rgb
        self.title_rgb = title_rgb
        self.result = None
        self.replacement_display = replacement_display  # NEW

    def menu(self):
        while True:
            os.system("cls")

            if self.replacement_display:
                if callable(self.replacement_display):
                    self.replacement_display(self)
                else:
                    print(self.replacement_display)
                uinput = input("> ").strip().lower()
            else:
                if self.title:
                    Special_Functions.print_rgb(self.title_rgb, self.title)

                keys = list(self.options.keys())
                if self.placement:
                    columns, rows = self.placement
                    count = 0
                    for _ in range(rows):
                        line = ""
                        for _ in range(columns):
                            if count < len(keys):
                                key_name = keys[count]
                                option_key = self.options[key_name].get("Key", "")
                                line += f"[{option_key.upper()}] {key_name} ".ljust(25)
                                count += 1
                        Special_Functions.print_rgb(self.rgb, line)
                else:
                    for key_name in keys:
                        option_key = self.options[key_name].get("Key", "")
                        Special_Functions.print_rgb(self.rgb, f"[{option_key.upper()}] {key_name}")

                uinput = input("> ").strip().lower()

            chosen_option = None
            for name, data in self.options.items():
                key = data.get("Key", "")
                if key.lower() == uinput:
                    chosen_option = data
                    break

            if not chosen_option:
                Special_Functions.print_rgb((255, 0, 0), "\nInvalid Option...")
                msvcrt.getch()
                continue

            func = chosen_option["Function"]
            single_run = chosen_option["Single Run"]

            if single_run:
                os.system("cls")
                result = func()
                if result == "exit":
                    return "exit" if self.main_menu else "back"
            else:
                while True:
                    os.system("cls")
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


def HMAC_SHA1(key, message):
    hmac_object = hmac.new(key.encode(), message.encode(), hashlib.sha1)
    return hmac_object.hexdigest()

def about():
    Special_Functions.print_rgb((255, 255, 255), f"You either stumbled upon this years later or you're a refund manager.")
    Special_Functions.print_rgb((255, 255, 255), f"This is the onelife refund manager made by shady.dev, everything on how to use this should be well outlined")
    msvcrt.getch()

def Add_Entry():
    print("Add Entry")

def Delete_Entry():
    print("Delete Entry")

def Refund_Manager():
    pass

def safe_exit():
    exit()

def initalize():
    
    main = Menu(
        main_menu=True,
        options={    
            "About 𝒊": {"Function": about, "Single Run": True, "Key": "A"},
            "Refund Manager": {"Function": Refund_Manager, "Single Run": True, "Key": "1"},
            "Add Entry": {"Function": Add_Entry, "Single Run": True, "Key": "2"},
            "Remove Entry": {"Function": Delete_Entry, "Single Run": True, "Key": "3"},
            "EXIT SAFELY": {"Function": safe_exit, "Single Run": True, "Key": "EXIT"},
        },
        title=f"REFUND MANAGER Version: {verison_number}\n---------------------"
    )


    main.menu()

initalize()

