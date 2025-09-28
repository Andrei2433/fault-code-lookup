# Fault Codes Database

## Database Information
- **Version**: 1.0.0
- **Created**: 2025-09-28T20:21:17.590498
- **Total Codes**: 2,245
- **PDF Codes**: 718
- **Ross-Tech Codes**: 842

## Files
- `fault_codes.db.gz` - Compressed database (0.5 MB)
- `database_info.json` - Database metadata
- `sync_database_android.py` - Android sync script

## How to Use on Android/Termux

1. Download the files to your Termux directory
2. Run: `python sync_database_android.py`
3. Start your Flask app: `python app_flask.py`

## Manual Installation
1. Download `fault_codes.db.gz`
2. Run: `gunzip fault_codes.db.gz`
3. Start your Flask app: `python app_flask.py`
