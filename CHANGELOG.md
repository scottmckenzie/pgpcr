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
 ~~Write a proper threat model for offline master key storage~~ This is too much. See above.

 - [x] GPGKey Object
 - [ ] Add newt progress bar
	- Much closer on this just need to figure out why it requires the screen to close before it will refresh
	- GPGME progress callback is confusing
 - [x] Write "user stories"
	- Figure out what exactly the user wants to do, what information we need from them, and how that maps to the traditional GPG key generation process
 - [x] Turn user stories into workflow
	- see workflow.md
 - [x] setup.py
 - [x] remove install hack from make-pgp-clean-room
	- Will build a pgpcr debian package and then install it in the clean room
 - [x] Learn more newt stuff
	- I've been using screen wrong, only finish once the program is over

2018-05-16
----------
 - [x] Speed up make-pgp-clean-room building
 - [x] Basic Debian packaging for pgpcr
 - [x] Build pgpcr in make-pgp-clean-room
 - [x] Read code of projects using newt
	- Just byobu in Debian, but I'll look for more in Fedora
	- spacewalk, system-firewall-tui in Fedora
 - [x] Proper newt progress bar
 - [x] Main menu skeleton
 - [x] Proper GPG key creation
 - [x] Add a few tests to common_newt and gpg_newt
	- Not proper unittests yet but I'll add those later
 - [x] Progress bars on master and sub key creation
	- Very approximate but some indication that something is happening
 - [x] Add gpg.conf to tempdir

2018-05-17
----------
 - [x] Return to main menu after operation
 - [x] Confirm before shutdown
 - [x] Test on real hardware
 - [x] Add newt password callback
	- Pinentry loopback might be safer, but pinentry curses breaks the screen
	- Disabled for now while I consider the security implications
 - [x] Handle GPGME general errors
	- Caught by gpg_newt, now just have to figure out why they're happening
 - [x] Restructure the UI
	- I think it's fairly final but we'll see
	- Puts me ahead of schedule

2018-05-18
----------
 - [x] Look into replacing lsblk with pyparted
	- Not feasible as pyparted doesn't expose as much information
 - [x] Virtual usb disk in KVM
 - [x] pyparted partitioning script
	- Separate script as it has to be run as root
 - [x] Load entire system into RAM
	- Allows user to eject disk and save a usb port
	- I've got a hack for this, but I need to research live-build more

Week 2
======

2018-05-21
----------
 - [x] Detect built-in SD card readers
	- The one I have access to apparently uses usb transport so I'll enable just that for now
	- Some may be sata which could be problematic, but I'll wait for bug reports once this is in the wild
 - [x] README
	- "I've just downloaded this, what do I do now?"
	- Need to calculate exact storage numbers once key generation is stable
 - [x] Unittests
	- Some of this is too interdependent for these kinds of tests but I split it up as best I could
 - [x] Let GPG do all the password management
	- Breaks screen at times but it's more secure
 - [x] Move gpg conffiles to their own directory in /etc

2018-05-22
----------
 - [x] Clarify gpg_ops API
 - [x] Disk mounting and formatting from pgpcr
 - [x] Pinentry: Permission denied?
	- This problem is no longer occurring, but I have no idea why
 - [x] Begin Disk handling UI

2018-05-23
----------
 - [x] Virtual USB devices
	- dummy_hcd and g_mass_storage
	- Development drivers not enabled in my kernel
 - [x] More diskhandling
 - [x] Begin skeleton UI for usb-based backups

2018-05-24
----------
 - [x] Disks class
	- Rewrite of disks module
 - [x] disks_mock module
 - [x] Disk handling exceptions
	- Catching everything now, just need to handle it

2018-05-25
----------
 - [x] Finish restructuring
	- It's really important to get this right before I start writing the major parts of this application
 - [x] external module for subprocess calls
 - [x] Finish Skeleton UI for disks
 - [x] Initial key generation and backup to external disks
 - [x] Key Export
	- Not directly exposed as part of the python bindings, but part of GPGME
	- Wrote a patch for the python bindings to do this: https://salsa.debian.org/tookmund-guest/gpgme/tree/python-export

Week 3 
======

2018-05-29
----------
 - [x] Upstream GPGME patches
	- Located a much better set of patches that must have gotten lost at some point:
		https://lists.gnupg.org/pipermail/gnupg-devel/2017-August/033031.html
	- Submitted them instead with a minor update: https://dev.gnupg.org/T4001
 - [x] gpg_ops export method
	- Will be simplified once the above patch lands, but for now we can use the lower-level interface
 - [x] Public key export disk
 - [x] Test disk handling UI on as many removable storage devices as I can get my hands on
	- A bunch of random storage devices and a VM with fake USB disks
 - [x] gpg_ops export testing

2018-05-30
----------
 - [x] GPGOpsTestKey testcase
 - [x] Distinguish between simliar disks
	- Many usb disks simply show as very generic names
	- Not much we can do about this but we can label the ones we've used
 - [x] Export only subkeys
	- For some reason the subkey export currently contains the master key
	- Need a GPGME equivalent of "gpg --export-secret-subkeys"

2018-05-31
----------
 - [x] Simplify file export for gpg operations and tests
 - [x] Log Everything
	- Still working on GPGME logging though
 - [x] Update workflow to match what we actually do
	- Workflow was a bit out-of-order
 - [ ] Skeleton UI for smartcards
 - [ ] Disk handling errors
	- Everything that can go wrong and how we recover from it
	- Mount failures are fairly common. Why?

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
 - [ ] Follow up on GPGME backport
 - [ ] Purchase another Yubikey for testing
	- Other smartcards?
 - [ ] Support for exporting to a smartcard
 - [ ] Generate GPG keys on a smartcard

Week 7
======

2018-06-25
----------
 - [ ] Generate GPG keys on a smartcard
	- Two weeks is a long time for developing support to generate keys on a smartcard, but this operation does not appear to be supported by GPGME

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
 - [ ] Figure out when progress_cb is called with primegen
	- Time based? amount of randomness gathered?
 - [ ] GPGME General Error
	- Getting these randomly during key generation
 - [ ] Pinentry: Permission Denied
 - [ ] PKI/CA UI
	- Scripts for this already exist on the PGP Clean Room, so this would simply be a matter of exposing them via python-newt
 - [ ] Secure the Live Environment as much as possible
	- Minimize local packages, remove device drivers for anything that's not keyboard/mouse/storage/graphics
 - [ ] Prepare application for translation
	- Research Debian's translation infrastructure and reach out to the appropriate teams to have the application translated
 - [ ] Alternative UI (Qt, GTK, etc)
 - [ ] Add the option to print key backups and revocation certificates
 - [ ] Run all tests in a virtual machine
	- kvm?
 - [ ] Better import UI
