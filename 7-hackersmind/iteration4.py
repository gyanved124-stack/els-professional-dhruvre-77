#!/usr/bin/env python3
"""
Iteration 4: Advanced Cryptography and Digital Forensics
========================================================
This program demonstrates advanced cryptographic techniques, steganography,
and digital forensics methods for cybersecurity analysis.
Focus: Encryption/decryption, steganography, forensic analysis, and crypto attacks.

⚠️  ETHICAL NOTICE: This program is for educational purposes only.
    Only use on data you own or have explicit permission to analyze.
"""

import hashlib
import base64
import os
import time
import itertools
from Crypto.Cipher import AES, DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PIL import Image
import numpy as np
import zipfile
import json
from pathlib import Path
import struct

class CryptographyLab:
    """Advanced cryptography testing and analysis"""
    
    def __init__(self):
        self.key_lengths = {
            'AES': [16, 24, 32],  # 128, 192, 256 bits
            'DES': [8],           # 64 bits (56 effective)
        }
    
    def demonstrate_symmetric_encryption(self):
        """Demonstrate various symmetric encryption algorithms"""
        print("\n--- Symmetric Encryption Demonstration ---")
        
        plaintext = "This is a secret message for encryption testing!"
        print(f"📝 Original message: {plaintext}")
        
        # AES Encryption
        print("\n🔐 AES-256 Encryption:")
        aes_key = get_random_bytes(32)  # 256-bit key
        
        cipher = AES.new(aes_key, AES.MODE_CBC)
        padded_text = pad(plaintext.encode(), AES.block_size)
        ciphertext = cipher.encrypt(padded_text)
        
        print(f"   Key (hex): {aes_key.hex()}")
        print(f"   IV (hex): {cipher.iv.hex()}")
        print(f"   Ciphertext (hex): {ciphertext.hex()}")
        
        # AES Decryption
        decipher = AES.new(aes_key, AES.MODE_CBC, cipher.iv)
        decrypted_padded = decipher.decrypt(ciphertext)
        decrypted = unpad(decrypted_padded, AES.block_size).decode()
        
        print(f"   Decrypted: {decrypted}")
        print(f"   ✅ Encryption/Decryption successful: {plaintext == decrypted}")
        
        return aes_key, cipher.iv, ciphertext
    
    def demonstrate_weak_encryption(self):
        """Demonstrate weak encryption that can be broken"""
        print("\n--- Weak Encryption Analysis ---")
        
        # Caesar cipher (very weak)
        def caesar_encrypt(text, shift):
            result = ""
            for char in text:
                if char.isalpha():
                    ascii_offset = 65 if char.isupper() else 97
                    result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
                else:
                    result += char
            return result
        
        def caesar_decrypt(text, shift):
            return caesar_encrypt(text, -shift)
        
        message = "HELLO HACKER"
        shift = 13  # ROT13
        
        encrypted = caesar_encrypt(message, shift)
        print(f"📝 Original: {message}")
        print(f"🔐 Caesar cipher (shift {shift}): {encrypted}")
        
        # Brute force attack
        print("\n🔨 Brute force attack on Caesar cipher:")
        for test_shift in range(26):
            decrypted = caesar_decrypt(encrypted, test_shift)
            print(f"   Shift {test_shift:2d}: {decrypted}")
            
            # Check if we found meaningful text
            if "HELLO" in decrypted:
                print(f"   ✅ Key found! Shift: {test_shift}")
                break
    
    def frequency_analysis_attack(self):
        """Demonstrate frequency analysis on substitution cipher"""
        print("\n--- Frequency Analysis Attack ---")
        
        # Sample encrypted text (substitution cipher)
        encrypted_text = """
        WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ.
        WKLV LV D VLPSOH VXEVWLWXWLRQ FLSKHU WKDW FDQ EH EURNHQ.
        """
        
        print(f"🔐 Encrypted text: {encrypted_text}")
        
        # Count letter frequencies
        frequency = {}
        for char in encrypted_text.upper():
            if char.isalpha():
                frequency[char] = frequency.get(char, 0) + 1
        
        # Sort by frequency
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        print("\n📊 Letter frequency analysis:")
        print("   Letter | Count | Frequency")
        println("   -------|-------|----------")
        total_letters = sum(frequency.values())
        
        for letter, count in sorted_freq[:10]:
            freq_percent = (count / total_letters) * 100
            print(f"   {letter:6s} | {count:5d} | {freq_percent:6.2f}%")
        
        # English letter frequencies for comparison
        english_freq = {
            'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,
            'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3
        }
        
        print("\n💡 Most common English letters: E, T, A, O, I, N, S, H, R, D")
        print("   Analysis suggests this might be a Caesar cipher with shift 3")
        
        # Test Caesar decryption with shift 3
        def caesar_decrypt(text, shift):
            result = ""
            for char in text:
                if char.isalpha():
                    ascii_offset = 65 if char.isupper() else 97
                    result += chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
                else:
                    result += char
            return result
        
        decrypted = caesar_decrypt(encrypted_text, 3)
        print(f"\n🔓 Decrypted with shift 3: {decrypted}")

