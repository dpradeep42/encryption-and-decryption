from cryptography.fernet import Fernet

key = Fernet.generate_key()

with open('myKey.key', 'wb') as myKey:
    myKey.write(key)