Workflow
========

 - Create temporary GPG directory
 - Present New/Load/Advanced menu
	- Stops us messing with any hardware the user doesn't want us to

New
---
 - Generate new GPG Master key, prompting for userid and password
 - Backup master key to two backup disks (using the same process as storage export below)
 - Ask user how they want to export their key

### Storage (better name needed)
 - Ask user to connect it, then confirm that we detect the right device
 - prompt and then wipe it
 - Format it
	- See format.md
 - copy gnupghome from tempdir to usb
 - Ask for second USB, and repeat process

### Smartcard
 - List attached and supported smartcards
	- Perhaps we can support any smartcard but will require testing
 - Keytocard the subkeys
 - No need for public key export, since I'm pretty sure you can get the key from the smartcard?
	- Will require testing

Load
----
 - Ask user to insert a storage device containing their key
 - Confirm we detect the right device
 - Mount it and copy contents to tempdir
 - create GPGKey based in tempdir
 - Prompt to sign or revoke a key

### Sign
 - Copy public usb to another tempdir
 - For each key on usb, prompt user to confirm and then sign the key
 - Copy tempdir back to public usb

### Revoke
 - Ask which keys to revoke
 - Generate Revocation certificate
 - Ask if user wants to generate new keys to replace the revoked ones

Advanced
--------
### Generate a key on a smartcard
 - This breaks the standard workflow above and leaves the user with no backups
 - Available for those who want it but not the default

### Import old key
 - A feature I would definitely use but likely not helpful for most users

### Shell
 - Keeps main menu cleaner
