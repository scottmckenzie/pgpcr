PGP Clean Room
==============

This is the PGP Clean Room application, designed to be run as part of the
[PGP/PKI Clean Room Live CD](https://salsa.debian.org/tookmund-guest/make-pgp-clean-room)

Dependencies
------------
On Debian:

* debhelper (>= 11)
* devscripts
* gnupg (>= 2.1.21-4)
* libgpgme-dev (>= 1.11.1-1)
* dh-python
* python3-newt
* python3-babel
* python3-setuptools
* python3-all
* python3-gpg (>= 1.11.1-1)

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
You'll need the following Debian packages to use these commands:

* python3
* python3-setuptools
* python3-babel

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

Add your translations to the install file by appending the line below to `debian/python3-pgpcr.install`:
```
po/$LANG/LC_MESSAGES/$LANG.mo	/usr/share/locales/$LANG/LC_MESSAGES/
```

Add your translation to the language selection menu in `pgp-clean-room`.

### Updating your translation
```
./setup.py update_catalog -l $LANG
```

Then manually inspect the file and update it.
