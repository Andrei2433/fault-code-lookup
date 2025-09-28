#!/usr/bin/env python3
"""
Debug database issues on Android/Termux
"""

import sqlite3
import os

def debug_database():
    """Debug database issues."""
    print("Debugging fault codes database...")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists("fault_codes.db"):
        print("❌ ERROR: fault_codes.db not found!")
        print("Please download the database first:")
        print("wget https://raw.githubusercontent.com/Andrei2433/fault-code-lookup/main/fault_codes.db.gz")
        print("gunzip fault_codes.db.gz")
        return False
    
    # Check file size
    db_size = os.path.getsize("fault_codes.db")
    print(f"📁 Database file size: {db_size:,} bytes ({db_size/1024/1024:.1f} MB)")
    
    if db_size < 1000000:  # Less than 1MB
        print("❌ ERROR: Database file is too small!")
        print("Expected: ~5.7 MB")
        print("This suggests the download was incomplete or corrupted.")
        return False
    
    if db_size > 10000000:  # More than 10MB
        print("⚠️  WARNING: Database file is unusually large!")
        print("This might be a different database file.")
    
    # Try to open database
    try:
        conn = sqlite3.connect("fault_codes.db")
        cursor = conn.cursor()
        print("✅ Database file can be opened")
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fault_codes'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ ERROR: 'fault_codes' table not found!")
            print("This is not the correct database file.")
            conn.close()
            return False
        
        print("✅ 'fault_codes' table exists")
        
        # Count total codes
        cursor.execute("SELECT COUNT(*) FROM fault_codes")
        total = cursor.fetchone()[0]
        print(f"📊 Total codes in database: {total:,}")
        
        if total < 1000:
            print("❌ ERROR: Too few codes in database!")
            print("Expected: ~2,245 codes")
            print("This suggests the database is incomplete.")
            conn.close()
            return False
        
        # Check for PDF codes
        cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content LIKE '%extracted from the VAG fault codes PDF%'")
        pdf_codes = cursor.fetchone()[0]
        print(f"📄 PDF codes: {pdf_codes:,}")
        
        # Check for Ross-Tech codes
        cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content LIKE '%Possible Symptoms%'")
        ross_tech_codes = cursor.fetchone()[0]
        print(f"🌐 Ross-Tech codes: {ross_tech_codes:,}")
        
        # Test specific codes
        print(f"\n🧪 Testing specific codes:")
        test_codes = ['00277', '00278', 'P1757', 'P0102']
        found_codes = 0
        
        for code in test_codes:
            cursor.execute("SELECT code, title FROM fault_codes WHERE code = ?", (code,))
            result = cursor.fetchone()
            if result:
                print(f"  ✅ {code}: {result[1]}")
                found_codes += 1
            else:
                print(f"  ❌ {code}: NOT FOUND")
        
        conn.close()
        
        # Final assessment
        print(f"\n📋 Summary:")
        print(f"  File size: {db_size:,} bytes")
        print(f"  Total codes: {total:,}")
        print(f"  PDF codes: {pdf_codes:,}")
        print(f"  Ross-Tech codes: {ross_tech_codes:,}")
        print(f"  Test codes found: {found_codes}/4")
        
        if total >= 2000 and pdf_codes >= 500 and found_codes >= 3:
            print("\n✅ SUCCESS: Database appears to be working correctly!")
            return True
        else:
            print("\n❌ ERROR: Database is incomplete or corrupted!")
            print("\n🔧 Solution:")
            print("1. Delete the current database: rm fault_codes.db")
            print("2. Download fresh: wget https://raw.githubusercontent.com/Andrei2433/fault-code-lookup/main/fault_codes.db.gz")
            print("3. Decompress: gunzip fault_codes.db.gz")
            print("4. Verify: python debug_database.py")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ ERROR: Database error - {e}")
        print("The database file is corrupted or not a valid SQLite database.")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")
        return False

if __name__ == "__main__":
    debug_database()
