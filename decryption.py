from cryptography.fernet import Fernet

with open('myKey.key', 'rb') as myKey:
    key = myKey.read()

keySave = Fernet(key)

with open('EncryptedFile.csv', 'rb') as encryptedFile:
    encrypted = encryptedFile.read()

decryption = keySave.decrypt(encrypted)

with open('DecryptedFile.csv', 'wb') as decryptedFile:
    decryptedFile.write(decryption)