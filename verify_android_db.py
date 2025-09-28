#!/usr/bin/env python3
"""
Verify database on Android/Termux
"""

import sqlite3
import os

def verify_database():
    """Verify the database has the expected content."""
    print("Verifying fault codes database...")
    print("=" * 40)
    
    if not os.path.exists("fault_codes.db"):
        print("ERROR: fault_codes.db not found!")
        print("Make sure you've transferred and decompressed the database.")
        return False
    
    # Get file size
    db_size = os.path.getsize("fault_codes.db")
    print(f"Database file size: {db_size:,} bytes ({db_size/1024/1024:.1f} MB)")
    
    try:
        conn = sqlite3.connect("fault_codes.db")
        cursor = conn.cursor()
        
        # Count total codes
        cursor.execute("SELECT COUNT(*) FROM fault_codes")
        total = cursor.fetchone()[0]
        
        # Count PDF codes
        cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content LIKE '%extracted from the VAG fault codes PDF%'")
        pdf_codes = cursor.fetchone()[0]
        
        # Count Ross-Tech codes
        cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content LIKE '%Possible Symptoms%'")
        ross_tech_codes = cursor.fetchone()[0]
        
        # Test a few specific codes
        test_codes = ['00277', '00278', 'P1757', 'P0102']
        print(f"\nTesting specific codes:")
        for code in test_codes:
            cursor.execute("SELECT code, title FROM fault_codes WHERE code = ?", (code,))
            result = cursor.fetchone()
            if result:
                print(f"  ✓ {code}: {result[1]}")
            else:
                print(f"  ✗ {code}: NOT FOUND")
        
        conn.close()
        
        print(f"\nDatabase Statistics:")
        print(f"  Total codes: {total:,}")
        print(f"  PDF codes: {pdf_codes:,}")
        print(f"  Ross-Tech codes: {ross_tech_codes:,}")
        
        if pdf_codes > 0:
            print("\n✅ SUCCESS: Database contains PDF definitions!")
            print("Your Flask app should now show proper descriptions for PDF codes.")
            return True
        else:
            print("\n❌ ERROR: No PDF definitions found!")
            print("The database may not be properly updated.")
            return False
            
    except sqlite3.Error as e:
        print(f"ERROR: Database error - {e}")
        return False

if __name__ == "__main__":
    verify_database()
