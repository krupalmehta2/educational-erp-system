# Educational ERP System

A console-based Educational ERP (Enterprise Resource Planning) System built with Python for managing educational institutions.

## Features

- Stream management (BCA, BSc IT, etc.)
- Class management within streams
- Student enrollment with auto-generated IDs
- Faculty management with assignment to classes
- Data persistence using JSON files
- Search functionality for students and faculty
- Backup system

## How to Use

1. Make sure you have Python installed
2. Run the program: `python erp_system.py`
3. Follow the menu options to manage your educational institution

## File Structure

- `erp_system.py` - Main program file
- `erp_data.json` - Data storage (created automatically)
- `erp_backup_YYYYMMDD_HHMMSS.json` - Backup files (created when using backup feature)

## Requirements

- Python 3.x
- No external dependencies
