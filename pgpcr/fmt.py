import os

def listdir(path):
    ld = os.listdir(path)
    ld.sort()
    return ld

# Check if a directory contains gpg backups
# If so return a list of keys backed up
def backups(path):
    if "gpg" not in listdir(path):
        return None
    else:
        return listdir(path+"/gpg")

def signing(path):
    if "signing" not in listdir(path):
        return None
    else:
        if "pending" not in listdir(path+"/signing"):
            return None
        else:
            return listdir(path+"/signing/pending")
