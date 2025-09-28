# Simple Android/Termux Setup

## Quick Setup (3 steps)

### Step 1: Download the database
```bash
# In Termux, run these commands:
wget https://raw.githubusercontent.com/Andrei2433/fault-code-lookup/main/fault_codes.db.gz
```

### Step 2: Decompress the database
```bash
gunzip fault_codes.db.gz
```

### Step 3: Start your app
```bash
python app_flask.py
```

## Alternative: Manual Download

If `wget` doesn't work, you can:

1. **Download manually** from: https://github.com/Andrei2433/fault-code-lookup/raw/main/fault_codes.db.gz
2. **Transfer** the file to your Termux directory
3. **Decompress**: `gunzip fault_codes.db.gz`
4. **Start app**: `python app_flask.py`

## Verify it's working

Test with these codes:
- `00277` → Should show "ABS Inlet or Outlet Valve - Left Front (N137)"
- `00278` → Should show "ABS Main Valve (N105)"
- `P1757` → Should show full Ross-Tech diagnostic info

## Database Info
- **Total codes**: 2,245
- **PDF codes**: 718 (with real descriptions)
- **Ross-Tech codes**: 842 (with full diagnostic info)
- **File size**: 5.7 MB (compressed to 0.5 MB)

## Troubleshooting

If you get "No results found":
1. Check the database file exists: `ls -la fault_codes.db`
2. Check file size: `du -h fault_codes.db` (should be ~5.7MB)
3. Verify with: `python verify_android_db.py`
