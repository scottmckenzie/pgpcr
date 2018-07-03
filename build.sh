#!/bin/sh

DATE=`date +%Y%m%d`
COMMIT=`git describe --always`
rm -f debian/changelog
EDITOR=true dch --create --empty --package pgp-clean-room
sed -i s/\(.*\)/\($DATE~$COMMIT\)/g debian/changelog
dpkg-buildpackage -us -ui -uc
