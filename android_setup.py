#!/usr/bin/env python3
"""
Android/Termux setup script
Downloads and sets up the updated fault codes database
"""

import requests
import gzip
import json
import os
import sqlite3

def download_file(url, filename):
    """Download a file from URL."""
    try:
        print(f"Downloading {filename}...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✓ {filename} downloaded successfully")
            return True
        else:
            print(f"✗ Failed to download {filename}: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error downloading {filename}: {e}")
        return False

def setup_database():
    """Download and setup the database."""
    
    # GitHub repository URLs (update these with your actual repo)
    base_url = "https://raw.githubusercontent.com/Andrei2433/fault-code-lookup/main/"
    
    files_to_download = [
        "database_info.json",
        "fault_codes.db.gz",
        "verify_android_db.py"
    ]
    
    print("Setting up fault codes database for Android...")
    print("=" * 50)
    
    # Download files
    for filename in files_to_download:
        url = base_url + filename
        if not download_file(url, filename):
            print(f"Failed to download {filename}")
            return False
    
    # Show database info
    if os.path.exists("database_info.json"):
        with open("database_info.json", "r") as f:
            info = json.load(f)
        print(f"\nDatabase Information:")
        print(f"  Version: {info['version']}")
        print(f"  Total codes: {info['total_codes']:,}")
        print(f"  PDF codes: {info['pdf_codes']:,}")
        print(f"  Ross-Tech codes: {info['ross_tech_codes']:,}")
    
    # Decompress database
    if os.path.exists("fault_codes.db.gz"):
        print(f"\nDecompressing database...")
        try:
            with gzip.open("fault_codes.db.gz", "rb") as f_in:
                with open("fault_codes.db", "wb") as f_out:
                    f_out.write(f_in.read())
            print("✓ Database decompressed successfully")
            
            # Clean up compressed file
            os.remove("fault_codes.db.gz")
            print("✓ Cleaned up compressed file")
            
        except Exception as e:
            print(f"✗ Error decompressing database: {e}")
            return False
    
    # Verify database
    print(f"\nVerifying database...")
    try:
        conn = sqlite3.connect("fault_codes.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM fault_codes")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content LIKE '%extracted from the VAG fault codes PDF%'")
        pdf_codes = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✓ Database verified: {total:,} total codes, {pdf_codes:,} PDF codes")
        
        if pdf_codes > 0:
            print("✅ SUCCESS: Database is ready!")
            print("\nYou can now run: python app_flask.py")
            return True
        else:
            print("❌ ERROR: Database appears to be incomplete")
            return False
            
    except Exception as e:
        print(f"✗ Error verifying database: {e}")
        return False

if __name__ == "__main__":
    if setup_database():
        print("\n🎉 Setup complete! Your fault codes app is ready to use.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
