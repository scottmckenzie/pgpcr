from pgpcr import common_newt as common
from pgpcr import ca

def new(workdir):
    screen = common.Screen()
    ew = common.EW(screen, _("New CA"), _("Fill out the fields below to create"
        " a new Certificate Authority."), [_("Name of CA"), _("Days CA should"
            " be valid for"), _("Domain of CA"), _("Days Server certificates"
                " should be valid for"), _("Key Type"), _("Key Size"),
            _("Certificate Digest")])
    if ew[0] == "cancel":
        return
    CA = ca.CA(workdir)
    CA.name = ew[1][0]
    CA.daysValid = ew[1][1]
    CA.domain = ew[1][2]
    CA.serverValid = ew[1][3]
    CA.keyType = ew[1][4]
    CA.keySize = ew[1][5]
    CA.digest = ew[1][6]

    CA.save(workdir+"/temp.ca")

