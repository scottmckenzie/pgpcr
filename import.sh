#!/bin/sh

gpg --import ./public/*.pub
gpg --import ./private/*.subsec

REV=${GNUPGHOME:-${HOME}/.gnupg}/openpgp-revocs.d/
mkdir -p $REV
cp ./public/*.rev  $REV
