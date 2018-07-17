import gettext

def inittran(lang):
    tran = gettext.translation("pgpcr", "/usr/share/locale/", [lang],
        fallback=True)
    tran.install()
    if type(tran) is gettext.NullTranslations and lang != "en":
        return False
    else:
        return True
