# Backup and Restore System
A graphical application for creating and restoring folder backups with encryption and file splitting capabilities.
## Key Features
- Complete folder backup (including subfolders)
- AES-256 encryption option
- Backup splitting into manageable parts
- Simple restoration process
- Intuitive graphical interface

## Installation
Install dependencies:
 ```bash
pip install -r requirements.txt
```

## Running the Application
Basic Execution
 ```bash
py .\main.py
```

## Basic Usage
- Creating a Backup:
   - Select folder(s) to backup
   - Specify destination folder
   - Configure options (encryption, splitting)
   - Click "Create Backup"
- Restoring a Backup:
   - Select .zip file or fragments folder
   - Specify destination folder
   - Provide encryption key if needed
   - Click "Restore Backup"

## Architecture Overview
This project is a modular backup and restore application with a Tkinter-based GUI. Its main components are:

- *GUI (gui/app.py)*: Lets users select folders/files, configure options (encryption, fragmentation, cloud upload), and start backup/restore operations.
- *Backup Module (backup/create.py, compressor.py)*: Compresses files (using Dask for parallelism), optionally encrypts and fragments the backup.
- *Restore Module (backup/restore.py)*: Restores backups, handling decryption and defragmentation if needed.
- *Cloud Integration (backup/cloud/google_drive.py)*: Uploads backups to Google Drive.
The app is designed for easy maintenance and extension, with each feature in its own module.

## Why Python?
Python was chosen for this project because it offers:

- Cross-platform support: Python runs on Windows, macOS, and Linux, making the app accessible to many users.
- Rich ecosystem: Libraries like Tkinter, Dask, zipfile, and cryptography simplify GUI development, parallel processing, compression, and encryption.
- Rapid development: Python’s clear syntax and dynamic typing allow for fast prototyping and easy maintenance.
- Strong community: Extensive documentation and community support make it easier to solve problems and extend functionality.

Overall, Python enables quick development of robust, user-friendly backup tools with advanced features. Also, it was an opportunity to expand the knowledge on python tools.

## Parallel Processing with Dask

This implementation uses Dask for parallel compression of files during backup operations. Here's a detailed explanation:
Implementation in ```backup/compressor.py```:

### How It Works:
1. Dask Delayed Decorator:
   - The @delayed decorator marks the agregar_archivo function as a lazy operation that should be executed in parallel
2. Task Graph Construction:
   - We create one delayed task per file to add to the ZIP archive
   - Each task is independent, allowing parallel execution
3. Parallel Execution:
   - compute(*tareas) triggers the parallel execution of all tasks
   - Dask automatically handles:
      - Task scheduling
      - Worker management
      - Memory optimization
4. ZIP File Handling:
   - First creates an empty ZIP file
   - Each task appends ('a' mode) its file to the archive
   - Uses ZIP_DEFLATED for compression

## Compression Implementation

### Technical Foundation
The backup system employs the industry-standard DEFLATE compression algorithm through Python's built-in zipfile module. This combination provides:

1. Algorithm: DEFLATE (LZ77 + Huffman coding)
   - Lossless data compression
   - Balanced compression ratio (typically 2:1 to 3:1 for text)
   - Fast processing suitable for backup operations
2. Library: Python's zipfile
   - Native implementation requiring no additional dependencies
   - Supports ZIP64 for large files (>4GB)
   - Preserves file metadata and directory structure

## Google Drive Integration

The system integrates with Google Drive for cloud backup storage using the official Google Drive API.

### How It Works:
1. Authentication
   - Uses OAuth 2.0 for secure access
   - Requires credentials.json from Google Cloud Platform
   - Grants limited access only to files created by the application
2. Storage Process
   - Encrypted backups are uploaded as single files or split fragments
   - Maintains original folder structure when restored
   - Uses efficient resumable uploads for large files
3. Security
   - Operates under drive.file scope (access only to created files)
   - Encryption occurs locally before cloud transfer
   - Credentials are never stored in plain text
### Setup Requirements:
- Enable Google Drive API in Google Cloud Console
- Configure OAuth consent screen
- Download credentials.json to your project's secure config directory

## Storage on Disk

The application allows users to choose a specific disk drive (such as C: or D:\) as the backup destination. When the user clicks the "Select Disk..." button in the GUI, the app:
1. Detects all available drives on the system using Windows APIs.
2. Displays a list of drives in a popup window.
3. The user selects a drive, and its path is automatically set as the backup destination.

This feature makes it easy to save backups directly to external drives, USB sticks, or other partitions, improving flexibility and data safety.

## Team Members
This project was made by Paulina Cerón, Camilo Córdoba and Sara Valentina Cortes.

You can find the explanatory video [HERE](https://eafit-my.sharepoint.com/:v:/g/personal/pceronm_eafit_edu_co/EZBvRZwr0ApEuAl-XLwknbUBLbwQTF39aGMYifFNp0ZYKg?e=h3C3ZG&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D)

