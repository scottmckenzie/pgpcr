import gettext

def init(lang=None):
    ll = None
    if lang is not None:
        ll = [lang]
    tran = gettext.translation("pgpcr", languages=ll, fallback=True)
    tran.install()
    if type(tran) is gettext.NullTranslations and lang != "en":
        return False
    else:
        return True
