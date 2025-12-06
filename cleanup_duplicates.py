#!/usr/bin/env python3
"""
Guardian Node - Cleanup Script
Removes duplicate and outdated files for investor presentation
"""

import os
import shutil
from pathlib import Path

# Files to remove (duplicates and outdated documentation)
FILES_TO_REMOVE = [
    "README-NEW.md",  # Duplicate README
    "README-UPDATED.md",  # Duplicate README
    "cleanup_proposal.txt",  # Old cleanup notes
    "REMAINING_TASKS.md",  # Outdated (all tasks complete)
    "test_al_nodie.md",  # Test file
    "gemma-2-2b-it-Q4_K_M.ggufZone.Identifier",  # Zone identifier file
    "guardian_gui.pyZone.Identifier",  # Zone identifier file
]

# Directories to clean (optional - keep for now)
DIRS_TO_REVIEW = [
    "__pycache__",  # Python cache (can be regenerated)
]

def cleanup_files():
    """Remove duplicate and outdated files"""
    print("="*70)
    print("GUARDIAN NODE - CLEANUP SCRIPT")
    print("="*70)
    print("\nThis script will remove duplicate and outdated files.")
    print("All important functionality is preserved.\n")
    
    removed_count = 0
    skipped_count = 0
    
    for file_path in FILES_TO_REMOVE:
        full_path = Path(file_path)
        
        if full_path.exists():
            try:
                if full_path.is_file():
                    full_path.unlink()
                    print(f"✅ Removed: {file_path}")
                    removed_count += 1
                elif full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"✅ Removed directory: {file_path}")
                    removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
                skipped_count += 1
        else:
            print(f"⚠️  Not found: {file_path}")
            skipped_count += 1
    
    print("\n" + "="*70)
    print("CLEANUP SUMMARY")
    print("="*70)
    print(f"\n✅ Removed: {removed_count} items")
    print(f"⚠️  Skipped: {skipped_count} items")
    
    if removed_count > 0:
        print("\n🎉 Cleanup complete! Repository is now investor-ready.")
    else:
        print("\n✅ Repository is already clean!")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Review ALL_TASKS_COMPLETE.md for feature summary
2. Run tests: python test_noddy_simple.py
3. Run tests: python test_smart_home.py
4. Run tests: python test_api.py
5. Review COMPREHENSIVE_TESTING_GUIDE.md for investor demo
6. Check API_DOCUMENTATION.md for API reference
7. Review CHANGES.md for complete change log

Ready for investor presentation! 🚀
""")

def show_file_sizes():
    """Show sizes of key files"""
    print("\n" + "="*70)
    print("KEY FILE SIZES")
    print("="*70)
    
    key_files = [
        "guardian_interpreter/main.py",
        "guardian_interpreter/api_server.py",
        "guardian_interpreter/memory_vault.py",
        "guardian_interpreter/network_scanner.py",
        "guardian_interpreter/smart_home.py",
        "README.md",
        "CHANGES.md",
        "ALL_TASKS_COMPLETE.md",
    ]
    
    total_size = 0
    
    for file_path in key_files:
        full_path = Path(file_path)
        if full_path.exists():
            size = full_path.stat().st_size
            total_size += size
            size_kb = size / 1024
            print(f"  {file_path:<50} {size_kb:>8.1f} KB")
    
    print(f"\n  {'Total:':<50} {total_size/1024:>8.1f} KB")

if __name__ == "__main__":
    try:
        cleanup_files()
        show_file_sizes()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Cleanup failed: {e}")
