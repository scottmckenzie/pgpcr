#!/bin/sh

gpg --import ./public/*.pub
gpg --import ./private/*.subsec
gpg --import-ownertrust ./public/ownertrust

REV=${GNUPGHOME:-${HOME}/.gnupg}/openpgp-revocs.d/
mkdir -p $REV
cp ./public/*.rev  $REV
