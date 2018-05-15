
Based primarily on the layout ideas on the [wiki](https://wiki.debian.org/OpenPGP/CleanRoomLiveEnvironment/#Flash_card_layout)
Private Backups
===============
gpg/${FINGERPRINT} 			-- GnuPG home directory for private key identified by ${FINGERPRINT}

Public Export
=============
public/${FINGERPRINT}.asc 		-- Ascii-armored public key

signing/pending/${FINGERPRINT}.asc 	-- Key to be signed

signing/done/${FINGERPRINT}.asc		-- Signed key
