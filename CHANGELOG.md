Community Bonding Period
========================

 - [x] Write proof-of-concept to test Python's GPGME bindings.
	- [x] Key Generation written
	- [x] Just need moving keys to card and signing keys
 - [x] Research disk handling with Python
	- [x] Use lsblk to get information on local drives
	- [x] Use pyparted to format drives
	- [x] Switch from lsblk to just pyparted?
 - [x] Locate various communities around these tools (gnupg-users, etc) to assist when stuck.
 - [x] Minimum hardware requirements
	- i386
	- One USB port or SD card slot

Week 1
======

2018-05-14
----------
 - [x] Research smartcard handling and key generation with Python
	- GPA and Kleopatra do this already with GPGME, so just follow their example.
	- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=gpa.git;a=blob;f=src/cm-openpgp.c
 - [x] Test ejecting disk while running application
	- Should theoretically be able to eject the live usb after booting, but I'll need to do some testing and confirm
	- This does NOT appear to be the case by default
 - [x] Refamilarize myself with pgp-clean-room codebase (haven't touched it in a bit)
 - [x] Research how "user stories" work
	- As a < type of user >, I want < some goal > so that < some reason >.
 - [x] Write a few user stories
 - [x] Read up on threat modelling
	- The physical safety of the storage is probably more of a deterrent than an encrypted storage device
	- Fewer passwords is better, so unencrypted storage but enforce having a password on the key

2018-05-15
----------
 ~~- [ ] Write a proper threat model for offline master key storage~~
	This is too much. See above.
 - [x] GPGKey Object
 - [ ] Add newt progress bar
	- Some progress made, but not ready yet
	- GPGME progress callback is confusing
 - [x] Write "user stories"
	- Figure out what exactly the user wants to do, what information we need from them, and how that maps to the traditional GPG key generation process
 - [x] Turn user stories into workflow
	- see workflow.md
 - [x] setup.py
 - [x] remove install hack from make-pgp-clean-room
	- Will build a pgpcr debian package and then install it in the clean room
 - [ ] Restructure the UI

Week 2
======

2018-05-14
----------
 - [ ] Follow up on GPGME backport
 - [ ] Finish restructuring
	- [ ] It's really important to get this right before I start writing the major parts of this application
 - [ ] Skeleton UI

Week 3 
======

2018-05-28
----------
 - [ ] Disk handling UI
	- [ ] This is basically what makes or breaks this application so it has to work and work really well
 - [ ] Test disk handling UI on as many removable storage devices as I can get my hands on

Week 4 
======

2018-06-04
----------

 - [ ] Test everything we have so far
 - [ ] Automated testing for python-newt
	- [ ] Allow tests to mock user input and write tests to take advantage of this
 - [ ] Overflow for anything not finished on schedule

Evaluation Period 1 / Week 5
============================

2018-06-11
----------
 - [ ] Generate GPG keys on disk
 - [ ] Add keysigning and revocation process

Week 6
======

2018-06-18
----------
 - [ ] Support for exporting to a smartcard
 - [ ] Generate GPG keys on a smartcard

Week 7
======

2018-06-25
----------
 - [ ] Generate GPG keys on a smartcard
	- [ ] Two weeks is a long time for developing support to generate keys on a smartcard, but this operation does not appear to be supported by GPGME

Week 8
======

2018-07-02
----------
 - [ ] Test everything
 - [ ] Overflow for anything not finished on schedule

Evaluation Period 2 / Week 9
============================

2018-07-09
----------
 - [ ] Call for testing from the wider Debian/FLOSS community
 - [ ] Create a Debian package for the pgp-clean-room application and submit it to mentors.d.o

Week 10
=======

2018-07-16
----------
TBD

Week 11
=======

2018-07-23
----------
TBD

Week 12
=======

2018-07-30
----------
TBD

Evaluation Period 3 / Week 13
=============================

2018-08-06
----------
 - [ ] Testing, testing and more testing
 - [ ] Overflow for anything not finished on schedule
 - [ ] Debconf18? (Would need sponsorship, but I don't want to apply for that unless I have a project to present about)
 - [ ] Incorporate translations and community testing
 - [ ] Bug fixes

Misc
====

Would like to do these if I have time but we'll see how this goes
 - [ ] PKI/CA UI
	- Scripts for this already exist on the PGP Clean Room, so this would simply be a matter of exposing them via python-newt
 - [ ] Secure the Live Environment as much as possible
	- Minimize local packages, remove device drivers for anything that's not keyboard/mouse/storage/graphics
 - [ ] Prepare application for translation
	- Research Debian's translation infrastructure and reach out to the appropriate teams to have the application translated
 - [ ] Alternative UI (Qt, GTK, etc)

