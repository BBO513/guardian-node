"""
Data Encryption Module for Guardian Node
Provides encryption/decryption for sensitive family data
"""

import os
import json
import logging
from pathlib import Path
from typing import Union, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class DataEncryptor:
    """
    Handles encryption and decryption of sensitive family data
    Uses Fernet symmetric encryption with key derivation
    """
    
    def __init__(self, key_file: str = "/data/guardian.key", password: str = None):
        """
        Initialize DataEncryptor with key file and optional password
        
        Args:
            key_file: Path to store/load encryption key
            password: Optional password for key derivation
        """
        self.key_file = Path(key_file)
        self.password = password
        self._ensure_key_directory()
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
        logger.info(f"DataEncryptor initialized with key file: {key_file}")
    
    def _ensure_key_directory(self):
        """Ensure the key file directory exists"""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate new one"""
        if self.key_file.exists():
            try:
                with open(self.key_file, "rb") as f:
                    key = f.read()
                logger.info("Loaded existing encryption key")
                return key
            except Exception as e:
                logger.error(f"Failed to load encryption key: {e}")
                raise
        else:
            return self._generate_new_key()
    
    def _generate_new_key(self) -> bytes:
        """Generate new encryption key"""
        if self.password:
            # Derive key from password
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
            
            # Store salt with key for future derivation
            key_data = {
                'key': base64.urlsafe_b64encode(key).decode(),
                'salt': base64.urlsafe_b64encode(salt).decode(),
                'method': 'pbkdf2'
            }
            
            with open(self.key_file, "w") as f:
                json.dump(key_data, f)
        else:
            # Generate random key
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        
        # Set restrictive permissions on key file
        os.chmod(self.key_file, 0o600)
        logger.info("Generated new encryption key")
        return key
    
    def encrypt(self, data: Union[str, bytes, Dict[str, Any]]) -> bytes:
        """
        Encrypt data
        
        Args:
            data: Data to encrypt (string, bytes, or JSON-serializable dict)
            
        Returns:
            Encrypted data as bytes
        """
        try:
            if isinstance(data, dict):
                data = json.dumps(data, separators=(',', ':')).encode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8')
            elif not isinstance(data, bytes):
                raise ValueError(f"Unsupported data type: {type(data)}")
            
            encrypted = self.cipher.encrypt(data)
            logger.debug(f"Encrypted {len(data)} bytes of data")
            return encrypted
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, token: bytes) -> bytes:
        """
        Decrypt data
        
        Args:
            token: Encrypted data to decrypt
            
        Returns:
            Decrypted data as bytes
        """
        try:
            decrypted = self.cipher.decrypt(token)
            logger.debug(f"Decrypted {len(decrypted)} bytes of data")
            return decrypted
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_json(self, data: Dict[str, Any]) -> bytes:
        """
        Encrypt JSON data
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted JSON as bytes
        """
        return self.encrypt(data)
    
    def decrypt_json(self, token: bytes) -> Dict[str, Any]:
        """
        Decrypt JSON data
        
        Args:
            token: Encrypted JSON data
            
        Returns:
            Decrypted dictionary
        """
        try:
            decrypted_bytes = self.decrypt(token)
            return json.loads(decrypted_bytes.decode('utf-8'))
        except Exception as e:
            logger.error(f"JSON decryption failed: {e}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """
        Encrypt a file
        
        Args:
            file_path: Path to file to encrypt
            output_path: Optional output path (defaults to file_path + '.enc')
            
        Returns:
            Path to encrypted file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if output_path is None:
            output_path = str(file_path) + '.enc'
        
        try:
            with open(file_path, 'rb') as infile:
                data = infile.read()
            
            encrypted_data = self.encrypt(data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted_data)
            
            logger.info(f"Encrypted file: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> str:
        """
        Decrypt a file
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Optional output path
            
        Returns:
            Path to decrypted file
        """
        encrypted_file_path = Path(encrypted_file_path)
        if not encrypted_file_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
        
        if output_path is None:
            # Remove .enc extension if present
            if str(encrypted_file_path).endswith('.enc'):
                output_path = str(encrypted_file_path)[:-4]
            else:
                output_path = str(encrypted_file_path) + '.dec'
        
        try:
            with open(encrypted_file_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            decrypted_data = self.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(decrypted_data)
            
            logger.info(f"Decrypted file: {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise
    
    def rotate_key(self, new_password: str = None) -> bool:
        """
        Rotate encryption key (for security maintenance)
        
        Args:
            new_password: Optional new password for key derivation
            
        Returns:
            True if rotation successful
        """
        try:
            # Backup old key
            backup_path = str(self.key_file) + '.backup'
            if self.key_file.exists():
                import shutil
                shutil.copy2(self.key_file, backup_path)
            
            # Generate new key
            old_cipher = self.cipher
            self.password = new_password
            self.key = self._generate_new_key()
            self.cipher = Fernet(self.key)
            
            logger.info("Encryption key rotated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            # Restore backup if available
            if Path(backup_path).exists():
                import shutil
                shutil.copy2(backup_path, self.key_file)
            raise
    
    def verify_key(self) -> bool:
        """
        Verify encryption key is valid
        
        Returns:
            True if key is valid
        """
        try:
            test_data = b"test_encryption_verification"
            encrypted = self.encrypt(test_data)
            decrypted = self.decrypt(encrypted)
            return decrypted == test_data
        except Exception as e:
            logger.error(f"Key verification failed: {e}")
            return False


class SecureStorage:
    """
    Secure storage wrapper that automatically encrypts/decrypts data
    """
    
    def __init__(self, storage_dir: str = "/data/secure", encryptor: DataEncryptor = None):
        """
        Initialize secure storage
        
        Args:
            storage_dir: Directory for secure storage
            encryptor: DataEncryptor instance (creates new if None)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.encryptor = encryptor or DataEncryptor()
        logger.info(f"SecureStorage initialized: {storage_dir}")
    
    def store(self, key: str, data: Union[str, bytes, Dict[str, Any]]) -> bool:
        """
        Store encrypted data
        
        Args:
            key: Storage key (filename)
            data: Data to store
            
        Returns:
            True if successful
        """
        try:
            file_path = self.storage_dir / f"{key}.enc"
            encrypted_data = self.encryptor.encrypt(data)
            
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions
            os.chmod(file_path, 0o600)
            logger.debug(f"Stored encrypted data: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store data for key '{key}': {e}")
            return False
    
    def retrieve(self, key: str) -> Union[bytes, None]:
        """
        Retrieve and decrypt data
        
        Args:
            key: Storage key
            
        Returns:
            Decrypted data or None if not found
        """
        try:
            file_path = self.storage_dir / f"{key}.enc"
            if not file_path.exists():
                return None
            
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.encryptor.decrypt(encrypted_data)
            logger.debug(f"Retrieved encrypted data: {key}")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve data for key '{key}': {e}")
            return None
    
    def retrieve_json(self, key: str) -> Union[Dict[str, Any], None]:
        """
        Retrieve and decrypt JSON data
        
        Args:
            key: Storage key
            
        Returns:
            Decrypted dictionary or None if not found
        """
        try:
            data = self.retrieve(key)
            if data is None:
                return None
            
            return json.loads(data.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Failed to retrieve JSON data for key '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete stored data
        
        Args:
            key: Storage key
            
        Returns:
            True if successful
        """
        try:
            file_path = self.storage_dir / f"{key}.enc"
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted encrypted data: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete data for key '{key}': {e}")
            return False
    
    def list_keys(self) -> list:
        """
        List all stored keys
        
        Returns:
            List of storage keys
        """
        try:
            keys = []
            for file_path in self.storage_dir.glob("*.enc"):
                key = file_path.stem
                keys.append(key)
            return sorted(keys)
            
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []