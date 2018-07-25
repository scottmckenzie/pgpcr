#!/bin/sh

rm -f ../pgp-clean-room* ../*.deb
DATE=`date +%Y%m%d`
COMMIT=`git rev-parse --short HEAD`
rm -f debian/changelog
EDITOR=true dch --create --package pgp-clean-room
sed -i s/\(.*\)/\($DATE~$COMMIT\)/g debian/changelog
dpkg-buildpackage -us -ui -uc
