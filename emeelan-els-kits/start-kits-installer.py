"""
Professional-looking compact installer UI for EMEELAN ELS Kits.
- Modern compact layout using ttk styles
- Left: process steps list (status icons)
- Right: styled console/log with syntax-like highlighting and timestamps
- Bottom: sleek progress bar + compact action buttons with tooltips

Drop-in replacement for your previous start-kits-installer.py. It re-uses
existing helpers (get_all_kits, get_current_kit, update_status, etc.) and
assumes utils/software-installer.py and utils/setup-kit.py exist.

Notes:
- This is Tkinter (no external deps) but styled to look more professional.
- If you want a native installer look (NSIS/Windows MSI), that's a different
  approach; this remains a cross-platform GUI wrapper for your scripts.
"""

import json
import os
import re
import shutil
import subprocess
import threading
import sys
import time
from pathlib import Path
from tkinter import *
from tkinter import ttk, messagebox

# ---------------------- Paths & helpers ----------------------

def get_root():
    return Path(__file__).parent

root_dir = get_root()
kits_dir = root_dir / 'my-els-kits'
app_dir = root_dir / 'emeelan-els-app'
status_path = root_dir / 'status.json'


def get_all_kits():
    if not kits_dir.exists():
        return []
    return sorted([p.name for p in kits_dir.iterdir() if p.is_dir()])


def get_current_kit():
    if not status_path.exists():
        return ''
    try:
        with open(status_path) as f:
            data = json.load(f)
        return data.get('status', '')
    except Exception:
        return ''


def update_status(new_status):
    try:
        with open(status_path, 'w') as f:
            json.dump({'status': new_status}, f)
    except Exception as e:
        print(f"Failed to update status.json: {e}", file=sys.stderr)


# ---------------------- UI helpers ----------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 14
        y = self.widget.winfo_rooty() + 18
        self.tip = Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = Label(self.tip, text=self.text, justify='left', background='#ffffe0', relief='solid', borderwidth=1,
                    font=("Segoe UI", 9))
        lbl.pack(ipadx=6, ipady=4)

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class ConsoleLog:
    """Styled console logger using Text widget with tags for levels."""
    def __init__(self, text_widget):
        self.text = text_widget
        # configure tags
        monospace = ("Consolas", 10) if os.name == 'nt' else ("Courier New", 10)
        self.text.configure(font=monospace, padx=6, pady=6)
        self.text.tag_configure('info', foreground='#eaeaea')
        self.text.tag_configure('time', foreground='#9aa7b0')
        self.text.tag_configure('ok', foreground='#7bd389', font=(None, 10, 'bold'))
        self.text.tag_configure('warn', foreground='#ffb86b')
        self.text.tag_configure('err', foreground='#ff6b6b', font=(None, 10, 'bold'))
        self.text.tag_configure('cmd', foreground='#b5e0ff')
        self.text.tag_configure('bold', font=(None, 10, 'bold'))

    def timestamp(self):
        return time.strftime('%H:%M:%S')

    def write(self, msg, level='info'):
        if not msg:
            return
        ts = self.timestamp()
        try:
            self.text.configure(state=NORMAL)
            self.text.insert(END, f'[{ts}] ', ('time',))
            if level == 'info':
                self.text.insert(END, msg + '\n', ('info',))
            elif level == 'ok':
                self.text.insert(END, msg + '\n', ('ok',))
            elif level == 'warn':
                self.text.insert(END, msg + '\n', ('warn',))
            elif level == 'err':
                self.text.insert(END, msg + '\n', ('err',))
            elif level == 'cmd':
                self.text.insert(END, msg + '\n', ('cmd',))
            else:
                self.text.insert(END, msg + '\n')
            self.text.see(END)
            self.text.configure(state=DISABLED)
        except Exception:
            print(msg)


