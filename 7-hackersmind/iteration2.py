#!/usr/bin/env python3
"""
Iteration 2: Multi-Layer ZIP Cracking and Network Reconnaissance
==============================================================
This program implements advanced ZIP file analysis with multiple password layers
and introduces basic network reconnaissance techniques.
Focus: Multi-stage attacks, steganography detection, and network scanning.

⚠️  ETHICAL NOTICE: This program is for educational purposes only.
    Only use on systems you own or have explicit permission to test.
"""

import zipfile
import socket
import threading
import time
import hashlib
import base64
import os
import json
from pathlib import Path
import itertools
import string

class MultiLayerZipCracker:
    """Advanced ZIP cracking with multiple layers and hints"""
    
    def __init__(self):
        self.layer_count = 0
        self.extracted_hints = []
        self.password_history = []
        self.start_time = time.time()
    
    def create_multi_layer_zip(self):
        """Create a multi-layer ZIP file with progressive difficulty"""
        print("\n--- Creating Multi-Layer Challenge ZIP ---")
        
        sample_dir = Path("multilayer_challenge")
        sample_dir.mkdir(exist_ok=True)
        
        # Layer 1: Simple hint
        layer1_content = """
🎉 Congratulations on cracking Layer 1!

HINT FOR LAYER 2:
The password is the first name of the famous physicist who developed 
the theory of relativity, followed by the year he won the Nobel Prize.
Format: firstname+year (all lowercase)

Also found: encoded message below
SGVsbG8gSGFja2VyISBZb3UncmUgZG9pbmcgZ3JlYXQh
        """
        
        # Layer 2: Physics knowledge required
        layer2_content = """
🚀 Excellent! Layer 2 defeated!

HINT FOR LAYER 3:
The password combines:
1. The capital of France (lowercase)
2. The symbol for Gold on periodic table
3. The answer to "What is 7 squared?"
4. An exclamation mark

Hidden coordinates: 48.8566, 2.3522
Base64 secret: VGhlIGZpbmFsIGxheWVyIGF3YWl0cyE=
        """
        
        # Layer 3: Final challenge
        layer3_content = """
🏆 MASTER HACKER ACHIEVED! 🏆

You have successfully:
✅ Cracked a simple dictionary password
✅ Applied domain knowledge to crack Layer 2
✅ Combined multiple clues for Layer 3
✅ Demonstrated persistence and logical thinking

FINAL SECRET:
The coordinates point to the Louvre Museum in Paris.
The base64 message says: "The final layer awaits!"

You are now ready for network reconnaissance challenges!

BONUS: Hidden flag{m4st3r_0f_l4y3rs_2024}
        """
        
        # Create Layer 3 (innermost)
        layer3_zip = sample_dir / "layer3.zip"
        with zipfile.ZipFile(layer3_zip, 'w') as zip_ref:
            zip_ref.writestr("victory.txt", layer3_content, pwd=b"parisau49!")
        
        # Create Layer 2 (contains Layer 3)
        layer2_zip = sample_dir / "layer2.zip"
        with zipfile.ZipFile(layer2_zip, 'w') as zip_ref:
            zip_ref.writestr("hint2.txt", layer2_content, pwd=b"albert1921")
            with open(layer3_zip, 'rb') as f:
                zip_ref.writestr("next_challenge.zip", f.read())
        
        # Create Layer 1 (outermost)
        layer1_zip = sample_dir / "layer1.zip"
        with zipfile.ZipFile(layer1_zip, 'w') as zip_ref:
            zip_ref.writestr("welcome.txt", layer1_content, pwd=b"start123")
            with open(layer2_zip, 'rb') as f:
                zip_ref.writestr("deeper.zip", f.read())
        
        print(f"✅ Multi-layer ZIP created: {layer1_zip}")
        print("📋 Layer Information:")
        print("   Layer 1: start123 (hint: 'start' + common numbers)")
        print("   Layer 2: albert1921 (Albert Einstein + Nobel Prize year)")
        print("   Layer 3: parisau49! (paris + au + 49 + !)")
        
        return str(layer1_zip)
    
    def decode_base64_hints(self, text):
        """Extract and decode base64 messages from text"""
        print("\n--- Decoding Hidden Messages ---")
        
        import re
        
        # Find base64-like strings
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(base64_pattern, text)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8')
                print(f"🔍 Found encoded message: {match}")
                print(f"🔓 Decoded: {decoded}")
            except:
                continue
    
    def extract_coordinates(self, text):
        """Extract coordinate information from text"""
        print("\n--- Extracting Coordinates ---")
        
        import re
        
        # Pattern for coordinates (latitude, longitude)
        coord_pattern = r'(-?\d{1,3}\.\d{4}),?\s*(-?\d{1,3}\.\d{4})'
        matches = re.findall(coord_pattern, text)
        
        for lat, lon in matches:
            print(f"📍 Coordinates found: {lat}, {lon}")
            # Simple reverse geocoding hint
            lat_f, lon_f = float(lat), float(lon)
            if 48.0 < lat_f < 49.0 and 2.0 < lon_f < 3.0:
                print("🗼 Location hint: Paris, France area")
    
    def intelligent_crack_layer(self, zip_path, layer_num, hint_text=""):
        """Crack a single layer with intelligent guessing"""
        print(f"\n--- Cracking Layer {layer_num} ---")
        
        if hint_text:
            print(f"💡 Available hint: {hint_text[:100]}...")
            self.decode_base64_hints(hint_text)
            self.extract_coordinates(hint_text)
        
        # Layer-specific password strategies
        if layer_num == 1:
            # Simple combinations
            candidates = self.generate_simple_passwords()
        elif layer_num == 2:
            # Science/history based
            candidates = self.generate_knowledge_passwords()
        else:
            # Complex combinations
            candidates = self.generate_complex_passwords()
        
        return self.try_passwords(zip_path, candidates)
    
    def generate_simple_passwords(self):
        """Generate simple password candidates for Layer 1"""
        candidates = [
            "start", "start123", "begin", "begin123", "layer1",
            "password", "123456", "welcome", "hello", "first"
        ]
        
        # Add variations
        for base in ["start", "begin", "first"]:
            for num in ["1", "12", "123", "2024", "2023"]:
                candidates.append(base + num)
        
        return candidates
    
    def generate_knowledge_passwords(self):
        """Generate knowledge-based passwords for Layer 2"""
        # Famous scientists and years
        scientists = [
            ("albert", "1921"), ("einstein", "1921"), ("albert1921", ""),
            ("newton", "1687"), ("darwin", "1859"), ("curie", "1903"),
            ("tesla", "1856"), ("galileo", "1564")
        ]
        
        candidates = []
        for name, year in scientists:
            candidates.extend([
                name + year,
                name.capitalize() + year,
                name + year[-2:],  # Last 2 digits of year
            ])
        
        return candidates
    
    def generate_complex_passwords(self):
        """Generate complex password candidates for Layer 3"""
        cities = ["paris", "london", "berlin", "madrid", "rome"]
        elements = ["au", "ag", "fe", "cu", "pb", "sn"]  # Gold, Silver, Iron, etc.
        numbers = ["49", "64", "36", "25", "16"]  # Perfect squares
        symbols = ["!", "@", "#", "$", "%"]
        
        candidates = []
        for city in cities:
            for element in elements:
                for num in numbers:
                    for symbol in symbols:
                        candidates.append(city + element + num + symbol)
        
        return candidates
    
    def try_passwords(self, zip_path, candidates):
        """Try a list of password candidates"""
        print(f"🔍 Trying {len(candidates)} password candidates...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for i, password in enumerate(candidates, 1):
                    try:
                        # Create temporary extraction directory
                        extract_dir = Path(f"temp_extract_{self.layer_count}")
                        extract_dir.mkdir(exist_ok=True)
                        
                        zip_ref.extractall(path=extract_dir, pwd=password.encode())
                        print(f"🎉 SUCCESS! Password found: '{password}' (attempt {i})")
                        
                        # Read extracted content for hints
                        self.process_extracted_content(extract_dir)
                        
                        return password, extract_dir
                        
                    except (RuntimeError, zipfile.BadZipFile):
                        if i % 50 == 0:
                            print(f"⏳ Tried {i}/{len(candidates)} passwords...")
                        continue
                
                print(f"🚫 Failed to crack with {len(candidates)} attempts")
                return None, None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, None
    
    def process_extracted_content(self, extract_dir):
        """Process extracted content for hints and next steps"""
        print(f"\n📂 Processing extracted content from {extract_dir}")
        
        for file_path in extract_dir.rglob("*"):
            if file_path.is_file():
                print(f"📄 Found file: {file_path.name}")
                
                if file_path.suffix == '.txt':
                    try:
                        content = file_path.read_text()
                        print(f"📖 Content preview: {content[:200]}...")
                        
                        # Extract hints
                        if "HINT" in content.upper():
                            hint_start = content.upper().find("HINT")
                            hint_section = content[hint_start:hint_start+500]
                            self.extracted_hints.append(hint_section)
                            print(f"💡 Hint extracted and stored")
                        
                        # Look for encoded messages
                        self.decode_base64_hints(content)
                        self.extract_coordinates(content)
                        
                    except Exception as e:
                        print(f"❌ Error reading {file_path}: {e}")
                
                elif file_path.suffix == '.zip':
                    print(f"🔗 Found nested ZIP: {file_path.name}")
                    return file_path
        
        return None
    
    def crack_multi_layer_zip(self, zip_path):
        """Main function to crack multi-layer ZIP file"""
        print(f"\n{'='*60}")
        print("🎯 MULTI-LAYER ZIP CRACKING CHALLENGE")
        print("="*60)
        
        current_zip = Path(zip_path)
        layer = 1
        
        while current_zip and current_zip.exists():
            print(f"\n🎯 LAYER {layer} CHALLENGE")
            print("-" * 40)
            
            # Get hint from previous layer
            hint = self.extracted_hints[-1] if self.extracted_hints else ""
            
            # Crack current layer
            password, extract_dir = self.intelligent_crack_layer(
                str(current_zip), layer, hint
            )
            
            if not password:
                print(f"🚫 Failed to crack Layer {layer}")
                break
            
            self.password_history.append((layer, password))
            
            # Look for next layer
            next_zip = None
            if extract_dir:
                for file_path in extract_dir.rglob("*.zip"):
                    if file_path.is_file():
                        next_zip = file_path
                        break
            
            if next_zip:
                print(f"🔗 Found next layer: {next_zip.name}")
                current_zip = next_zip
                layer += 1
                self.layer_count += 1
            else:
                print(f"🏆 Final layer reached! Challenge completed!")
                break
        
        # Summary
        elapsed = time.time() - self.start_time
        print(f"\n{'='*60}")
        print("📊 CHALLENGE SUMMARY")
        print("="*60)
        print(f"⏱️  Total time: {elapsed:.2f} seconds")
        print(f"🎯 Layers cracked: {len(self.password_history)}")
        print(f"💡 Hints collected: {len(self.extracted_hints)}")
        
        print("\n🔐 Password History:")
        for layer_num, pwd in self.password_history:
            print(f"   Layer {layer_num}: '{pwd}'")

class BasicNetworkRecon:
    """Basic network reconnaissance tools"""
    
    def __init__(self):
        self.open_ports = []
        self.scan_results = {}
    
    def port_scanner(self, target_host, port_range=(20, 100)):
        """Simple port scanner for educational purposes"""
        print(f"\n--- Port Scanning {target_host} ---")
        print(f"🔍 Scanning ports {port_range[0]}-{port_range[1]}")
        print("⚠️  Note: Only scan hosts you own or have permission to test!")
        
        start_time = time.time()
        self.open_ports = []
        
        def scan_port(host, port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    self.open_ports.append(port)
                    print(f"✅ Port {port}: OPEN")
                sock.close()
            except socket.gaierror:
                pass
            except Exception as e:
                pass
        
        # Multi-threaded scanning for speed
        threads = []
        for port in range(port_range[0], port_range[1] + 1):
            thread = threading.Thread(target=scan_port, args=(target_host, port))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        print(f"\n📊 Scan completed in {elapsed:.2f} seconds")
        print(f"🎯 Open ports found: {len(self.open_ports)}")
        
        if self.open_ports:
            print("📋 Open ports:", ", ".join(map(str, self.open_ports)))
        else:
            print("🚫 No open ports found in range")
        
        return self.open_ports
    
    def banner_grabbing(self, host, port):
        """Simple banner grabbing for service identification"""
        print(f"\n--- Banner Grabbing {host}:{port} ---")
        
        try:
            sock = socket.socket()
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Send HTTP request for web servers
            if port in [80, 8080, 443, 8443]:
                sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
            
            banner = sock.recv(1024).decode().strip()
            sock.close()
            
            if banner:
                print(f"🏷️  Banner received:")
                print(f"   {banner[:200]}...")
                return banner
            else:
                print("🚫 No banner received")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

def demonstrate_hash_cracking():
    """Demonstrate basic hash cracking techniques"""
    print("\n--- Hash Cracking Demonstration ---")
    
    # Common hash types
    test_passwords = ["password", "123456", "admin", "hello"]
    
    print("🔒 Hash Examples:")
    hashes = {}
    
    for pwd in test_passwords:
        # MD5
        md5_hash = hashlib.md5(pwd.encode()).hexdigest()
        hashes[md5_hash] = pwd
        print(f"MD5    '{pwd}' -> {md5_hash}")
        
        # SHA256
        sha256_hash = hashlib.sha256(pwd.encode()).hexdigest()
        hashes[sha256_hash] = pwd
        print(f"SHA256 '{pwd}' -> {sha256_hash[:32]}...")
    
    # Demonstrate rainbow table attack
    print(f"\n🌈 Rainbow Table Attack Simulation:")
    target_hash = hashlib.md5("admin".encode()).hexdigest()
    print(f"Target hash: {target_hash}")
    
    for stored_hash, original_pwd in hashes.items():
        if stored_hash == target_hash:
            print(f"🎉 Hash cracked! '{original_pwd}' -> {stored_hash}")
            break

def main():
    """Main function for Iteration 2"""
    print("Iteration 2: Multi-Layer ZIP Cracking and Network Reconnaissance")
    print("This program demonstrates advanced password cracking and basic network analysis.\n")
    
    print("⚠️  ETHICAL NOTICE:")
    print("   • Educational purposes only")
    print("   • Only test on systems you own or have permission")
    print("   • Follow responsible disclosure for any vulnerabilities found")
    print("   • Respect privacy and applicable laws")
    
    # Main demonstration
    print("\n" + "="*60)
    print("🎯 ADVANCED CRACKING TECHNIQUES")
    print("="*60)
    
    cracker = MultiLayerZipCracker()
    
    # Create and crack multi-layer ZIP
    multilayer_zip = cracker.create_multi_layer_zip()
    
    print("\n🎮 Ready to start the multi-layer challenge?")
    input("Press Enter to begin...")
    
    cracker.crack_multi_layer_zip(multilayer_zip)
    
    # Network reconnaissance demo
    print("\n" + "="*60)
    print("🌐 NETWORK RECONNAISSANCE")
    print("="*60)
    
    recon = BasicNetworkRecon()
    
    # Demonstrate on localhost (safe)
    print("🔍 Demonstrating port scan on localhost (127.0.0.1)")
    recon.port_scanner("127.0.0.1", (20, 100))
    
    # Hash cracking demonstration
    demonstrate_hash_cracking()
    
    print("\n" + "="*60)
    print("🎓 KEY LEARNING POINTS:")
    print("="*60)
    print("1. Multi-layer security challenges")
    print("2. Hint extraction and analysis")
    print("3. Base64 encoding/decoding")
    print("4. Coordinate extraction techniques")
    print("5. Basic network port scanning")
    print("6. Banner grabbing for service identification")
    print("7. Hash functions and rainbow table attacks")
    print("8. Multi-threaded operations for efficiency")
    print("="*60)

if __name__ == "__main__":
    main()