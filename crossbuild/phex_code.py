import socket
import threading
import time
import hmac
import hashlib
from typing import Optional

EOT = chr(4)          # \x04
KA_INTERVAL = 45      # most servers expect keep-alive ~30–60 s

def hmac_sha1_hex(key: str, msg: str) -> str:
    """Compute HMAC-SHA1 and return uppercase hex digest"""
    key_b = key.encode('utf-8')
    msg_b = msg.encode('utf-8')
    digest = hmac.new(key_b, msg_b, hashlib.sha1).digest()
    return digest.hex().upper()


class PhexClient:
    def __init__(self,
                 host: str = "phex.antinoid.com",
                 port: int = 6567,
                 channel: str = "bigserver2.onehouronelife.com",
                 email: str = "76561199174387437@steamgames.com",
                 account_key: str = "G33J8N3YR9Y6JYWRHR6X",
                 username: str = "BotTest",
                 life_id: int = 9999):

        self.host = host
        self.port = port
        self.default_channel = channel

        self.email = email
        self.account_key = account_key
        self.username = username
        self.life_id = life_id

        # Computed once
        self.secret_hash = self._compute_secret_hash()

        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = True

        # State
        self.public_hash = None
        self.current_channel = ""
        self.users = {}          # hash → username
        self.user_lives = {}     # hash → life id (when known)

    def _compute_secret_hash(self) -> str:
        # Exactly how the official mod computes it:
        # sprintf(key, "%sphex", accKey);  hmac_sha1("phex", key)
        to_hash = self.account_key + "phex"
        return hmac_sha1_hex("phex", to_hash)

    def connect(self):
        print(f"Connecting to {self.host}:{self.port} …")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            print("→ Connected")
        except Exception as e:
            print("Connection failed:", e)
            self.connected = False
            return

        self.send_first_message()

        threading.Thread(target=self._receive_loop, daemon=True).start()
        threading.Thread(target=self._keepalive_loop, daemon=True).start()

    def disconnect(self):
        self.connected = False
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        print("Disconnected")

    def send(self, msg: str):
        if not self.connected or not self.socket:
            return
        try:
            full = msg.rstrip() + EOT
            self.socket.sendall(full.encode("utf-8"))
            # print("→", msg)   # uncomment for heavy debugging
        except Exception as e:
            print("Send failed:", e)
            self.disconnect()

    def send_first_message(self):
        msg = (
            f"FIRST yumlife "
            f"10 "                             # phex protocol version
            f"{self.secret_hash} "
            f"1"                                # usually jason's OneLife version
        )
        print("Sending FIRST handshake...")
        self.send(msg)

    def _receive_loop(self):
        buffer = ""
        while self.connected and self.running:
            try:
                data = self.socket.recv(8192).decode("utf-8", errors="replace")
                if not data:
                    break
                buffer += data

                while EOT in buffer:
                    msg, buffer = buffer.split(EOT, 1)
                    msg = msg.strip()
                    if msg:
                        self._handle_message(msg)

            except socket.timeout:
                continue
            except Exception as e:
                print("Receive error:", e)
                break

        print("Receive loop ended")
        self.disconnect()

    def _keepalive_loop(self):
        while self.running and self.connected:
            time.sleep(KA_INTERVAL)
            if self.connected:
                self.send("KA")

    def _handle_message(self, msg: str):
        # print("←", msg)   # uncomment to see everything

        parts = msg.split()
        if not parts:
            return

        cmd = parts[0]

        if cmd == "HASH":
            self.public_hash = parts[1]
            print(f"Your public hash = {self.public_hash}")

            # Auto-join & set name & send life
            self.join_channel(self.default_channel)
            self.set_name(self.username)
            self.send_life()

        elif cmd == "USERNAME":
            print(f"Server accepted name → {parts[1]}")

        elif cmd == "USERNAME_ERR":
            print("Name rejected:", " ".join(parts[1:]))

        elif cmd == "JASON_AUTH":
            if len(parts) < 2:
                return
            challenge = parts[1]
            response = hmac_sha1_hex(self.account_key, challenge)
            print(f"JASON_AUTH challenge → responding...")
            self.send(f"JASON_AUTH {self.email} {response}")

        elif cmd == "SAY":
            # SAY channel hash timestamp  word word word...
            if len(parts) < 5:
                return
            channel, user_hash, ts = parts[1], parts[2], parts[3]
            text = " ".join(parts[4:])
            name = self.users.get(user_hash, user_hash[:8]+"…")
            print(f"[{ts}] {name}: {text}")

        elif cmd == "SAY_RAW":
            print("[raw]", " ".join(parts[1:]))

        elif cmd == "HASH_USERNAME":
            if len(parts) >= 3:
                h, name = parts[1], " ".join(parts[2:])
                self.users[h] = name
                print(f"→ {name} is {h[:8]}…")

        elif cmd == "HASH_SERVER_LIFE":
            if len(parts) >= 4:
                h, srv, lid = parts[1], parts[2], parts[3]
                self.user_lives[h] = lid
                print(f"Life mapping: {h[:8]}… → {lid}  ({srv})")

        elif cmd == "ONLINE":
            h = parts[1]
            name = self.users.get(h, h[:8]+"…")
            print(f"* {name} is now online")

        elif cmd == "OFFLINE":
            h = parts[1]
            name = self.users.get(h, h[:8]+"…")
            print(f"* {name} went offline")

        elif cmd == "JOINED_CHANNEL":
            if len(parts) >= 3:
                h, ch = parts[1], parts[2]
                print(f"* {self.users.get(h, h[:8]+'…')} joined {ch}")

        elif cmd == "VERSION":
            print("Server version:", parts[1] if len(parts)>1 else "?")

        else:
            print(f"[{cmd}]", " ".join(parts[1:]))

    # ────────────────────────────────────────────────
    #   Commands you can call
    # ────────────────────────────────────────────────

    def join_channel(self, channel: str):
        if self.current_channel:
            self.send(f"LEAVE {self.current_channel}")
        self.current_channel = channel
        self.send(f"JOIN {channel}")
        self.send(f"GETLAST {channel} 40")

    def set_name(self, new_name: str):
        if not new_name.strip():
            return
        self.username = new_name.strip()
        self.send(f"USERNAME {self.username}")

    def say(self, text: str):
        if not self.current_channel:
            print("Cannot say – not in any channel yet")
            return
        if not text.strip():
            return
        self.send(f"SAY {self.current_channel} {text}")

    def send_life(self):
        if not self.current_channel:
            return
        self.send(f"SERVER_LIFE {self.current_channel} {self.life_id}")

    def user_cmd(self, cmd: str):
        """Send /help, /list, /block … etc"""
        self.send(f"USER_CMD {cmd}")

    def stop(self):
        self.running = False
        self.disconnect()


# ────────────────────────────────────────────────
#   Example usage
# ────────────────────────────────────────────────

def main():
    # Change these values !
    client = PhexClient(
        account_key = "G33J8N3YR9Y6JYWRHR6X",   # ← your real key
        email       = "76561199174387437@steamgames.com",
        username    = "BotExample",
        life_id     = 1234567,
        channel     = "bigserver2.onehouronelife.com"
    )

    client.connect()

    print("\nCommands:")
    print("  /name Bob")
    print("  /list")
    print("  /help")
    print("  text           → normal chat")
    print("  quit           → exit\n")

    while client.running:
        try:
            line = input("> ").strip()
            if not line:
                continue

            if line.lower() == "quit":
                client.stop()
                break

            elif line.startswith("/"):
                client.user_cmd(line[1:])

            else:
                client.say(line)

        except KeyboardInterrupt:
            client.stop()
            break
        except Exception as e:
            print("Main loop error:", e)

    print("Exited.")


if __name__ == "__main__":
    main()