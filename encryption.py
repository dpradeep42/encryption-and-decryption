from cryptography.fernet import Fernet

with open('myKey.key', 'rb') as myKey:
    key = myKey.read()

#print(key)

keySave = Fernet(key)

with open('health-medicare-drug-spending (1).csv', 'rb') as sourceFile:
    original = sourceFile.read()

encryption = keySave.encrypt(original)

with open('EncryptedFile.csv', 'wb') as encryptedFile:
    encryptedFile.write(encryption)