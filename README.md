#  WiFi-Demon - The Ultimate WiFi Penetration Testing Toolkit


**WiFi-Demon** is a comprehensive WiFi penetration testing toolkit designed for red team operations, security assessments, and authorized network testing. This tool automates the entire WiFi hacking workflow from scanning to cracking.

##  Features That Will Blow Your Mind

###  **Network Reconnaissance**
- **Full Spectrum Scanning**: Detect all nearby WiFi networks with detailed information
- **BSSID/ESSID Extraction**: Get MAC addresses, channels, encryption types, and signal strength
- **Client Detection**: Identify connected devices to target
- **Multi-Interface Support**: Works with wlan0, wlan1, wlan2, and any monitor-capable interface

###  **Attack Modules**
- **WPA/WPA2 Handshake Capture**: Automatically capture authentication handshakes
- **Deauthentication Attacks**: Force clients to reconnect for handshake capture
- **PMKID Extraction**: Alternative method for WPA handshake collection
- **Rogue AP Detection**: Identify malicious access points in your area

###  **Cracking Power**
- **Wordlist Attacks**: Crack handshakes using rockyou.txt and custom wordlists
- **Hashcat Integration**: Export hashes for GPU cracking
- **Live Cracking**: Real-time password attempts with progress tracking
- **Custom Wordlist Generator**: Create targeted wordlists based on network info

### 🛠 **Advanced Features**
- **Monitor Mode Management**: Automatic interface switching
- **Packet Injection**: Test network security and client isolation
- **MAC Address Spoofing**: Stay anonymous during operations
- **Logging & Reporting**: Detailed logs and exportable reports
- **GUI & CLI**: Both interface options available

##  Quick Start

### Prerequisites
- **Linux** (Kali, Parrot, Ubuntu recommended)
- **Root privileges** (sudo access)
- **WiFi adapter** with monitor mode and packet injection support
  - Recommended: Alfa AWUS036ACH, AWUS036NHA, or Panda PAU09

### Installation (One Command)

```bash
# Clone the repository
git clone https://github.com/n0merc/wifi-demon.git

# Navigate to directory
cd wifi-demon

# Run the installer (requires root)
sudo chmod +x install.sh
sudo ./install.sh
```

### Manual Installation

```bash
# Install dependencies
sudo apt update
sudo apt install python3 aircrack-ng wireless-tools python3-colorama

# Run directly
sudo python3 wifi_demon.py
```

##  Usage Examples

### Basic Usage
```bash
# Start WiFi-Demon
sudo wifi-demon

# Or use the alias
wifidemon
```

### Command Line Options
```bash
# Scan specific interface
sudo wifi-demon --interface wlan0 --scan

# Target specific network
sudo wifi-demon --bssid AA:BB:CC:DD:EE:FF --channel 6

# Crack handshake with custom wordlist
sudo wifi-demon --crack handshake.cap --wordlist /path/to/wordlist.txt

# Deauth attack
sudo wifi-demon --deauth --bssid AA:BB:CC:DD:EE:FF --packets 100
```

### Menu Interface
```
┌─────────────────────────────────────────────┐
│              WiFi-Demon v1.0                │
│                by n0merc                    │
└─────────────────────────────────────────────┘

[1] Scan WiFi Networks
[2] Capture WPA Handshake  
[3] Crack Handshake
[4] Deauthentication Attack
[5] Show Interface Info
[6] Exit

Enter your choice: 
```

##  Attack Workflow

### Step 1: Network Discovery
```bash
# Put interface in monitor mode
sudo airmon-ng start wlan0

# Scan for networks
sudo wifi-demon --scan
```

### Step 2: Target Selection
```
[+] Available Networks:
[1] Home-WiFi          BSSID: AA:BB:CC:DD:EE:FF CH: 6  ENC: WPA2
[2] Starbucks-Free     BSSID: 11:22:33:44:55:66 CH: 11 ENC: WPA2
[3] Admin-Network      BSSID: 77:88:99:AA:BB:CC CH: 1  ENC: WPA2
```