class SteganographyLab:
    """Steganography techniques for hiding data"""
    
    def __init__(self):
        self.temp_dir = Path("steganography_temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_sample_image(self):
        """Create a sample image for steganography testing"""
        # Create a simple test image
        width, height = 200, 200
        image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        
        # Add some patterns to make it more realistic
        for i in range(height):
            for j in range(width):
                if (i + j) % 20 < 10:
                    image_array[i, j] = [100, 150, 200]  # Light blue
                else:
                    image_array[i, j] = [200, 200, 200]  # Light gray
        
        image = Image.fromarray(image_array)
        image_path = self.temp_dir / "cover_image.png"
        image.save(image_path)
        
        print(f"✅ Created sample image: {image_path}")
        return str(image_path)
    
    def hide_message_in_image(self, image_path, secret_message):
        """Hide a message in an image using LSB steganography"""
        print(f"\n--- Hiding Message in Image ---")
        print(f"📝 Secret message: {secret_message}")
        
        # Load the image
        image = Image.open(image_path)
        pixels = list(image.getdata())
        
        # Convert message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
        binary_message += '1111111111111110'  # Delimiter to mark end
        
        print(f"🔢 Message in binary ({len(binary_message)} bits): {binary_message[:50]}...")
        
        # Hide message in LSBs
        modified_pixels = []
        bit_index = 0
        
        for pixel in pixels:
            if isinstance(pixel, tuple):
                r, g, b = pixel
            else:
                r = g = b = pixel
            
            # Modify LSBs of RGB channels
            if bit_index < len(binary_message):
                r = (r & 0xFE) | int(binary_message[bit_index])
                bit_index += 1
            
            if bit_index < len(binary_message):
                g = (g & 0xFE) | int(binary_message[bit_index])
                bit_index += 1
            
            if bit_index < len(binary_message):
                b = (b & 0xFE) | int(binary_message[bit_index])
                bit_index += 1
            
            modified_pixels.append((r, g, b))
            
            if bit_index >= len(binary_message):
                # Add remaining pixels unchanged
                modified_pixels.extend(pixels[len(modified_pixels):])
                break
        
        # Create new image with hidden message
        stego_image = Image.new(image.mode, image.size)
        stego_image.putdata(modified_pixels)
        
        stego_path = self.temp_dir / "stego_image.png"
        stego_image.save(stego_path)
        
        print(f"✅ Message hidden in: {stego_path}")
        return str(stego_path)
    
    def extract_message_from_image(self, stego_image_path):
        """Extract hidden message from steganographic image"""
        print(f"\n--- Extracting Hidden Message ---")
        
        # Load the steganographic image
        image = Image.open(stego_image_path)
        pixels = list(image.getdata())
        
        # Extract LSBs
        binary_message = ""
        
        for pixel in pixels:
            if isinstance(pixel, tuple):
                r, g, b = pixel
            else:
                r = g = b = pixel
            
            # Extract LSBs from RGB channels
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
        
        # Find the delimiter
        delimiter = '1111111111111110'
        end_index = binary_message.find(delimiter)
        
        if end_index == -1:
            print("❌ No hidden message found")
            return None
        
        # Extract the actual message
        message_binary = binary_message[:end_index]
        
        # Convert binary to text
        if len(message_binary) % 8 != 0:
            print("❌ Invalid message length")
            return None
        
        hidden_message = ""
        for i in range(0, len(message_binary), 8):
            byte = message_binary[i:i+8]
            hidden_message += chr(int(byte, 2))
        
        print(f"🔓 Extracted message: {hidden_message}")
        return hidden_message
    
    def hide_file_in_image(self, image_path, secret_file_path):
        """Hide an entire file in an image"""
        print(f"\n--- Hiding File in Image ---")
        
        # Read the secret file
        with open(secret_file_path, 'rb') as f:
            file_data = f.read()
        
        print(f"📁 Hiding file: {secret_file_path} ({len(file_data)} bytes)")
        
        # Convert file data to binary
        binary_data = ''.join(format(byte, '08b') for byte in file_data)
        
        # Add file size header and delimiter
        file_size = len(file_data)
        size_header = format(file_size, '032b')  # 32-bit file size
        binary_message = size_header + binary_data + '1111111111111110'
        
        # Use the same LSB method as before
        return self.hide_binary_in_image(image_path, binary_message)
    
    def hide_binary_in_image(self, image_path, binary_data):
        """Helper method to hide binary data in image"""
        image = Image.open(image_path)
        pixels = list(image.getdata())
        
        if len(binary_data) > len(pixels) * 3:
            print("❌ Image too small to hide the data")
            return None
        
        modified_pixels = []
        bit_index = 0
        
        for pixel in pixels:
            if isinstance(pixel, tuple):
                r, g, b = pixel
            else:
                r = g = b = pixel
            
            # Modify LSBs
            if bit_index < len(binary_data):
                r = (r & 0xFE) | int(binary_data[bit_index])
                bit_index += 1
            
            if bit_index < len(binary_data):
                g = (g & 0xFE) | int(binary_data[bit_index])
                bit_index += 1
            
            if bit_index < len(binary_data):
                b = (b & 0xFE) | int(binary_data[bit_index])
                bit_index += 1
            
            modified_pixels.append((r, g, b))
            
            if bit_index >= len(binary_data):
                modified_pixels.extend(pixels[len(modified_pixels):])
                break
        
        # Save steganographic image
        stego_image = Image.new(image.mode, image.size)
        stego_image.putdata(modified_pixels)
        
        stego_path = self.temp_dir / "file_stego_image.png"
        stego_image.save(stego_path)
        
        print(f"✅ File hidden in: {stego_path}")
        return str(stego_path)

class DigitalForensicsLab:
    """Digital forensics analysis tools"""
    
    def __init__(self):
        self.evidence_dir = Path("forensics_evidence")
        self.evidence_dir.mkdir(exist_ok=True)
    
    def create_forensic_evidence(self):
        """Create sample forensic evidence for analysis"""
        print("\n--- Creating Forensic Evidence ---")
        
        # Create a suspicious file with metadata
        suspicious_content = """
        Meeting Notes - Project Blue
        ============================
        Date: 2024-10-26
        Attendees: Alice, Bob, Charlie
        
        Discussed:
        - New security protocols
        - Access code changes: 7734 -> 8847
        - Server migration scheduled for midnight
        - Backup location: /hidden/backup/sensitive/
        
        Action items:
        - Update firewall rules
        - Revoke old certificates
        - Test emergency procedures
        
        CONFIDENTIAL - DO NOT DISTRIBUTE
        """
        
        evidence_file = self.evidence_dir / "meeting_notes.txt"
        with open(evidence_file, 'w') as f:
            f.write(suspicious_content)
        
        # Create a file with hidden data
        hidden_data = {
            "user_accounts": [
                {"username": "admin", "password_hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"},
                {"username": "guest", "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"}
            ],
            "network_config": {
                "internal_ip": "192.168.1.100",
                "external_ip": "203.45.67.89",
                "backdoor_port": "31337"
            },
            "timestamps": {
                "last_login": "2024-10-25 23:45:12",
                "last_modified": "2024-10-26 02:15:33"
            }
        }
        
        json_file = self.evidence_dir / "system_config.json"
        with open(json_file, 'w') as f:
            json.dump(hidden_data, f, indent=2)
        
        # Create a ZIP file with password
        zip_file = self.evidence_dir / "encrypted_backup.zip"
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr("secret.txt", "Top secret information", pwd=b"forensics123")
            zf.writestr("logs.txt", "System logs with sensitive data", pwd=b"forensics123")
        
        print(f"✅ Created evidence files in {self.evidence_dir}")
        return [str(evidence_file), str(json_file), str(zip_file)]
    
    def analyze_file_metadata(self, file_path):
        """Analyze file metadata for forensic information"""
        print(f"\n--- File Metadata Analysis: {file_path} ---")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            print("❌ File not found")
            return
        
        # Basic file information
        stat = file_path.stat()
        
        print(f"📁 File name: {file_path.name}")
        print(f"📏 File size: {stat.st_size} bytes")
        print(f"📅 Created: {time.ctime(stat.st_ctime)}")
        print(f"📝 Modified: {time.ctime(stat.st_mtime)}")
        print(f"👁️  Accessed: {time.ctime(stat.st_atime)}")
        print(f"🔒 Permissions: {oct(stat.st_mode)}")
        
        # File hash for integrity
        with open(file_path, 'rb') as f:
            content = f.read()
            md5_hash = hashlib.md5(content).hexdigest()
            sha256_hash = hashlib.sha256(content).hexdigest()
        
        print(f"🔢 MD5: {md5_hash}")
        print(f"🔢 SHA256: {sha256_hash}")
        
        # Content analysis
        if file_path.suffix == '.txt':
            self.analyze_text_content(file_path)
        elif file_path.suffix == '.json':
            self.analyze_json_content(file_path)
    
    def analyze_text_content(self, file_path):
        """Analyze text file for forensic artifacts"""
        print(f"\n🔍 Text Content Analysis:")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Look for patterns
        patterns = {
            'IP addresses': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'Email addresses': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'Phone numbers': r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b',
            'Dates': r'\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b',
            'Times': r'\b\d{2}:\d{2}:\d{2}\b',
            'URLs': r'https?://[^\s]+',
            'File paths': r'[/\\][^\s]*[/\\][^\s]*',
            'Passwords/Keys': r'(?i)(password|key|secret|token)[^\w]*[:\s=][^\s]+',
        }
        
        import re
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                print(f"   {pattern_name}: {matches}")
        
        # Word frequency analysis
        words = content.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Most common words (excluding common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        common_words = [(word, count) for word, count in word_freq.items() 
                       if word not in stop_words and len(word) > 3]
        common_words.sort(key=lambda x: x[1], reverse=True)
        
        if common_words:
            print(f"   Common words: {common_words[:5]}")
    
    def analyze_json_content(self, file_path):
        """Analyze JSON file for sensitive information"""
        print(f"\n🔍 JSON Content Analysis:")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Look for sensitive keys
            sensitive_keys = ['password', 'key', 'secret', 'token', 'credential', 'hash']
            
            def find_sensitive_data(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # Check if key name suggests sensitive data
                        if any(sensitive in key.lower() for sensitive in sensitive_keys):
                            print(f"   🚨 Sensitive key found: {current_path} = {value}")
                        
                        find_sensitive_data(value, current_path)
                        
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_sensitive_data(item, f"{path}[{i}]")
            
            find_sensitive_data(data)
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
    
    def timeline_analysis(self, evidence_files):
        """Perform timeline analysis of evidence files"""
        print(f"\n--- Timeline Analysis ---")
        
        timeline_events = []
        
        for file_path in evidence_files:
            file_path = Path(file_path)
            if file_path.exists():
                stat = file_path.stat()
                
                timeline_events.append({
                    'timestamp': stat.st_ctime,
                    'event': f"File created: {file_path.name}",
                    'type': 'creation'
                })
                
                timeline_events.append({
                    'timestamp': stat.st_mtime,
                    'event': f"File modified: {file_path.name}",
                    'type': 'modification'
                })
        
        # Sort events by timestamp
        timeline_events.sort(key=lambda x: x['timestamp'])
        
        print("📅 Timeline of Events:")
        for event in timeline_events:
            timestamp = time.ctime(event['timestamp'])
            print(f"   {timestamp} | {event['event']}")

def advanced_cryptanalysis_challenge():
    """Advanced cryptanalysis challenge"""
    print("\n" + "="*60)
    print("🧩 ADVANCED CRYPTANALYSIS CHALLENGE")
    print("="*60)
    
    # Multi-layer encrypted message
    original_message = "The key to the vault is hidden in the frequency analysis"
    
    print(f"🎯 Challenge: Decrypt the multi-layer encrypted message")
    print(f"💡 Hint: Multiple encryption layers have been applied")
    
    # Layer 1: Base64 encoding
    layer1 = base64.b64encode(original_message.encode()).decode()
    print(f"\n🔐 Layer 1 (Base64): {layer1}")
    
    # Layer 2: Caesar cipher (shift 7)
    def caesar_encrypt(text, shift):
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            else:
                result += char
        return result
    
    layer2 = caesar_encrypt(layer1, 7)
    print(f"🔐 Layer 2 (Caesar+7): {layer2}")
    
    # Layer 3: Reverse string
    layer3 = layer2[::-1]
    print(f"🔐 Layer 3 (Reversed): {layer3}")
    
    print(f"\n🎮 Your task: Decrypt this step by step!")
    print(f"Final encrypted message: {layer3}")
    
    # Solution process
    print(f"\n💡 Solution process:")
    print(f"1. Reverse the string: {layer3[::-1]}")
    print(f"2. Apply Caesar decrypt (shift -7): {caesar_encrypt(layer3[::-1], -7)}")
    
    decrypted_base64 = caesar_encrypt(layer3[::-1], -7)
    final_message = base64.b64decode(decrypted_base64).decode()
    print(f"3. Decode Base64: {final_message}")
    
    return final_message == original_message

def main():
    """Main function for Iteration 4"""
    print("Iteration 4: Advanced Cryptography and Digital Forensics")
    print("This program demonstrates advanced cryptographic techniques and forensic analysis.\n")
    
    print("⚠️  ETHICAL NOTICE:")
    print("   • Educational and research purposes only")
    print("   • Only analyze data you own or have permission to examine")
    print("   • Respect privacy laws and regulations")
    print("   • Use knowledge for defensive cybersecurity")
    
    # Cryptography demonstrations
    print("\n" + "="*60)
    print("🔐 ADVANCED CRYPTOGRAPHY")
    print("="*60)
    
    crypto_lab = CryptographyLab()
    crypto_lab.demonstrate_symmetric_encryption()
    crypto_lab.demonstrate_weak_encryption()
    crypto_lab.frequency_analysis_attack()
    
    # Steganography demonstrations
    print("\n" + "="*60)
    print("🖼️  STEGANOGRAPHY TECHNIQUES")
    print("="*60)
    
    stego_lab = SteganographyLab()
    
    try:
        # Create sample image and hide message
        image_path = stego_lab.create_sample_image()
        secret_message = "This is a hidden message in the image pixels!"
        
        stego_image_path = stego_lab.hide_message_in_image(image_path, secret_message)
        extracted_message = stego_lab.extract_message_from_image(stego_image_path)
        
        print(f"✅ Steganography test: {'PASSED' if extracted_message == secret_message else 'FAILED'}")
        
    except ImportError:
        print("⚠️  PIL/Pillow not available - skipping image steganography demo")
        print("   Install with: pip install Pillow")
    
    # Digital forensics demonstrations
    print("\n" + "="*60)
    print("🔍 DIGITAL FORENSICS ANALYSIS")
    print("="*60)
    
    forensics_lab = DigitalForensicsLab()
    evidence_files = forensics_lab.create_forensic_evidence()
    
    # Analyze each evidence file
    for evidence_file in evidence_files:
        forensics_lab.analyze_file_metadata(evidence_file)
    
    # Timeline analysis
    forensics_lab.timeline_analysis(evidence_files)
    
    # Advanced cryptanalysis challenge
    success = advanced_cryptanalysis_challenge()
    print(f"\n🏆 Cryptanalysis challenge: {'COMPLETED' if success else 'INCOMPLETE'}")
    
    print("\n" + "="*60)
    print("🎓 KEY LEARNING POINTS:")
    print("="*60)
    print("1. Symmetric encryption algorithms (AES, DES)")
    print("2. Cryptanalysis techniques (frequency analysis, brute force)")
    print("3. Steganography in images using LSB method")
    print("4. Digital forensics and metadata analysis")
    print("5. Timeline reconstruction from file artifacts")
    print("6. Multi-layer encryption and decryption")
    print("7. Pattern recognition in forensic data")
    print("8. Hash functions for integrity verification")
    print("="*60)
    
    print("\n🔧 Advanced Topics to Explore:")
    print("   • RSA and public-key cryptography")
    print("   • Blockchain and cryptocurrency forensics")
    print("   • Network packet analysis with Wireshark")
    print("   • Memory dump analysis")
    print("   • Mobile device forensics")

if __name__ == "__main__":
    main()