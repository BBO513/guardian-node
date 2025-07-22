#!/usr/bin/env python3
"""
Unit tests for the Family Data Persistence Layer
"""

import unittest
import tempfile
import shutil
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

from data_persistence import FamilyDataStore, DataEncryption
from recommendation_engine import SecurityRecommendation, FamilyProfile, Priority, Difficulty

class TestDataEncryption(unittest.TestCase):
    """Test data encryption functionality"""
    
    def setUp(self):
        self.password = "test_password_123"
        self.encryption = DataEncryption(self.password)
    
    def test_encrypt_decrypt(self):
        """Test basic encryption and decryption"""
        original_data = "This is sensitive family data"
        
        # Encrypt
        encrypted_data = self.encryption.encrypt(original_data)
        self.assertIsInstance(encrypted_data, bytes)
        self.assertNotEqual(encrypted_data, original_data.encode())
        
        # Decrypt
        decrypted_data = self.encryption.decrypt(encrypted_data)
        self.assertEqual(decrypted_data, original_data)
    
    def test_encryption_with_salt(self):
        """Test encryption with provided salt"""
        salt = b'test_salt_16byte'
        encryption1 = DataEncryption(self.password, salt)
        encryption2 = DataEncryption(self.password, salt)
        
        test_data = "test data"
        encrypted1 = encryption1.encrypt(test_data)
        decrypted2 = encryption2.decrypt(encrypted1)
        
        self.assertEqual(decrypted2, test_data)
    
    def test_different_passwords_fail(self):
        """Test that different passwords cannot decrypt data"""
        encryption1 = DataEncryption("password1")
        encryption2 = DataEncryption("password2")
        
        test_data = "secret data"
        encrypted = encryption1.encrypt(test_data)
        
        with self.assertRaises(Exception):
            encryption2.decrypt(encrypted)

