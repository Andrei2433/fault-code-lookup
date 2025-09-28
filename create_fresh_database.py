#!/usr/bin/env python3
"""
Create a fresh, verified database for Android transfer
"""

import sqlite3
import gzip
import os

def create_fresh_database():
    """Create a fresh database package."""
    
    print("Creating fresh database package...")
    print("=" * 40)
    
    # Check if source database exists
    if not os.path.exists("fault_codes.db"):
        print("ERROR: fault_codes.db not found!")
        return False
    
    # Verify source database
    print("Verifying source database...")
    conn = sqlite3.connect("fault_codes.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM fault_codes")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content LIKE '%extracted from the VAG fault codes PDF%'")
    pdf_codes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content LIKE '%Possible Symptoms%'")
    ross_tech_codes = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Source database stats:")
    print(f"  Total codes: {total:,}")
    print(f"  PDF codes: {pdf_codes:,}")
    print(f"  Ross-Tech codes: {ross_tech_codes:,}")
    
    if total < 2000 or pdf_codes < 500:
        print("ERROR: Source database is incomplete!")
        return False
    
    # Create compressed version
    print("\nCreating compressed database...")
    with open("fault_codes.db", "rb") as f_in:
        with gzip.open("fault_codes_fresh.db.gz", "wb") as f_out:
            f_out.write(f_in.read())
    
    # Verify compressed file
    compressed_size = os.path.getsize("fault_codes_fresh.db.gz")
    original_size = os.path.getsize("fault_codes.db")
    
    print(f"Compression complete:")
    print(f"  Original size: {original_size:,} bytes ({original_size/1024/1024:.1f} MB)")
    print(f"  Compressed size: {compressed_size:,} bytes ({compressed_size/1024/1024:.1f} MB)")
    print(f"  Compression ratio: {compressed_size/original_size*100:.1f}%")
    
    # Test decompression
    print("\nTesting decompression...")
    try:
        with gzip.open("fault_codes_fresh.db.gz", "rb") as f_in:
            test_data = f_in.read()
        
        if len(test_data) == original_size:
            print("✅ Decompression test passed")
        else:
            print("❌ Decompression test failed")
            return False
            
    except Exception as e:
        print(f"❌ Decompression test failed: {e}")
        return False
    
    print(f"\n✅ Fresh database package created successfully!")
    print(f"File: fault_codes_fresh.db.gz ({compressed_size:,} bytes)")
    
    return True

if __name__ == "__main__":
    create_fresh_database()
