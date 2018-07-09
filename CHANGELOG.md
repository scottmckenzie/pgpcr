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
 - [x] Log paritioning process
	- Should help fixing occasional mount errors
	- Still working on GPGME logging though
 - [x] Update workflow to match what we actually do
	- Workflow was a bit out-of-order
 - [x] Fix occasional mount failure
	- Logging revealed that mkfs occasionally couldn't see the newly-created partition
	- Inserting a sleep after committing partition changes to disk appears to have fixed it
 - [x] GPGME logging
	- Environment variable doesn't seem to have an effect when set from python
	- Can't call set_global_flag from the python bindings as it unecessarily passes the context object
	- Solved by setting it in the systemd service file

2018-06-01
----------
 - [x] import.sh
 - [x] Skeleton UI for smartcards
 - [x] Disk progress bars
	- Progress on reformatting, paritioning, exporting, etc.
 - [x] Hide notice log messages
	- Stops kernel from breaking our progress bars
 - [x] Use live build's toram instead of custom solution
	- Didn't realize it existed, but it massively simplifies things

Week 4
======

2018-06-04
----------
 - [x] Make sure all button do something
	- Many NotImplementedYet alerts
	- Cancel buttons also work
 - [x] Research unittest.mock
	- Not quite what I'm looking for but close
 - [x] Comply with PEP8
	- Important for future maintainability

2018-06-05
----------
 - [ ] Mock disks for disk_newt tests
	- Doesn't work yet
 - [x] Automate testing of pgpcr with a vm
	- Some of the sleeps are definitely too long, but it works!
 - [x] Disk handling errors
	- Everything that can go wrong and how we recover from it
	- For now we loop. More sophisticated error handling later
 - [x] Begin Key loading

2018-06-06
----------
 - [x] Initial key loading works
 - [ ] Automated testing for python-newt
	- Research done into various possible methods but no concrete results yet
		- ~~Messing with sys.stdin~~
		- ~~Writing to /proc/self/fd/0~~
	- [x] Allow tests to mock user input and write tests to take advantage of this
		- We can do this with virsh send-key but it's fragile

2018-06-07
----------
 - [x] Test everything we have so far
	- Everything except user interfaces has comprehensive testing
	- Can't yet perfectly test UI stuff
 - [x] Allow for more than three subkeys
	- Perhaps the users subkeys have expired
	- No need for an artificial limitation
 - [x] Save key back to disk
	- Unecessary reformatting for now
 - [x] Use directories consistently
	- Import to root of temporary directory
	- export to gpg / key fingerprint
 - [x] Add and revoke UIDs
 - [x] Tests for adding and revoking UIDs

2018-06-08
----------
 - [x] Consistent UI for dangerous operations
 - [x] Optionally backup to more than two disks
 - [x] Don't unecessarily reformat a disk
 - [x] Store multiple keys on one disks
	- Basically just don't always reformat?
 - [x] Export public key after load

Evaluation Period 1 / Week 5
============================

2018-06-11
----------
 - [x] Clean up boot menu
 - [x] Drop user back to the main menu if they don't want to shutdown
 - [x] Prepare interface for translation
	- Should do this ASAP as it's only going to get more difficult as more is added to the project
 - [x] More explanatory interface
	- Initial steps taken, but will do more thinking on this.
	- Not sure how best to present this information
 - [x] Show key algorithms and allow user to set them
 - [x] Use unifont like the Debian Installer

2018-06-12
----------
 - [x] Indicate boot media can be removed
 - [x] Use GPGME's redraw flag to redraw progress bars after pinentry
	- Much better than it was but still not perfect
 - [x] Ensure tty1 is owned by pgp to prevent pinentry problems
	- Haven't seen any since I enforced this
	- This is definitely the cause and sometimes it is still not set correctly, despite chown
 - [x] Experiment with status callback
	- Can't stop it from generating revocation certificates and the like but perhaps we can at least alert the user
	- Does not alert of revocation certificate so doesn't help in this case
 - [x] Setup gettext in pgpcr-part
 - [x] Refresh disk labels when converted to string
 - [x] Add status callback to subkey generation

2018-06-13
----------
 - [x] Move folder format checking to its own module
 - [x] Extensive testing with checkboxes for keysigning
	- Quite poorly documented unfortunately
 - [x] Use documented format for export
 - [x] Key signing

