# emeelan-els-kits/reset-kits.py
import json
import os
import shutil
from pathlib import Path

def get_root():
    return Path(__file__).parent

root = get_root()
kits_dir = root / 'my-els-kits'
app_dir = root / 'emeelan-els-app'
status_path = root / 'status.json'

def get_current_kit():
    if not status_path.exists():
        return ''
    with open(status_path) as f:
        data = json.load(f)
    return data.get('status', '')

def merge_directories(src, dst):
    for root_dir, dirs, files in os.walk(src):
        rel_root = os.path.relpath(root_dir, src)
        dst_root = dst / rel_root
        dst_root.mkdir(parents=True, exist_ok=True)
        for file_name in files:
            src_file = Path(root_dir) / file_name
            dst_file = dst_root / file_name
            shutil.copy2(src_file, dst_file)  # Overwrite for reset

def reset_kits():
    current_kit = get_current_kit()
    if not current_kit:
        print("No kit specified in status.json.")
        return
    
    kit_dir = kits_dir / current_kit
    if not kit_dir.exists():
        print(f"Kit {current_kit} not found.")
        return
    
    # For reset, we force overwrite but don't delete extra files
    merge_directories(kit_dir, app_dir)
    print(f"Reset emeelan-els-app to match {current_kit}.")

if __name__ == '__main__':
    reset_kits()