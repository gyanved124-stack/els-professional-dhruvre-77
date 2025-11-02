# emeelan-els-kits/utils/setup-kit.py
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def timestamp():
    return time.strftime("%H:%M:%S")

def get_root():
    return Path(__file__).parent.parent

root = get_root()
kits_dir = root / 'my-els-kits'
app_dir = root / 'emeelan-els-app'
apk_dir = root / 'my-els-apk'
apk_dir.mkdir(exist_ok=True)
status_path = root / 'status.json'

def print_step(message):
    """Print step messages that the UI can parse"""
    print(f"STEP: {message}")
    sys.stdout.flush()

def print_progress(message):
    """Print progress messages that the UI can parse"""
    print(f"PROGRESS: {message}")
    sys.stdout.flush()

def print_error(message):
    """Print error messages that the UI can parse"""
    print(f"ERROR: {message}")
    sys.stdout.flush()

def print_success(message):
    """Print success messages that the UI can parse"""
    print(f"SUCCESS: {message}")
    sys.stdout.flush()

def get_current_kit():
    if not status_path.exists():
        return ''
    with open(status_path) as f:
        data = json.load(f)
    return data.get('status', '')

def get_kit_config(kit_name):
    kit_dir = kits_dir / kit_name
    config_path = kit_dir / 'kit.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {"name": kit_name, "type": "android", "build_command": "assembleDebug"}

def merge_directories(src, dst):
    """Merge source directory into destination, excluding kit.json"""
    print_step(f"Merging kit files from {src.name} to {dst.name}")
    
    files_copied = 0
    for root_dir_path, dirs, files in os.walk(src):
        if 'kit.json' in files:
            files.remove('kit.json')
            
        rel_root = os.path.relpath(root_dir_path, src)
        dst_root = dst / rel_root
        dst_root.mkdir(parents=True, exist_ok=True)
        
        for file_name in files:
            src_file = Path(root_dir_path) / file_name
            dst_file = dst_root / file_name
            
            if dst_file.exists():
                with open(src_file, 'rb') as f1, open(dst_file, 'rb') as f2:
                    if f1.read() != f2.read():
                        shutil.copy2(src_file, dst_file)
                        files_copied += 1
                        print_progress(f"Updated: {file_name}")
            else:
                shutil.copy2(src_file, dst_file)
                files_copied += 1
                print_progress(f"Copied: {file_name}")
    
    print_success(f"Merged {files_copied} files successfully")
    return True

def run_npm_command(command, description, cwd=None):
    """Run an npm command with proper error handling and output"""
    if cwd is None:
        cwd = app_dir
    
    print_step(f"{description}...")
    
    try:
        # Run command with real-time output
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                output_lines.append(line)
                print_progress(line)
        
        return_code = process.poll()
        
        if return_code == 0:
            print_success(f"{description} completed successfully")
            return True
        else:
            print_error(f"{description} failed with exit code {return_code}")
            return False
            
    except Exception as e:
        print_error(f"{description} failed: {str(e)}")
        return False

