#!/usr/bin/env python3
"""
Quick script to check what data we're now capturing from fault code pages.
"""

import sqlite3

def check_fault_code_data():
    conn = sqlite3.connect('fault_codes.db')
    cursor = conn.cursor()
    
    # Get a sample fault code with all the new data
    cursor.execute('''
        SELECT code, title, full_content, symptoms, causes, solutions, special_notes, technical_info 
        FROM fault_codes 
        WHERE full_content IS NOT NULL AND full_content != ''
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    if result:
        code, title, full_content, symptoms, causes, solutions, special_notes, technical_info = result
        
        print(f"Fault Code: {code}")
        print(f"Title: {title}")
        print("=" * 50)
        
        if full_content:
            print(f"Full Content Length: {len(full_content)} characters")
            print(f"Full Content Preview: {full_content[:500]}...")
            print()
        
        if symptoms:
            print(f"Symptoms: {symptoms}")
            print()
        
        if causes:
            print(f"Causes: {causes}")
            print()
        
        if solutions:
            print(f"Solutions: {solutions}")
            print()
        
        if special_notes:
            print(f"Special Notes: {special_notes}")
            print()
        
        if technical_info:
            print(f"Technical Info: {technical_info}")
            print()
    else:
        print("No enhanced data found yet. Run the crawler to populate the new fields.")
    
    # Show database statistics
    cursor.execute("SELECT COUNT(*) FROM fault_codes")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fault_codes WHERE full_content IS NOT NULL AND full_content != ''")
    enhanced_count = cursor.fetchone()[0]
    
    print(f"Database Statistics:")
    print(f"Total fault codes: {total_count}")
    print(f"Enhanced fault codes: {enhanced_count}")
    
    conn.close()

if __name__ == "__main__":
    check_fault_code_data()
