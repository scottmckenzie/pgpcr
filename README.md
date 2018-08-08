PGP Clean Room
==============

This is the PGP Clean Room application, designed to be run as part of the
[PGP/PKI Clean Room Live CD](https://salsa.debian.org/tookmund-guest/make-pgp-clean-room)

Dependencies
------------
```
apt-get install debhelper devscripts gnupg libgpgme-dev dh-python python3-newt python3-babel python3-setuptools python3-all python3-gpg
```

You'll need a recent version of `libgpgme`, at least 1.11.1

Building
--------
**This should only be used for testing!**

See the [PGP/PKI Clean Room Live CD](https://salsa.debian.org/tookmund-guest/make-pgp-clean-room/blob/master/README.md)
for instructions on how to build this application properly

Run the build script:
```
./build.sh
```

Translations
------------
To update the template, run:
```
./setup.py extract_messages
```

### Adding New Translations
Add a catalog for your language:
```
./setup.py init_catalog -l $LANG
```

Add your translations to the newly created po file at `po/$LANG/LC_MESSAGES/pgpcr.po`

Add your translations to the install file by appending the line below to `debian/pgp-clean-room.install`:
```
po/$LANG/LC_MESSAGES/$LANG.mo	/usr/share/locales/$LANG/LC_MESSAGES/
```

Add your translation to the language selection menu in `pgp-clean-room`.

### Updating your translation
```
./setup.py update_catalog -l $LANG
```

Then manually inspect the file and update it.
