#!/usr/bin/env python3
"""
Family Data Persistence Layer
Provides secure local file storage for family profiles, recommendations, and settings
with encryption and backup capabilities
"""

import os
import json
import logging
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from recommendation_engine import SecurityRecommendation, FamilyProfile

class DataEncryption:
    """Handles encryption and decryption of family data"""
    
    def __init__(self, password: str, salt: Optional[bytes] = None):
        """Initialize encryption with password-based key derivation"""
        if salt is None:
            salt = os.urandom(16)
        
        self.salt = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data back to string"""
        return self.cipher.decrypt(encrypted_data).decode()
    
    def get_salt(self) -> bytes:
        """Get the salt used for key derivation"""
        return self.salt

class FamilyDataStore:
    """
    Secure local storage for family cybersecurity data
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, encryption_password: str = None):
        self.config = config
        self.logger = logger
        
        # Setup data directories
        self.data_dir = Path(config.get('family_assistant', {}).get('data_directory', 'data/families'))
        self.backup_dir = Path(config.get('family_assistant', {}).get('backup_directory', 'data/backups'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.families_file = self.data_dir / "families.json"
        self.recommendations_file = self.data_dir / "recommendations.json"
        self.settings_file = self.data_dir / "settings.json"
        self.salt_file = self.data_dir / ".salt"
        
        # Setup encryption if password provided
        self.encryption = None
        if encryption_password:
            self._setup_encryption(encryption_password)
        
        self.logger.info(f"Family data store initialized at {self.data_dir}")
    
    def _setup_encryption(self, password: str):
        """Setup encryption with password"""
        salt = None
        
        # Load existing salt if available
        if self.salt_file.exists():
            try:
                with open(self.salt_file, 'rb') as f:
                    salt = f.read()
            except Exception as e:
                self.logger.warning(f"Could not load existing salt: {e}")
        
        # Create encryption instance
        self.encryption = DataEncryption(password, salt)
        
        # Save salt if it's new
        if not self.salt_file.exists():
            try:
                with open(self.salt_file, 'wb') as f:
                    f.write(self.encryption.get_salt())
                # Make salt file read-only
                os.chmod(self.salt_file, 0o400)
            except Exception as e:
                self.logger.error(f"Could not save encryption salt: {e}")
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data to JSON string with datetime handling"""
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(data, indent=2, default=json_serializer)
    
    def _deserialize_data(self, json_str: str) -> Any:
        """Deserialize JSON string to data"""
        return json.loads(json_str)
    
    def _write_file(self, file_path: Path, data: Any, encrypted: bool = True):
        """Write data to file with optional encryption"""
        try:
            json_data = self._serialize_data(data)
            
            if encrypted and self.encryption:
                # Encrypt the data
                encrypted_data = self.encryption.encrypt(json_data)
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # Write as plain text
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json_data)
            
            # Set restrictive permissions
            os.chmod(file_path, 0o600)
            
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            raise
    
    def _read_file(self, file_path: Path, encrypted: bool = True) -> Any:
        """Read data from file with optional decryption"""
        if not file_path.exists():
            return None
        
        try:
            if encrypted and self.encryption:
                # Read and decrypt
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                json_data = self.encryption.decrypt(encrypted_data)
            else:
                # Read as plain text
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = f.read()
            
            return self._deserialize_data(json_data)
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def save_family_profile(self, family_profile: FamilyProfile) -> bool:
        """Save family profile to storage"""
        try:
            # Load existing families
            families_data = self._read_file(self.families_file) or {}
            
            # Update with new/modified family
            families_data[family_profile.family_id] = asdict(family_profile)
            
            # Save back to file
            self._write_file(self.families_file, families_data)
            
            self.logger.info(f"Saved family profile: {family_profile.family_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving family profile {family_profile.family_id}: {e}")
            return False
    
    def load_family_profile(self, family_id: str) -> Optional[FamilyProfile]:
        """Load family profile from storage"""
        try:
            families_data = self._read_file(self.families_file)
            if not families_data or family_id not in families_data:
                return None
            
            profile_data = families_data[family_id]
            
            # Convert datetime strings back to datetime objects
            profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
            profile_data['updated_at'] = datetime.fromisoformat(profile_data['updated_at'])
            
            return FamilyProfile(**profile_data)
            
        except Exception as e:
            self.logger.error(f"Error loading family profile {family_id}: {e}")
            return None
    
    def list_family_profiles(self) -> List[str]:
        """Get list of all family profile IDs"""
        try:
            families_data = self._read_file(self.families_file)
            return list(families_data.keys()) if families_data else []
        except Exception as e:
            self.logger.error(f"Error listing family profiles: {e}")
            return []
    
    def delete_family_profile(self, family_id: str) -> bool:
        """Delete family profile from storage"""
        try:
            families_data = self._read_file(self.families_file)
            if not families_data or family_id not in families_data:
                return False
            
            del families_data[family_id]
            self._write_file(self.families_file, families_data)
            
            self.logger.info(f"Deleted family profile: {family_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting family profile {family_id}: {e}")
            return False
    
    def save_recommendations(self, family_id: str, recommendations: List[SecurityRecommendation]) -> bool:
        """Save recommendations for a family"""
        try:
            # Load existing recommendations
            all_recommendations = self._read_file(self.recommendations_file) or {}
            
            # Convert recommendations to dictionaries
            rec_data = [rec.to_dict() for rec in recommendations]
            all_recommendations[family_id] = rec_data
            
            # Save back to file
            self._write_file(self.recommendations_file, all_recommendations)
            
            self.logger.info(f"Saved {len(recommendations)} recommendations for family {family_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving recommendations for family {family_id}: {e}")
            return False
    
    def load_recommendations(self, family_id: str) -> List[SecurityRecommendation]:
        """Load recommendations for a family"""
        try:
            all_recommendations = self._read_file(self.recommendations_file)
            if not all_recommendations or family_id not in all_recommendations:
                return []
            
            rec_data_list = all_recommendations[family_id]
            recommendations = []
            
            for rec_data in rec_data_list:
                recommendations.append(SecurityRecommendation.from_dict(rec_data))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error loading recommendations for family {family_id}: {e}")
            return []
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save application settings"""
        try:
            self._write_file(self.settings_file, settings)
            self.logger.info("Saved application settings")
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """Load application settings"""
        try:
            settings = self._read_file(self.settings_file)
            return settings or {}
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return {}
    
    def create_backup(self, backup_name: Optional[str] = None) -> bool:
        """Create a backup of all family data"""
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Copy all data files to backup directory
            files_to_backup = [
                self.families_file,
                self.recommendations_file,
                self.settings_file
            ]
            
            backed_up_count = 0
            for file_path in files_to_backup:
                if file_path.exists():
                    backup_file_path = backup_path / file_path.name
                    shutil.copy2(file_path, backup_file_path)
                    backed_up_count += 1
            
            # Create backup metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'files_backed_up': backed_up_count,
                'backup_name': backup_name
            }
            
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Created backup '{backup_name}' with {backed_up_count} files")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore data from a backup"""
        try:
            backup_path = self.backup_dir / backup_name
            if not backup_path.exists():
                self.logger.error(f"Backup '{backup_name}' not found")
                return False
            
            # Create current backup before restoring
            self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Restore files
            files_to_restore = [
                "families.json",
                "recommendations.json", 
                "settings.json"
            ]
            
            restored_count = 0
            for filename in files_to_restore:
                backup_file = backup_path / filename
                if backup_file.exists():
                    target_file = self.data_dir / filename
                    shutil.copy2(backup_file, target_file)
                    restored_count += 1
            
            self.logger.info(f"Restored {restored_count} files from backup '{backup_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup '{backup_name}': {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            backups = []
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / "backup_metadata.json"
                    
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            metadata['backup_name'] = backup_dir.name
                            backups.append(metadata)
                        except Exception:
                            # If metadata is corrupted, create basic info
                            backups.append({
                                'backup_name': backup_dir.name,
                                'created_at': datetime.fromtimestamp(backup_dir.stat().st_mtime).isoformat(),
                                'files_backed_up': len(list(backup_dir.glob('*.json'))),
                                'metadata_corrupted': True
                            })
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            return backups
            
        except Exception as e:
            self.logger.error(f"Error listing backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            removed_count = 0
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    backup_time = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                    
                    if backup_time < cutoff_date:
                        shutil.rmtree(backup_dir)
                        removed_count += 1
                        self.logger.info(f"Removed old backup: {backup_dir.name}")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            stats = {
                'data_directory': str(self.data_dir),
                'backup_directory': str(self.backup_dir),
                'encryption_enabled': self.encryption is not None,
                'files': {},
                'backups': len(list(self.backup_dir.iterdir())),
                'total_size_bytes': 0
            }
            
            # Get file sizes
            for file_path in [self.families_file, self.recommendations_file, self.settings_file]:
                if file_path.exists():
                    size = file_path.stat().st_size
                    stats['files'][file_path.name] = {
                        'size_bytes': size,
                        'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    stats['total_size_bytes'] += size
            
            # Get backup directory size
            backup_size = sum(f.stat().st_size for f in self.backup_dir.rglob('*') if f.is_file())
            stats['backup_size_bytes'] = backup_size
            stats['total_size_bytes'] += backup_size
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def verify_data_integrity(self) -> Dict[str, bool]:
        """Verify integrity of stored data"""
        integrity_results = {
            'families_file': False,
            'recommendations_file': False,
            'settings_file': False,
            'encryption_working': False
        }
        
        try:
            # Test families file
            families_data = self._read_file(self.families_file)
            integrity_results['families_file'] = families_data is not None
            
            # Test recommendations file
            rec_data = self._read_file(self.recommendations_file)
            integrity_results['recommendations_file'] = rec_data is not None
            
            # Test settings file
            settings_data = self._read_file(self.settings_file)
            integrity_results['settings_file'] = settings_data is not None
            
            # Test encryption if enabled
            if self.encryption:
                test_data = "integrity_test"
                encrypted = self.encryption.encrypt(test_data)
                decrypted = self.encryption.decrypt(encrypted)
                integrity_results['encryption_working'] = (decrypted == test_data)
            else:
                integrity_results['encryption_working'] = True  # Not applicable
            
        except Exception as e:
            self.logger.error(f"Error verifying data integrity: {e}")
        
        return integrity_results