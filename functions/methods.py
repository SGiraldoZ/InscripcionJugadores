from random import randint
import hashlib

def random_key():
    random_key = ''
    for n in range(30):
        d1 = randint(1,3)
        if d1 == 1:
            c = chr(randint(48,57))
        elif d1 == 2:
            c = chr(randint(65,90))
        else:
            c = chr(randint(97,122))
        random_key += c
    return random_key

def hashPasswd(password):
    hashedPasswd = hashlib.sha256(password.encode()).hexdigest()
    return hashedPasswd

def getExtension(fileName):
    fileNameParts = fileName.split(".")
    fileExtension = fileNameParts[-1]
    return fileExtension

def getNameWithoutExtension(fileName):
    fileNameParts = fileName.split(".")
    i = 0
    name = ""
    if len(fileNameParts) > 1:
        while (i < (len(fileNameParts)-1)):
            name += fileNameParts[i]
            i += 1
        return name
    else:
        return fileName

