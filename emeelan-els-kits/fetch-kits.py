# emeelan-els-kits/fetch-kits.py
import json
from pathlib import Path

def get_root():
    return Path(__file__).parent

root = get_root()
kits_dir = root / 'my-els-kits'
status_path = root / 'status.json'

def get_all_kits():
    return sorted([p.name for p in kits_dir.iterdir() if p.is_dir()])

def get_current_kit():
    if not status_path.exists():
        return ''
    with open(status_path) as f:
        data = json.load(f)
    return data.get('status', '')

def update_status(new_status):
    with open(status_path, 'w') as f:
        json.dump({'status': new_status}, f)

def fetch_kits():
    current = get_current_kit()
    if current == '':
        all_kits = get_all_kits()
        if all_kits:
            update_status(all_kits[0])
            print(f"Updated status to {all_kits[0]}")
        else:
            print("No new kits found.")
    else:
        print("Status not empty, no update performed.")

if __name__ == '__main__':
    fetch_kits()