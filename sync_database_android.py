#!/usr/bin/env python3
"""
Sync database from GitHub
Run this script in Termux to update your database
"""

import requests
import gzip
import json
import os
import sqlite3

def download_database():
    """Download and restore database from GitHub."""
    
    # Database info URL (you'll need to update this with your actual GitHub URL)
    info_url = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/database_info.json"
    db_url = "https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v1.0.0/fault_codes.db.gz"
    
    print("Downloading database info...")
    try:
        response = requests.get(info_url)
        if response.status_code == 200:
            info = response.json()
            print(f"Database version: {info['version']}")
            print(f"Total codes: {info['total_codes']:,}")
            print(f"PDF codes: {info['pdf_codes']:,}")
            print(f"Ross-Tech codes: {info['ross_tech_codes']:,}")
        else:
            print("Could not fetch database info")
    except Exception as e:
        print(f"Error fetching info: {e}")
    
    print("\nDownloading database...")
    try:
        response = requests.get(db_url)
        if response.status_code == 200:
            with open("fault_codes.db.gz", "wb") as f:
                f.write(response.content)
            print("Database downloaded successfully!")
            
            # Decompress
            print("Decompressing database...")
            with gzip.open("fault_codes.db.gz", "rb") as f_in:
                with open("fault_codes.db", "wb") as f_out:
                    f_out.write(f_in.read())
            
            # Clean up
            os.remove("fault_codes.db.gz")
            
            print("Database restored successfully!")
            return True
        else:
            print(f"Failed to download database: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading database: {e}")
        return False

if __name__ == "__main__":
    print("Syncing fault codes database...")
    print("=" * 40)
    download_database()
