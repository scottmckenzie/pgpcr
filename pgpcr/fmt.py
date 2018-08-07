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
        ld = listdir(path+"/gpg")
        if not ld:
            return None
        else:
            return ld

def signpending(path):
    if "signing" not in listdir(path):
        return None
    else:
        if "pending" not in listdir(path+"/signing"):
            return None
        else:
            ld = listdir(path+"/signing/pending")
            if not ld:
                return None
            else:
                return ld

def signdone(path):
    if "signing" not in listdir(path):
        return None
    else:
        if "done" not in listdir(path+"/signing"):
            return None
        else:
            ld = listdir(path+"/signing/done")
            if not ld:
                return None
            else:
                return ld

def pki(path):
    if "pki" not in listdir(path):
        return None
    else:
        ld = listdir(path+"/pki")
        if not ld:
            return None
        else:
            return ld

def csr(path):
    if "csr" not in listdir(path):
        return None
    else:
        ld = listdir(path+"/csr")
        if not ld:
            return None
        else:
            return ld
