.PHONY: _pwd_prompt decrypt_conf encrypt_conf

# Configuration files
DECRYPTED_CONFIG_FILES= $(wildcard config/*.json)
ENCRYPTED_CONFIG_FILES= $(wildcard config/*.cast5)

# Private task for echoing instructions
_pwd_prompt:
	@echo "Contact Rukmal Weerawarana for decryption password."

# to decrypt config vars
decrypt_conf: _pwd_prompt
	@$(foreach f, $(ENCRYPTED_CONFIG_FILES), echo "\nDecrypting $(basename $(f))..." && openssl cast5-cbc -d -in $(f) -out $(basename $(f))${\n})

# to encrypt config vars
encrypt_conf: _pwd_prompt
	@$(foreach f, $(DECRYPTED_CONFIG_FILES), echo "\nEncrypting $(f)..." && openssl cast5-cbc -e -in $(f) -out $(f).cast5${\n})


# Other definitions
# =================
define \n


endef