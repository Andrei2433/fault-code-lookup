# Ross-Tech VCDS Fault Codes Desktop Application

A Python desktop application for looking up Ross-Tech VCDS fault codes offline. This application consists of a web crawler that scrapes fault code data from the Ross-Tech wiki and a Tkinter-based desktop app for searching the collected data.

## Features

- **Offline Operation**: Once the database is built, the app works completely offline
- **Comprehensive Data**: Extracts fault codes, titles, symptoms, causes, and solutions
- **User-Friendly Interface**: Clean Tkinter GUI with formatted results
- **Smart Search**: Supports partial fault code matching
- **SQLite Database**: Fast and reliable local storage

## Files

- `crawler.py` - Web crawler script to scrape fault codes from Ross-Tech wiki
- `app.py` - Desktop application with Tkinter GUI
- `requirements.txt` - Python dependencies
- `fault_codes.db` - SQLite database (created after running crawler)
- `crawler.log` - Crawler execution log

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Crawler** (First time only):
   ```bash
   python crawler.py
   ```
   
   This will:
   - Create a SQLite database (`fault_codes.db`)
   - Scrape fault codes from the Ross-Tech wiki
   - Save all data for offline use
   - Display progress and completion status

3. **Run the Desktop Application**:
   ```bash
   python app.py
   ```

## Usage

### Building the Database (First Time)

1. Run `python crawler.py`
2. The crawler will start from the Ross-Tech fault codes index page
3. It will visit each fault code page and extract:
   - Fault Code (e.g., "00532")
   - Title (e.g., "Supply Voltage B+")
   - Possible Symptoms
   - Possible Causes
   - Possible Solutions
4. Progress is logged to both console and `crawler.log`
5. The process may take several minutes depending on the number of fault codes

### Using the Desktop App

1. Run `python app.py`
2. Enter a fault code in the search box (e.g., "00532" or "532")
3. Press Enter or click "Search"
4. View the formatted results including:
   - Fault code and title
   - Possible symptoms
   - Possible causes
   - Possible solutions

### Search Features

- **Exact Match**: Enter the full 5-digit fault code (e.g., "00532")
- **Partial Match**: Enter fewer digits (e.g., "532") to find all matching codes
- **Auto-formatting**: The app automatically pads shorter codes with leading zeros
- **Real-time Validation**: Search button is enabled only for valid numeric input

## Database Schema

The SQLite database uses the following schema:

```sql
CREATE TABLE fault_codes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    title TEXT,
    symptoms TEXT,
    causes TEXT,
    solutions TEXT,
    UNIQUE(code)
);
```

## Troubleshooting

### Database Not Found
- Make sure you've run `crawler.py` at least once
- Check that `fault_codes.db` exists in the same directory as `app.py`

### Empty Database
- The crawler may have encountered errors
- Check `crawler.log` for detailed error messages
- Try running the crawler again

### Network Issues
- The crawler requires internet access to scrape the Ross-Tech wiki
- If the initial crawl fails, you can run it again (it will update existing entries)

### No Results Found
- Verify the fault code format (should be 1-5 digits)
- Try searching with fewer digits for partial matches
- Check if the fault code exists in the database

## Technical Details

### Crawler Features
- Respectful scraping with 1-second delays between requests
- Robust error handling and logging
- Automatic pagination handling
- Duplicate prevention with UNIQUE constraints
- Progress tracking and statistics

### App Features
- Clean, responsive Tkinter interface
- Formatted text display with color coding
- Scrollable results for long content
- Real-time input validation
- Status bar with helpful messages

## Requirements

- Python 3.7 or higher
- Internet connection (for initial database building only)
- Required packages: `requests`, `beautifulsoup4`, `lxml`

## License

This project is for educational and personal use. Please respect the Ross-Tech wiki's terms of service when using the crawler.
