import sys
from hashlib import sha256

from Crypto.Cipher import AES

APP_KEY = "ac21b9f9cbfe4ca5a88562ef25e2b768"


def encode_app_key() -> bytes:
    hash = sha256(APP_KEY.encode()).hexdigest()
    return hash[:16].encode()


def encode_iv() -> bytes:
    hash = sha256(APP_KEY.encode()).hexdigest()
    return hash[16:32].encode()


def decrypt_lua(data) -> str:
    key = encode_app_key()
    iv = encode_iv()
    return AES.new(key, AES.MODE_CBC, iv=iv).decrypt(data).decode("utf-8")


with open(sys.argv[1]) as f:
    data = bytes.fromhex(f.readlines()[0])
    decrypted = decrypt_lua(data)

with open(sys.argv[1] + ".dec", "w") as f:
    f.write(decrypted)
