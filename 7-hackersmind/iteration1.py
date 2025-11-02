#!/usr/bin/env python3
"""
Iteration 1: Basic Password Cracking and ZIP File Analysis
==========================================================
This program introduces basic password cracking techniques and ZIP file manipulation.
Focus: Dictionary attacks, brute force basics, and file analysis.

⚠️  ETHICAL NOTICE: This program is for educational purposes only.
    Only use on files you own or have explicit permission to test.
"""

import zipfile
import itertools
import string
import time
import os
from pathlib import Path

class BasicPasswordCracker:
    """Basic password cracking utilities"""
    
    def __init__(self):
        self.common_passwords = [
            "password", "123456", "password123", "admin", "letmein",
            "welcome", "monkey", "1234567890", "qwerty", "abc123",
            "Password1", "welcome123", "admin123", "root", "toor",
            "guest", "test", "demo", "user", "login"
        ]
        self.attempts = 0
        self.start_time = None
    
    def dictionary_attack(self, zip_file_path, wordlist=None):
        """Perform dictionary attack on ZIP file"""
        print(f"\n--- Dictionary Attack on {zip_file_path} ---")
        
        if not os.path.exists(zip_file_path):
            print(f"❌ File not found: {zip_file_path}")
            return None
        
        wordlist = wordlist or self.common_passwords
        self.start_time = time.time()
        self.attempts = 0
        
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                print(f"📦 ZIP file loaded: {len(zip_ref.filelist)} files inside")
                
                for password in wordlist:
                    self.attempts += 1
                    try:
                        zip_ref.extractall(pwd=password.encode())
                        elapsed = time.time() - self.start_time
                        print(f"🎉 SUCCESS! Password found: '{password}'")
                        print(f"⏱️  Attempts: {self.attempts}, Time: {elapsed:.2f}s")
                        return password
                    except (RuntimeError, zipfile.BadZipFile):
                        print(f"❌ Failed: '{password}' (attempt {self.attempts})")
                        continue
                
                print(f"🚫 Dictionary attack failed after {self.attempts} attempts")
                return None
                
        except zipfile.BadZipFile:
            print("❌ Not a valid ZIP file")
            return None
    
    def brute_force_numeric(self, zip_file_path, max_length=4):
        """Brute force attack with numeric passwords"""
        print(f"\n--- Numeric Brute Force Attack (max length: {max_length}) ---")
        
        if not os.path.exists(zip_file_path):
            print(f"❌ File not found: {zip_file_path}")
            return None
        
        self.start_time = time.time()
        self.attempts = 0
        
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Try all numeric combinations
                for length in range(1, max_length + 1):
                    print(f"🔍 Trying {length}-digit combinations...")
                    
                    for combo in itertools.product(string.digits, repeat=length):
                        password = ''.join(combo)
                        self.attempts += 1
                        
                        try:
                            zip_ref.extractall(pwd=password.encode())
                            elapsed = time.time() - self.start_time
                            print(f"🎉 SUCCESS! Password found: '{password}'")
                            print(f"⏱️  Attempts: {self.attempts}, Time: {elapsed:.2f}s")
                            return password
                        except (RuntimeError, zipfile.BadZipFile):
                            if self.attempts % 100 == 0:
                                print(f"⏳ Tried {self.attempts} combinations...")
                            continue
                
                print(f"🚫 Brute force failed after {self.attempts} attempts")
                return None
                
        except zipfile.BadZipFile:
            print("❌ Not a valid ZIP file")
            return None
    
    def pattern_based_attack(self, zip_file_path, base_word, variations=True):
        """Try pattern-based password variations"""
        print(f"\n--- Pattern-Based Attack with base: '{base_word}' ---")
        
        patterns = [base_word]
        
        if variations:
            # Common variations
            patterns.extend([
                base_word.upper(),
                base_word.lower(),
                base_word.capitalize(),
                base_word + "1",
                base_word + "123",
                base_word + "2023",
                base_word + "2024",
                "1" + base_word,
                base_word + "!",
                base_word + "@",
                base_word.replace('a', '@'),
                base_word.replace('o', '0'),
                base_word.replace('e', '3'),
                base_word.replace('i', '1'),
                base_word[::-1],  # Reverse
            ])
        
        return self.dictionary_attack(zip_file_path, patterns)

