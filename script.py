import os
from base64 import b64encode
from nacl import encoding, public, secret
import requests
import logging
import sys
file_path = "D:/a/sparrow-app/sparrow-app/src-tauri/target/debug/bundle/msi/sparrow-app_1.0.0_x64_en-US.msi.zip.sig"
with open(file_path, "r") as file:
    file_content = file.read()
print(file_content)

file_path_2 = "D:/a/sparrow-app/sparrow-app/src-tauri/target/debug/bundle/nsis/sparrow-app_1.0.0_x64-setup.nsis.zip.sig"
with open(file_path_2, "r") as file:
    file_content_2 = file.read()
print(file_content_2)
def encrypt_secret(secret_value, public_key_base64):
    try:
        public_key = public.PublicKey(public_key_base64, encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = b64encode(sealed_box.encrypt(secret_value.encode())).decode()
        return encrypted
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        sys.exit(1)
def decrypt_secret(encrypted_secret, private_key_base64):
    try:
        private_key = secret.SecretKey(private_key_base64, encoding.Base64Encoder())
        box = public.SealedBox(private_key.public_key)
        decrypted = box.decrypt(b64encode(encrypted_secret).decode()).decode()
        return decrypted
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        sys.exit(1)
def update_github_secret(repository_owner, repository_name, secret_name, new_secret_value, token):
    try:
        url = f"https://api.github.com/repos/{repository_owner}/{repository_name}/actions/secrets/{secret_name}"
        # Get the public key for encryption
        public_key_info = requests.get(f"https://api.github.com/repos/{repository_owner}/{repository_name}/actions/secrets/public-key", headers={"Authorization": f"Bearer {token}"})
        public_key_info = public_key_info.json()
        logging.info(f"Public Key Info: {public_key_info}")
        key_id = public_key_info.get('key_id')
        logging.info(f"Key ID: {key_id}")
        public_key_base64 = public_key_info.get('key')
        # Encrypt the new secret value
        encrypted_secret = encrypt_secret(new_secret_value, public_key_base64)
        # Update the secret on GitHub
        response = requests.put(url, json={"encrypted_value": encrypted_secret, "key_id": key_id}, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()  # Raise an error for bad responses
        if response.status_code == 204:
            logging.info(f"Secret '{secret_name}' updated successfully.")
        else:
            logging.error(f"Failed to update secret '{secret_name}'. Status code: {response.status_code}, Response: {response.text}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repository_owner = os.getenv("INPUT_REPOSITORY_OWNER")
    repository_name = os.getenv("INPUT_REPOSITORY_NAME")
    secret_name = os.getenv("INPUT_SECRET_NAME")
    secret_name_2 = os.getenv("INPUT_SECRET_NAME_2")
    new_secret_value = file_content
    github_token = os.getenv("INPUT_GITHUB_TOKEN")
    if not all([repository_owner, repository_name, secret_name, new_secret_value, github_token]):
        logging.error("Missing required environment variables.")
        sys.exit(1)
    update_github_secret(repository_owner, repository_name, secret_name, new_secret_value, github_token)
    new_secret_value_2 = file_content_2
    update_github_secret(repository_owner, repository_name, secret_name_2, new_secret_value_2, github_token)