### Step 3: Handshake Capture
```bash
# Capture handshake from target
sudo wifi-demon --bssid AA:BB:CC:DD:EE:FF --channel 6 --capture

# Or use deauth to force reconnection
sudo wifi-demon --deauth --bssid AA:BB:CC:DD:EE:FF --client 11:22:33:44:55:66
```

### Step 4: Crack the Password
```bash
# Crack with default wordlist
sudo wifi-demon --crack handshake_Home-WiFi.cap

# Use custom wordlist
sudo wifi-demon --crack handshake.cap --wordlist /usr/share/wordlists/rockyou.txt

# Export for hashcat
sudo wifi-demon --export-hash handshake.cap --format hashcat
```

##  Advanced Configuration

### Custom Wordlists
Create targeted wordlists based on:
- Company names
- Location-based passwords
- Common password patterns
- Social engineering data

### Scripting & Automation
```python
#!/usr/bin/env python3
from wifi_demon import WiFiDemon

# Automated penetration test
wd = WiFiDemon(interface='wlan0')
networks = wd.scan()
target = wd.select_target(networks)
handshake = wd.capture_handshake(target)
result = wd.crack(handshake, wordlist='custom.txt')
```

### Integration with Other Tools
- **Hashcat**: Export hashes for GPU cracking
- **Metasploit**: Use captured credentials for further exploitation
- **John the Ripper**: Alternative cracking engine
- **Wireshark**: Analyze captured packets

##  Performance Benchmarks

| Operation | Time | Success Rate |
|-----------|------|--------------|
| Network Scan | 10-30 seconds | 100% |
| Handshake Capture | 1-5 minutes | 85-95% |
| Deauth Attack | Instant | 98% |
| Cracking (rockyou) | Variable | Depends on password strength |

##  Troubleshooting

### Common Issues & Solutions

**Issue**: "No WiFi interfaces found"
```bash
# Check available interfaces
iwconfig

# Install drivers for your adapter
sudo apt install firmware-atheros  # For Atheros chipsets
sudo apt install firmware-realtek  # For Realtek chipsets
```

**Issue**: "Monitor mode not supported"
```bash
# Check adapter capabilities
sudo iw list

# Try different interface
sudo wifi-demon --interface wlan1
```

**Issue**: "Handshake not captured"
```bash
# Increase capture time
sudo wifi-demon --capture --timeout 300

# Use deauth attack
sudo wifi-demon --deauth --packets 50
```

##  Legal & Ethical Disclaimer

**IMPORTANT**: This tool is for:
- ✅ Authorized security testing
- ✅ Educational purposes  
- ✅ Personal network assessment (your own networks)
- ✅ CTF competitions
- ✅ Security research

**NOT FOR**:
- ❌ Unauthorized network access
- ❌ Illegal activities
- ❌ Harassment or stalking
- ❌ Commercial exploitation without permission

**By using this tool, you agree to:**
1. Use it only on networks you own or have explicit permission to test
2. Comply with all applicable laws and regulations
3. Accept full responsibility for your actions
4. Not use it for malicious purposes

##  Contributing

We fucking love contributions! Here's how to help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

Check out [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

##  Reporting Issues

Found a bug? Have a feature request? Open an issue with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Your system configuration

## Learning Resources

- [WiFi Security & Hacking Course](https://www.udemy.com/course/wifi-hacking/)
- [Aircrack-ng Documentation](https://www.aircrack-ng.org/doku.php)
- [OWASP Wireless Testing Guide](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/10-Testing_Weak_Cryptography)
- [Hashcat Examples](https://hashcat.net/wiki/doku.php?id=example_hashes)

##  Credits

- **n0merc** - Creator & Maintainer
- **HUBAX Team** - Testing & Development
- **Aircrack-ng Team** - Base tools
- **Contributors** - Everyone who helped improve this tool

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Support the Project

If this tool helped you, please:
1. **Star** the repository
2. **Share** with other security professionals
3. **Contribute** code or documentation
4. **Donate** (links in GitHub sponsor section)

---

**Remember**: With great power comes great responsibility. Use this tool ethically and legally. Stay safe, stay stealthy, and happy hacking! 🔥
