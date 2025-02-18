import os
import shutil
from pathlib import Path
from typing import Callable

def copy_files_with_hierarchy(
    src_dir: str,
    dest_dir: str,
    file_filter: Callable[[str], bool] = lambda f: f.endswith('.md')
) -> None:
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
        dest_path.mkdir(parents=True)
    
    for root, dirs, files in os.walk(src_dir):
        relative_path = Path(root).relative_to(src_dir)
        
        for file in files:
            if file_filter(file):
                src_file = Path(root) / file
                new_name = f"{'_'.join(relative_path.parts)}_{file}" if relative_path.parts else file
                dest_file = dest_path / new_name
                shutil.copy2(src_file, dest_file)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Recursively copy files while preserving directory hierarchy information')
    parser.add_argument('src_dir', help='Source directory path')
    parser.add_argument('dest_dir', help='Destination directory path')
    
    args = parser.parse_args()
    
    copy_files_with_hierarchy(args.src_dir, args.dest_dir)

if __name__ == '__main__':
    main()
