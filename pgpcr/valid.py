import re

# http://emailregex.com/
_email = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

def _matchregex(r, s):
    if r.match(s) is not None:
        return True
    else:
        return False

def email(address):
    return _matchregex(_email, address)

def date(d):
    return _matchregex(_date, d)