# ---------------------- Installer UI ----------------------
class ProInstallerUI:
    def __init__(self):
        self.window = Tk()
        self.window.title('EMEELAN Installer — Compact')
        # compact but readable size
        self.window.geometry('820x520')
        self.window.resizable(False, False)

        # style
        style = ttk.Style(self.window)
        style.theme_use('clam')
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Step.TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'))

        # main frames
        top = Frame(self.window, padx=12, pady=8)
        top.pack(fill=X)

        ttk.Label(top, text='EMEELAN ELS Kits Installer', style='Header.TLabel').pack(anchor=W)
        # Keep the subtitle as a regular tk.Label (so you can keep fg and font options if desired)
        Label(top, text='Professional installer view — compact and informative', font=('Segoe UI', 9), fg='#6b7280').pack(anchor=W)
        # middle: left steps, right console

        middle = Frame(self.window, padx=12, pady=6)
        middle.pack(fill=BOTH, expand=True)

        # left column: steps
        left = Frame(middle, width=260)
        left.pack(side=LEFT, fill=Y)
        left.pack_propagate(False)

        steps_label = Label(left, text='Steps', font=('Segoe UI', 11, 'bold'))
        steps_label.pack(anchor=W, pady=(0,6))

        # Treeview for steps
        self.step_tree = ttk.Treeview(left, columns=('status',), show='tree', selectmode='none', height=18)
        self.step_tree.pack(fill=Y, expand=True)
        # We'll insert items with tags; tags styled via tag_configure on the underlying widget

        # right column: console
        right = Frame(middle)
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        console_label = Label(right, text='Console / Log', font=('Segoe UI', 11, 'bold'))
        console_label.pack(anchor=W)

        console_box = Text(right, height=22, bg='#0f1724', fg='#e6eef8', relief='flat')
        console_box.pack(fill=BOTH, expand=True, padx=(6,0), pady=(6,0))
        console_box.configure(state=DISABLED)

        # attach logger
        self.logger = ConsoleLog(console_box)

        # bottom: progress + buttons
         # bottom: progress + buttons (fixed right column so buttons don't get clipped)
        bottom = Frame(self.window, padx=12, pady=8)
        bottom.pack(fill=X)

        # Left: progress area (expands)
        progress_container = Frame(bottom)
        progress_container.pack(side=LEFT, fill=X, expand=True)

        self.progress = ttk.Progressbar(progress_container, orient='horizontal',
                                        mode='determinate', length=520)
        self.progress.pack(fill=X, padx=(0,8), pady=(4,4))

        self.progress_label = Label(progress_container, text='0%', width=6,
                                    font=('Segoe UI', 10, 'bold'))
        # align the percent to the right inside the progress container
        self.progress_label.pack(anchor=E)

        # Right: fixed-width button column so buttons remain visible and do not get clipped
        btn_frame = Frame(bottom, width=220)
        btn_frame.pack(side=RIGHT, fill=Y)
        btn_frame.pack_propagate(False)  # keep width and allow internal widgets to size

        # helper to create compact ttk button + tooltip (clean look)
        def compact_btn(text, cmd, tip):
            b = ttk.Button(btn_frame, text=text, command=cmd)
            b.pack(fill=X, pady=6, padx=8)  # full width of btn_frame, spaced vertically
            ToolTip(b, tip)
            return b

        # compact buttons (use ttk for consistent modern style)
        self.start_button = compact_btn('Start Installation', self.start_install,
                                        'Checks/installs software, builds app and updates kit status.')
        self.software_button = compact_btn('Install Software Only', self.install_software_only,
                                           'Installs Node, JDK, Android SDK, Gradle, VS Code.')
        self.reset_button = compact_btn('Reset Current Kit', self.reset_kit,
                                        'Reset to the kit in status.json')
        self.vscode_button = compact_btn('Open in VS Code', self.open_vscode,
                                         'Open the project in VS Code')
        self.adb_button = compact_btn('Check ADB Devices', self.check_adb_devices,
                                      'List connected devices and emulators')
        self.emu_button = compact_btn('Start Emulator', self.start_emulator,
                                      'Start an installed emulator (optional)')
        # internal state
        self.steps = [
            ('check_software', 'Check prerequisites'),
            ('install_software', 'Install missing software'),
            ('merge_files', 'Merge kit files'),
            ('npm_deps', 'Install project dependencies'),
            ('react_build', 'Build React application'),
            ('cap_add', 'Add Android platform'),
            ('cap_sync', 'Capacitor sync'),
            ('apk_build', 'Build Android APK'),
            ('update_status', 'Update kit status'),
            ('post_tasks', 'Finalizing / optional tasks')
        ]

        # populate tree
        for key, label in self.steps:
            self.step_tree.insert('', 'end', iid=key, text=f'  {label}', tags=('pending',))

        # configure tag colors by using tag_bind and item styling hacks
        # Treeview doesn't directly support per-tag foreground without images, but we can change the whole item text
        # We'll update item text with prefixed icons: ⏳, ✅, ❌, ⚠

        # start main window
        self.update_progress(0, 'Idle')
        self.window.protocol('WM_DELETE_WINDOW', self.on_close)
        self.window.mainloop()

    # ------------------- UI helpers -------------------
    def set_step(self, key, status):
        """status in: pending, running, done, failed, warn"""
        icon = {
            'pending': '⏳',
            'running': '▶',
            'done': '✅',
            'failed': '❌',
            'warn': '⚠'
        }.get(status, '⏳')
        text = self.step_tree.item(key, 'text')
        # remove existing icon and replace
        # text stored like '  Label' so we use that label portion
        label = text.strip()
        self.step_tree.item(key, text=f' {icon} {label}')

    def write_log(self, msg, level='info'):
        self.logger.write(msg, level=level)

    def update_progress(self, val, status=''):
        try:
            self.progress['value'] = int(val)
            self.progress_label.config(text=f"{int(val)}%")
            if status:
                # show a short status in console as well
                self.write_log(status, 'info')
        except Exception:
            pass

    def _set_buttons(self, state):
        for b in (self.start_button, self.software_button, self.reset_button, self.vscode_button, self.adb_button, self.emu_button):
            try:
                b.config(state=state)
            except Exception:
                pass

    def on_close(self):
        # graceful shutdown
        if messagebox.askyesno('Quit', 'Are you sure you want to quit the installer?'):
            try:
                self.window.destroy()
            except Exception:
                sys.exit(0)

    # ------------------- Actions -------------------
    def open_vscode(self):
        try:
            subprocess.Popen(['code', str(app_dir)], shell=True)
            self.write_log('Opening VS Code...', 'ok')
        except Exception as e:
            self.write_log(f'Failed to open VS Code: {e}', 'err')

    def check_adb_devices(self):
        def worker():
            self._set_buttons('disabled')
            self.write_log('Checking for ADB...', 'info')
            try:
                adb = None
                for candidate in (os.path.join(os.environ.get('ANDROID_HOME', ''), 'platform-tools', 'adb'),
                                  os.path.join(os.environ.get('ANDROID_SDK_ROOT', ''), 'platform-tools', 'adb'),
                                  'adb'):
                    try:
                        rc = subprocess.run([candidate, 'devices'], capture_output=True, text=True, timeout=8)
                        if rc.returncode == 0:
                            adb = candidate
                            break
                    except Exception:
                        continue
                if adb:
                    self.write_log(f'ADB found: {adb}', 'ok')
                    rc = subprocess.run([adb, 'devices'], capture_output=True, text=True, timeout=15)
                    self.write_log(rc.stdout.strip(), 'info')
                else:
                    self.write_log('ADB not found. Run Install Software Only to install Android SDK.', 'warn')
            except Exception as e:
                self.write_log(f'Error checking ADB: {e}', 'err')
            finally:
                self._set_buttons('normal')

        threading.Thread(target=worker, daemon=True).start()

    def start_emulator(self):
        def worker():
            self._set_buttons('disabled')
            self.write_log('Attempting to start emulator...', 'info')
            try:
                emulator_cmds = [
                    os.path.join(os.environ.get('ANDROID_HOME', ''), 'emulator', 'emulator'),
                    os.path.join(os.environ.get('ANDROID_SDK_ROOT', ''), 'emulator', 'emulator'),
                    'emulator'
                ]
                started = False
                for cmd in emulator_cmds:
                    try:
                        full = f'{cmd} -avd Pixel_6 -no-snapshot-load -no-boot-anim'
                        subprocess.Popen(full, shell=True)
                        started = True
                        break
                    except Exception:
                        continue
                if started:
                    self.write_log('Emulator started (background)', 'ok')
                else:
                    self.write_log('No emulator binary found. Install Android SDK or configure AVD.', 'warn')
            except Exception as e:
                self.write_log(f'Emulator error: {e}', 'err')
            finally:
                self._set_buttons('normal')

        threading.Thread(target=worker, daemon=True).start()

    # synchronous software installer call used by Start Installation
    def _install_software_sync(self):
        software_script = root_dir / 'utils' / 'software-installer.py'
        if not software_script.exists():
            self.write_log('software-installer.py not found in utils/', 'err')
            return False
        self.write_log('Running software installer (requires elevation) ...', 'info')

        status_file = Path(r"C:\DevInstaller\install_status.json")
        log_file = Path(r"C:\DevInstaller\install_log.txt")

        pre_time = time.time()
        pre_mtime = os.path.getmtime(status_file) if status_file.exists() else 0
        pre_log_size = os.path.getsize(log_file) if log_file.exists() else 0

        proc = subprocess.run([sys.executable, str(software_script)], capture_output=True, text=True, cwd=root_dir, timeout=1800)
        if proc.stdout:
            for line in proc.stdout.splitlines():
                self.write_log(line, 'info')
        if proc.stderr:
            self.write_log(proc.stderr, 'err')

        elevated = 'UAC prompt opened' in proc.stdout

        if not elevated:
            return proc.returncode == 0

        # Poll for elevated completion
        self.write_log('Elevated installer running, waiting for completion...', 'info')
        timeout = 1800
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(5)
            # Append new log lines
            if log_file.exists():
                with open(log_file, 'r') as f:
                    f.seek(pre_log_size)
                    new_lines = f.read()
                    if new_lines:
                        for line in new_lines.splitlines():
                            self.write_log(line, 'info')
                        pre_log_size = os.path.getsize(log_file)
            if status_file.exists() and os.path.getmtime(status_file) > pre_mtime:
                with open(status_file) as f:
                    data = json.load(f)
                if data.get('complete'):
                    success = data.get('success', False)
                    self.write_log(f'Installer completed with success: {success}', 'ok' if success else 'err')
                    # Read remaining log
                    if log_file.exists():
                        with open(log_file, 'r') as f:
                            f.seek(pre_log_size)
                            rem = f.read()
                            if rem:
                                for line in rem.splitlines():
                                    self.write_log(line, 'info')
                    return success
        self.write_log('Timeout waiting for elevated installer', 'err')
        return False

    # install software only (async, UI friendly)
    def install_software_only(self):
        def worker():
            self._set_buttons('disabled')
            self.set_step('check_software', 'running')
            ok = self._install_software_sync()
            self.set_step('check_software', 'done' if ok else 'failed')
            self._set_buttons('normal')
            if ok:
                messagebox.showinfo('Success', 'Software installed successfully')
        threading.Thread(target=worker, daemon=True).start()

    def reset_kit(self):
        def worker():
            self._set_buttons('disabled')
            self.write_log('Resetting current kit...', 'info')
            try:
                reset_script = root_dir / 'reset-kits.py'
                if not reset_script.exists():
                    self.write_log('reset-kits.py not found.', 'err')
                    self._set_buttons('normal')
                    return
                proc = subprocess.run([sys.executable, str(reset_script)], capture_output=True, text=True, cwd=root_dir)
                if proc.stdout:
                    self.write_log(proc.stdout, 'info')
                if proc.returncode == 0:
                    self.write_log('Kit reset successful', 'ok')
                    messagebox.showinfo('Reset', 'Kit reset completed successfully')
                else:
                    self.write_log('Kit reset failed', 'err')
            except Exception as e:
                self.write_log(f'Reset error: {e}', 'err')
            finally:
                self._set_buttons('normal')
        threading.Thread(target=worker, daemon=True).start()

    # ------------------- Start Installation Flow -------------------
    def start_install(self):
        """Start full installation flow (runs in background thread)."""
        def worker():
            current = get_current_kit()
            if not current:
                self.write_log('No current kit in status.json', 'err')
                return

            self._set_buttons('disabled')

            # reset steps display
            for key, _ in self.steps:
                self.set_step(key, 'pending')

            self.update_progress(2, 'Beginning installation')

            # 1) Check & install software
            self.set_step('check_software', 'running')
            ok = self._install_software_sync()
            self.set_step('check_software', 'done' if ok else 'failed')
            self.set_step('install_software', 'done' if ok else 'failed')
            if not ok:
                self.write_log('Required software not installed. Aborting.', 'err')
                self._set_buttons('normal')
                return

            # 3) Run setup-kit.py (Capacitor build + APK)
            self.set_step('merge_files', 'running')
            self.update_progress(40, 'Running kit setup (build)')
            setup_script = root_dir / 'utils' / 'setup-kit.py'
            if not setup_script.exists():
                self.write_log('setup-kit.py not found in utils/', 'err')
                self.set_step('merge_files', 'failed')
                self._set_buttons('normal')
                return

            # prepare progress mapping and state flags
            progress_map = {
                'merging': 25,
                'npm': 35,
                'react': 45,
                'adding android': 50,
                'syncing': 55,
                'building android': 60,
                'capacitor': 50,
                'gradle': 60,
                'assemble': 70,
                '.apk': 82,
                'signing': 88,
                'apk generated': 92,
                'build successful': 94
            }
            cur_progress = 40
            last_time = time.time()

            apk_filename = None
            apk_src_path = None
            build_detected = False
            final_success = False

            try:
                proc = subprocess.Popen(
                    [sys.executable, str(setup_script)],
                    cwd=str(root_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                for raw_line in proc.stdout:
                    ln = raw_line.rstrip()
                    if not ln:
                        continue
                    self.write_log(ln, 'info')
                    low = ln.lower()

                    # capture explicit APK creation line, e.g.:
                    # "SUCCESS: APK created: els-starterkit-1-1.0.0-db.apk"
                    m_apk = re.search(r'apk created[: ]+\s*([^\s]+\.apk)', ln, re.IGNORECASE)
                    if m_apk:
                        apk_filename = m_apk.group(1).strip()
                        build_detected = True
                        # bump progress and record
                        cur_progress = max(cur_progress + 15, 82)
                        cur_progress = min(cur_progress, 92)
                        self.update_progress(cur_progress, 'APK created')
                        # attempt to find actual file path in repo (best-effort)
                        try:
                            for p in root_dir.rglob(apk_filename):
                                apk_src_path = p
                                break
                            if apk_src_path:
                                self.write_log(f'Found APK at: {apk_src_path}', 'info')
                            else:
                                self.write_log(f'APK filename detected ({apk_filename}) but file not found in repo', 'warn')
                        except Exception as _:
                            pass
                        continue

                    # detect JSON success lines like {"success": true, "message": "..."}
                    if '"success": true' in low or 'setup completed successfully' in low:
                        final_success = True
                        cur_progress = max(cur_progress, 92)
                        self.update_progress(cur_progress, 'Setup reported success')
                        continue

                    # APK installation on emulator failed — treat as warning
                    if 'apk installation failed' in low:
                        self.write_log('APK installation on emulator failed (warning, continuing).', 'warn')
                        cur_progress = max(cur_progress, 88)
                        self.update_progress(cur_progress, 'APK built (emulator install failed)')
                        continue

                    # percent printed by script (e.g., "50%")
                    m_pct = re.search(r'(\d{1,3})\s*%', ln)
                    if m_pct:
                        try:
                            val = int(m_pct.group(1))
                            if 0 <= val <= 99 and val > cur_progress:
                                if val - cur_progress > 25:
                                    val = cur_progress + 25
                                cur_progress = val
                                self.update_progress(cur_progress, f'Build {cur_progress}%')
                        except Exception:
                            pass
                        continue

                    # other keyword nudges
                    for k, v in progress_map.items():
                        if k in low and v > cur_progress:
                            step = min(cur_progress + 18, v)
                            cur_progress = step
                            self.update_progress(cur_progress, f'{k}...')
                            break

                    # gentle fallback tick
                    if time.time() - last_time > 6 and cur_progress < 80:
                        last_time = time.time()
                        cur_progress += 3
                        self.update_progress(cur_progress, 'Working...')

                    # Add step updates
                    if 'merging kit files' in low:
                        self.set_step('merge_files', 'running')
                    elif 'merged' in low and 'files successfully' in low:
                        self.set_step('merge_files', 'done')
                    elif 'npm dependencies' in low:
                        self.set_step('npm_deps', 'running')
                    elif 'npm dependencies completed successfully' in low:
                        self.set_step('npm_deps', 'done')
                    elif 'react application' in low:
                        self.set_step('react_build', 'running')
                    elif 'react application completed successfully' in low:
                        self.set_step('react_build', 'done')
                    elif 'adding android platform' in low:
                        self.set_step('cap_add', 'running')
                    elif 'adding android platform completed successfully' in low:
                        self.set_step('cap_add', 'done')
                    elif 'syncing capacitor' in low:
                        self.set_step('cap_sync', 'running')
                    elif 'syncing capacitor completed successfully' in low:
                        self.set_step('cap_sync', 'done')
                    elif 'building android apk' in low:
                        self.set_step('apk_build', 'running')
                    elif 'apk build completed successfully' in low:
                        self.set_step('apk_build', 'done')
                    elif 'error' in low:
                        # Set current step to failed if possible
                        pass  # Can add logic if needed

                # wait and evaluate outcome
                proc.wait()
                rc = proc.returncode

                succeeded = final_success or (rc == 0)

                if succeeded:
                    self.set_step('apk_build', 'done')
                    self.update_progress(95, 'Finalizing...')

                    # COPY APK to my-els-apk folder if we found it; otherwise just inform filename if known
                    try:
                        apk_dest_folder = root_dir / 'my-els-apk'
                        if apk_filename:
                            # if we located the real file path, copy from there; otherwise try to search by name
                            if not apk_src_path:
                                for p in root_dir.rglob(apk_filename):
                                    apk_src_path = p
                                    break
                            if apk_src_path and apk_src_path.exists():
                                apk_dest_folder.mkdir(exist_ok=True)
                                dest = apk_dest_folder / apk_filename
                                try:
                                    shutil.copy2(str(apk_src_path), str(dest))
                                    self.write_log(f'APK copied to: {dest}', 'ok')
                                    apk_final_location = dest
                                except Exception as ce:
                                    self.write_log(f'Failed to copy APK: {ce}', 'warn')
                                    apk_final_location = apk_src_path
                            else:
                                # not found — still inform user about detected filename
                                self.write_log(f'APK filename: {apk_filename} (file not found to copy)', 'warn')
                                apk_final_location = None
                        else:
                            apk_final_location = None
                    except Exception as e:
                        apk_final_location = None
                        self.write_log(f'Error handling APK file: {e}', 'warn')

                    # update status.json to next kit
                    all_kits = get_all_kits()
                    try:
                        idx = all_kits.index(current)
                    except ValueError:
                        idx = -1
                    next_kit = all_kits[idx + 1] if (idx != -1 and idx + 1 < len(all_kits)) else ''
                    update_status(next_kit)
                    self.write_log(f'Updated status to: {next_kit if next_kit else "None"}', 'ok')
                    self.set_step('update_status', 'done')

                    # finalize UI
                    self.update_progress(100, 'Installation completed successfully!')
                    self.set_step('post_tasks', 'done')
                    self.write_log('Installation completed successfully!', 'ok')

                    # explicit message to user about APK location
                    try:
                        if apk_final_location:
                            msg = f'APK created and copied to: {apk_final_location}\\n\\nYou can find your APK in the folder: {apk_final_location.parent}'
                            self.write_log(msg, 'ok')
                            try:
                                messagebox.showinfo('Success', f'Installation complete.\\nAPK copied to:\\n{apk_final_location}')
                            except Exception:
                                pass
                        elif apk_filename:
                            # filename known but not copied
                            self.write_log(f'APK filename: {apk_filename}. Check your build outputs.', 'ok')
                            try:
                                messagebox.showinfo('Success', f'Installation complete. APK: {apk_filename} (not copied).')
                            except Exception:
                                pass
                        else:
                            # no info about apk
                            self.write_log('Installation complete. APK location not detected automatically.', 'ok')
                            try:
                                messagebox.showinfo('Success', 'Installation complete. APK location not detected automatically.')
                            except Exception:
                                pass
                    except Exception:
                        pass

                    # launch optional tasks (non-blocking)
                    try:
                        threading.Thread(target=self.start_emulator, daemon=True).start()
                    except Exception as emu_err:
                        self.write_log(f'Emulator start failed: {emu_err}', 'warn')
                    try:
                        self.open_vscode()
                    except Exception:
                        pass

                    self._set_buttons('normal')

                else:
                    # failed
                    try:
                        rem = proc.stdout.read()
                        if rem:
                            self.write_log(rem, 'info')
                    except Exception:
                        pass
                    self.set_step('apk_build', 'failed')
                    self.write_log(f'setup-kit.py failed (rc={rc}).', 'err')
                    try:
                        messagebox.showerror('Error', f'Setup script failed (rc={rc}). See log for details.')
                    except Exception:
                        pass
                    self._set_buttons('normal')

            except Exception as e:
                self.set_step('apk_build', 'failed')
                self.write_log(f'Error running setup-kit.py: {e}', 'err')
                self._set_buttons('normal')
                return

        # run worker in background
        threading.Thread(target=worker, daemon=True).start()

if __name__ == '__main__':
    ProInstallerUI()

# """
# Professional-looking compact installer UI for EMEELAN ELS Kits.
# - Modern compact layout using ttk styles
# - Left: process steps list (status icons)
# - Right: styled console/log with syntax-like highlighting and timestamps
# - Bottom: sleek progress bar + compact action buttons with tooltips

# Drop-in replacement for your previous start-kits-installer.py. It re-uses
# existing helpers (get_all_kits, get_current_kit, update_status, etc.) and
# assumes utils/software-installer.py and utils/setup-kit.py exist.

# Notes:
# - This is Tkinter (no external deps) but styled to look more professional.
# - If you want a native installer look (NSIS/Windows MSI), that's a different
#   approach; this remains a cross-platform GUI wrapper for your scripts.
# """

# import json
# import os
# import subprocess
# import threading
# import sys
# import time
# from pathlib import Path
# from tkinter import *
# from tkinter import ttk, messagebox

# # ---------------------- Paths & helpers ----------------------

# def get_root():
#     return Path(__file__).parent

# root_dir = get_root()
# kits_dir = root_dir / 'my-els-kits'
# app_dir = root_dir / 'emeelan-els-app'
# status_path = root_dir / 'status.json'


# def get_all_kits():
#     if not kits_dir.exists():
#         return []
#     return sorted([p.name for p in kits_dir.iterdir() if p.is_dir()])


# def get_current_kit():
#     if not status_path.exists():
#         return ''
#     try:
#         with open(status_path) as f:
#             data = json.load(f)
#         return data.get('status', '')
#     except Exception:
#         return ''


# def update_status(new_status):
#     try:
#         with open(status_path, 'w') as f:
#             json.dump({'status': new_status}, f)
#     except Exception as e:
#         print(f"Failed to update status.json: {e}", file=sys.stderr)


# # ---------------------- UI helpers ----------------------
# class ToolTip:
#     def __init__(self, widget, text):
#         self.widget = widget
#         self.text = text
#         self.tip = None
#         widget.bind("<Enter>", self.show)
#         widget.bind("<Leave>", self.hide)

#     def show(self, event=None):
#         if self.tip or not self.text:
#             return
#         x = self.widget.winfo_rootx() + 14
#         y = self.widget.winfo_rooty() + 18
#         self.tip = Toplevel(self.widget)
#         self.tip.wm_overrideredirect(True)
#         self.tip.wm_geometry(f"+{x}+{y}")
#         lbl = Label(self.tip, text=self.text, justify='left', background='#ffffe0', relief='solid', borderwidth=1,
#                     font=("Segoe UI", 9))
#         lbl.pack(ipadx=6, ipady=4)

#     def hide(self, event=None):
#         if self.tip:
#             self.tip.destroy()
#             self.tip = None


# class ConsoleLog:
#     """Styled console logger using Text widget with tags for levels."""
#     def __init__(self, text_widget):
#         self.text = text_widget
#         # configure tags
#         monospace = ("Consolas", 10) if os.name == 'nt' else ("Courier New", 10)
#         self.text.configure(font=monospace, padx=6, pady=6)
#         self.text.tag_configure('info', foreground='#eaeaea')
#         self.text.tag_configure('time', foreground='#9aa7b0')
#         self.text.tag_configure('ok', foreground='#7bd389', font=(None, 10, 'bold'))
#         self.text.tag_configure('warn', foreground='#ffb86b')
#         self.text.tag_configure('err', foreground='#ff6b6b', font=(None, 10, 'bold'))
#         self.text.tag_configure('cmd', foreground='#b5e0ff')
#         self.text.tag_configure('bold', font=(None, 10, 'bold'))

#     def timestamp(self):
#         return time.strftime('%H:%M:%S')

#     def write(self, msg, level='info'):
#         if not msg:
#             return
#         ts = self.timestamp()
#         try:
#             self.text.configure(state=NORMAL)
#             self.text.insert(END, f'[{ts}] ', ('time',))
#             if level == 'info':
#                 self.text.insert(END, msg + '\n', ('info',))
#             elif level == 'ok':
#                 self.text.insert(END, msg + '\n', ('ok',))
#             elif level == 'warn':
#                 self.text.insert(END, msg + '\n', ('warn',))
#             elif level == 'err':
#                 self.text.insert(END, msg + '\n', ('err',))
#             elif level == 'cmd':
#                 self.text.insert(END, msg + '\n', ('cmd',))
#             else:
#                 self.text.insert(END, msg + '\n')
#             self.text.see(END)
#             self.text.configure(state=DISABLED)
#         except Exception:
#             print(msg)


# # ---------------------- Installer UI ----------------------
# class ProInstallerUI:
#     def __init__(self):
#         self.window = Tk()
#         self.window.title('EMEELAN Installer — Compact')
#         # compact but readable size
#         self.window.geometry('820x520')
#         self.window.resizable(False, False)

#         # style
#         style = ttk.Style(self.window)
#         style.theme_use('clam')
#         style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
#         style.configure('Step.TLabel', font=('Segoe UI', 10))
#         style.configure('TButton', font=('Segoe UI', 10, 'bold'))

#         # main frames
#         top = Frame(self.window, padx=12, pady=8)
#         top.pack(fill=X)

#         ttk.Label(top, text='EMEELAN ELS Kits Installer', style='Header.TLabel').pack(anchor=W)
#         # Keep the subtitle as a regular tk.Label (so you can keep fg and font options if desired)
#         Label(top, text='Professional installer view — compact and informative', font=('Segoe UI', 9), fg='#6b7280').pack(anchor=W)
#         # middle: left steps, right console

#         middle = Frame(self.window, padx=12, pady=6)
#         middle.pack(fill=BOTH, expand=True)

#         # left column: steps
#         left = Frame(middle, width=260)
#         left.pack(side=LEFT, fill=Y)
#         left.pack_propagate(False)

#         steps_label = Label(left, text='Steps', font=('Segoe UI', 11, 'bold'))
#         steps_label.pack(anchor=W, pady=(0,6))

#         # Treeview for steps
#         self.step_tree = ttk.Treeview(left, columns=('status',), show='tree', selectmode='none', height=18)
#         self.step_tree.pack(fill=Y, expand=True)
#         # We'll insert items with tags; tags styled via tag_configure on the underlying widget

#         # right column: console
#         right = Frame(middle)
#         right.pack(side=RIGHT, fill=BOTH, expand=True)

#         console_label = Label(right, text='Console / Log', font=('Segoe UI', 11, 'bold'))
#         console_label.pack(anchor=W)

#         console_box = Text(right, height=22, bg='#0f1724', fg='#e6eef8', relief='flat')
#         console_box.pack(fill=BOTH, expand=True, padx=(6,0), pady=(6,0))
#         console_box.configure(state=DISABLED)

#         # attach logger
#         self.logger = ConsoleLog(console_box)

#         # bottom: progress + buttons
#          # bottom: progress + buttons (fixed right column so buttons don't get clipped)
#         bottom = Frame(self.window, padx=12, pady=8)
#         bottom.pack(fill=X)

#         # Left: progress area (expands)
#         progress_container = Frame(bottom)
#         progress_container.pack(side=LEFT, fill=X, expand=True)

#         self.progress = ttk.Progressbar(progress_container, orient='horizontal',
#                                         mode='determinate', length=520)
#         self.progress.pack(fill=X, padx=(0,8), pady=(4,4))

#         self.progress_label = Label(progress_container, text='0%', width=6,
#                                     font=('Segoe UI', 10, 'bold'))
#         # align the percent to the right inside the progress container
#         self.progress_label.pack(anchor=E)

#         # Right: fixed-width button column so buttons remain visible and do not get clipped
#         btn_frame = Frame(bottom, width=220)
#         btn_frame.pack(side=RIGHT, fill=Y)
#         btn_frame.pack_propagate(False)  # keep width and allow internal widgets to size

#         # helper to create compact ttk button + tooltip (clean look)
#         def compact_btn(text, cmd, tip):
#             b = ttk.Button(btn_frame, text=text, command=cmd)
#             b.pack(fill=X, pady=6, padx=8)  # full width of btn_frame, spaced vertically
#             ToolTip(b, tip)
#             return b

#         # compact buttons (use ttk for consistent modern style)
#         self.start_button = compact_btn('Start Installation', self.start_install,
#                                         'Checks/installs software, builds app and updates kit status.')
#         self.software_button = compact_btn('Install Software Only', self.install_software_only,
#                                            'Installs Node, JDK, Android SDK, Gradle, VS Code.')
#         self.reset_button = compact_btn('Reset Current Kit', self.reset_kit,
#                                         'Reset to the kit in status.json')
#         self.vscode_button = compact_btn('Open in VS Code', self.open_vscode,
#                                          'Open the project in VS Code')
#         self.adb_button = compact_btn('Check ADB Devices', self.check_adb_devices,
#                                       'List connected devices and emulators')
#         self.emu_button = compact_btn('Start Emulator', self.start_emulator,
#                                       'Start an installed emulator (optional)')
#         # internal state
#         self.steps = [
#             ('check_software', 'Check prerequisites'),
#             ('install_software', 'Install missing software'),
#             ('npm_deps', 'Install project dependencies (npm/yarn)'),
#             ('capacitor_init', 'Capacitor init/build'),
#             ('gradle_build', 'Gradle assemble'),
#             ('signing', 'Signing / APK generation'),
#             ('update_status', 'Update kit status'),
#             ('post_tasks', 'Finalizing / optional tasks')
#         ]

#         # populate tree
#         for key, label in self.steps:
#             self.step_tree.insert('', 'end', iid=key, text=f'  {label}', tags=('pending',))

#         # configure tag colors by using tag_bind and item styling hacks
#         # Treeview doesn't directly support per-tag foreground without images, but we can change the whole item text
#         # We'll update item text with prefixed icons: ⏳, ✅, ❌, ⚠

#         # start main window
#         self.update_progress(0, 'Idle')
#         self.window.protocol('WM_DELETE_WINDOW', self.on_close)
#         self.window.mainloop()

#     # ------------------- UI helpers -------------------
#     def set_step(self, key, status):
#         """status in: pending, running, done, failed, warn"""
#         icon = {
#             'pending': '⏳',
#             'running': '▶',
#             'done': '✅',
#             'failed': '❌',
#             'warn': '⚠'
#         }.get(status, '⏳')
#         text = self.step_tree.item(key, 'text')
#         # remove existing icon and replace
#         # text stored like '  Label' so we use that label portion
#         label = text.strip()
#         self.step_tree.item(key, text=f' {icon} {label}')

#     def write_log(self, msg, level='info'):
#         self.logger.write(msg, level=level)

#     def update_progress(self, val, status=''):
#         try:
#             self.progress['value'] = int(val)
#             self.progress_label.config(text=f"{int(val)}%")
#             if status:
#                 # show a short status in console as well
#                 self.write_log(status, 'info')
#         except Exception:
#             pass

#     def _set_buttons(self, state):
#         for b in (self.start_button, self.software_button, self.reset_button, self.vscode_button, self.adb_button, self.emu_button):
#             try:
#                 b.config(state=state)
#             except Exception:
#                 pass

#     def on_close(self):
#         # graceful shutdown
#         if messagebox.askyesno('Quit', 'Are you sure you want to quit the installer?'):
#             try:
#                 self.window.destroy()
#             except Exception:
#                 sys.exit(0)

#     # ------------------- Actions -------------------
#     def open_vscode(self):
#         try:
#             subprocess.Popen(['code', str(app_dir)], shell=True)
#             self.write_log('Opening VS Code...', 'ok')
#         except Exception as e:
#             self.write_log(f'Failed to open VS Code: {e}', 'err')

#     def check_adb_devices(self):
#         def worker():
#             self._set_buttons('disabled')
#             self.write_log('Checking for ADB...', 'info')
#             try:
#                 adb = None
#                 for candidate in (os.path.join(os.environ.get('ANDROID_HOME', ''), 'platform-tools', 'adb'),
#                                   os.path.join(os.environ.get('ANDROID_SDK_ROOT', ''), 'platform-tools', 'adb'),
#                                   'adb'):
#                     try:
#                         rc = subprocess.run([candidate, 'devices'], capture_output=True, text=True, timeout=8)
#                         if rc.returncode == 0:
#                             adb = candidate
#                             break
#                     except Exception:
#                         continue
#                 if adb:
#                     self.write_log(f'ADB found: {adb}', 'ok')
#                     rc = subprocess.run([adb, 'devices'], capture_output=True, text=True, timeout=15)
#                     self.write_log(rc.stdout.strip(), 'info')
#                 else:
#                     self.write_log('ADB not found. Run Install Software Only to install Android SDK.', 'warn')
#             except Exception as e:
#                 self.write_log(f'Error checking ADB: {e}', 'err')
#             finally:
#                 self._set_buttons('normal')

#         threading.Thread(target=worker, daemon=True).start()

#     def start_emulator(self):
#         def worker():
#             self._set_buttons('disabled')
#             self.write_log('Attempting to start emulator...', 'info')
#             try:
#                 emulator_cmds = [
#                     os.path.join(os.environ.get('ANDROID_HOME', ''), 'emulator', 'emulator'),
#                     os.path.join(os.environ.get('ANDROID_SDK_ROOT', ''), 'emulator', 'emulator'),
#                     'emulator'
#                 ]
#                 started = False
#                 for cmd in emulator_cmds:
#                     try:
#                         full = f'{cmd} -avd Pixel_6 -no-snapshot-load -no-boot-anim'
#                         subprocess.Popen(full, shell=True)
#                         started = True
#                         break
#                     except Exception:
#                         continue
#                 if started:
#                     self.write_log('Emulator started (background)', 'ok')
#                 else:
#                     self.write_log('No emulator binary found. Install Android SDK or configure AVD.', 'warn')
#             except Exception as e:
#                 self.write_log(f'Emulator error: {e}', 'err')
#             finally:
#                 self._set_buttons('normal')

#         threading.Thread(target=worker, daemon=True).start()

#     # synchronous software installer call used by Start Installation
#     def _install_software_sync(self):
#         software_script = root_dir / 'utils' / 'software-installer.py'
#         if not software_script.exists():
#             self.write_log('software-installer.py not found in utils/', 'err')
#             return False
#         self.write_log('Running software installer (requires elevation) ...', 'info')
#         try:
#             proc = subprocess.run([sys.executable, str(software_script)], capture_output=True, text=True, cwd=root_dir, timeout=1800)
#             if proc.stdout:
#                 for line in proc.stdout.splitlines():
#                     self.write_log(line, 'info')
#             if proc.stderr:
#                 self.write_log(proc.stderr, 'err')
#             return proc.returncode == 0
#         except subprocess.TimeoutExpired:
#             self.write_log('Software installer timed out.', 'err')
#             return False
#         except Exception as e:
#             self.write_log(f'Software installer failed: {e}', 'err')
#             return False

#     # install software only (async, UI friendly)
#     def install_software_only(self):
#         def worker():
#             self._set_buttons('disabled')
#             self.set_step('check_software', 'running')
#             ok = self._install_software_sync()
#             self.set_step('check_software', 'done' if ok else 'failed')
#             self._set_buttons('normal')
#             if ok:
#                 messagebox.showinfo('Success', 'Software installed successfully')
#         threading.Thread(target=worker, daemon=True).start()

#     def reset_kit(self):
#         def worker():
#             self._set_buttons('disabled')
#             self.write_log('Resetting current kit...', 'info')
#             try:
#                 reset_script = root_dir / 'reset-kits.py'
#                 if not reset_script.exists():
#                     self.write_log('reset-kits.py not found.', 'err')
#                     self._set_buttons('normal')
#                     return
#                 proc = subprocess.run([sys.executable, str(reset_script)], capture_output=True, text=True, cwd=root_dir)
#                 if proc.stdout:
#                     self.write_log(proc.stdout, 'info')
#                 if proc.returncode == 0:
#                     self.write_log('Kit reset successful', 'ok')
#                     messagebox.showinfo('Reset', 'Kit reset completed successfully')
#                 else:
#                     self.write_log('Kit reset failed', 'err')
#             except Exception as e:
#                 self.write_log(f'Reset error: {e}', 'err')
#             finally:
#                 self._set_buttons('normal')
#         threading.Thread(target=worker, daemon=True).start()

#     # ------------------- Start Installation Flow -------------------
#     def start_install(self):
#         """Start full installation flow (runs in background thread)."""
#         def worker():
#             import re
#             import shutil

#             current = get_current_kit()
#             if not current:
#                 self.write_log('No current kit in status.json', 'err')
#                 return

#             self._set_buttons('disabled')

#             # reset steps display
#             for key, _ in self.steps:
#                 self.set_step(key, 'pending')

#             self.update_progress(2, 'Beginning installation')

#             # 1) Check & install software
#             self.set_step('check_software', 'running')
#             ok = self._install_software_sync()
#             self.set_step('check_software', 'done' if ok else 'failed')
#             if not ok:
#                 self.write_log('Required software not installed. Aborting.', 'err')
#                 self._set_buttons('normal')
#                 return

#             # 2) Install npm deps if present
#             self.set_step('npm_deps', 'running')
#             self.update_progress(20, 'Installing project dependencies')
#             try:
#                 pkg = app_dir / 'package.json'
#                 if pkg.exists():
#                     self.write_log('Running npm install...', 'info')
#                     p = subprocess.Popen(['npm', 'install'], cwd=str(app_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
#                     for ln in p.stdout:
#                         self.write_log(ln.rstrip(), 'info')
#                     p.wait()
#                     if p.returncode == 0:
#                         self.set_step('npm_deps', 'done')
#                         self.update_progress(35, 'Dependencies installed')
#                     else:
#                         self.set_step('npm_deps', 'warn')
#                         self.write_log('npm install returned non-zero', 'warn')
#                         self.update_progress(30, 'Dependencies may be incomplete')
#                 else:
#                     self.write_log('No package.json found; skipping npm install', 'warn')
#                     self.set_step('npm_deps', 'done')
#                     self.update_progress(30, 'No dependencies to install')
#             except Exception as e:
#                 self.set_step('npm_deps', 'warn')
#                 self.write_log(f'npm install error: {e}', 'warn')
#                 self.update_progress(30, 'Continuing despite npm errors')

#             # 3) Run setup-kit.py (Capacitor build + APK)
#             self.set_step('capacitor_init', 'running')
#             self.update_progress(40, 'Running kit setup (build)')
#             setup_script = root_dir / 'utils' / 'setup-kit.py'
#             if not setup_script.exists():
#                 self.write_log('setup-kit.py not found in utils/', 'err')
#                 self.set_step('capacitor_init', 'failed')
#                 self._set_buttons('normal')
#                 return

#             # prepare progress mapping and state flags
#             progress_map = {
#                 'capacitor': 50,
#                 'gradle': 60,
#                 'assemble': 70,
#                 '.apk': 82,
#                 'signing': 88,
#                 'apk generated': 92,
#                 'build successful': 94
#             }
#             cur_progress = 40
#             last_time = time.time()

#             apk_filename = None
#             apk_src_path = None
#             build_detected = False
#             final_success = False

#             try:
#                 proc = subprocess.Popen(
#                     [sys.executable, str(setup_script)],
#                     cwd=str(root_dir),
#                     stdout=subprocess.PIPE,
#                     stderr=subprocess.STDOUT,
#                     text=True
#                 )

#                 for raw_line in proc.stdout:
#                     ln = raw_line.rstrip()
#                     if not ln:
#                         continue
#                     self.write_log(ln, 'info')
#                     low = ln.lower()

#                     # capture explicit APK creation line, e.g.:
#                     # "SUCCESS: APK created: els-starterkit-1-1.0.0-db.apk"
#                     m_apk = re.search(r'apk created[: ]+\s*([^\s]+\.apk)', ln, re.IGNORECASE)
#                     if m_apk:
#                         apk_filename = m_apk.group(1).strip()
#                         build_detected = True
#                         # bump progress and record
#                         cur_progress = max(cur_progress + 15, 82)
#                         cur_progress = min(cur_progress, 92)
#                         self.update_progress(cur_progress, 'APK created')
#                         # attempt to find actual file path in repo (best-effort)
#                         try:
#                             for p in root_dir.rglob(apk_filename):
#                                 apk_src_path = p
#                                 break
#                             if apk_src_path:
#                                 self.write_log(f'Found APK at: {apk_src_path}', 'info')
#                             else:
#                                 self.write_log(f'APK filename detected ({apk_filename}) but file not found in repo', 'warn')
#                         except Exception as _:
#                             pass
#                         continue

#                     # detect JSON success lines like {"success": true, "message": "..."}
#                     if '"success": true' in low or 'setup completed successfully' in low:
#                         final_success = True
#                         cur_progress = max(cur_progress, 92)
#                         self.update_progress(cur_progress, 'Setup reported success')
#                         continue

#                     # APK installation on emulator failed — treat as warning
#                     if 'apk installation failed' in low:
#                         self.write_log('APK installation on emulator failed (warning, continuing).', 'warn')
#                         cur_progress = max(cur_progress, 88)
#                         self.update_progress(cur_progress, 'APK built (emulator install failed)')
#                         continue

#                     # percent printed by script (e.g., "50%")
#                     m_pct = re.search(r'(\d{1,3})\s*%', ln)
#                     if m_pct:
#                         try:
#                             val = int(m_pct.group(1))
#                             if 0 <= val <= 99 and val > cur_progress:
#                                 if val - cur_progress > 25:
#                                     val = cur_progress + 25
#                                 cur_progress = val
#                                 self.update_progress(cur_progress, f'Build {cur_progress}%')
#                         except Exception:
#                             pass
#                         continue

#                     # other keyword nudges
#                     for k, v in progress_map.items():
#                         if k in low and v > cur_progress:
#                             step = min(cur_progress + 18, v)
#                             cur_progress = step
#                             self.update_progress(cur_progress, f'{k}...')
#                             break

#                     # gentle fallback tick
#                     if time.time() - last_time > 6 and cur_progress < 80:
#                         last_time = time.time()
#                         cur_progress += 3
#                         self.update_progress(cur_progress, 'Working...')

#                 # wait and evaluate outcome
#                 proc.wait()
#                 rc = proc.returncode

#                 succeeded = final_success or (rc == 0)

#                 if succeeded:
#                     self.set_step('capacitor_init', 'done')
#                     self.update_progress(95, 'Finalizing...')

#                     # COPY APK to my-els-apk folder if we found it; otherwise just inform filename if known
#                     try:
#                         apk_dest_folder = root_dir / 'my-els-apk'
#                         if apk_filename:
#                             # if we located the real file path, copy from there; otherwise try to search by name
#                             if not apk_src_path:
#                                 for p in root_dir.rglob(apk_filename):
#                                     apk_src_path = p
#                                     break
#                             if apk_src_path and apk_src_path.exists():
#                                 apk_dest_folder.mkdir(exist_ok=True)
#                                 dest = apk_dest_folder / apk_filename
#                                 try:
#                                     shutil.copy2(str(apk_src_path), str(dest))
#                                     self.write_log(f'APK copied to: {dest}', 'ok')
#                                     apk_final_location = dest
#                                 except Exception as ce:
#                                     self.write_log(f'Failed to copy APK: {ce}', 'warn')
#                                     apk_final_location = apk_src_path
#                             else:
#                                 # not found — still inform user about detected filename
#                                 self.write_log(f'APK filename: {apk_filename} (file not found to copy)', 'warn')
#                                 apk_final_location = None
#                         else:
#                             apk_final_location = None
#                     except Exception as e:
#                         apk_final_location = None
#                         self.write_log(f'Error handling APK file: {e}', 'warn')

#                     # update status.json to next kit
#                     all_kits = get_all_kits()
#                     try:
#                         idx = all_kits.index(current)
#                     except ValueError:
#                         idx = -1
#                     next_kit = all_kits[idx + 1] if (idx != -1 and idx + 1 < len(all_kits)) else ''
#                     update_status(next_kit)
#                     self.write_log(f'Updated status to: {next_kit if next_kit else "None"}', 'ok')
#                     self.set_step('update_status', 'done')

#                     # finalize UI
#                     self.update_progress(100, 'Installation completed successfully!')
#                     self.set_step('post_tasks', 'done')
#                     self.write_log('Installation completed successfully!', 'ok')

#                     # explicit message to user about APK location
#                     try:
#                         if apk_final_location:
#                             msg = f'APK created and copied to: {apk_final_location}\\n\\nYou can find your APK in the folder: {apk_final_location.parent}'
#                             self.write_log(msg, 'ok')
#                             try:
#                                 messagebox.showinfo('Success', f'Installation complete.\\nAPK copied to:\\n{apk_final_location}')
#                             except Exception:
#                                 pass
#                         elif apk_filename:
#                             # filename known but not copied
#                             self.write_log(f'APK filename: {apk_filename}. Check your build outputs.', 'ok')
#                             try:
#                                 messagebox.showinfo('Success', f'Installation complete. APK: {apk_filename} (not copied).')
#                             except Exception:
#                                 pass
#                         else:
#                             # no info about apk
#                             self.write_log('Installation complete. APK location not detected automatically.', 'ok')
#                             try:
#                                 messagebox.showinfo('Success', 'Installation complete. APK location not detected automatically.')
#                             except Exception:
#                                 pass
#                     except Exception:
#                         pass

#                     # launch optional tasks (non-blocking)
#                     try:
#                         threading.Thread(target=self.start_emulator, daemon=True).start()
#                     except Exception as emu_err:
#                         self.write_log(f'Emulator start failed: {emu_err}', 'warn')
#                     try:
#                         self.open_vscode()
#                     except Exception:
#                         pass

#                     self._set_buttons('normal')

#                 else:
#                     # failed
#                     try:
#                         rem = proc.stdout.read()
#                         if rem:
#                             self.write_log(rem, 'info')
#                     except Exception:
#                         pass
#                     self.set_step('capacitor_init', 'failed')
#                     self.write_log(f'setup-kit.py failed (rc={rc}).', 'err')
#                     try:
#                         messagebox.showerror('Error', f'Setup script failed (rc={rc}). See log for details.')
#                     except Exception:
#                         pass
#                     self._set_buttons('normal')

#             except Exception as e:
#                 self.set_step('capacitor_init', 'failed')
#                 self.write_log(f'Error running setup-kit.py: {e}', 'err')
#                 self._set_buttons('normal')
#                 return

#         # run worker in background
#         threading.Thread(target=worker, daemon=True).start()

# if __name__ == '__main__':
#     ProInstallerUI()


# # emeelan-els-kits/start-kits-installer.py
# import json
# import os
# import subprocess
# import threading
# import sys
# import traceback
# import time
# from pathlib import Path
# from tkinter import *
# from tkinter import ttk, scrolledtext, messagebox

# def get_root():
#     return Path(__file__).parent

# root_dir = get_root()
# kits_dir = root_dir / 'my-els-kits'
# app_dir = root_dir / 'emeelan-els-app'
# status_path = root_dir / 'status.json'

# def get_all_kits():
#     if not kits_dir.exists():
#         return []
#     return sorted([p.name for p in kits_dir.iterdir() if p.is_dir()])

# def get_current_kit():
#     if not status_path.exists():
#         return ''
#     try:
#         with open(status_path) as f:
#             data = json.load(f)
#         return data.get('status', '')
#     except:
#         return ''

# def update_status(new_status):
#     with open(status_path, 'w') as f:
#         json.dump({'status': new_status}, f)

# # --- Add tooltip helper (paste after imports) ---
# class ToolTip:
#     """Simple hover tooltip for a widget."""
#     def __init__(self, widget, text):
#         self.widget = widget
#         self.text = text
#         self.tipwindow = None
#         widget.bind("<Enter>", self.show)
#         widget.bind("<Leave>", self.hide)

#     def show(self, event=None):
#         if self.tipwindow or not self.text:
#             return
#         x = self.widget.winfo_rootx() + 20
#         y = self.widget.winfo_rooty() + 20
#         tw = Toplevel(self.widget)
#         tw.wm_overrideredirect(True)
#         tw.wm_geometry(f"+{x}+{y}")
#         label = Label(tw, text=self.text, justify='left',
#                     background="#ffffe0", relief='solid', borderwidth=1,
#                     font=("tahoma", 8))
#         label.pack(ipadx=4)
#         self.tipwindow = tw

#     def hide(self, event=None):
#         if self.tipwindow:
#             self.tipwindow.destroy()
#             self.tipwindow = None
# # --- end tooltip helper ---

# class InstallerUI:
#     def __init__(self):
#         self.window = Tk()
#         self.window.title("EMEELAN ELS Kits Installer")
#         self.window.geometry("800x700")
        
#         # Main frame
#         main_frame = Frame(self.window)
#         main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
#         # Title
#         title_label = Label(main_frame, text="EMEELAN ELS Kits Installer", 
#                            font=("Arial", 16, "bold"))
#         title_label.pack(pady=10)
        
#         # Progress section
#         progress_frame = Frame(main_frame)
#         progress_frame.pack(fill=X, pady=10)
        
#         # Current kit display
#         self.current_label = Label(progress_frame, text="Current Kit: None", 
#                                   font=("Arial", 12, "bold"))
#         self.current_label.pack(anchor=W)
        
#         # Next kit display
#         self.next_label = Label(progress_frame, text="Next Kit: None", 
#                                font=("Arial", 10))
#         self.next_label.pack(anchor=W, pady=5)
        
#         # Progress bar with percentage
#         progress_bar_frame = Frame(progress_frame)
#         progress_bar_frame.pack(fill=X, pady=10)
        
#         self.progress = ttk.Progressbar(progress_bar_frame, orient="horizontal", 
#                                        length=400, mode="determinate")
#         self.progress.pack(side=LEFT, fill=X, expand=True)
        
#         self.progress_label = Label(progress_bar_frame, text="0%", 
#                                    font=("Arial", 10))
#         self.progress_label.pack(side=RIGHT, padx=5)
        
#         # Status label
#         self.status_label = Label(progress_frame, text="Ready to start", 
#                                  font=("Arial", 10, "bold"), fg="blue")
#         self.status_label.pack(anchor=W, pady=5)
        
#         # Log text area with scrollbar
#         log_frame = LabelFrame(main_frame, text="Installation Log", 
#                               font=("Arial", 10, "bold"))
#         log_frame.pack(fill=BOTH, expand=True, pady=10)
        
#         self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80,
#                                                  font=("Courier New", 9))
#         self.log_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
#         # Button frame
#         button_frame = Frame(main_frame)
#         button_frame.pack(pady=10)

#         # helper to create a button with a small '!' icon and tooltip
#         def make_button_with_tooltip(parent, text, cmd, tooltip_text,
#                                      bg="#4CAF50", width=15, height=2, font=("Arial", 10, "bold")):
#             container = Frame(parent)
#             container.pack(side=LEFT, padx=5)
#             btn = Button(container, text=text, command=cmd, bg=bg, fg="white",
#                          font=font, width=width, height=height)
#             btn.pack(side=LEFT)
#             icon = Label(container, text="❗", fg="orange", font=("Arial", 12, "bold"))
#             icon.pack(side=LEFT, padx=(6,0))
#             ToolTip(icon, tooltip_text)
#             return btn

#         # Create buttons with tooltips (texts explained below)
#         self.start_button = make_button_with_tooltip(
#             button_frame,
#             "Start Installation",
#             self.start_install,
#             "Runs software checks, installs missing software, builds the app (Capacitor/Android) and updates kit status.",
#             bg="#4CAF50"
#         )

#         self.software_button = make_button_with_tooltip(
#             button_frame,
#             "Install Software Only",
#             self.install_software_only,
#             "Installs Node.js, Java JDK, Android SDK, Gradle, and VS Code.",
#             bg="#2196F3",
#             font=("Arial", 10)
#         )

#         self.reset_button = make_button_with_tooltip(
#             button_frame,
#             "Reset Current Kit",
#             self.reset_kit,
#             "Resets the current kit back to the kit specified in status.json.",
#             bg="#FF9800",
#             font=("Arial", 10)
#         )

#         self.open_vscode_button = make_button_with_tooltip(
#             button_frame,
#             "Open in VS Code",
#             self.open_vscode,
#             "Opens the current project in Visual Studio Code.",
#             bg="#9C27B0",
#             font=("Arial", 10)
#         )

#         self.adb_button = make_button_with_tooltip(
#             button_frame,
#             "Check ADB Devices",
#             self.check_adb_devices,
#             "Lists connected Android devices and installed emulators on your PC.",
#             bg="#607D8B",
#             font=("Arial", 10)
#         )

#         self.emulator_button = make_button_with_tooltip(
#             button_frame,
#             "Start Emulator",
#             self.start_emulator,
#             "Starts an installed Android emulator on your PC (non-blocking).",
#             bg="#FF5722",
#             font=("Arial", 10)
#         )
        
#         self.update_ui()
#         self.window.mainloop()
        

#     def _set_all_buttons_state(self, state):
#         """Enable/disable all primary buttons from one place."""
#         for btn in (self.start_button, self.software_button, self.reset_button,
#                     self.open_vscode_button, self.adb_button, self.emulator_button):
#             try:
#                 btn.config(state=state)
#             except:
#                 pass
    
#     def _start_install_thread(self):
#         """Thread: install software (synchronously), then run kit setup."""
#         current = get_current_kit()
#         if not current:
#             self.log("No kits available.", "red")
#             self.window.after(0, lambda: self._set_all_buttons_state("normal"))
#             return

#         try:
#             # 1) Install software as part of the start flow
#             self.update_progress(2, "Checking & installing required software...")
#             self.log("=== Installing/Checking required software (part of Start Installation) ===", "blue")

#             success = False
#             try:
#                 success = self._install_software_sync()  # this runs utils/software-installer.py with a timeout
#             except Exception as e:
#                 self.log(f"Software installer error: {e}", "orange")
#                 success = False

#             if not success:
#                 self.log("✗ Software installation failed. Aborting.", "red")
#                 messagebox.showerror("Error", "Required software installation failed. See logs.")
#                 self.update_progress(0, "Software installation failed")
#                 self.window.after(0, lambda: self._set_all_buttons_state("normal"))
#                 return

#             # 2) Run the rest of the installation (kit setup) after software is present
#             self.run_installation_core()
#         finally:
#             # ensure UI is re-enabled in case something unexpected happens here
#             self.window.after(0, lambda: self._set_all_buttons_state("normal"))

#     def start_install(self):
#         """Start a full installation: install software first, then kit installation."""
#         # disable UI
#         self._set_all_buttons_state("disabled")
#         threading.Thread(target=self._start_install_thread, daemon=True).start()
    
#     def update_ui(self):
#         current = get_current_kit()
#         all_kits = get_all_kits()
        
#         self.current_label.config(text=f"Current Kit: {current if current else 'None'}")
        
#         # Determine next kit
#         if current and current in all_kits:
#             idx = all_kits.index(current)
#             next_kit = all_kits[idx + 1] if idx + 1 < len(all_kits) else "All kits completed!"
#             status_text = f"Next Kit: {next_kit} ({idx+1}/{len(all_kits)})"
#         else:
#             next_kit = all_kits[0] if all_kits else "No kits available"
#             status_text = f"Next Kit: {next_kit} (0/{len(all_kits)})" if all_kits else "No kits available"
        
#         self.next_label.config(text=status_text)
        
#         # Update button state
#         if not current or current not in all_kits:
#             self.start_button.config(state="disabled")
#         else:
#             self.start_button.config(state="normal")
    
#     def log(self, msg, color="black"):
#         """Add a message to the log with optional color"""
#         self.log_text.insert(END, msg + "\n")
#         self.log_text.see(END)
#         self.window.update_idletasks()
    
#     def update_progress(self, value, status=""):
#         """Update progress bar and status"""
#         self.progress['value'] = value
#         self.progress_label.config(text=f"{int(value)}%")
#         if status:
#             self.status_label.config(text=status)
#         self.window.update_idletasks()
    
#     def open_vscode(self):
#         """Open the app directory in VS Code"""
#         try:
#             subprocess.Popen(['code', str(app_dir)], shell=True)
#             self.log("✓ Opening VS Code...", "green")
#         except Exception as e:
#             self.log(f"✗ Failed to open VS Code: {str(e)}", "red")
    
#     def check_adb_devices(self):
#         """Check ADB devices"""
#         def run_adb_check():
#             self.adb_button.config(state="disabled")
#             self.log("=== Checking ADB Devices ===", "blue")
            
#             try:
#                 # Try to find ADB in common locations
#                 adb_paths = [
#                     os.path.join(os.environ.get('ANDROID_HOME', ''), 'platform-tools', 'adb'),
#                     os.path.join(os.environ.get('ANDROID_SDK_ROOT', ''), 'platform-tools', 'adb'),
#                     os.path.join(str(root_dir), 'android-sdk', 'platform-tools', 'adb'),
#                     'adb'  # Try system ADB
#                 ]
                
#                 adb_found = None
#                 for path in adb_paths:
#                     if os.path.exists(path) or path == 'adb':
#                         try:
#                             result = subprocess.run([path, 'devices'], capture_output=True, text=True, timeout=10)
#                             if result.returncode == 0:
#                                 adb_found = path
#                                 break
#                         except:
#                             continue
                
#                 if adb_found:
#                     self.log(f"✓ ADB found at: {adb_found}", "green")
#                     result = subprocess.run([adb_found, 'devices'], capture_output=True, text=True, timeout=30)
#                     self.log("ADB Devices Output:", "blue")
#                     self.log(result.stdout)
#                     if result.stderr:
#                         self.log(f"ADB Error: {result.stderr}", "red")
#                 else:
#                     self.log("✗ ADB not found. Please install Android SDK first.", "red")
#                     self.log("Run 'Install Software Only' to install Android SDK", "blue")
                    
#             except Exception as e:
#                 self.log(f"✗ Error checking ADB devices: {str(e)}", "red")
#             finally:
#                 self.adb_button.config(state="normal")
        
#         threading.Thread(target=run_adb_check, daemon=True).start()

#     def start_emulator(self):
#         """Start the Android emulator"""
#         def run_emulator_start():
#             self.emulator_button.config(state="disabled")
#             self.log("=== Starting Android Emulator ===", "blue")
            
#             try:
#                 # Try to find emulator in common locations
#                 emulator_paths = [
#                     os.path.join(os.environ.get('ANDROID_HOME', ''), 'emulator', 'emulator'),
#                     os.path.join(os.environ.get('ANDROID_SDK_ROOT', ''), 'emulator', 'emulator'),
#                     os.path.join(str(root_dir), 'android-sdk', 'emulator', 'emulator'),
#                     'emulator'  # Try system emulator
#                 ]
                
#                 emulator_found = None
#                 for path in emulator_paths:
#                     if os.path.exists(path) or path == 'emulator':
#                         try:
#                             # Start emulator in background
#                             cmd = f'{path} -avd Pixel_6 -no-snapshot-load -no-boot-anim -wipe-data'
#                             subprocess.Popen(cmd, shell=True)
#                             emulator_found = path
#                             break
#                         except:
#                             continue
                
#                 if emulator_found:
#                     self.log("✓ Android emulator started in background", "green")
#                     self.log("Waiting for emulator to boot...", "blue")
                    
#                     # Wait for emulator to be ready
#                     for i in range(12):  # Wait up to 2 minutes
#                         time.sleep(10)
#                         rc, out = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=30)
#                         if "emulator" in out and "device" in out:
#                             self.log("✓ Android emulator is ready", "green")
#                             break
#                         self.log(f"Waiting for emulator... ({i+1}/12)", "blue")
#                     else:
#                         self.log("⚠ Emulator is taking longer than expected to start", "orange")
#                 else:
#                     self.log("✗ Emulator not found. Please install Android SDK first.", "red")
                    
#             except Exception as e:
#                 self.log(f"✗ Error starting emulator: {str(e)}", "red")
#             finally:
#                 self.emulator_button.config(state="normal")
        
#         threading.Thread(target=run_emulator_start, daemon=True).start()

#     def _install_software_sync(self):
#         """Helper method to install software synchronously"""
#         try:
#             software_script = root_dir / 'utils' / 'software-installer.py'
#             process = subprocess.run([sys.executable, str(software_script)], 
#                                    capture_output=True, text=True, cwd=root_dir,
#                                    timeout=1800)  # 30 minute timeout
#             return process.returncode == 0
#         except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
#             return False

#     def install_software_only(self):
#         def run_software_install():
#             self.software_button.config(state="disabled")
#             self.start_button.config(state="disabled")
#             self.reset_button.config(state="disabled")
#             self.open_vscode_button.config(state="disabled")
#             self.adb_button.config(state="disabled")
#             self.emulator_button.config(state="disabled")
#             self.update_progress(0, "Installing software dependencies...")
#             self.log("=== Starting software installation ===", "blue")
#             self.log("Installing from: utils/software-installer.py", "blue")
#             self.log("This will install: Node.js, Java JDK, Android SDK, Gradle, VS Code", "blue")
            
#             try:
#                 software_script = root_dir / 'utils' / 'software-installer.py'
#                 software_script_str = str(software_script)
                
#                 # Use PowerShell to run with elevation and wait for completion
#                 powershell_cmd = [
#                     'powershell', '-Command',
#                     f'$process = Start-Process -FilePath "{sys.executable}" -ArgumentList "{software_script_str}" -Verb runas -PassThru -Wait; exit $process.ExitCode'
#                 ]
                
#                 process = subprocess.Popen(powershell_cmd, 
#                                          stdout=subprocess.PIPE, 
#                                          stderr=subprocess.STDOUT,
#                                          text=True, 
#                                          cwd=root_dir,
#                                          encoding='utf-8',
#                                          errors='replace')
                
#                 # Stream output in real-time
#                 for line in process.stdout:
#                     line = line.strip()
#                     if line:
#                         self.log(line)
#                         # Update progress based on content
#                         if "Installing Python" in line:
#                             self.update_progress(10, "Installing Python...")
#                         elif "Installing Node" in line:
#                             self.update_progress(20, "Installing Node.js...")
#                         elif "Installing JDK" in line:
#                             self.update_progress(30, "Installing Java JDK...")
#                         elif "Installing VSCode" in line:
#                             self.update_progress(40, "Installing VS Code...")
#                         elif "Setting up Android SDK" in line:
#                             self.update_progress(50, "Setting up Android SDK...")
#                         elif "Installing Gradle" in line:
#                             self.update_progress(70, "Installing Gradle...")
#                         elif "Configuring environment variables" in line:
#                             self.update_progress(90, "Configuring environment...")
                
#                 process.wait()
                
#                 if process.returncode == 0:
#                     self.log("✅ Software installation completed successfully!", "green")
#                     self.update_progress(100, "Software installation completed")
#                     messagebox.showinfo("Success", "Software installation completed successfully!")
#                 else:
#                     self.log("❌ Software installation failed", "red")
#                     self.update_progress(0, "Software installation failed")
#                     messagebox.showerror("Error", "Software installation failed. Check logs for details.")
#             except Exception as e:
#                 self.log(f"❌ Error during software installation: {str(e)}", "red")
#                 self.log(traceback.format_exc(), "red")
#                 self.update_progress(0, "Software installation failed")
#                 messagebox.showerror("Error", f"Software installation failed: {str(e)}")
#             finally:
#                 self.software_button.config(state="normal")
#                 self.start_button.config(state="normal")
#                 self.reset_button.config(state="normal")
#                 self.open_vscode_button.config(state="normal")
#                 self.adb_button.config(state="normal")
#                 self.emulator_button.config(state="normal")
        
#         threading.Thread(target=run_software_install, daemon=True).start()
    
#     def reset_kit(self):
#         def run_reset():
#             self.reset_button.config(state="disabled")
#             self.update_progress(0, "Resetting kit...")
#             self.log("=== Resetting kit ===", "blue")
            
#             try:
#                 reset_script = root_dir / 'reset-kits.py'
#                 process = subprocess.Popen([sys.executable, str(reset_script)], 
#                                          stdout=subprocess.PIPE, 
#                                          stderr=subprocess.STDOUT,
#                                          text=True, cwd=root_dir)
                
#                 # Stream output in real-time
#                 for line in process.stdout:
#                     self.log(line.strip())
                
#                 process.wait()
                
#                 if process.returncode == 0:
#                     self.log("✓ Kit reset successfully!", "green")
#                     self.update_progress(100, "Kit reset completed")
#                     messagebox.showinfo("Success", "Kit reset completed successfully!")
#                 else:
#                     self.log("✗ Kit reset failed", "red")
#                     self.update_progress(0, "Kit reset failed")
#                     messagebox.showerror("Error", "Kit reset failed. Check logs for details.")
#             except Exception as e:
#                 self.log(f"Error during kit reset: {str(e)}", "red")
#                 self.log(traceback.format_exc(), "red")
#                 self.update_progress(0, "Kit reset failed")
#                 messagebox.showerror("Error", f"Kit reset failed: {str(e)}")
#             finally:
#                 self.reset_button.config(state="normal")
        
#         threading.Thread(target=run_reset, daemon=True).start()
    
#     def run_installation(self):
#         current = get_current_kit()
#         if not current:
#             self.log("No kits available.", "red")
#             return

#         try:
#             # Step 1: Check dependencies
#             self.update_progress(0, "Checking software dependencies...")
#             self.log(f"=== Starting installation for kit: {current} ===", "blue")
#             self.log("Checking if required software is installed...")

#             software_installed = False
#             try:
#                 node_check = subprocess.run(['node', '--version'], capture_output=True, text=True)
#                 java_check = subprocess.run(['java', '-version'], capture_output=True, text=True)

#                 if node_check.returncode == 0 and java_check.returncode == 0:
#                     self.log("✓ Required software found.", "green")
#                     software_installed = True
#                 else:
#                     self.log("Some software missing, installing...", "orange")
#                     software_installed = self._install_software_sync()
#             except (subprocess.CalledProcessError, FileNotFoundError) as e:
#                 self.log(f"Software check failed: {e}", "orange")
#                 software_installed = self._install_software_sync()

#             if not software_installed:
#                 self.log("✗ Software installation failed. Aborting kit installation.", "red")
#                 self.update_progress(0, "Software installation failed")
#                 return

#             # Step 2: Run setup-kit.py (Capacitor build & APK)
#             self.update_progress(10, "Preparing kit setup...")
#             self.log(f"Setting up kit: {current}")
#             setup_script = root_dir / 'utils' / 'setup-kit.py'

#             process = subprocess.Popen(
#                 [sys.executable, str(setup_script)],
#                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
#                 text=True, cwd=root_dir, bufsize=1, universal_newlines=True
#             )

#             # Map keywords (lowercase) -> progress value. Add or modify keywords according to your script output.
#             progress_keywords = {
#                 'npm install': 30,
#                 'installing dependencies': 30,
#                 'building': 45,
#                 'capacitor': 50,
#                 'cordova': 50,
#                 'gradle': 60,
#                 'assemble': 70,
#                 'built apk': 80,
#                 '.apk': 80,
#                 'build successful': 85,
#                 'signing': 90,
#                 'apk generated': 95,
#                 'done': 98,
#                 'completed': 98
#             }

#             current_progress = 10
#             last_tick = time.time()
#             tick_increment_interval = 5  # seconds - fallback increment interval
#             max_fallback_progress = 65    # do not exceed this with fallback ticks (we rely on keywords for higher progress)

#             # Helper to update progress only if increased
#             def maybe_update_progress(pct, status_msg=None):
#                 nonlocal current_progress
#                 try:
#                     pct = int(pct)
#                 except:
#                     return
#                 if pct > current_progress:
#                     current_progress = pct
#                     self.update_progress(current_progress, status_msg if status_msg else "")
            
#             # Stream output and update progress dynamically
#             self.log("=== Running setup-kit.py (this may take a while) ===", "blue")
#             while True:
#                 line = process.stdout.readline()
#                 if not line:
#                     # no line right now
#                     if process.poll() is not None:
#                         break  # process ended
#                     # fallback tick to show progress moving
#                     if time.time() - last_tick > tick_increment_interval and current_progress < max_fallback_progress:
#                         last_tick = time.time()
#                         maybe_update_progress(min(current_progress + 2, max_fallback_progress),
#                                             "Working... (please wait)")
#                     time.sleep(0.1)
#                     continue

#                 line = line.rstrip()
#                 if line:
#                     self.log(line)
#                     lower = line.lower()

#                     # If the script prints explicit percent-like progress, honor it (e.g., "50%")
#                     import re
#                     m = re.search(r'(\d{1,3})\s*%', line)
#                     if m:
#                         try:
#                             percent_val = int(m.group(1))
#                             maybe_update_progress(percent_val, f"Progress: {percent_val}%")
#                         except:
#                             pass

#                     # Keyword based progress boosts
#                     for key, pct in progress_keywords.items():
#                         if key in lower:
#                             maybe_update_progress(pct, f"{key.capitalize()}...")
#                             break

#             # Wait for process to exit and capture return code
#             process.wait()
#             rc = process.returncode

#             if rc == 0:
#                 maybe_update_progress(85, "Build finished, finalizing...")
#                 self.log("✓ Kit setup successful.", "green")
#             else:
#                 # read any remaining output
#                 remaining = process.stdout.read()
#                 if remaining:
#                     self.log(remaining)
#                 raise Exception(f"Setup script failed with return code {rc}")

#             # Step 3: Update status immediately after the build (Capacitor/APK generated)
#             maybe_update_progress(90, "Updating to next kit...")
#             all_kits = get_all_kits()
#             try:
#                 idx = all_kits.index(current)
#             except ValueError:
#                 idx = -1
#             next_kit = all_kits[idx + 1] if (idx != -1 and idx + 1 < len(all_kits)) else ""
#             update_status(next_kit)
#             self.log(f"Updated status to next kit: {next_kit if next_kit else 'None'}")

#             # Small pause for UI feedback, then finish
#             maybe_update_progress(95, "Finishing up...")
#             time.sleep(0.6)
#             maybe_update_progress(100, "Installation completed successfully!")
#             self.log("✓ Installation completed successfully!", "green")
#             messagebox.showinfo("Success", "Installation completed successfully!")

#             # Try to start emulator optionally (non-blocking)
#             try:
#                 self.log("Attempting to start emulator (optional)...", "blue")
#                 # call start_emulator() in a safe non-blocking way
#                 threading.Thread(target=self.start_emulator, daemon=True).start()
#             except Exception as emu_err:
#                 self.log(f"⚠ Emulator failed to start: {emu_err}", "orange")

#             # Open VS Code after successful installation
#             self.open_vscode()
#             self.window.after(0, self.update_ui)

#         except Exception as e:
#             self.log(f"✗ Error during installation: {str(e)}", "red")
#             self.update_progress(0, "Installation failed")
#             messagebox.showerror("Error", f"Installation failed: {str(e)}")

#             self.log("Reverting changes...")
#             try:
#                 reset_script = root_dir / 'reset-kits.py'
#                 subprocess.run(
#                     [sys.executable, str(reset_script)],
#                     check=True, capture_output=True, text=True, cwd=root_dir
#                 )
#                 self.log("✓ Changes reverted successfully.", "green")
#             except Exception as revert_error:
#                 self.log(f"✗ Error during revert: {str(revert_error)}", "red")
#         finally:
#             # Always re-enable buttons
#             self.start_button.config(state="normal")
#             self.software_button.config(state="normal")
#             self.reset_button.config(state="normal")
#             self.open_vscode_button.config(state="normal")
#             self.adb_button.config(state="normal")
#             self.emulator_button.config(state="normal")

# if __name__ == '__main__':
#     InstallerUI()

# # emeelan-els-kits/start-kits-installer.py
# import json
# import os
# import subprocess
# import threading
# import sys
# import traceback
# from pathlib import Path
# from tkinter import *
# from tkinter import ttk, scrolledtext, messagebox

# def get_root():
#     return Path(__file__).parent

# root_dir = get_root()
# kits_dir = root_dir / 'my-els-kits'
# app_dir = root_dir / 'emeelan-els-app'
# status_path = root_dir / 'status.json'

# def get_all_kits():
#     return sorted([p.name for p in kits_dir.iterdir() if p.is_dir()])

# def get_current_kit():
#     if not status_path.exists():
#         return ''
#     with open(status_path) as f:
#         data = json.load(f)
#     return data.get('status', '')

# def update_status(new_status):
#     with open(status_path, 'w') as f:
#         json.dump({'status': new_status}, f)

# class InstallerUI:
#     def __init__(self):
#         self.window = Tk()
#         self.window.title("EMEELAN ELS Kits Installer")
#         self.window.geometry("800x700")
        
#         # Main frame
#         main_frame = Frame(self.window)
#         main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
#         # Title
#         title_label = Label(main_frame, text="EMEELAN ELS Kits Installer", 
#                            font=("Arial", 16, "bold"))
#         title_label.pack(pady=10)
        
#         # Progress section
#         progress_frame = Frame(main_frame)
#         progress_frame.pack(fill=X, pady=10)
        
#         # Current kit display
#         self.current_label = Label(progress_frame, text="Current Kit: None", 
#                                   font=("Arial", 12, "bold"))
#         self.current_label.pack(anchor=W)
        
#         # Next kit display
#         self.next_label = Label(progress_frame, text="Next Kit: None", 
#                                font=("Arial", 10))
#         self.next_label.pack(anchor=W, pady=5)
        
#         # Progress bar with percentage
#         progress_bar_frame = Frame(progress_frame)
#         progress_bar_frame.pack(fill=X, pady=10)
        
#         self.progress = ttk.Progressbar(progress_bar_frame, orient="horizontal", 
#                                        length=400, mode="determinate")
#         self.progress.pack(side=LEFT, fill=X, expand=True)
        
#         self.progress_label = Label(progress_bar_frame, text="0%", 
#                                    font=("Arial", 10))
#         self.progress_label.pack(side=RIGHT, padx=5)
        
#         # Status label
#         self.status_label = Label(progress_frame, text="Ready to start", 
#                                  font=("Arial", 10, "bold"), fg="blue")
#         self.status_label.pack(anchor=W, pady=5)
        
#         # Log text area with scrollbar
#         log_frame = LabelFrame(main_frame, text="Installation Log", 
#                               font=("Arial", 10, "bold"))
#         log_frame.pack(fill=BOTH, expand=True, pady=10)
        
#         self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80,
#                                                  font=("Courier New", 9))
#         self.log_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
#         # Button frame
#         button_frame = Frame(main_frame)
#         button_frame.pack(pady=10)
        
#         self.start_button = Button(button_frame, text="Start Installation", 
#                                   command=self.start_install, 
#                                   bg="#4CAF50", fg="white", 
#                                   font=("Arial", 10, "bold"),
#                                   width=15, height=2)
#         self.start_button.pack(side=LEFT, padx=5)
        
#         self.software_button = Button(button_frame, text="Install Software Only", 
#                                      command=self.install_software_only,
#                                      bg="#2196F3", fg="white", 
#                                      font=("Arial", 10),
#                                      width=15, height=2)
#         self.software_button.pack(side=LEFT, padx=5)
        
#         self.reset_button = Button(button_frame, text="Reset Current Kit", 
#                                   command=self.reset_kit,
#                                   bg="#FF9800", fg="white", 
#                                   font=("Arial", 10),
#                                   width=15, height=2)
#         self.reset_button.pack(side=LEFT, padx=5)
        
#         self.open_vscode_button = Button(button_frame, text="Open in VS Code", 
#                                         command=self.open_vscode,
#                                         bg="#9C27B0", fg="white", 
#                                         font=("Arial", 10),
#                                         width=15, height=2)
#         self.open_vscode_button.pack(side=LEFT, padx=5)
        
#         self.update_ui()
#         self.window.mainloop()
    
#     def update_ui(self):
#         current = get_current_kit()
#         all_kits = get_all_kits()
        
#         self.current_label.config(text=f"Current Kit: {current if current else 'None'}")
        
#         # Determine next kit
#         if current and current in all_kits:
#             idx = all_kits.index(current)
#             next_kit = all_kits[idx + 1] if idx + 1 < len(all_kits) else "All kits completed!"
#             status_text = f"Next Kit: {next_kit} ({idx+1}/{len(all_kits)})"
#         else:
#             next_kit = all_kits[0] if all_kits else "No kits available"
#             status_text = f"Next Kit: {next_kit} (0/{len(all_kits)})" if all_kits else "No kits available"
        
#         self.next_label.config(text=status_text)
        
#         # Update button state
#         if not current or current not in all_kits:
#             self.start_button.config(state="disabled")
#         else:
#             self.start_button.config(state="normal")
    
#     def log(self, msg, color="black"):
#         """Add a message to the log with optional color"""
#         self.log_text.insert(END, msg + "\n")
#         self.log_text.see(END)
#         self.window.update_idletasks()
    
#     def update_progress(self, value, status=""):
#         """Update progress bar and status"""
#         self.progress['value'] = value
#         self.progress_label.config(text=f"{int(value)}%")
#         if status:
#             self.status_label.config(text=status)
#         self.window.update_idletasks()
    
#     def open_vscode(self):
#         """Open the app directory in VS Code"""
#         try:
#             subprocess.Popen(['code', str(app_dir)], shell=True)
#             self.log("✓ Opening VS Code...", "green")
#         except Exception as e:
#             self.log(f"✗ Failed to open VS Code: {str(e)}", "red")

#     def _install_software_sync(self):
#         """Helper method to install software synchronously"""
#         try:
#             software_script = root_dir / 'utils' / 'software-installer.py'
#             process = subprocess.run([sys.executable, str(software_script)], 
#                                    capture_output=True, text=True, cwd=root_dir,
#                                    timeout=600)  # 10 minute timeout
#             return process.returncode == 0
#         except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
#             return False

#     def install_software_only(self):
#         def run_software_install():
#             self.software_button.config(state="disabled")
#             self.start_button.config(state="disabled")
#             self.reset_button.config(state="disabled")
#             self.open_vscode_button.config(state="disabled")
#             self.update_progress(0, "Installing software dependencies...")
#             self.log("=== Starting software installation ===", "blue")
#             self.log("Installing from: utils/software-installer.py", "blue")
#             self.log("This will install: Node.js, Java JDK, Android SDK, Gradle, VS Code", "blue")
            
#             try:
#                 # Run software installer directly with more detailed output
#                 software_script = root_dir / 'utils' / 'software-installer.py'
#                 process = subprocess.Popen([sys.executable, str(software_script)], 
#                                          stdout=subprocess.PIPE, 
#                                          stderr=subprocess.STDOUT,
#                                          text=True, cwd=root_dir,
#                                          universal_newlines=True)
                
#                 # Stream output in real-time with better parsing
#                 for line in process.stdout:
#                     if line.strip():
#                         # Parse different types of log messages
#                         if "STEP:" in line:
#                             self.log(f"🔧 {line.replace('STEP:', '').strip()}", "blue")
#                         elif "PROGRESS:" in line:
#                             self.log(f"📦 {line.replace('PROGRESS:', '').strip()}", "black")
#                         elif "SUCCESS:" in line:
#                             self.log(f"✅ {line.replace('SUCCESS:', '').strip()}", "green")
#                         elif "ERROR:" in line:
#                             self.log(f"❌ {line.replace('ERROR:', '').strip()}", "red")
#                         else:
#                             self.log(line.strip())
                        
#                         # Update progress based on certain markers
#                         if "Installing Python" in line:
#                             self.update_progress(10, "Installing Python...")
#                         elif "Installing Node" in line:
#                             self.update_progress(20, "Installing Node.js...")
#                         elif "Installing JDK" in line:
#                             self.update_progress(30, "Installing Java JDK...")
#                         elif "Installing VSCode" in line:
#                             self.update_progress(40, "Installing VS Code...")
#                         elif "Setting up Android SDK" in line:
#                             self.update_progress(50, "Setting up Android SDK...")
#                         elif "Installing Gradle" in line:
#                             self.update_progress(70, "Installing Gradle...")
#                         elif "Configuring environment variables" in line:
#                             self.update_progress(90, "Configuring environment...")
                
#                 process.wait()
                
#                 if process.returncode == 0:
#                     self.log("✅ Software installation completed successfully!", "green")
#                     self.update_progress(100, "Software installation completed")
#                     messagebox.showinfo("Success", "Software installation completed successfully!")
#                     return True
#                 else:
#                     self.log("❌ Software installation failed", "red")
#                     self.update_progress(0, "Software installation failed")
#                     messagebox.showerror("Error", "Software installation failed. Check logs for details.")
#                     return False
#             except Exception as e:
#                 self.log(f"❌ Error during software installation: {str(e)}", "red")
#                 self.log(traceback.format_exc(), "red")
#                 self.update_progress(0, "Software installation failed")
#                 messagebox.showerror("Error", f"Software installation failed: {str(e)}")
#                 return False
#             finally:
#                 self.software_button.config(state="normal")
#                 self.start_button.config(state="normal")
#                 self.reset_button.config(state="normal")
#                 self.open_vscode_button.config(state="normal")
        
#         threading.Thread(target=run_software_install, daemon=True).start()
    
#     def reset_kit(self):
#         def run_reset():
#             self.reset_button.config(state="disabled")
#             self.update_progress(0, "Resetting kit...")
#             self.log("=== Resetting kit ===", "blue")
            
#             try:
#                 reset_script = root_dir / 'reset-kits.py'
#                 process = subprocess.Popen([sys.executable, str(reset_script)], 
#                                          stdout=subprocess.PIPE, 
#                                          stderr=subprocess.STDOUT,
#                                          text=True, cwd=root_dir)
                
#                 # Stream output in real-time
#                 for line in process.stdout:
#                     self.log(line.strip())
                
#                 process.wait()
                
#                 if process.returncode == 0:
#                     self.log("✓ Kit reset successfully!", "green")
#                     self.update_progress(100, "Kit reset completed")
#                     messagebox.showinfo("Success", "Kit reset completed successfully!")
#                 else:
#                     self.log("✗ Kit reset failed", "red")
#                     self.update_progress(0, "Kit reset failed")
#                     messagebox.showerror("Error", "Kit reset failed. Check logs for details.")
#             except Exception as e:
#                 self.log(f"Error during kit reset: {str(e)}", "red")
#                 self.log(traceback.format_exc(), "red")
#                 self.update_progress(0, "Kit reset failed")
#                 messagebox.showerror("Error", f"Kit reset failed: {str(e)}")
#             finally:
#                 self.reset_button.config(state="normal")
        
#         threading.Thread(target=run_reset, daemon=True).start()
    
#     def start_install(self):
#         self.start_button.config(state="disabled")
#         self.software_button.config(state="disabled")
#         self.reset_button.config(state="disabled")
#         self.open_vscode_button.config(state="disabled")
#         threading.Thread(target=self.run_installation, daemon=True).start()
    
#     def run_installation(self):
#         current = get_current_kit()
#         if not current:
#             self.log("No kits available.", "red")
#             return
#         try:
#             # Update progress
#             self.update_progress(0, "Checking software dependencies...")
#             self.log(f"=== Starting installation for kit: {current} ===", "blue")
            
#             # Check if software is installed
#             self.log("Checking if required software is installed...")
            
#             # Run software installer if needed - but wait for completion
#             software_installed = False
#             try:
#                 # Check for Node.js
#                 node_check = subprocess.run(['node', '--version'], capture_output=True, text=True)
#                 # Check for Java
#                 java_check = subprocess.run(['java', '-version'], capture_output=True, text=True)
                
#                 if node_check.returncode == 0 and java_check.returncode == 0:
#                     self.log("✓ Required software found.", "green")
#                     software_installed = True
#                 else:
#                     self.log("Some software missing, installing...", "orange")
#                     # Create a thread but wait for it to complete
#                     install_done = threading.Event()
#                     install_success = [False]  # Use list to store result from thread
                    
#                     def software_install_thread():
#                         try:
#                             success = self._install_software_sync()
#                             install_success[0] = success
#                         finally:
#                             install_done.set()
                    
#                     threading.Thread(target=software_install_thread, daemon=True).start()
                    
#                     # Wait for installation to complete with timeout
#                     install_done.wait(timeout=600)  # 10 minute timeout
#                     software_installed = install_success[0]
#             except (subprocess.CalledProcessError, FileNotFoundError) as e:
#                 self.log(f"Software check failed: {e}", "orange")
#                 self.log("Installing software dependencies...", "orange")
#                 software_installed = self._install_software_sync()
            
#             if not software_installed:
#                 self.log("✗ Software installation failed. Aborting kit installation.", "red")
#                 self.update_progress(0, "Software installation failed")
#                 return
            
#             # Update progress
#             self.update_progress(30, "Setting up kit...")
            
#             # Run setup-kit.py
#             self.log(f"Setting up kit: {current}")
#             setup_script = root_dir / 'utils' / 'setup-kit.py'
            
#             # Run with real-time output
#             process = subprocess.Popen([
#                 sys.executable, str(setup_script)
#             ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=root_dir)
            
#             # Stream output in real-time
#             for line in process.stdout:
#                 self.log(line.strip())
            
#             process.wait()
            
#             if process.returncode == 0:
#                 try:
#                     # Try to parse the last line as JSON
#                     last_line = line.strip() if line else ""
#                     if last_line and last_line.startswith('{') and last_line.endswith('}'):
#                         result_dict = json.loads(last_line)
#                         if not result_dict['success']:
#                             raise Exception(result_dict['message'])
#                         self.log("✓ Kit setup successful.", "green")
#                     else:
#                         self.log("✓ Setup completed successfully.", "green")
#                 except json.JSONDecodeError:
#                     self.log("✓ Setup completed but could not parse output.", "green")
#             else:
#                 raise Exception(f"Setup script failed with return code {process.returncode}")
            
#             # Update progress
#             self.update_progress(70, "Updating to next kit...")
            
#             # Update to next kit
#             all_kits = get_all_kits()
#             idx = all_kits.index(current)
#             next_kit = all_kits[idx + 1] if idx + 1 < len(all_kits) else ""
#             update_status(next_kit)
            
#             self.log(f"Updated status to next kit: {next_kit if next_kit else 'None'}")
            
#             # Update progress
#             self.update_progress(100, "Installation completed successfully!")
#             self.log("✓ Installation completed successfully!", "green")
#             messagebox.showinfo("Success", "Installation completed successfully!")
            
#             # Open VS Code after successful installation
#             self.open_vscode()
            
#             # Update UI
#             self.window.after(0, self.update_ui)
            
#         except Exception as e:
#             self.log(f"✗ Error during installation: {str(e)}", "red")
#             self.update_progress(0, "Installation failed")
#             messagebox.showerror("Error", f"Installation failed: {str(e)}")
            
#             # Revert on error
#             self.log("Reverting changes...")
#             try:
#                 reset_script = root_dir / 'reset-kits.py'
#                 subprocess.run([
#                     sys.executable, str(reset_script)
#                 ], check=True, capture_output=True, text=True, cwd=root_dir)
#                 self.log("✓ Changes reverted successfully.", "green")
#             except Exception as revert_error:
#                 self.log(f"✗ Error during revert: {str(revert_error)}", "red")
#         finally:
#             self.start_button.config(state="normal")
#             self.software_button.config(state="normal")
#             self.reset_button.config(state="normal")
#             self.open_vscode_button.config(state="normal")

# if __name__ == '__main__':
#     InstallerUI()