#!/usr/bin/env python3
"""
Update the Flask app to mobile-optimized version
"""

import shutil
import os
from datetime import datetime

def backup_original():
    """Create a backup of the original app."""
    if os.path.exists("app_flask.py"):
        backup_name = f"app_flask_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        shutil.copy2("app_flask.py", backup_name)
        print(f"✅ Backup created: {backup_name}")
        return True
    return False

def update_to_mobile():
    """Replace the original app with mobile-optimized version."""
    
    print("Updating Flask app to mobile-optimized version...")
    print("=" * 50)
    
    # Create backup
    if not backup_original():
        print("❌ Original app_flask.py not found!")
        return False
    
    # Replace with mobile version
    if os.path.exists("app_flask_mobile.py"):
        shutil.copy2("app_flask_mobile.py", "app_flask.py")
        print("✅ App updated to mobile-optimized version")
        
        # Show what's new
        print("\n📱 Mobile Optimizations Added:")
        print("  • Responsive design for all screen sizes")
        print("  • Touch-friendly buttons and inputs")
        print("  • Improved mobile typography")
        print("  • Better tab navigation on mobile")
        print("  • Auto-focus on search input")
        print("  • Optimized for portrait orientation")
        print("  • Better spacing and padding")
        print("  • Improved color contrast")
        print("  • Smooth animations and transitions")
        
        return True
    else:
        print("❌ Mobile version not found!")
        return False

if __name__ == "__main__":
    if update_to_mobile():
        print("\n🎉 Update complete!")
        print("You can now run: python app_flask.py")
        print("The app will be optimized for mobile devices.")
    else:
        print("\n❌ Update failed!")
