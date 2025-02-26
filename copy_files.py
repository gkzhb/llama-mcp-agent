#!/usr/bin/env python3
import os
import shutil
import logging
from pathlib import Path
from typing import Callable

def default_file_filter(filename: str) -> bool:
    """Default file filter (preserves original filter logic)"""
    return filename.endswith(('.md', '.rst'))

def copy_files_with_hierarchy(
    src_dir: str,
    dest_dir: str,
    file_filter: Callable[[str], bool] = default_file_filter  # Use the default filter defined by def
) -> int:
    """
    Recursively traverse the source directory and copy files that match the filter criteria
    to the destination directory. The new filenames will include folder hierarchy information.

    Args:
        src_dir (str): Source directory path
        dest_dir (str): Destination directory path
        file_filter (Callable[[str], bool]): File filter function, defaults to filtering .md files
    """
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    if not dest_path.exists():
        logging.info(f"Creating target directory: {dest_dir}")
        dest_path.mkdir(parents=True)
    
    copied_count = 0
    copied_count = 0
    try:
        for entry in src_path.rglob('*'):
            if entry.is_file() and file_filter(entry.name):
                relative_path = entry.relative_to(src_path)
                parent_path = relative_path.parent
                
                # Generate new filename with path information
                new_name = f"{'_'.join(parent_path.parts)}_{entry.name}" if parent_path.parts else entry.name
                dest_file = dest_path / new_name
                
                # Create target directory structure
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                logging.debug(f"Copying file: {entry} -> {dest_file}")
                shutil.copy2(entry, dest_file)
                copied_count += 1
                
    except KeyboardInterrupt:
        logging.warning("Operation interrupted by user")
        return 0
                
    logging.info(f"File copy completed, {copied_count} files copied")
    return copied_count

def main():
    import argparse
    
    # Configure logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    parser = argparse.ArgumentParser(description='Recursively copy files while preserving directory hierarchy information')
    parser.add_argument('src_dir', help='Source directory path')
    parser.add_argument('dest_dir', help='Destination directory path')
    
    args = parser.parse_args()
    
    logging.info(f"Starting file copy, source directory: {args.src_dir}, target directory: {args.dest_dir}")
    copied_count = copy_files_with_hierarchy(args.src_dir, args.dest_dir)
    logging.info(f"Operation completed, {copied_count} files copied")

if __name__ == '__main__':
    main()