def create_sample_zip_files():
    """Create sample ZIP files for testing"""
    print("\n--- Creating Sample ZIP Files for Testing ---")
    
    sample_dir = Path("sample_files")
    sample_dir.mkdir(exist_ok=True)
    
    # Create simple text files first
    easy_content = "Congratulations! You cracked the easy password.\nHint for next level: Think about common passwords."
    medium_content = "Well done! You're getting better.\nThis demonstrates dictionary attacks."
    hard_content = "Excellent! You understand patterns.\nYou've completed the basic challenges."
    
    # Create text files
    easy_file = sample_dir / "secret.txt"
    medium_file = sample_dir / "message.txt" 
    hard_file = sample_dir / "final.txt"
    
    easy_file.write_text(easy_content)
    medium_file.write_text(medium_content)
    hard_file.write_text(hard_content)
    
    # Create ZIP files (without password for now - this is a demonstration)
    easy_zip = sample_dir / "level1_easy.zip"
    medium_zip = sample_dir / "level2_medium.zip"
    hard_zip = sample_dir / "level3_hard.zip"
    
    with zipfile.ZipFile(easy_zip, 'w') as zip_ref:
        zip_ref.write(easy_file, "secret.txt")
    
    with zipfile.ZipFile(medium_zip, 'w') as zip_ref:
        zip_ref.write(medium_file, "message.txt")
    
    with zipfile.ZipFile(hard_zip, 'w') as zip_ref:
        zip_ref.write(hard_file, "final.txt")
    
    print(f"✅ Created: {easy_zip} (Simulated password: 123456)")
    print(f"✅ Created: {medium_zip} (Simulated password: password)")
    print(f"✅ Created: {hard_zip} (Simulated password: hello42)")
    print("📝 Note: For demonstration purposes, these ZIPs are not password protected")
    print("    In real scenarios, you would use tools like John the Ripper or hashcat")
    
    return [str(easy_zip), str(medium_zip), str(hard_zip)]

def analyze_zip_file(zip_path):
    """Analyze ZIP file structure and properties"""
    print(f"\n--- ZIP File Analysis: {zip_path} ---")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print(f"📊 File Count: {len(zip_ref.filelist)}")
            print(f"💾 Total Size: {sum(f.file_size for f in zip_ref.filelist)} bytes")
            print(f"📦 Compressed Size: {sum(f.compress_size for f in zip_ref.filelist)} bytes")
            
            print("\n📋 File Details:")
            for file_info in zip_ref.filelist:
                print(f"  📄 {file_info.filename}")
                print(f"     Size: {file_info.file_size} bytes")
                print(f"     Compressed: {file_info.compress_size} bytes")
                print(f"     Modified: {file_info.date_time}")
                print(f"     Encrypted: {'Yes' if file_info.flag_bits & 0x1 else 'No'}")
                
    except zipfile.BadZipFile:
        print("❌ Invalid ZIP file")
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")

def password_strength_analyzer():
    """Analyze password strength and common patterns"""
    print("\n--- Password Strength Analyzer ---")
    
    def analyze_password(password):
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 2
        elif len(password) >= 6:
            score += 1
        else:
            feedback.append("Too short (minimum 6 characters)")
        
        # Character variety
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
            
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
            
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Add numbers")
            
        if any(c in "!@#$%^&*()_+-=[]{}|;:',.<>?" for c in password):
            score += 2
        else:
            feedback.append("Add special characters")
        
        # Common patterns (negative points)
        common_patterns = ["123", "abc", "qwe", "password", "admin"]
        for pattern in common_patterns:
            if pattern.lower() in password.lower():
                score -= 1
                feedback.append(f"Avoid common pattern: {pattern}")
        
        # Strength rating
        if score >= 6:
            strength = "🟢 Strong"
        elif score >= 4:
            strength = "🟡 Medium"
        else:
            strength = "🔴 Weak"
        
        return score, strength, feedback
    
    test_passwords = [
        "123456",
        "password",
        "Password1",
        "MySecure123!",
        "Tr0ub4dor&3",
        "correct horse battery staple"
    ]
    
    for pwd in test_passwords:
        score, strength, feedback = analyze_password(pwd)
        print(f"\nPassword: '{pwd}'")
        print(f"Strength: {strength} (Score: {score})")
        if feedback:
            print("Recommendations:")
            for suggestion in feedback:
                print(f"  • {suggestion}")

