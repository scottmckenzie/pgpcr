from . import newt
from . import ca
from . import disks_newt

def new(workdir):
    screen = newt.Screen()
    ew = newt.EW(screen, _("New CA"), _("Fill out the fields below to create"
        " a new Certificate Authority."), [_("Name of CA"), _("Days CA should"
            " be valid for"), _("Domain of CA"), _("Days Server certificates"
                " should be valid for"), _("Key Type"), _("Key Size"),
            _("Certificate Digest")])
    if ew[0] == "cancel":
        return
    CA = ca.CA(workdir)
    CA.name = ew[1][0]
    CA.CAValid = ew[1][1]
    CA.domain = ew[1][2]
    CA.serverValid = ew[1][3]
    CA.keyType = ew[1][4]
    CA.keySize = ew[1][5]
    CA.digest = ew[1][6]

    CA.save()
    CA.genroot()

    disks_newt.store(screen, workdir, "pki/"+CA.name,
            _("CA private key backup"), "PKICR Backup")