2018-06-14
----------
 - [x] Remove pending keys once they are signed
 - [ ] Display first UID along with fingerprints
	- We have a \_\_str\_\_ for this but not sure where to use it
 - [x] Key revocation
	- For now this requires interacting with GPG directly which is less than ideal
	- Will look into what other applications do for this
	- Can only revoke master key for now
 - [x] Fix ```Pinentry: Permission Denied```
	- See [#8](https://salsa.debian.org/tookmund-guest/pgpcr/issues/8) and [#9](https://salsa.debian.org/tookmund-guest/pgpcr/issues/9)
 - [x] Look into writing simple GPGME c tools for subkey revocation and expiration
	- op_interact doesn't work with the python bindings currently
	- Could be used in other projects

2018-06-15
----------
 - [x] Write simple GPGME C tools for subkey revocation and expiration
	- op_interact doesn't work with the python bindings currently
	- Could be used in other projects
	- Could also help with future keytocard stuff
 - [x] Incorporate tools into build
 - [x] Rewrite revocation using new tools

Week 6
======

2018-06-18
----------
 - [x] Purchase another Yubikey for testing
	- Also looking into a Nitrokey Start
 - [x] Document translation
 - [x] Key expiration
 - [x] After load, confirm before saving
 - [x] Rewrite revocation and expiration in python

2018-06-19
----------
 - [x] Fix up revocation
 - [x] Smartcard properties
 - [x] Smartcard keytocard
 - [x] Initial support for exporting to a smartcard

2018-06-20
----------
 - [x] Logging
 - [x] Clean up exporting to smartcard code
 - [x] Set smartcard properties if it's new
 - [ ] Set key properties in advanced menu
	- Requires a GPG Key...
 - [x] Show user the default PIN and admin PIN

2018-06-21
----------
 - [x] Smartcard set PINs
 - [x] Allow user to set PIN on smartcard
 - [x] Always export public key to USB
 - [x] Pick key algorithms from a list
 - [x] Support ECC
	- 25519 requires an [odd hack](https://salsa.debian.org/tookmund-guest/pgpcr/commit/8baf9ae429f461b2fd004d6d6173201fa6192e70), will have to look into why
	- NIST curves don't work for any subkeys but encryption, disabling for now
 - [x] Smartcard catch errors

2018-06-22
----------
 - [x] Common methods for each window to simplify button translation
 - [x] Rewrite smartcard properties to use Assuan commands instead of interact
	- Allows setting properties without a GPG key
 - [x] Better smartcard error handling
	- Unable to catch keytocard errors still...

Week 7
======

2018-06-25
----------
 - [x] Only run interactive tests if they are explicitly enabled
 - [x] Smartcard generate keys on card
 - [x] Generate GPG keys on a smartcard
 - [x] Raise better exceptions when disk mounting fails
 - [x] Fix smartcard "IPC connect failed" errors
	- Have to use gpgconf to create socketdirs when not using the default GNUPGHOME
	- Not totally fixed as /run/$uid isn't created automatically
 - [x] Research a proper login process
	- Rolling our own login process was causing too many bugs, even if it was initially simpler


2018-06-26
----------
 - [x] ~~Use a proper login process through getty~~
	- ~~Added a second user for the clean room application~~
 - Removed the above as it added complexity without actually solving the problem
 - [x] Fake a user session
	- Not created in the live CD for some reason
	- Assuan engine still checks the base ```/run/user/1000/gnupg``` directory
 - [x] Move working directory to .gnupg
	- Assuan is much happier this way
	- Doesn't really matter since this is a live CD anyway

2018-06-27
----------
 - [ ] Work on solving ```Pinentry: Inappropriate ioctl for device``` [#10](https://salsa.debian.org/tookmund-guest/pgpcr/issues/10)
 - [x] Add a simplified proper login
	- More "correct" but doesn't seem to help anything
 - [x] Add a cancel button to pickdisk dialogs
	- Update pickdisk users to support this as well
 - [x] Import key from other backups
	- Exported secret key file or GNUPGHOME folder

2018-06-28
----------
 - [x] Catch import errors
 - [x] Remove unecessary recursion in pickdisks
	- Better as a while loop
 - [x] Add tests for smartcard
	- Fails often, not totally sure why
 - [x] Add translatable help line
 - [x] Split key algorithm selection into algorithm and size
	- Makes adding more algorithms significantly easier
 - [x] Add back ECC for master keys
	- Still need to sort out subkeys [#11](https://salsa.debian.org/tookmund-guest/pgpcr/issues/11)
 - [x] Add support for cancelling disk export
 - [x] Test translations and fix up mistakes
	- The previous approach did not work at all and failed silently
 - [x] Update translations and combine a few strings
 - [x] Simplify the process of makng new translations

2018-06-29
----------
 - [x] Inform user of what keys are being generated, as per [#5](https://salsa.debian.org/tookmund-guest/pgpcr/issues/5)
	- Still can't do anything to inform the user about generating the revocation certificate
 - [x] Check logs to see if system has actually been loaded to RAM [#3](https://salsa.debian.org/tookmund-guest/pgpcr/issues/3)
 - [x] Test generating ECC subkeys with GPGME C api, for [#11](https://salsa.debian.org/tookmund-guest/pgpcr/issues/11)
 - [x] Investigate pinentry issues
	- Have a much better idea of what's going on now, even if I don't yet know how to fix it.

Week 8
======

2018-07-02
----------
 - [x] Add support for ECC subkeys, solving [#11](https://salsa.debian.org/tookmund-guest/pgpcr/issues/11)
 - [x] Ensure gpg-agent is started before doing smartcard operations
 - [x] Generate revocation certificate manually so we can alert the user, solving [#12](https://salsa.debian.org/tookmund-guest/pgpcr/issues/12)
 - [x] Confirm that the user wants to use a given disk
 - [x] Memory wipe like TAILS
	- Page poisoning enabled
 - [x] Reenable keysigning test
	- Was broken for a while, but seems to work now
 - [ ] Continue investigating Pinentry issues
	- For some reason gpg-agent just isn't passing pinentry the TTY name

2018-07-03
----------
 - [x] Reported ECC subkey bug against gpg
	- https://dev.gnupg.org/T4052
 - [x] Add proper package versioning
 - [x] Add build script
 - [ ] Isolate pinentry issue
	- Can't seem to do this.
 - [x] Patch pinentry to fix [#10](https://salsa.debian.org/tookmund-guest/pgpcr/issues/10)
	- The issue lies with gpg-agent not setting GPG_TTY for some reason
	- Getting it from pinetry fixes the problem, but its not the best solution
 - [x] Split smartcard setup into pins and properties
	- Fix up advanced menu to use these new functions
 - [x] Set sex and name correctly on smartcard
	- Property support hadn't been tested much and it did not work correctly

2018-07-04
----------
 - National holiday, so I took the day off.

2018-07-05
----------
 - [x] Pass the default homedir as None to fix [#10](https://salsa.debian.org/tookmund-guest/pgpcr/issues/10)
 - [x] Ask for given name and surname not just name for smartcard properties
 - [x] Ensure GPGKey.homedir is never None
 - [x] Format disk labels better in alerts
 - [x] Export reusable functionality of GPGKey as Context parent class
	- So that Smartcard can use redraw and homedir
	- Also move gpg agent handling to context
 - [x] Form validation

2018-07-06
----------
 - [x] Update automated testing to account for new interface changes
 - [x] Remove help popup
	- Unused for now
	- Will add back if I find a good use for them
 - [x] Pinentry: Operation Cancelled
 - [x] Catch invalid values for smartcard properties
 - [x] Update translations template
 - [x] Move build instructions to the parent repository
 - [ ] Test everything

Evaluation Period 2 / Week 9
============================

2018-07-09
----------
 - [ ] Support setting yubikey touch operation
	- Wasted a bunch of time trying to figure this out
	- Requires low-level smartcard operations that I don't totally understand
	- Will take another crack at this tomorrow
 - [x] Begin PKI UI
 - [ ] PKI/CA UI
	- Scripts for this already exist on the PGP Clean Room, so this would simply be a matter of exposing them via python-newt
 - [ ] Secure the Live Environment as much as possible
	- Minimize local packages, remove device drivers for anything that's not keyboard/mouse/storage/graphics
	- USBGuard?
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
 - [ ] Research Debian's translation infrastructure and reach out to the appropriate teams to have the application translated
 - [ ] Alternative UI (Qt, GTK, etc)
 - [ ] Add the option to print key backups and revocation certificates
 - [ ] Run all tests in a virtual machine
	- kvm?
 - [ ] Better import UI
 - [ ] Optional signature expiry date?
	- I have no idea if people use this