def interactive_cracking_session():
    """Interactive password cracking session"""
    print("\n" + "="*60)
    print("🎯 INTERACTIVE CRACKING SESSION")
    print("="*60)
    
    cracker = BasicPasswordCracker()
    
    # Create sample files
    sample_files = create_sample_zip_files()
    
    print("\n🎮 Choose your challenge:")
    print("1. Easy Level (Dictionary Attack)")
    print("2. Medium Level (Pattern Attack)")
    print("3. Hard Level (Custom Strategy)")
    print("4. Analyze ZIP file structure")
    print("5. Password strength analysis")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🎯 Level 1: Basic Dictionary Attack")
            zip_file = sample_files[0]
            analyze_zip_file(zip_file)
            result = cracker.dictionary_attack(zip_file)
            if result:
                print(f"🏆 Level 1 completed! Found password: {result}")
        
        elif choice == "2":
            print("\n🎯 Level 2: Pattern-Based Attack")
            zip_file = sample_files[1]
            analyze_zip_file(zip_file)
            base_word = input("Enter a base word to try patterns with: ").strip()
            result = cracker.pattern_based_attack(zip_file, base_word)
            if result:
                print(f"🏆 Level 2 completed! Found password: {result}")
        
        elif choice == "3":
            print("\n🎯 Level 3: Advanced Challenge")
            zip_file = sample_files[2]
            analyze_zip_file(zip_file)
            print("💡 Hint: Try combining words with numbers")
            
            strategy = input("Choose strategy (1=Dictionary, 2=Brute Force, 3=Pattern): ").strip()
            if strategy == "1":
                result = cracker.dictionary_attack(zip_file)
            elif strategy == "2":
                result = cracker.brute_force_numeric(zip_file, 3)
            elif strategy == "3":
                base = input("Enter base word: ").strip()
                result = cracker.pattern_based_attack(zip_file, base)
            
            if result:
                print(f"🏆 Level 3 completed! Found password: {result}")
        
        elif choice == "4":
            zip_file = input("Enter ZIP file path to analyze: ").strip()
            analyze_zip_file(zip_file)
        
        elif choice == "5":
            password_strength_analyzer()
        
        else:
            print("❌ Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Session interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function demonstrating basic password cracking concepts"""
    print("Iteration 1: Basic Password Cracking and ZIP File Analysis")
    print("This program introduces fundamental concepts of password security testing.\n")
    
    print("⚠️  ETHICAL NOTICE:")
    print("   • This is for educational purposes only")
    print("   • Only test on files you own or have permission to test")
    print("   • Respect others' privacy and follow applicable laws")
    print("   • Use knowledge responsibly for defensive security")
    
    # Demonstrate basic concepts
    print("\n" + "="*60)
    print("🔍 BASIC CONCEPTS DEMONSTRATION")
    print("="*60)
    
    # Create and analyze sample files
    sample_files = create_sample_zip_files()
    
    # Demonstrate different attack methods
    cracker = BasicPasswordCracker()
    
    print(f"\n🎯 Demonstrating Dictionary Attack:")
    analyze_zip_file(sample_files[0])
    cracker.dictionary_attack(sample_files[0])
    
    # Interactive session
    interactive_cracking_session()
    
    print("\n" + "="*60)
    print("🎓 KEY LEARNING POINTS:")
    print("="*60)
    print("1. Password attacks: Dictionary, Brute Force, Pattern-based")
    print("2. ZIP file structure and encryption analysis")
    print("3. Password strength evaluation")
    print("4. Time complexity in password cracking")
    print("5. Ethical considerations in security testing")
    print("6. Defensive strategies against common attacks")
    print("="*60)

if __name__ == "__main__":
    main()