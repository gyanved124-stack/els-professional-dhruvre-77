# emeelan-els-kits/utils/software-installer.py
#!/usr/bin/env python3
"""
software-installer.py

Complete automated software installation for EMEELAN ELS Kits
Includes silent Android Studio installation, SDK setup, and emulator creation
"""
from __future__ import annotations
import ctypes
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
import urllib.request
import json
import shutil

# ---------------- CONFIG ----------------
LOG_DIR = Path(r"C:\DevInstaller")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "install_log.txt"

# Android configuration
ANDROID_SDK_ROOT = Path(r"C:\Android\Sdk")
ANDROID_HOME = ANDROID_SDK_ROOT  # Use ANDROID_HOME as primary
ANDROID_STUDIO_PATH = Path(r"C:\Program Files\Android\Android Studio")
GRADLE_INSTALL_DIR = Path(r"C:\Gradle")

# Package candidates for winget
CANDIDATES = {
    "python": ["Python.Python.3.11", "Python.Python.3.12", "Python.Python.3.10"],
    "node": ["OpenJS.NodeJS", "OpenJS.NodeJS.LTS", "CoreyButler.NVMforWindows"],
    "jdk": [
        "EclipseAdoptium.Temurin.17.JDK",
        "Azul.Zulu.17.JDK",
        "Amazon.Corretto.17.JDK",
        "Oracle.JDK.17",
        "Microsoft.OpenJDK.17"
    ],
    "vscode": ["Microsoft.VisualStudioCode", "VSCodium.VSCodium"],
    "gradle": ["Gradle.Gradle", "gradle.gradle"],
    "android-studio": ["Google.AndroidStudio", "Google.AndroidStudio.Canary"]
}

WINGET_FLAGS = "--accept-source-agreements --accept-package-agreements -h --silent"

# ---------------- In-memory logging ----------------
# Removed _memory_log, now logging directly to file