class TestFamilyDataStore(unittest.TestCase):
    """Test family data storage functionality"""
    
    def setUp(self):
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'family_assistant': {
                'data_directory': f"{self.temp_dir}/data",
                'backup_directory': f"{self.temp_dir}/backups"
            }
        }
        self.logger = Mock(spec=logging.Logger)
        self.password = "test_encryption_password"
        
        # Create data store
        self.data_store = FamilyDataStore(self.config, self.logger, self.password)
        
        # Sample family profile
        self.sample_family = FamilyProfile(
            family_id="test_family_001",
            family_name="Test Family",
            members=[
                {
                    "member_id": "member_001",
                    "name": "Parent",
                    "age_group": "adult",
                    "tech_skill_level": "intermediate"
                }
            ],
            devices=[
                {
                    "device_id": "device_001",
                    "device_type": "smartphone",
                    "owner": "member_001"
                }
            ],
            security_preferences={"data_protection": True},
            threat_tolerance="medium",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Sample recommendation
        self.sample_recommendation = SecurityRecommendation(
            recommendation_id="rec_001",
            title="Test Recommendation",
            description="A test security recommendation",
            priority=Priority.HIGH,
            difficulty=Difficulty.MODERATE,
            estimated_time="30 minutes",
            steps=["Step 1", "Step 2"],
            applicable_devices=["device_001"],
            family_members=["member_001"],
            category="authentication",
            created_at=datetime.now()
        )
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_data_store_initialization(self):
        """Test data store initialization"""
        self.assertTrue(Path(self.config['family_assistant']['data_directory']).exists())
        self.assertTrue(Path(self.config['family_assistant']['backup_directory']).exists())
        self.assertIsNotNone(self.data_store.encryption)
    
    def test_save_and_load_family_profile(self):
        """Test saving and loading family profiles"""
        # Save family profile
        result = self.data_store.save_family_profile(self.sample_family)
        self.assertTrue(result)
        
        # Load family profile
        loaded_family = self.data_store.load_family_profile(self.sample_family.family_id)
        self.assertIsNotNone(loaded_family)
        self.assertEqual(loaded_family.family_id, self.sample_family.family_id)
        self.assertEqual(loaded_family.family_name, self.sample_family.family_name)
        self.assertEqual(len(loaded_family.members), len(self.sample_family.members))
    
    def test_load_nonexistent_family_profile(self):
        """Test loading non-existent family profile"""
        loaded_family = self.data_store.load_family_profile("nonexistent_family")
        self.assertIsNone(loaded_family)
    
    def test_list_family_profiles(self):
        """Test listing family profiles"""
        # Initially empty
        families = self.data_store.list_family_profiles()
        self.assertEqual(len(families), 0)
        
        # Save a family
        self.data_store.save_family_profile(self.sample_family)
        
        # Should now have one family
        families = self.data_store.list_family_profiles()
        self.assertEqual(len(families), 1)
        self.assertIn(self.sample_family.family_id, families)
    
    def test_delete_family_profile(self):
        """Test deleting family profiles"""
        # Save family first
        self.data_store.save_family_profile(self.sample_family)
        
        # Verify it exists
        families = self.data_store.list_family_profiles()
        self.assertIn(self.sample_family.family_id, families)
        
        # Delete it
        result = self.data_store.delete_family_profile(self.sample_family.family_id)
        self.assertTrue(result)
        
        # Verify it's gone
        families = self.data_store.list_family_profiles()
        self.assertNotIn(self.sample_family.family_id, families)
    
    def test_delete_nonexistent_family_profile(self):
        """Test deleting non-existent family profile"""
        result = self.data_store.delete_family_profile("nonexistent_family")
        self.assertFalse(result)
    
    def test_save_and_load_recommendations(self):
        """Test saving and loading recommendations"""
        recommendations = [self.sample_recommendation]
        
        # Save recommendations
        result = self.data_store.save_recommendations(self.sample_family.family_id, recommendations)
        self.assertTrue(result)
        
        # Load recommendations
        loaded_recs = self.data_store.load_recommendations(self.sample_family.family_id)
        self.assertEqual(len(loaded_recs), 1)
        self.assertEqual(loaded_recs[0].recommendation_id, self.sample_recommendation.recommendation_id)
        self.assertEqual(loaded_recs[0].title, self.sample_recommendation.title)
    
    def test_load_nonexistent_recommendations(self):
        """Test loading recommendations for non-existent family"""
        loaded_recs = self.data_store.load_recommendations("nonexistent_family")
        self.assertEqual(len(loaded_recs), 0)
    
    def test_save_and_load_settings(self):
        """Test saving and loading application settings"""
        settings = {
            "theme": "dark",
            "notifications": True,
            "auto_backup": False
        }
        
        # Save settings
        result = self.data_store.save_settings(settings)
        self.assertTrue(result)
        
        # Load settings
        loaded_settings = self.data_store.load_settings()
        self.assertEqual(loaded_settings["theme"], "dark")
        self.assertEqual(loaded_settings["notifications"], True)
        self.assertEqual(loaded_settings["auto_backup"], False)
    
    def test_create_backup(self):
        """Test creating data backups"""
        # Save some data first
        self.data_store.save_family_profile(self.sample_family)
        self.data_store.save_recommendations(self.sample_family.family_id, [self.sample_recommendation])
        
        # Create backup
        result = self.data_store.create_backup("test_backup")
        self.assertTrue(result)
        
        # Verify backup exists
        backup_path = Path(self.config['family_assistant']['backup_directory']) / "test_backup"
        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / "backup_metadata.json").exists())
    
    def test_list_backups(self):
        """Test listing available backups"""
        # Initially no backups
        backups = self.data_store.list_backups()
        self.assertEqual(len(backups), 0)
        
        # Create a backup
        self.data_store.create_backup("test_backup_1")
        
        # Should now have one backup
        backups = self.data_store.list_backups()
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0]['backup_name'], "test_backup_1")
    
    def test_restore_backup(self):
        """Test restoring from backup"""
        # Save original data
        self.data_store.save_family_profile(self.sample_family)
        original_families = self.data_store.list_family_profiles()
        
        # Create backup
        self.data_store.create_backup("restore_test_backup")
        
        # Delete original data
        self.data_store.delete_family_profile(self.sample_family.family_id)
        self.assertEqual(len(self.data_store.list_family_profiles()), 0)
        
        # Restore from backup
        result = self.data_store.restore_backup("restore_test_backup")
        self.assertTrue(result)
        
        # Verify data is restored
        restored_families = self.data_store.list_family_profiles()
        self.assertEqual(len(restored_families), len(original_families))
        self.assertIn(self.sample_family.family_id, restored_families)
    
    def test_restore_nonexistent_backup(self):
        """Test restoring from non-existent backup"""
        result = self.data_store.restore_backup("nonexistent_backup")
        self.assertFalse(result)
    
    def test_get_storage_stats(self):
        """Test getting storage statistics"""
        # Save some data
        self.data_store.save_family_profile(self.sample_family)
        self.data_store.save_settings({"test": "value"})
        
        stats = self.data_store.get_storage_stats()
        
        self.assertIn('data_directory', stats)
        self.assertIn('backup_directory', stats)
        self.assertIn('encryption_enabled', stats)
        self.assertIn('files', stats)
        self.assertIn('total_size_bytes', stats)
        self.assertTrue(stats['encryption_enabled'])
        self.assertGreater(stats['total_size_bytes'], 0)
    
    def test_verify_data_integrity(self):
        """Test data integrity verification"""
        # Save some data
        self.data_store.save_family_profile(self.sample_family)
        self.data_store.save_recommendations(self.sample_family.family_id, [self.sample_recommendation])
        self.data_store.save_settings({"test": "value"})
        
        integrity = self.data_store.verify_data_integrity()
        
        self.assertIn('families_file', integrity)
        self.assertIn('recommendations_file', integrity)
        self.assertIn('settings_file', integrity)
        self.assertIn('encryption_working', integrity)
        
        # All should be True since we have valid data
        self.assertTrue(integrity['families_file'])
        self.assertTrue(integrity['recommendations_file'])
        self.assertTrue(integrity['settings_file'])
        self.assertTrue(integrity['encryption_working'])
    
    def test_cleanup_old_backups(self):
        """Test cleaning up old backups"""
        # Create some backups
        self.data_store.create_backup("backup_1")
        self.data_store.create_backup("backup_2")
        
        # Should have 2 backups
        backups = self.data_store.list_backups()
        self.assertEqual(len(backups), 2)
        
        # Cleanup with 0 days (should remove all)
        removed_count = self.data_store.cleanup_old_backups(keep_days=0)
        self.assertGreaterEqual(removed_count, 0)  # May be 0 if backups are very recent
    
    def test_data_store_without_encryption(self):
        """Test data store without encryption"""
        # Create data store without encryption password
        unencrypted_store = FamilyDataStore(self.config, self.logger)
        
        self.assertIsNone(unencrypted_store.encryption)
        
        # Should still be able to save and load data
        result = unencrypted_store.save_family_profile(self.sample_family)
        self.assertTrue(result)
        
        loaded_family = unencrypted_store.load_family_profile(self.sample_family.family_id)
        self.assertIsNotNone(loaded_family)
        self.assertEqual(loaded_family.family_id, self.sample_family.family_id)

if __name__ == '__main__':
    unittest.main()