def ensure_android_emulator_running():
    """Check if Android emulator is running and start one if not"""
    print_step("Checking Android emulator status...")
    
    try:
        # Check if any devices are connected
        result = subprocess.run(
            ['adb', 'devices'],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and any('device' in line for line in result.stdout.split('\n')):
            print_success("Android device/emulator is connected")
            return True
        else:
            print_progress("No Android devices found. Starting emulator...")
            
            # Start the emulator
            emulator_process = subprocess.Popen(
                ['emulator', '-avd', 'Pixel_6', '-no-snapshot-load', '-no-boot-anim', '-wipe-data'],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for emulator to start with progress updates
            for i in range(12):  # Wait up to 2 minutes
                time.sleep(10)
                result = subprocess.run(['adb', 'devices'], shell=True, capture_output=True, text=True)
                if any('device' in line for line in result.stdout.split('\n')):
                    print_success("Android emulator started successfully")
                    return True
                print_progress(f"Waiting for emulator... ({i*10} seconds)")
            
            print_error("Emulator failed to start within 2 minutes")
            return False
            
    except Exception as e:
        print_error(f"Failed to start emulator: {str(e)}")
        return False
    
def run_capacitor_command(command, description, cwd=None):
    """Run a Capacitor command with proper error handling"""
    if cwd is None:
        cwd = app_dir
    
    print_step(f"{description}...")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.stdout:
            for line in result.stdout.splitlines():
                if line.strip():
                    print_progress(line.strip())
        
        if result.stderr:
            for line in result.stderr.splitlines():
                if line.strip():
                    print_progress(line.strip())
        
        if result.returncode == 0:
            print_success(f"{description} completed successfully")
            return True
        else:
            print_error(f"{description} failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} timed out after 5 minutes")
        return False
    except Exception as e:
        print_error(f"{description} failed: {str(e)}")
        return False

def open_vs_code():
    """Open the app directory in VS Code"""
    try:
        print_step("Opening project in VS Code...")
        subprocess.Popen(['code', str(app_dir)], shell=True)
        print_success("VS Code opened successfully")
        return True
    except Exception as e:
        print_error(f"Failed to open VS Code: {str(e)}")
        return False

def launch_android_emulator():
    """Launch Android emulator if available"""
    try:
        print_step("Checking for Android emulator...")
        
        # First, try to list available emulators
        result = subprocess.run(
            ['emulator', '-list-avds'],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Emulators available, launch the first one
            emulator_name = result.stdout.splitlines()[0].strip()
            print_progress(f"Launching emulator: {emulator_name}")
            
            # Launch emulator in the background
            subprocess.Popen(['emulator', '-avd', emulator_name, '-no-snapshot-load'], 
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a bit for emulator to start
            time.sleep(10)
            print_success("Android emulator launched")
            return True
        else:
            print_progress("No Android emulators found or emulator command not available")
            return False
            
    except Exception as e:
        print_error(f"Failed to launch Android emulator: {str(e)}")
        return False

def run_on_android_emulator():
    """Run the app on Android emulator"""
    try:
        print_step("Running app on Android emulator...")
        
        # First, check if any emulator is running
        result = subprocess.run(
            ['adb', 'devices'],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and 'device' in result.stdout:
            # Device found, run the app
            android_dir = app_dir / 'android'
            os.chdir(android_dir)
            
            gradle_cmd = 'gradlew.bat' if os.name == 'nt' else './gradlew'
            subprocess.run([gradle_cmd, 'installDebug'], shell=True, check=True)
            
            print_success("App installed on Android emulator")
            return True
        else:
            print_progress("No Android device/emulator found. Please start an emulator manually.")
            return False
            
    except Exception as e:
        print_error(f"Failed to run app on Android emulator: {str(e)}")
        return False

def build_android_apk(kit_name):
    """Build the Android APK and optionally install it on emulator/device."""
    android_dir = app_dir / "android"
    gradle_cmd = "gradlew.bat" if os.name == "nt" else "./gradlew"
    apk_path = android_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"

    print(f"[{timestamp()}] Building Android APK for {kit_name} ...")
    sys.stdout.flush()

    # Run Gradle assemble
    result = subprocess.run([gradle_cmd, "assembleDebug"], capture_output=True, text=True, cwd=android_dir)

    if result.returncode != 0:
        print(f"[{timestamp()}] ERROR: Gradle build failed")
        print(result.stdout)
        print(result.stderr)
        sys.stdout.flush()
        sys.exit(1)

    # Confirm APK exists
    if apk_path.exists():
        print(f"[{timestamp()}] APK created: {apk_path}")
        sys.stdout.flush()
    else:
        print(f"[{timestamp()}] ERROR: APK build failed (no file found at {apk_path})")
        sys.stdout.flush()
        sys.exit(1)

    # Try installing on emulator/device (optional step)
    install_result = subprocess.run([gradle_cmd, "installDebug"], capture_output=True, text=True, cwd=android_dir)

    if install_result.returncode != 0:
        print(f"[{timestamp()}] WARNING: APK installation failed (but APK was built successfully)")
        sys.stdout.flush()
    else:
        print(f"[{timestamp()}] SUCCESS: APK installed on emulator/device")
        sys.stdout.flush()

    # ✅ Always report success if APK exists
    if apk_path.exists():
        print(f"[{timestamp()}] APK build completed successfully")
        print(json.dumps({"success": True, "message": f"Setup completed successfully for {kit_name}"}))
        sys.stdout.flush()
        sys.exit(0)
    else:
        print(f"[{timestamp()}] ERROR: APK build failed unexpectedly")
        sys.stdout.flush()
        sys.exit(1)


def setup_kit():
    current_kit = get_current_kit()
    if not current_kit:
        return {'success': False, 'message': 'No kit to setup'}

    kit_dir = kits_dir / current_kit
    if not kit_dir.exists():
        return {'success': False, 'message': f'Kit {current_kit} not found'}

    print_step(f"Starting setup for kit: {current_kit}")
    kit_config = get_kit_config(current_kit)
    prev_cwd = os.getcwd()
    
    try:
        # Step 1: Merge kit files into app
        if not merge_directories(kit_dir, app_dir):
            return {'success': False, 'message': 'Failed to merge kit files'}

        # Change to app directory
        os.chdir(app_dir)

        # Step 2: Install npm dependencies if package.json exists
        if (app_dir / 'package.json').exists():
            if not run_npm_command('npm install', 'NPM dependencies'):
                return {'success': False, 'message': 'npm install failed'}
        else:
            print_progress("No package.json found, skipping npm install")

        # Step 3: Build React app if package.json exists
        if (app_dir / 'package.json').exists():
            if not run_npm_command('npm run build', 'React application'):
                return {'success': False, 'message': 'npm run build failed'}
        else:
            print_progress("No package.json found, skipping React build")

        # Step 4: Start app in browser (non-blocking)
        if (app_dir / 'package.json').exists():
            try:
                print_step("Starting web application in browser")
                subprocess.Popen(['npm', 'start'], shell=True, cwd=str(app_dir))
                print_success("Web application started")
                time.sleep(3)  # Give it time to start
            except Exception as e:
                print_error(f"Failed to start web app: {e}")

        # Step 5: Open VS Code with the project
        open_vs_code()

        # Step 6: Android-specific setup
        if kit_config.get('type') == 'android':
            capacitor_config = app_dir / 'capacitor.config.json'
            if capacitor_config.exists():
                print_step("Setting up Android platform")
                
                android_dir = app_dir / 'android'
                if not android_dir.exists():
                    if not run_capacitor_command('npx cap add android', 'Adding Android platform'):
                        return {'success': False, 'message': 'Capacitor Android add failed'}
                
                # Sync Capacitor
                if not run_capacitor_command('npx cap sync', 'Syncing Capacitor'):
                    return {'success': False, 'message': 'Capacitor sync failed'}

                # Open Android Studio after sync
                if not run_capacitor_command('npx cap open android', 'Opening Android Studio'):
                    print_error("Failed to open Android Studio, continuing anyway")

                # Launch Android emulator only after Capacitor setup
                print_step("Launching Android emulator...")
                emulator_started = ensure_android_emulator_running()
                if not emulator_started:
                    print_error("Android emulator failed to launch, continuing setup")

                # Install and run the app on the emulator (if started)
                if emulator_started:
                    if not run_on_android_emulator():
                        print_error("Failed to install/run app on emulator")
                else:
                    print_progress("Skipping app install/run since emulator isn't running")

                # Build the Android APK
                if not build_android_apk(current_kit):
                    return {'success': False, 'message': 'APK build failed'}
                    
            else:
                print_progress("No Capacitor config found, skipping Android setup")
        else:
            print_progress("Kit type is not Android, skipping Android-specific setup")

        return {'success': True, 'message': f'Setup completed successfully for {current_kit}'}

    except Exception as e:
        print_error(f"Setup failed: {str(e)}")
        
        # Attempt rollback
        try:
            print_step("Attempting to rollback changes")
            reset_script = root / 'reset-kits.py'
            subprocess.run(['python', str(reset_script)], 
                         check=True, capture_output=True, text=True, cwd=root)
            print_success("Rollback completed")
        except Exception as rollback_error:
            print_error(f"Rollback failed: {str(rollback_error)}")
        
        return {'success': False, 'message': str(e)}
    finally:
        os.chdir(prev_cwd)

if __name__ == '__main__':
    try:
        result = setup_kit()
        print(json.dumps(result))
    except KeyboardInterrupt:
        print_error("Setup interrupted by user")
        print(json.dumps({'success': False, 'message': 'Setup interrupted by user'}))
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        print(json.dumps({'success': False, 'message': f'Unexpected error: {str(e)}'}))

# # emeelan-els-kits/utils/setup-kit.py
# import json
# import os
# import shutil
# import subprocess
# import sys
# import time
# from pathlib import Path

# def get_root():
#     return Path(__file__).parent.parent

# root = get_root()
# kits_dir = root / 'my-els-kits'
# app_dir = root / 'emeelan-els-app'
# apk_dir = root / 'my-els-apk'
# apk_dir.mkdir(exist_ok=True)
# status_path = root / 'status.json'

# def print_step(message):
#     """Print step messages that the UI can parse"""
#     print(f"STEP: {message}")
#     sys.stdout.flush()

# def print_progress(message):
#     """Print progress messages that the UI can parse"""
#     print(f"PROGRESS: {message}")
#     sys.stdout.flush()

# def print_error(message):
#     """Print error messages that the UI can parse"""
#     print(f"ERROR: {message}")
#     sys.stdout.flush()

# def print_success(message):
#     """Print success messages that the UI can parse"""
#     print(f"SUCCESS: {message}")
#     sys.stdout.flush()

# def get_current_kit():
#     if not status_path.exists():
#         return ''
#     with open(status_path) as f:
#         data = json.load(f)
#     return data.get('status', '')

# def get_kit_config(kit_name):
#     kit_dir = kits_dir / kit_name
#     config_path = kit_dir / 'kit.json'
#     if config_path.exists():
#         with open(config_path) as f:
#             return json.load(f)
#     return {"name": kit_name, "type": "android", "build_command": "assembleDebug"}

# def merge_directories(src, dst):
#     """Merge source directory into destination, excluding kit.json"""
#     print_step(f"Merging kit files from {src.name} to {dst.name}")
    
#     files_copied = 0
#     for root_dir_path, dirs, files in os.walk(src):
#         if 'kit.json' in files:
#             files.remove('kit.json')
            
#         rel_root = os.path.relpath(root_dir_path, src)
#         dst_root = dst / rel_root
#         dst_root.mkdir(parents=True, exist_ok=True)
        
#         for file_name in files:
#             src_file = Path(root_dir_path) / file_name
#             dst_file = dst_root / file_name
            
#             if dst_file.exists():
#                 with open(src_file, 'rb') as f1, open(dst_file, 'rb') as f2:
#                     if f1.read() != f2.read():
#                         shutil.copy2(src_file, dst_file)
#                         files_copied += 1
#                         print_progress(f"Updated: {file_name}")
#             else:
#                 shutil.copy2(src_file, dst_file)
#                 files_copied += 1
#                 print_progress(f"Copied: {file_name}")
    
#     print_success(f"Merged {files_copied} files successfully")
#     return True

# def run_npm_command(command, description, cwd=None):
#     """Run an npm command with proper error handling and output"""
#     if cwd is None:
#         cwd = app_dir
    
#     print_step(f"{description}...")
    
#     try:
#         # Run command with real-time output
#         process = subprocess.Popen(
#             command,
#             shell=True,
#             cwd=str(cwd),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             universal_newlines=True
#         )
        
#         output_lines = []
#         while True:
#             output = process.stdout.readline()
#             if output == '' and process.poll() is not None:
#                 break
#             if output:
#                 line = output.strip()
#                 output_lines.append(line)
#                 print_progress(line)
        
#         return_code = process.poll()
        
#         if return_code == 0:
#             print_success(f"{description} completed successfully")
#             return True
#         else:
#             print_error(f"{description} failed with exit code {return_code}")
#             return False
            
#     except Exception as e:
#         print_error(f"{description} failed: {str(e)}")
#         return False

# def ensure_android_emulator_running():
#     """Check if Android emulator is running and start one if not"""
#     print_step("Checking Android emulator status...")
    
#     try:
#         # Check if any devices are connected
#         result = subprocess.run(
#             ['adb', 'devices'],
#             shell=True,
#             capture_output=True,
#             text=True
#         )
        
#         if result.returncode == 0 and any('device' in line for line in result.stdout.split('\n')):
#             print_success("Android device/emulator is connected")
#             return True
#         else:
#             print_progress("No Android devices found. Starting emulator...")
            
#             # Start the emulator
#             emulator_process = subprocess.Popen(
#                 ['emulator', '-avd', 'Pixel_6', '-no-snapshot-load', '-no-boot-anim', '-wipe-data'],
#                 shell=True,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL
#             )
            
#             # Wait for emulator to start with progress updates
#             for i in range(12):  # Wait up to 2 minutes
#                 time.sleep(10)
#                 result = subprocess.run(['adb', 'devices'], shell=True, capture_output=True, text=True)
#                 if any('device' in line for line in result.stdout.split('\n')):
#                     print_success("Android emulator started successfully")
#                     return True
#                 print_progress(f"Waiting for emulator... ({i*10} seconds)")
            
#             print_error("Emulator failed to start within 2 minutes")
#             return False
            
#     except Exception as e:
#         print_error(f"Failed to start emulator: {str(e)}")
#         return False
    
# def run_capacitor_command(command, description, cwd=None):
#     """Run a Capacitor command with proper error handling"""
#     if cwd is None:
#         cwd = app_dir
    
#     print_step(f"{description}...")
    
#     try:
#         result = subprocess.run(
#             command,
#             shell=True,
#             cwd=str(cwd),
#             capture_output=True,
#             text=True,
#             timeout=300  # 5 minute timeout
#         )
        
#         if result.stdout:
#             for line in result.stdout.splitlines():
#                 if line.strip():
#                     print_progress(line.strip())
        
#         if result.stderr:
#             for line in result.stderr.splitlines():
#                 if line.strip():
#                     print_progress(line.strip())
        
#         if result.returncode == 0:
#             print_success(f"{description} completed successfully")
#             return True
#         else:
#             print_error(f"{description} failed with exit code {result.returncode}")
#             return False
            
#     except subprocess.TimeoutExpired:
#         print_error(f"{description} timed out after 5 minutes")
#         return False
#     except Exception as e:
#         print_error(f"{description} failed: {str(e)}")
#         return False

# def open_vs_code():
#     """Open the app directory in VS Code"""
#     try:
#         print_step("Opening project in VS Code...")
#         subprocess.Popen(['code', str(app_dir)], shell=True)
#         print_success("VS Code opened successfully")
#         return True
#     except Exception as e:
#         print_error(f"Failed to open VS Code: {str(e)}")
#         return False

# def launch_android_emulator():
#     """Launch Android emulator if available"""
#     try:
#         print_step("Checking for Android emulator...")
        
#         # First, try to list available emulators
#         result = subprocess.run(
#             ['emulator', '-list-avds'],
#             shell=True,
#             capture_output=True,
#             text=True
#         )
        
#         if result.returncode == 0 and result.stdout.strip():
#             # Emulators available, launch the first one
#             emulator_name = result.stdout.splitlines()[0].strip()
#             print_progress(f"Launching emulator: {emulator_name}")
            
#             # Launch emulator in the background
#             subprocess.Popen(['emulator', '-avd', emulator_name, '-no-snapshot-load'], 
#                            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
#             # Wait a bit for emulator to start
#             time.sleep(10)
#             print_success("Android emulator launched")
#             return True
#         else:
#             print_progress("No Android emulators found or emulator command not available")
#             return False
            
#     except Exception as e:
#         print_error(f"Failed to launch Android emulator: {str(e)}")
#         return False

# def run_on_android_emulator():
#     """Run the app on Android emulator"""
#     try:
#         print_step("Running app on Android emulator...")
        
#         # First, check if an emulator is running
#         result = subprocess.run(
#             ['adb', 'devices'],
#             shell=True,
#             capture_output=True,
#             text=True
#         )
        
#         if result.returncode == 0 and 'device' in result.stdout:
#             # Device found, run the app
#             android_dir = app_dir / 'android'
#             os.chdir(android_dir)
            
#             gradle_cmd = 'gradlew.bat' if os.name == 'nt' else './gradlew'
#             subprocess.run([gradle_cmd, 'installDebug'], shell=True, check=True)
            
#             print_success("App installed on Android emulator")
#             return True
#         else:
#             print_progress("No Android device/emulator found. Please start an emulator manually.")
#             return False
            
#     except Exception as e:
#         print_error(f"Failed to run app on Android emulator: {str(e)}")
#         return False

# def build_android_apk(current_kit):
#     """Build Android APK with proper progress tracking"""
#     android_dir = app_dir / 'android'
#     if not android_dir.exists():
#         print_error("Android directory not found")
#         return False
    
#     print_step("Building Android APK")
#     prev_cwd = os.getcwd()
    
#     try:
#         os.chdir(android_dir)
#         gradle_cmd = 'gradlew.bat' if os.name == 'nt' else './gradlew'
        
#         # Clean first
#         print_progress("Cleaning Android project...")
#         clean_result = subprocess.run([gradle_cmd, 'clean'], 
#                                     shell=True, capture_output=True, text=True, timeout=180)
        
#         if clean_result.returncode != 0:
#             print_error(f"Gradle clean failed: {clean_result.stderr}")
#             return False
        
#         print_success("Android project cleaned")
#         time.sleep(2)
        
#         # Build APK with real-time progress
#         print_progress("Starting APK build (this may take several minutes)...")
        
#         build_process = subprocess.Popen(
#             [gradle_cmd, 'assembleDebug', '--console=plain'],
#             shell=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             universal_newlines=True
#         )
        
#         task_count = 0
#         build_output = []
#         while True:
#             output = build_process.stdout.readline()
#             if output == '' and build_process.poll() is not None:
#                 break
#             if output:
#                 line = output.strip()
#                 if line:
#                     print(line)  # Print raw output for UI to capture
#                     build_output.append(line)
#                     if line.startswith('> Task :'):
#                         task_count += 1
#                         if task_count % 5 == 0:  # Update every 5 tasks to avoid spam
#                             print_progress(f"Building... ({task_count} tasks completed)")
#                     elif "BUILD SUCCESSFUL" in line:
#                         print_success("APK build completed successfully")
#                     elif "BUILD FAILED" in line:
#                         print_error("APK build failed")
        
#         return_code = build_process.poll()
        
#         if return_code == 0:
#             # Copy APK to output directory
#             apk_path = android_dir / 'app' / 'build' / 'outputs' / 'apk' / 'debug' / 'app-debug.apk'
#             if apk_path.exists():
#                 version = "1.0.0"
#                 if (app_dir / 'package.json').exists():
#                     try:
#                         with open(app_dir / 'package.json') as f:
#                             version = json.load(f).get('version', '1.0.0')
#                     except:
#                         pass
                
#                 dst_apk = apk_dir / f'els-{current_kit}-{version}-db.apk'
#                 shutil.copy2(apk_path, dst_apk)
#                 print_success(f"APK created: {dst_apk.name}")
                
#                 # Try to install on emulator if available
#                 if ensure_android_emulator_running():
#                     try:
#                         print_step("Installing APK on emulator...")
#                         install_result = subprocess.run(
#                             [gradle_cmd, 'installDebug'],
#                             shell=True,
#                             capture_output=True,
#                             text=True,
#                             timeout=120
#                         )
                        
#                         if install_result.returncode == 0:
#                             print_success("APK installed successfully on emulator")
#                         else:
#                             print_progress("APK installation failed (but APK was built successfully)")
#                     except:
#                         print_progress("APK installation skipped (but APK was built successfully)")
                
#                 return True
#             else:
#                 print_error("APK file not found after successful build")
#                 return False
#         else:
#             print_error(f"Gradle build failed with exit code {return_code}")
#             return False
            
#     except subprocess.TimeoutExpired:
#         print_error("Gradle build timed out")
#         return False
#     except Exception as e:
#         print_error(f"APK build error: {str(e)}")
#         return False
#     finally:
#         os.chdir(prev_cwd)
        

# def setup_kit():
#     current_kit = get_current_kit()
#     if not current_kit:
#         return {'success': False, 'message': 'No kit to setup'}

#     kit_dir = kits_dir / current_kit
#     if not kit_dir.exists():
#         return {'success': False, 'message': f'Kit {current_kit} not found'}

#     print_step(f"Starting setup for kit: {current_kit}")
#     kit_config = get_kit_config(current_kit)
#     prev_cwd = os.getcwd()
    
#     try:
#         # Step 1: Merge kit files into app
#         if not merge_directories(kit_dir, app_dir):
#             return {'success': False, 'message': 'Failed to merge kit files'}

#         # Change to app directory
#         os.chdir(app_dir)

#         # Step 2: Install npm dependencies if package.json exists
#         if (app_dir / 'package.json').exists():
#             if not run_npm_command('npm install', 'Installing NPM dependencies'):
#                 return {'success': False, 'message': 'npm install failed'}
#         else:
#             print_progress("No package.json found, skipping npm install")

#         # Step 3: Build React app if package.json exists
#         if (app_dir / 'package.json').exists():
#             if not run_npm_command('npm run build', 'Building React application'):
#                 return {'success': False, 'message': 'npm run build failed'}
#         else:
#             print_progress("No package.json found, skipping React build")

#         # Step 4: Start app in browser (non-blocking)
#         if (app_dir / 'package.json').exists():
#             try:
#                 print_step("Starting web application in browser")
#                 subprocess.Popen(['npm', 'start'], shell=True, cwd=str(app_dir))
#                 print_success("Web application started")
#                 time.sleep(3)  # Give it time to start
#             except Exception as e:
#                 print_error(f"Failed to start web app: {e}")

#         # Step 5: Open VS Code with the project
#         open_vs_code()

#         # Step 6: Android-specific setup
#         if kit_config.get('type') == 'android':
#             capacitor_config = app_dir / 'capacitor.config.json'
#             if capacitor_config.exists():
#                 print_step("Setting up Android platform")
                
#                 android_dir = app_dir / 'android'
#                 if not android_dir.exists():
#                     if not run_capacitor_command('npx cap add android', 'Adding Android platform'):
#                         return {'success': False, 'message': 'Capacitor Android add failed'}
                
#                 # Sync Capacitor
#                 if not run_capacitor_command('npx cap sync', 'Syncing Capacitor'):
#                     return {'success': False, 'message': 'Capacitor sync failed'}

#                 # Open Android Studio after sync
#                 if not run_capacitor_command('npx cap open android', 'Opening Android Studio'):
#                     print_error("Failed to open Android Studio, continuing anyway")

#                 # Launch Android emulator only after Capacitor setup
#                 print_step("Launching Android emulator...")
#                 emulator_started = ensure_android_emulator_running()
#                 if not emulator_started:
#                     print_error("Android emulator failed to launch, continuing setup")

#                 # Install and run the app on the emulator (if started)
#                 if emulator_started:
#                     if not run_on_android_emulator():
#                         print_error("Failed to install/run app on emulator")
#                 else:
#                     print_progress("Skipping app install/run since emulator isn't running")

#                 # Build the Android APK
#                 if not build_android_apk(current_kit):
#                     return {'success': False, 'message': 'APK build failed'}
                    
#             else:
#                 print_progress("No Capacitor config found, skipping Android setup")
#         else:
#             print_progress("Kit type is not Android, skipping Android-specific setup")

#         return {'success': True, 'message': f'Setup completed successfully for {current_kit}'}

#     except Exception as e:
#         print_error(f"Setup failed: {str(e)}")
        
#         # Attempt rollback
#         try:
#             print_step("Attempting to rollback changes")
#             reset_script = root / 'reset-kits.py'
#             subprocess.run(['python', str(reset_script)], 
#                          check=True, capture_output=True, text=True, cwd=root)
#             print_success("Rollback completed")
#         except Exception as rollback_error:
#             print_error(f"Rollback failed: {str(rollback_error)}")
        
#         return {'success': False, 'message': str(e)}
#     finally:
#         os.chdir(prev_cwd)

# if __name__ == '__main__':
#     try:
#         result = setup_kit()
#         print(json.dumps(result))
#     except KeyboardInterrupt:
#         print_error("Setup interrupted by user")
#         print(json.dumps({'success': False, 'message': 'Setup interrupted by user'}))
#     except Exception as e:
#         print_error(f"Unexpected error: {str(e)}")
#         print(json.dumps({'success': False, 'message': f'Unexpected error: {str(e)}'}))