def log_to_file(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        tmp = Path(tempfile.gettempdir()) / f"installer_log_{int(time.time())}.txt"
        with tmp.open("w", encoding="utf-8") as f:
            f.write(line)
        print(f"Failed to write to {LOG_FILE}. Wrote to {tmp} instead: {e}")

# ---------------- Privilege / elevation ----------------
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def elevate_and_exit():
    script = sys.executable
    # Get absolute path of the current script
    script_path = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{script_path}"'] + sys.argv[1:])
    log_to_file(f"Requesting elevation: {script} {params}")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
    print("UAC prompt opened — please accept to continue (elevated run will proceed).")
    sys.exit(0)

# ---------------- Subprocess streaming ----------------
def run_cmd_capture(cmd: str, timeout: Optional[int] = None) -> tuple[int, str]:
    """Run command and capture output"""
    log_to_file(f"CMD: {cmd}")
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        log_to_file(f"Failed to launch command: {cmd} -> {e}")
        return -1, str(e)

    out_buf = []
    try:
        while True:
            o = proc.stdout.readline()
            if o:
                out_buf.append(o)
                log_to_file("STDOUT: " + o.rstrip())
            e = proc.stderr.readline()
            if e:
                out_buf.append(e)
                log_to_file("STDERR: " + e.rstrip())
            if proc.poll() is not None:
                rem_out, rem_err = proc.communicate(timeout=5 if timeout else None)
                if rem_out:
                    out_buf.append(rem_out)
                    for line in rem_out.splitlines():
                        log_to_file("STDOUT: " + line)
                if rem_err:
                    out_buf.append(rem_err)
                    for line in rem_err.splitlines():
                        log_to_file("STDERR: " + line)
                break
            time.sleep(0.05)
    except Exception as ex:
        proc.kill()
        log_to_file(f"Exception while running command: {ex}")
    rc = proc.returncode if proc.returncode is not None else -1
    log_to_file(f"CMD EXIT {rc}: {cmd}")
    return rc, "".join(out_buf)

# ---------------- Android Studio Installation ----------------
def install_android_studio_with_winget():
    """Install Android Studio using winget"""
    log_to_file("Checking for Android Studio...")
    rc, output = run_cmd_capture('winget list --id Google.AndroidStudio', timeout=30)
    if rc == 0 and "Google.AndroidStudio" in output:
        log_to_file("Android Studio is already installed.")
        return True
    
    log_to_file("Installing Android Studio via winget...")
    rc, output = run_cmd_capture(f'winget install --id Google.AndroidStudio -e --silent --accept-source-agreements --accept-package-agreements', timeout=1200)
    
    if rc == 0:
        log_to_file("Android Studio installed successfully via winget")
        return True
    else:
        log_to_file(f"Android Studio installation via winget failed: {output}")
        return False
    
# ---------------- Android SDK Setup ----------------
def setup_android_sdk_complete():
    """Complete Android SDK setup with all necessary components"""
    # Create SDK directory
    ANDROID_HOME.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    os.environ["ANDROID_HOME"] = str(ANDROID_HOME)
    os.environ["ANDROID_SDK_ROOT"] = str(ANDROID_HOME)  # For compatibility
    
    # Add to PATH
    path_additions = [
        str(ANDROID_HOME / "platform-tools"),
        str(ANDROID_HOME / "tools"),
        str(ANDROID_HOME / "emulator"),
        str(ANDROID_HOME / "cmdline-tools" / "latest" / "bin")
    ]
    
    for path in path_additions:
        if path not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + path
    
    # Download and install latest SDK command-line tools
    cmdline_tools_url = "https://dl.google.com/android/repository/commandlinetools-win-13114758_latest.zip"
    cmdline_tools_zip = str(ANDROID_HOME / "cmdline-tools.zip")
    cmdline_tools_dir = ANDROID_HOME / "cmdline-tools" / "latest"
    sdkmanager_path = cmdline_tools_dir / "bin" / "sdkmanager.bat"
    
    if not sdkmanager_path.exists():
        log_to_file("Downloading Android SDK command-line tools...")
        try:
            urllib.request.urlretrieve(cmdline_tools_url, cmdline_tools_zip)
            log_to_file("Extracting command-line tools...")
            with zipfile.ZipFile(cmdline_tools_zip, "r") as zip_ref:
                extract_path = str(ANDROID_HOME / "cmdline-tools" / "temp")
                zip_ref.extractall(extract_path)
            # Move the extracted cmdline-tools into 'latest'
            extracted_dir = Path(extract_path) / "cmdline-tools"
            if cmdline_tools_dir.exists():
                shutil.rmtree(str(cmdline_tools_dir))
            shutil.move(str(extracted_dir), str(cmdline_tools_dir))
            shutil.rmtree(extract_path)
            os.remove(cmdline_tools_zip)
            log_to_file(f"Command-line tools installed at {cmdline_tools_dir}")
        except Exception as e:
            log_to_file(f"Failed to install command-line tools: {e}")
            return False
    else:
        log_to_file("Android SDK command-line tools already installed.")
    
    # Accept licenses
    log_to_file("Accepting Android SDK licenses...")
    rc, _ = run_cmd_capture(f'"{sdkmanager_path}" --licenses', timeout=300)
    if rc != 0:
        log_to_file("Failed to accept licenses")
    
    # Install necessary packages
    packages = [
        "platform-tools",
        "platforms;android-33",
        "build-tools;33.0.2",
        "system-images;android-33;google_apis;x86_64",
        "emulator"
    ]
    
    for package in packages:
        log_to_file(f"Installing {package}...")
        rc, output = run_cmd_capture(f'"{sdkmanager_path}" "{package}"', timeout=600)
        if rc != 0:
            log_to_file(f"Failed to install {package}: {output}")
            return False
    
    return True

# ---------------- AVD Creation ----------------
def create_android_avd_automated():
    """Create Android Virtual Device without manual intervention"""
    # Find avdmanager path
    avdmanager_path = None
    possible_paths = [
        ANDROID_HOME / "cmdline-tools" / "latest" / "bin" / "avdmanager.bat",
        Path(r"C:\Program Files\Android\Android SDK Command Line Tools\tools\bin\avdmanager.bat")
    ]
    
    for path in possible_paths:
        if path.exists():
            avdmanager_path = path
            break
    
    if not avdmanager_path:
        log_to_file("avdmanager not found")
        return False
    
    # Create AVD
    avd_name = "Pixel_6"
    system_image = "system-images;android-33;google_apis;x86_64"
    device = "pixel"
    
    # Delete existing AVD if exists
    run_cmd_capture(f'"{avdmanager_path}" delete avd -n {avd_name}')
    
    # Create new AVD
    rc, output = run_cmd_capture(f'"{avdmanager_path}" create avd -n {avd_name} -k "{system_image}" --device {device} --force', timeout=300)
    
    if rc == 0:
        log_to_file("AVD created successfully")
        return True
    else:
        log_to_file(f"AVD creation failed: {output}")
        return False
    
# ---------------- Emulator Startup ----------------
# Removed as per instructions

# ---------------- Android Setup Verification ----------------
def verify_android_installation():
    """Verify that Android installation is complete and working"""
    checks = [
        ("adb", "adb --version"),
        ("emulator", "emulator -version"),
        ("sdkmanager", "sdkmanager --version")
    ]
    
    for tool, cmd in checks:
        rc, output = run_cmd_capture(cmd, timeout=30)
        if rc != 0:
            log_to_file(f"Tool {tool} verification failed")
            return False
    
    return True

# ---------------- Complete Android Setup ----------------
def automated_android_setup():
    """Complete automated Android Studio and emulator setup"""
    log_to_file("Starting automated Android setup...")
    
    # Step 1: Install Android Studio using winget
    if not install_android_studio_with_winget():
        log_to_file("Android Studio installation failed")
        return False
    
    # Step 2: Setup Android SDK
    if not setup_android_sdk_complete():
        log_to_file("Android SDK setup failed")
        return False
    
    # Step 3: Create virtual device
    if not create_android_avd_automated():
        log_to_file("AVD creation failed")
        return False
    
    # Step 4: Start emulator removed
    
    # Step 5: Verify installation
    if verify_android_installation():
        log_to_file("Android setup completed successfully")
        return True
    else:
        log_to_file("Android setup verification failed")
        return False

# ---------------- Winget Helpers ----------------
def winget_show_exists(id_: str) -> bool:
    rc, out = run_cmd_capture(f'winget show --id {id_}', timeout=30)
    return rc == 0

def winget_list_contains(id_or_name: str) -> bool:
    rc, out = run_cmd_capture(f'winget list --id {id_or_name}', timeout=20)
    return rc == 0 and id_or_name in out

def pick_first_available(candidates: list[str]) -> Optional[str]:
    for cand in candidates:
        if winget_show_exists(cand):
            log_to_file(f"Found candidate: {cand}")
            return cand
    log_to_file(f"No candidate found in list: {candidates}")
    return None

# ---------------- Package Installation ----------------
def install_package(name: str, candidate_id: Optional[str]) -> Dict[str, Any]:
    """High-level installation step"""
    result: Dict[str, Any] = {"id": candidate_id, "ok": False, "reason": None}
    log_to_file(f"Install step for {name} using id {candidate_id}")

    # detect installed by winget list
    if candidate_id and winget_list_contains(candidate_id):
        result["ok"] = True
        result["reason"] = "already_installed_winget"
        log_to_file(f"{name}: detected by winget list ({candidate_id})")
        return result

    # detect by common commands
    if name.lower().startswith("python"):
        rc_py, _ = run_cmd_capture("python --version")
        if rc_py == 0:
            result["ok"] = True
            result["reason"] = "already_installed_command"
            log_to_file("Python present on PATH (python --version detected).")
            return result
        rc_py2, _ = run_cmd_capture("py -3 --version")
        if rc_py2 == 0:
            result["ok"] = True
            result["reason"] = "already_installed_command"
            log_to_file("Python present on PATH (py -3 --version detected).")
            return result

    if name.lower().startswith("node"):
        rc_n, _ = run_cmd_capture("node --version")
        if rc_n == 0:
            result["ok"] = True
            result["reason"] = "already_installed_command"
            log_to_file("Node present on PATH (node --version detected).")
            return result

    if "vscode" in name.lower():
        rc_code, _ = run_cmd_capture("code --version")
        if rc_code == 0:
            result["ok"] = True
            result["reason"] = "already_installed_command"
            log_to_file("VS Code present on PATH (code --version detected).")
            return result

    if "android" in name.lower():
        # Check if Android Studio is already installed
        studio_path = Path(r"C:\Program Files\Android\Android Studio\bin\studio64.exe")
        if studio_path.exists():
            result["ok"] = True
            result["reason"] = "already_installed_path"
            log_to_file("Android Studio found in Program Files")
            return result

    if candidate_id is None:
        result["reason"] = "no_candidate"
        log_to_file(f"No winget candidate for {name}; skipping install.")
        return result

    # attempt install
    log_to_file(f"Running winget install for {name} (id={candidate_id})")
    rc, out = run_cmd_capture(f'winget install -e --id {candidate_id} {WINGET_FLAGS}', timeout=60*30)
    if rc == 0:
        result["ok"] = True
        result["reason"] = "installed"
        log_to_file(f"{name} installed successfully via winget.")
        return result

    # retry once
    log_to_file(f"{name} first install failed (rc={rc}). Retrying once after brief wait.")
    time.sleep(3)
    rc2, out2 = run_cmd_capture(f'winget install -e --id {candidate_id} {WINGET_FLAGS}', timeout=60*30)
    if rc2 == 0:
        result["ok"] = True
        result["reason"] = "installed_on_retry"
        log_to_file(f"{name} installed on retry.")
        return result

    # failure
    result["ok"] = False
    result["reason"] = "install_failed"
    log_to_file(f"{name} failed after retry. rc1={rc}, rc2={rc2}")
    return result

# ---------------- Gradle Installation ----------------
def get_latest_gradle_version() -> str | None:
    """Fetch latest Gradle version from services.gradle.org"""
    try:
        # Use HTTPS
        with urllib.request.urlopen("https://services.gradle.org/versions/current") as resp:
            data = json.loads(resp.read().decode())
            return data.get("version")
    except Exception as e:
        log_to_file(f"Failed to fetch latest Gradle version: {e}")
        return None

def install_gradle_download(version: str | None = None) -> Optional[str]:
    if not version:
        version = get_latest_gradle_version()
        if not version:
            log_to_file("❌ Could not determine Gradle version.")
            return None

    url = f"https://services.gradle.org/distributions/gradle-{version}-bin.zip"
    tmpzip = Path(tempfile.gettempdir()) / f"gradle-{version}.zip"
    log_to_file(f"Downloading Gradle {version} from {url} to {tmpzip}")
    try:
        urllib.request.urlretrieve(url, str(tmpzip))
        log_to_file("Gradle zip downloaded")
        GRADLE_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(tmpzip, "r") as z:
            z.extractall(str(GRADLE_INSTALL_DIR))
        extracted = GRADLE_INSTALL_DIR / f"gradle-{version}"
        log_to_file(f"Gradle extracted to {extracted}")
        return str(extracted)
    except Exception as e:
        log_to_file(f"Gradle fallback failed: {e}")
        return None

# ---------------- JDK Detection ----------------
def detect_jdk_path() -> Optional[str]:
    pf = Path(r"C:\Program Files")
    patterns = ["**/*temurin*17*", "**/*jdk*17*", "**/*jdk-17*", "**/*Adoptium*17*"]
    for pat in patterns:
        for p in pf.glob(pat):
            if p.is_dir():
                return str(p.resolve())
    if Path(r"C:\Program Files\Java").exists():
        candidates = list(Path(r"C:\Program Files\Java").glob("jdk*17*")) + list(Path(r"C:\Program Files\Java").glob("jdk*"))
        if candidates:
            return str(candidates[0].resolve())
    return None

# ---------------- Environment Configuration ----------------
def configure_env_vars(jdk_path: Optional[str], grad_path: Optional[str]):
    """Configure system environment variables for development"""
    log_to_file("Configuring environment variables (machine-wide)")

    if jdk_path:
        # Use PowerShell to set environment variables properly
        ps_cmd = f'''
        [Environment]::SetEnvironmentVariable("JAVA_HOME", "{jdk_path}", "Machine")
        $path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($path -notlike "*{jdk_path}\\bin*") {{
            [Environment]::SetEnvironmentVariable("PATH", "$path;{jdk_path}\\bin", "Machine")
        }}
        '''
        run_cmd_capture(f'powershell -Command "{ps_cmd}"')
        log_to_file(f"Set JAVA_HOME to {jdk_path}")

    if grad_path:
        ps_cmd = f'''
        [Environment]::SetEnvironmentVariable("GRADLE_HOME", "{grad_path}", "Machine")
        $path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($path -notlike "*{grad_path}\\bin*") {{
            [Environment]::SetEnvironmentVariable("PATH", "$path;{grad_path}\\bin", "Machine")
        }}
        '''
        run_cmd_capture(f'powershell -Command "{ps_cmd}"')
        log_to_file(f"Set GRADLE_HOME to {grad_path}")
    
    # Add Android SDK to PATH
    ps_cmd = f'''
    [Environment]::SetEnvironmentVariable("ANDROID_HOME", "{ANDROID_HOME}", "Machine")
    [Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", "{ANDROID_HOME}", "Machine")
    $path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    $new_paths = @("{ANDROID_HOME}\\platform-tools", "{ANDROID_HOME}\\tools", "{ANDROID_HOME}\\emulator", "{ANDROID_HOME}\\cmdline-tools\\latest\\bin")
    foreach ($new_path in $new_paths) {{
        if ($path -notlike "*$new_path*") {{
            $path = "$path;$new_path"
        }}
    }}
    [Environment]::SetEnvironmentVariable("PATH", $path, "Machine")
    '''
    run_cmd_capture(f'powershell -Command "{ps_cmd}"')
    log_to_file("Android environment variables configured successfully")

# ---------------- Installation Status Functions ----------------
def set_installation_complete(success: bool):
    """Set the installation status"""
    # Write status to file for synchronization
    status_file = LOG_DIR / "install_status.json"
    status_data = {
        "complete": True,
        "success": success,
        "timestamp": time.time()
    }
    
    try:
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    except Exception as e:
        log_to_file(f"Failed to write status file: {e}")

# ---------------- Main Flow ----------------
def main():
    print("Starting software installer...")
    log_to_file("=== Software installer started ===")

    if not is_admin():
        log_to_file("Not admin, requesting elevation")
        elevate_and_exit()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # ensure winget present
    rc, out = run_cmd_capture("winget --version", timeout=30)
    if rc != 0:
        print("ERROR: winget not available. See log file after completion.")
        log_to_file("winget missing or not functioning: " + (out or ""))
        set_installation_complete(False)
        return 1
    log_to_file("winget available: " + (out.splitlines()[0] if out else "unknown"))

    # pick candidates
    selected = {}
    for key, candidates in CANDIDATES.items():
        sel = pick_first_available(candidates)
        selected[key] = sel

    print("Selected packages (will be installed if not present):")
    for k, v in selected.items():
        print(f" - {k}: {v or 'NONE'}")
    log_to_file("Selected map: " + str(selected))

    # Install sequence for basic software
    order = [("Python", selected.get("python")),
             ("Node", selected.get("node")),
             ("JDK", selected.get("jdk")),
             ("VSCode", selected.get("vscode")),
             ("AndroidStudio", selected.get("android-studio"))]

    results = {}
    for name, cid in order:
        print(f"Installing {name} ...", end="", flush=True)
        log_to_file(f"Beginning install step: {name}")
        res = install_package(name, cid)
        results[name] = res
        print(" Done." if res.get("ok") else " Failed.")
        log_to_file(f"Result for {name}: {res}")

    # Automated Android setup (Studio, SDK, Emulator)
    print("Setting up Android environment...", end="", flush=True)
    android_success = automated_android_setup()
    print(" Done." if android_success else " Failed.")
    results["Android"] = {"ok": android_success, "reason": "automated_setup"}

    # Gradle handling
    print("Installing Gradle ...", end="", flush=True)
    log_to_file("Gradle step started")

    grad_candidate = selected.get("gradle")
    grad_path = None
    grad_ok = False

    if grad_candidate and winget_show_exists(grad_candidate):
        rcg, _ = run_cmd_capture(f'winget install -e --id {grad_candidate} {WINGET_FLAGS}', timeout=60*10)
        if rcg == 0:
            log_to_file("Gradle installed via winget candidate")
            grad_ok = True
        else:
            log_to_file("Gradle winget candidate failed; using download fallback")
    # fallback to download latest version
    if not grad_ok:
        grad_path = install_gradle_download()
        grad_ok = grad_path is not None

    print(" Done." if grad_ok else " Failed.")
    results["Gradle"] = {"id": grad_candidate or "download-fallback", "ok": grad_ok, "path": grad_path}

    # Detect JDK path for env
    jdk_path = detect_jdk_path()
    if jdk_path:
        log_to_file(f"Detected JDK path: {jdk_path}")
    else:
        log_to_file("Could not auto-detect JDK path")

    # configure environment variables
    configure_env_vars(jdk_path, grad_path)

    # Check if all critical components were installed successfully
    critical_components = ["Python", "Node", "JDK", "Gradle", "Android"]
    all_success = all(results.get(comp, {}).get("ok", False) for comp in critical_components)

    # Set installation status
    set_installation_complete(all_success)

    if all_success:
        print("\n✅ Software installation completed successfully!")
        print("Full logs written to:", LOG_FILE)
        print("\nYou can now run your kits installer.")
    else:
        print("\n❌ Software installation completed with errors!")
        print("Check the log file for details:", LOG_FILE)
        print("\nFailed components:")
        for comp in critical_components:
            if not results.get(comp, {}).get("ok", False):
                print(f" - {comp}")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        log_to_file(f"Unhandled exception: {e}")
        import traceback
        log_to_file(traceback.format_exc())
        set_installation_complete(False)
        print("An unexpected error occurred. Full log written to:", LOG_FILE)
        sys.exit(1)

# # emeelan-els-kits/utils/software-installer.py
# #!/usr/bin/env python3
# """
# software-installer.py

# Complete automated software installation for EMEELAN ELS Kits
# Includes silent Android Studio installation, SDK setup, and emulator creation
# """
# from __future__ import annotations
# import ctypes
# import os
# import subprocess
# import sys
# import tempfile
# import time
# import zipfile
# from pathlib import Path
# from typing import Optional, Dict, Any
# import urllib.request
# import json
# import shutil

# # ---------------- CONFIG ----------------
# LOG_DIR = Path(r"C:\DevInstaller")
# LOG_DIR.mkdir(parents=True, exist_ok=True)
# LOG_FILE = LOG_DIR / "install_log.txt"

# # Android configuration
# ANDROID_SDK_ROOT = Path(r"C:\Android\Sdk")
# ANDROID_HOME = ANDROID_SDK_ROOT  # Use ANDROID_HOME as primary
# ANDROID_STUDIO_PATH = Path(r"C:\Program Files\Android\Android Studio")
# GRADLE_INSTALL_DIR = Path(r"C:\Gradle")

# # Package candidates for winget
# CANDIDATES = {
#     "python": ["Python.Python.3.11", "Python.Python.3.12", "Python.Python.3.10"],
#     "node": ["OpenJS.NodeJS", "OpenJS.NodeJS.LTS", "CoreyButler.NVMforWindows"],
#     "jdk": [
#         "EclipseAdoptium.Temurin.17.JDK",
#         "Azul.Zulu.17.JDK",
#         "Amazon.Corretto.17.JDK",
#         "Oracle.JDK.17",
#         "Microsoft.OpenJDK.17"
#     ],
#     "vscode": ["Microsoft.VisualStudioCode", "VSCodium.VSCodium"],
#     "gradle": ["Gradle.Gradle", "gradle.gradle"],
#     "android-studio": ["Google.AndroidStudio", "Google.AndroidStudio.Canary"]
# }

# WINGET_FLAGS = "--accept-source-agreements --accept-package-agreements -h --silent"

# # ---------------- In-memory logging ----------------
# _memory_log: list[str] = []

# def mem_log(msg: str):
#     ts = time.strftime("%Y-%m-%d %H:%M:%S")
#     _memory_log.append(f"[{ts}] {msg}")

# def flush_memory_log_to_file():
#     header = f"==== Installer log written at {time.strftime('%Y-%m-%d %H:%M:%S')} ====\n"
#     all_text = header + "\n".join(_memory_log) + "\n"
#     try:
#         with LOG_FILE.open("a", encoding="utf-8") as f:
#             f.write(all_text)
#     except Exception as e:
#         tmp = Path(tempfile.gettempdir()) / f"installer_log_{int(time.time())}.txt"
#         with tmp.open("w", encoding="utf-8") as f:
#             f.write(all_text)
#         print(f"Failed to write to {LOG_FILE}. Wrote to {tmp} instead: {e}")

# # ---------------- Privilege / elevation ----------------
# def is_admin() -> bool:
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin() != 0
#     except Exception:
#         return False

# def elevate_and_exit():
#     script = sys.executable
#     # Get absolute path of the current script
#     script_path = os.path.abspath(sys.argv[0])
#     params = " ".join([f'"{script_path}"'] + sys.argv[1:])
#     mem_log(f"Requesting elevation: {script} {params}")
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
#     print("UAC prompt opened — please accept to continue (elevated run will proceed).")
#     sys.exit(0)

# # ---------------- Subprocess streaming ----------------
# def run_cmd_capture(cmd: str, timeout: Optional[int] = None) -> tuple[int, str]:
#     """Run command and capture output"""
#     mem_log(f"CMD: {cmd}")
#     try:
#         proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     except Exception as e:
#         mem_log(f"Failed to launch command: {cmd} -> {e}")
#         return -1, str(e)

#     out_buf = []
#     try:
#         while True:
#             o = proc.stdout.readline()
#             if o:
#                 out_buf.append(o)
#                 mem_log("STDOUT: " + o.rstrip())
#             e = proc.stderr.readline()
#             if e:
#                 out_buf.append(e)
#                 mem_log("STDERR: " + e.rstrip())
#             if proc.poll() is not None:
#                 rem_out, rem_err = proc.communicate(timeout=5 if timeout else None)
#                 if rem_out:
#                     out_buf.append(rem_out)
#                     for line in rem_out.splitlines():
#                         mem_log("STDOUT: " + line)
#                 if rem_err:
#                     out_buf.append(rem_err)
#                     for line in rem_err.splitlines():
#                         mem_log("STDERR: " + line)
#                 break
#             time.sleep(0.05)
#     except Exception as ex:
#         proc.kill()
#         mem_log(f"Exception while running command: {ex}")
#     rc = proc.returncode if proc.returncode is not None else -1
#     mem_log(f"CMD EXIT {rc}: {cmd}")
#     return rc, "".join(out_buf)

# # ---------------- Android Studio Installation ----------------
# def install_android_studio_with_winget():
#     """Install Android Studio using winget"""
#     mem_log("Checking for Android Studio...")
#     rc, output = run_cmd_capture('winget list --id Google.AndroidStudio', timeout=30)
#     if rc == 0 and "Google.AndroidStudio" in output:
#         mem_log("Android Studio is already installed.")
#         return True
    
#     mem_log("Installing Android Studio via winget...")
#     rc, output = run_cmd_capture(f'winget install --id Google.AndroidStudio -e --silent --accept-source-agreements --accept-package-agreements', timeout=1200)
    
#     if rc == 0:
#         mem_log("Android Studio installed successfully via winget")
#         return True
#     else:
#         mem_log(f"Android Studio installation via winget failed: {output}")
#         return False
    
# # ---------------- Android SDK Setup ----------------
# def setup_android_sdk_complete():
#     """Complete Android SDK setup with all necessary components"""
#     # Create SDK directory
#     ANDROID_HOME.mkdir(parents=True, exist_ok=True)
    
#     # Set environment variables
#     os.environ["ANDROID_HOME"] = str(ANDROID_HOME)
#     os.environ["ANDROID_SDK_ROOT"] = str(ANDROID_HOME)  # For compatibility
    
#     # Add to PATH
#     path_additions = [
#         str(ANDROID_HOME / "platform-tools"),
#         str(ANDROID_HOME / "tools"),
#         str(ANDROID_HOME / "emulator"),
#         str(ANDROID_HOME / "cmdline-tools" / "latest" / "bin")
#     ]
    
#     for path in path_additions:
#         if path not in os.environ["PATH"]:
#             os.environ["PATH"] += os.pathsep + path
    
#     # Download and install latest SDK command-line tools
#     cmdline_tools_url = "https://dl.google.com/android/repository/commandlinetools-win-13114758_latest.zip"
#     cmdline_tools_zip = str(ANDROID_HOME / "cmdline-tools.zip")
#     cmdline_tools_dir = ANDROID_HOME / "cmdline-tools" / "latest"
#     sdkmanager_path = cmdline_tools_dir / "bin" / "sdkmanager.bat"
    
#     if not sdkmanager_path.exists():
#         mem_log("Downloading Android SDK command-line tools...")
#         try:
#             urllib.request.urlretrieve(cmdline_tools_url, cmdline_tools_zip)
#             mem_log("Extracting command-line tools...")
#             with zipfile.ZipFile(cmdline_tools_zip, "r") as zip_ref:
#                 extract_path = str(ANDROID_HOME / "cmdline-tools" / "temp")
#                 zip_ref.extractall(extract_path)
#             # Move the extracted cmdline-tools into 'latest'
#             extracted_dir = Path(extract_path) / "cmdline-tools"
#             if cmdline_tools_dir.exists():
#                 shutil.rmtree(str(cmdline_tools_dir))
#             shutil.move(str(extracted_dir), str(cmdline_tools_dir))
#             shutil.rmtree(extract_path)
#             os.remove(cmdline_tools_zip)
#             mem_log(f"Command-line tools installed at {cmdline_tools_dir}")
#         except Exception as e:
#             mem_log(f"Failed to install command-line tools: {e}")
#             return False
#     else:
#         mem_log("Android SDK command-line tools already installed.")
    
#     # Accept licenses
#     mem_log("Accepting Android SDK licenses...")
#     rc, _ = run_cmd_capture(f'"{sdkmanager_path}" --licenses', timeout=300)
#     if rc != 0:
#         mem_log("Failed to accept licenses")
    
#     # Install necessary packages
#     packages = [
#         "platform-tools",
#         "platforms;android-33",
#         "build-tools;33.0.2",
#         "system-images;android-33;google_apis;x86_64",
#         "emulator"
#     ]
    
#     for package in packages:
#         mem_log(f"Installing {package}...")
#         rc, output = run_cmd_capture(f'"{sdkmanager_path}" "{package}"', timeout=600)
#         if rc != 0:
#             mem_log(f"Failed to install {package}: {output}")
#             return False
    
#     return True

# # ---------------- AVD Creation ----------------
# def create_android_avd_automated():
#     """Create Android Virtual Device without manual intervention"""
#     # Find avdmanager path
#     avdmanager_path = None
#     possible_paths = [
#         ANDROID_HOME / "cmdline-tools" / "latest" / "bin" / "avdmanager.bat",
#         Path(r"C:\Program Files\Android\Android SDK Command Line Tools\tools\bin\avdmanager.bat")
#     ]
    
#     for path in possible_paths:
#         if path.exists():
#             avdmanager_path = path
#             break
    
#     if not avdmanager_path:
#         mem_log("avdmanager not found")
#         return False
    
#     # Create AVD
#     avd_name = "Pixel_6"
#     system_image = "system-images;android-33;google_apis;x86_64"
#     device = "pixel"
    
#     # Delete existing AVD if exists
#     run_cmd_capture(f'"{avdmanager_path}" delete avd -n {avd_name}')
    
#     # Create new AVD
#     rc, output = run_cmd_capture(f'"{avdmanager_path}" create avd -n {avd_name} -k "{system_image}" --device {device} --force', timeout=300)
    
#     if rc == 0:
#         mem_log("AVD created successfully")
#         return True
#     else:
#         mem_log(f"AVD creation failed: {output}")
#         return False
    
# # ---------------- Emulator Startup ----------------
# # Removed as per instructions

# # ---------------- Android Setup Verification ----------------
# def verify_android_installation():
#     """Verify that Android installation is complete and working"""
#     checks = [
#         ("adb", "adb --version"),
#         ("emulator", "emulator -version"),
#         ("sdkmanager", "sdkmanager --version")
#     ]
    
#     for tool, cmd in checks:
#         rc, output = run_cmd_capture(cmd, timeout=30)
#         if rc != 0:
#             mem_log(f"Tool {tool} verification failed")
#             return False
    
#     return True

# # ---------------- Complete Android Setup ----------------
# def automated_android_setup():
#     """Complete automated Android Studio and emulator setup"""
#     mem_log("Starting automated Android setup...")
    
#     # Step 1: Install Android Studio using winget
#     if not install_android_studio_with_winget():
#         mem_log("Android Studio installation failed")
#         return False
    
#     # Step 2: Setup Android SDK
#     if not setup_android_sdk_complete():
#         mem_log("Android SDK setup failed")
#         return False
    
#     # Step 3: Create virtual device
#     if not create_android_avd_automated():
#         mem_log("AVD creation failed")
#         return False
    
#     # Step 4: Start emulator removed
    
#     # Step 5: Verify installation
#     if verify_android_installation():
#         mem_log("Android setup completed successfully")
#         return True
#     else:
#         mem_log("Android setup verification failed")
#         return False

# # ---------------- Winget Helpers ----------------
# def winget_show_exists(id_: str) -> bool:
#     rc, out = run_cmd_capture(f'winget show --id {id_}', timeout=30)
#     return rc == 0

# def winget_list_contains(id_or_name: str) -> bool:
#     rc, out = run_cmd_capture(f'winget list --id {id_or_name}', timeout=20)
#     return rc == 0 and id_or_name in out

# def pick_first_available(candidates: list[str]) -> Optional[str]:
#     for cand in candidates:
#         if winget_show_exists(cand):
#             mem_log(f"Found candidate: {cand}")
#             return cand
#     mem_log(f"No candidate found in list: {candidates}")
#     return None

# # ---------------- Package Installation ----------------
# def install_package(name: str, candidate_id: Optional[str]) -> Dict[str, Any]:
#     """High-level installation step"""
#     result: Dict[str, Any] = {"id": candidate_id, "ok": False, "reason": None}
#     mem_log(f"Install step for {name} using id {candidate_id}")

#     # detect installed by winget list
#     if candidate_id and winget_list_contains(candidate_id):
#         result["ok"] = True
#         result["reason"] = "already_installed_winget"
#         mem_log(f"{name}: detected by winget list ({candidate_id})")
#         return result

#     # detect by common commands
#     if name.lower().startswith("python"):
#         rc_py, _ = run_cmd_capture("python --version")
#         if rc_py == 0:
#             result["ok"] = True
#             result["reason"] = "already_installed_command"
#             mem_log("Python present on PATH (python --version detected).")
#             return result
#         rc_py2, _ = run_cmd_capture("py -3 --version")
#         if rc_py2 == 0:
#             result["ok"] = True
#             result["reason"] = "already_installed_command"
#             mem_log("Python present on PATH (py -3 --version detected).")
#             return result

#     if name.lower().startswith("node"):
#         rc_n, _ = run_cmd_capture("node --version")
#         if rc_n == 0:
#             result["ok"] = True
#             result["reason"] = "already_installed_command"
#             mem_log("Node present on PATH (node --version detected).")
#             return result

#     if "vscode" in name.lower():
#         rc_code, _ = run_cmd_capture("code --version")
#         if rc_code == 0:
#             result["ok"] = True
#             result["reason"] = "already_installed_command"
#             mem_log("VS Code present on PATH (code --version detected).")
#             return result

#     if "android" in name.lower():
#         # Check if Android Studio is already installed
#         studio_path = Path(r"C:\Program Files\Android\Android Studio\bin\studio64.exe")
#         if studio_path.exists():
#             result["ok"] = True
#             result["reason"] = "already_installed_path"
#             mem_log("Android Studio found in Program Files")
#             return result

#     if candidate_id is None:
#         result["reason"] = "no_candidate"
#         mem_log(f"No winget candidate for {name}; skipping install.")
#         return result

#     # attempt install
#     mem_log(f"Running winget install for {name} (id={candidate_id})")
#     rc, out = run_cmd_capture(f'winget install -e --id {candidate_id} {WINGET_FLAGS}', timeout=60*30)
#     if rc == 0:
#         result["ok"] = True
#         result["reason"] = "installed"
#         mem_log(f"{name} installed successfully via winget.")
#         return result

#     # retry once
#     mem_log(f"{name} first install failed (rc={rc}). Retrying once after brief wait.")
#     time.sleep(3)
#     rc2, out2 = run_cmd_capture(f'winget install -e --id {candidate_id} {WINGET_FLAGS}', timeout=60*30)
#     if rc2 == 0:
#         result["ok"] = True
#         result["reason"] = "installed_on_retry"
#         mem_log(f"{name} installed on retry.")
#         return result

#     # failure
#     result["ok"] = False
#     result["reason"] = "install_failed"
#     mem_log(f"{name} failed after retry. rc1={rc}, rc2={rc2}")
#     return result

# # ---------------- Gradle Installation ----------------
# def get_latest_gradle_version() -> str | None:
#     """Fetch latest Gradle version from services.gradle.org"""
#     try:
#         # Use HTTPS
#         with urllib.request.urlopen("https://services.gradle.org/versions/current") as resp:
#             data = json.loads(resp.read().decode())
#             return data.get("version")
#     except Exception as e:
#         mem_log(f"Failed to fetch latest Gradle version: {e}")
#         return None

# def install_gradle_download(version: str | None = None) -> Optional[str]:
#     if not version:
#         version = get_latest_gradle_version()
#         if not version:
#             mem_log("❌ Could not determine Gradle version.")
#             return None

#     url = f"https://services.gradle.org/distributions/gradle-{version}-bin.zip"
#     tmpzip = Path(tempfile.gettempdir()) / f"gradle-{version}.zip"
#     mem_log(f"Downloading Gradle {version} from {url} to {tmpzip}")
#     try:
#         urllib.request.urlretrieve(url, str(tmpzip))
#         mem_log("Gradle zip downloaded")
#         GRADLE_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
#         with zipfile.ZipFile(tmpzip, "r") as z:
#             z.extractall(str(GRADLE_INSTALL_DIR))
#         extracted = GRADLE_INSTALL_DIR / f"gradle-{version}"
#         mem_log(f"Gradle extracted to {extracted}")
#         return str(extracted)
#     except Exception as e:
#         mem_log(f"Gradle fallback failed: {e}")
#         return None

# # ---------------- JDK Detection ----------------
# def detect_jdk_path() -> Optional[str]:
#     pf = Path(r"C:\Program Files")
#     patterns = ["**/*temurin*17*", "**/*jdk*17*", "**/*jdk-17*", "**/*Adoptium*17*"]
#     for pat in patterns:
#         for p in pf.glob(pat):
#             if p.is_dir():
#                 return str(p.resolve())
#     if Path(r"C:\Program Files\Java").exists():
#         candidates = list(Path(r"C:\Program Files\Java").glob("jdk*17*")) + list(Path(r"C:\Program Files\Java").glob("jdk*"))
#         if candidates:
#             return str(candidates[0].resolve())
#     return None

# # ---------------- Environment Configuration ----------------
# def configure_env_vars(jdk_path: Optional[str], grad_path: Optional[str]):
#     """Configure system environment variables for development"""
#     mem_log("Configuring environment variables (machine-wide)")

#     if jdk_path:
#         # Use PowerShell to set environment variables properly
#         ps_cmd = f'''
#         [Environment]::SetEnvironmentVariable("JAVA_HOME", "{jdk_path}", "Machine")
#         $path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
#         if ($path -notlike "*{jdk_path}\\bin*") {{
#             [Environment]::SetEnvironmentVariable("PATH", "$path;{jdk_path}\\bin", "Machine")
#         }}
#         '''
#         run_cmd_capture(f'powershell -Command "{ps_cmd}"')
#         mem_log(f"Set JAVA_HOME to {jdk_path}")

#     if grad_path:
#         ps_cmd = f'''
#         [Environment]::SetEnvironmentVariable("GRADLE_HOME", "{grad_path}", "Machine")
#         $path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
#         if ($path -notlike "*{grad_path}\\bin*") {{
#             [Environment]::SetEnvironmentVariable("PATH", "$path;{grad_path}\\bin", "Machine")
#         }}
#         '''
#         run_cmd_capture(f'powershell -Command "{ps_cmd}"')
#         mem_log(f"Set GRADLE_HOME to {grad_path}")
    
#     # Add Android SDK to PATH
#     ps_cmd = f'''
#     [Environment]::SetEnvironmentVariable("ANDROID_HOME", "{ANDROID_HOME}", "Machine")
#     [Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", "{ANDROID_HOME}", "Machine")
#     $path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
#     $new_paths = @("{ANDROID_HOME}\\platform-tools", "{ANDROID_HOME}\\tools", "{ANDROID_HOME}\\emulator", "{ANDROID_HOME}\\cmdline-tools\\latest\\bin")
#     foreach ($new_path in $new_paths) {{
#         if ($path -notlike "*$new_path*") {{
#             $path = "$path;$new_path"
#         }}
#     }}
#     [Environment]::SetEnvironmentVariable("PATH", $path, "Machine")
#     '''
#     run_cmd_capture(f'powershell -Command "{ps_cmd}"')
#     mem_log("Android environment variables configured successfully")

# # ---------------- Installation Status Functions ----------------
# def set_installation_complete(success: bool):
#     """Set the installation status"""
#     # Write status to file for synchronization
#     status_file = LOG_DIR / "install_status.json"
#     status_data = {
#         "complete": True,
#         "success": success,
#         "timestamp": time.time()
#     }
    
#     try:
#         with open(status_file, 'w') as f:
#             json.dump(status_data, f)
#     except Exception as e:
#         mem_log(f"Failed to write status file: {e}")

# # ---------------- Main Flow ----------------
# def main():
#     print("Starting software installer...")
#     mem_log("=== Software installer started ===")

#     if not is_admin():
#         mem_log("Not admin, requesting elevation")
#         elevate_and_exit()

#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     os.chdir(script_dir)
    
#     # ensure winget present
#     rc, out = run_cmd_capture("winget --version", timeout=30)
#     if rc != 0:
#         print("ERROR: winget not available. See log file after completion.")
#         mem_log("winget missing or not functioning: " + (out or ""))
#         flush_memory_log_to_file()
#         set_installation_complete(False)
#         return 1
#     mem_log("winget available: " + (out.splitlines()[0] if out else "unknown"))

#     # pick candidates
#     selected = {}
#     for key, candidates in CANDIDATES.items():
#         sel = pick_first_available(candidates)
#         selected[key] = sel

#     print("Selected packages (will be installed if not present):")
#     for k, v in selected.items():
#         print(f" - {k}: {v or 'NONE'}")
#     mem_log("Selected map: " + str(selected))

#     # Install sequence for basic software
#     order = [("Python", selected.get("python")),
#              ("Node", selected.get("node")),
#              ("JDK", selected.get("jdk")),
#              ("VSCode", selected.get("vscode")),
#              ("AndroidStudio", selected.get("android-studio"))]

#     results = {}
#     for name, cid in order:
#         print(f"Installing {name} ...", end="", flush=True)
#         mem_log(f"Beginning install step: {name}")
#         res = install_package(name, cid)
#         results[name] = res
#         print(" Done." if res.get("ok") else " Failed.")
#         mem_log(f"Result for {name}: {res}")

#     # Automated Android setup (Studio, SDK, Emulator)
#     print("Setting up Android environment...", end="", flush=True)
#     android_success = automated_android_setup()
#     print(" Done." if android_success else " Failed.")
#     results["Android"] = {"ok": android_success, "reason": "automated_setup"}

#     # Gradle handling
#     print("Installing Gradle ...", end="", flush=True)
#     mem_log("Gradle step started")

#     grad_candidate = selected.get("gradle")
#     grad_path = None
#     grad_ok = False

#     if grad_candidate and winget_show_exists(grad_candidate):
#         rcg, _ = run_cmd_capture(f'winget install -e --id {grad_candidate} {WINGET_FLAGS}', timeout=60*10)
#         if rcg == 0:
#             mem_log("Gradle installed via winget candidate")
#             grad_ok = True
#         else:
#             mem_log("Gradle winget candidate failed; using download fallback")
#     # fallback to download latest version
#     if not grad_ok:
#         grad_path = install_gradle_download()
#         grad_ok = grad_path is not None

#     print(" Done." if grad_ok else " Failed.")
#     results["Gradle"] = {"id": grad_candidate or "download-fallback", "ok": grad_ok, "path": grad_path}

#     # Detect JDK path for env
#     jdk_path = detect_jdk_path()
#     if jdk_path:
#         mem_log(f"Detected JDK path: {jdk_path}")
#     else:
#         mem_log("Could not auto-detect JDK path")

#     # configure environment variables
#     configure_env_vars(jdk_path, grad_path)

#     # Check if all critical components were installed successfully
#     critical_components = ["Python", "Node", "JDK", "Gradle", "Android"]
#     all_success = all(results.get(comp, {}).get("ok", False) for comp in critical_components)

#     # write the full memory log to file now
#     flush_memory_log_to_file()

#     # Set installation status
#     set_installation_complete(all_success)

#     if all_success:
#         print("\n✅ Software installation completed successfully!")
#         print("Full logs written to:", LOG_FILE)
#         print("\nYou can now run your kits installer.")
#     else:
#         print("\n❌ Software installation completed with errors!")
#         print("Check the log file for details:", LOG_FILE)
#         print("\nFailed components:")
#         for comp in critical_components:
#             if not results.get(comp, {}).get("ok", False):
#                 print(f" - {comp}")
    
#     return 0 if all_success else 1

# if __name__ == "__main__":
#     try:
#         exit_code = main()
#         sys.exit(exit_code)
#     except Exception as e:
#         mem_log(f"Unhandled exception: {e}")
#         import traceback
#         mem_log(traceback.format_exc())
#         flush_memory_log_to_file()
#         set_installation_complete(False)
#         print("An unexpected error occurred. Full log written to:", LOG_FILE)
#         sys.exit(1)