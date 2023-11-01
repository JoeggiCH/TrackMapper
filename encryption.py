"""
encryption.py uses the fernet module to encrypt the configuration file - including
the API passwords - in TrackMapper

"""

# https://cryptography.io/en/latest/
# https://www.pythoninformer.com/python-libraries/cryptography/fernet/

import base64
import os
from os.path import expanduser
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json

debug=False

# encrypts a text using a key, which is derived from a password
def encrypt(pw,clear_data) -> str:
    password = pw.encode()

    # then we create a SHA256 hash of that PW
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        salt=b"",
        length=32,
        iterations=480000,
    )
    # and convert the hash to a key suitable for Fernet
    hashed=kdf.derive(password);
    if (debug): print ("hashed password is:",hashed)
    key = base64.urlsafe_b64encode(hashed)

    # create a Fernet object
    f = Fernet(key)
    # and encrypt something
    token = f.encrypt(clear_data.encode())
    if (debug): print ("token is ",token)
    return token.decode()

# decrypts a text using a key, which is derived from a password
def decrypt(pw,encrypted_data) -> str:
    password = pw.encode()

    # then we create a SHA256 hash of that PW
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        salt=b"",
        length=32,
        iterations=480000,
    )
    # and convert the hash to a key suitable for Fernet
    hashed=kdf.derive(password);
    if (debug): print ("hashed password is:",hashed)
    key = base64.urlsafe_b64encode(hashed)

    # create a Fernet object
    f = Fernet(key)
    # and encrypt something
    
    try:
        cleartext = f.decrypt(encrypted_data)
        if (debug): print ("cleartext is ",cleartext.decode())
        return cleartext.decode()
    except:
        print ("wrong password or token was tampered with!")

def rd_dec_dict(pw, fn) -> dict:
    try:
        f=open(fn,"r")
        encrypted=f.read()
        f.close()
        return json.loads(decrypt(pw,encrypted))
    except:
        print (f'failed to read {fn}, invalid password or format')
        return {}

def wr_enc_dict(pw, fn, dct):
    try:
        f=open(fn,"w")
        print(encrypt(pw,json.dumps(dct)),file=f)
        f.close()
    except:
        print (f'failed to write {fn} or invalid format')
        

if (__name__ == "__main__"):
    st="die waldfee"
    print (f'"{st}"')
    print ("should be the same as")
    encrypted=encrypt("holla",st)
    decrypted=decrypt("holla",encrypted)
    print (f'"{decrypted}"\n')

    dictis={"a string":"das ist ein Geheimnis", "and a number": 5.1}
    print (dictis)
    print ("should be the same as")
    fp=expanduser('~')+'/Documents/python/'+"scrambled.enc".replace("\\","/")
    
    wr_enc_dict("wurzel",fp,dictis)
    dictos=rd_dec_dict("wurzel",fp)
    
    print (dictos)
