PGP Clean Room
==============

This is the PGP Clean Room application, designed to be run as part of the
[PGP/PKI Clean Room Live CD](https://salsa.debian.org/tookmund-guest/make-pgp-clean-room)

Requirements
------------

 - Three external storage devices with at least 5 MB of storage
	- Such as USB flash drives or SD cards
	- They will be wiped during the export step so ensure any of the data currently on them is backed up
	- Two will be for master key backups and need to be stored in a safe place, preferably two different safe places
	- The last will be for public key export and can be reused for other things after your new key is imported to your computer
 - One i686-compatible PC
	- Most modern computers and even many older computers should work
	- You need at least 1 GB of RAM

 - One blank cd or blank USB drive
	- To run the installer off of
	- Could be reused as a backup drive after the system is booted

 - A PC running Debian
	- Only required to generate the install CD from source
	- Could be done from another Debian live CD as well

Building from source
-------------------

Clone the PGP/PKI Clean Room Live CD repository:

```
git clone https://salsa.debian.org/tookmund-guest/make-pgp-clean-room.git
cd make-pgp-clean-room
git submodule init
```

Install its dependencies:

```
apt-get install build-essential live-build debootstrap rsync sudo libgpgme-dev:i386 dh-python python3-babel
```
(Note that this will uninstall the amd64 version of libgpgme-dev if you have it installed.)

Run the build script:
```
./scripts/make-pgp-clean-room

```

Running
-------
 - Burn the ISO image to a CD or USB
	- See the [Debian installation manual](https://www.debian.org/releases/stretch/i386/ch04s03.html.en) for tips on how to write the ISO to a USB flash drive
 - Boot from this device
	- Again, see the [Debian installation manual](https://www.debian.org/releases/stretch/i386/ch05s01.html.en)
 - Follow the instructions in the PGP Clean Room application that appears once the system boots
