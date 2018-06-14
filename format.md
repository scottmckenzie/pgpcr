
Based primarily on the layout ideas on the [wiki](https://wiki.debian.org/OpenPGP/CleanRoomLiveEnvironment/#Flash_card_layout)
Private Backups
===============
gpg/${FINGERPRINT} 			-- GnuPG home directory for private key identified by ${FINGERPRINT}

Public Export
=============
public/${FINGERPRINT}.pub		-- Ascii-armored public key

private/${FINGERPRINT}.subsec		-- Optional secret subkey export

signing/pending/${FINGERPRINT}.asc 	-- Key to be signed

signing/done/${FINGERPRINT}.asc		-- Signed key
