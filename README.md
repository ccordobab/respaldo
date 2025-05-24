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
