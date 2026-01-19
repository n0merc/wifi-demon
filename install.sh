#!/bin/bash
# WiFi-Demon Installer
# Author: n0merc
# GitHub: https://github.com/n0merc/wifi-demon

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

BANNER="${RED}
██╗    ██╗██╗███████╗██╗     
██║    ██║██║██╔════╝██║     
██║ █╗ ██║██║█████╗  ██║     
██║███╗██║██║██╔══╝  ██║          
╚███╔███╔╝██║██║     ██║
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝
${YELLOW}
██████╗ ███████╗███╗   ███╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝████╗ ████║██╔═══██╗████╗  ██║
██║  ██║█████╗  ██╔████╔██║██║   ██║██╔██╗ ██║
██║  ██║██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║
██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
${CYAN}
                WiFi-Demon Installer
                Created by n0merc
        https://github.com/n0merc/wifi-demon
${NC}"

print_banner() {
    clear
    echo -e "$BANNER"
    echo -e "${GREEN}=======================================================${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}[!] This installer must be run as root!${NC}"
        echo -e "${YELLOW}[*] Run: sudo ./install.sh${NC}"
        exit 1
    fi
}

check_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    echo -e "${CYAN}[*] Detected OS: $OS $VER${NC}"
    
    case $OS in
        *Debian*|*Ubuntu*|*Kali*|*Parrot*)
            PKG_MGR="apt"
            ;;
        *Arch*|*Manjaro*)
            PKG_MGR="pacman"
            ;;
        *Fedora*|*CentOS*|*RHEL*)
            PKG_MGR="yum"
            ;;
        *)
            echo -e "${YELLOW}[!] Unknown distribution. Trying apt...${NC}"
            PKG_MGR="apt"
            ;;
    esac
}

install_dependencies() {
    echo -e "${CYAN}[*] Installing dependencies...${NC}"
    
    case $PKG_MGR in
        "apt")
            apt update
            apt install -y python3 python3-pip aircrack-ng wireless-tools \
                          net-tools iw ethtool rfkill hashcat hcxdumptool \
                          hcxtools macchanger hostapd dnsmasq lighttpd \
                          php-cgi php-xml python3-colorama
            ;;
        "pacman")
            pacman -Syu --noconfirm
            pacman -S --noconfirm python python-pip aircrack-ng wireless_tools \
                    net-tools iw ethtool rfkill hashcat hcxdumptool \
                    hcxtools macchanger hostapd dnsmasq lighttpd \
                    php php-xml python-colorama
            ;;
        "yum")
            yum update -y
            yum install -y python3 python3-pip aircrack-ng wireless-tools \
                          net-tools iw ethtool rfkill hashcat hcxdumptool \
                          hcxtools macchanger hostapd dnsmasq lighttpd \
                          php php-xml python3-colorama
            ;;
    esac
    
    # Install Python packages
    echo -e "${CYAN}[*] Installing Python packages...${NC}"
    pip3 install colorama
    
    # Check for wordlists
    echo -e "${CYAN}[*] Checking for wordlists...${NC}"
    if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
        echo -e "${YELLOW}[!] rockyou.txt not found. Downloading...${NC}"
        if [ -f "/usr/share/wordlists/rockyou.txt.gz" ]; then
            gunzip /usr/share/wordlists/rockyou.txt.gz
        else
            wget -O /usr/share/wordlists/rockyou.txt.gz https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt.gz
            gunzip /usr/share/wordlists/rockyou.txt.gz
        fi
    fi
}

install_wifi_demon() {
    echo -e "${CYAN}[*] Installing WiFi-Demon...${NC}"
    
    # Create installation directory
    INSTALL_DIR="/opt/wifi-demon"
    mkdir -p $INSTALL_DIR
    
    # Copy main script
    cp wifi_demon.py $INSTALL_DIR/
    chmod +x $INSTALL_DIR/wifi_demon.py
    
    # Create symlink
    ln -sf $INSTALL_DIR/wifi_demon.py /usr/local/bin/wifi-demon
    
    # Create configuration directory
    mkdir -p /etc/wifi-demon
    
    # Create wordlists directory
    mkdir -p /usr/share/wifi-demon/wordlists
    
    # Download additional wordlists if needed
    echo -e "${CYAN}[*] Downloading additional wordlists...${NC}"
    if [ ! -f "/usr/share/wifi-demon/wordlists/wpa.txt" ]; then
        wget -O /usr/share/wifi-demon/wordlists/wpa.txt https://raw.githubusercontent.com/berzerk0/Probable-Wordlists/master/Real-Passwords/Top304Thousand-probable-v2.txt
    fi
    
    # Create systemd service
    echo -e "${CYAN}[*] Creating systemd service...${NC}"
    cat > /etc/systemd/system/wifi-demon.service << EOF
[Unit]
Description=WiFi-Demon Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/wifi-demon/wifi_demon.py
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
}

create_desktop_entry() {
    echo -e "${CYAN}[*] Creating desktop entry...${NC}"
    
    if [ -d "/usr/share/applications" ]; then
        cat > /usr/share/applications/wifi-demon.desktop << EOF
[Desktop Entry]
Name=WiFi-Demon
Comment=WiFi Penetration Testing Tool
Exec=sudo wifi-demon
Icon=/opt/wifi-demon/icon.png
Terminal=true
Type=Application
Categories=Network;Security;
Keywords=wifi;hacking;security;pentest;
EOF
    fi
    
    # Download icon
    wget -O /opt/wifi-demon/icon.png https://raw.githubusercontent.com/n0merc/wifi-demon/main/icon.png 2>/dev/null || true
}

setup_aliases() {
    echo -e "${CYAN}[*] Setting up shell aliases...${NC}"
    
    # Add to bashrc
    if [ -f "$HOME/.bashrc" ]; then
        if ! grep -q "wifi-demon" "$HOME/.bashrc"; then
            echo "" >> "$HOME/.bashrc"
            echo "# WiFi-Demon aliases" >> "$HOME/.bashrc"
            echo "alias wifidemon='sudo wifi-demon'" >> "$HOME/.bashrc"
            echo "alias wifiscan='sudo iwlist wlan0 scan'" >> "$HOME/.bashrc"
            echo "alias monmode='sudo airmon-ng start wlan0'" >> "$HOME/.bashrc"
        fi
    fi
    
    # Add to zshrc
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q "wifi-demon" "$HOME/.zshrc"; then
            echo "" >> "$HOME/.zshrc"
            echo "# WiFi-Demon aliases" >> "$HOME/.zshrc"
            echo "alias wifidemon='sudo wifi-demon'" >> "$HOME/.zshrc"
            echo "alias wifiscan='sudo iwlist wlan0 scan'" >> "$HOME/.zshrc"
            echo "alias monmode='sudo airmon-ng start wlan0'" >> "$HOME/.zshrc"
        fi
    fi
}

install_optional_tools() {
    echo -e "${CYAN}[*] Installing optional tools...${NC}"
    
    read -p "$(echo -e ${YELLOW}"[?] Install additional WiFi tools? (y/n): "${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $PKG_MGR in
            "apt")
                apt install -y bully reaver wifite fern-wifi-cracker \
                              kismet bettercap wifiphisher pixiewps \
                              mdk4 wifite2
                ;;
            "pacman")
                pacman -S --noconfirm bully reaver wifite fern-wifi-cracker \
                        kismet bettercap wifiphisher pixiewps \
                        mdk4 wifite2
                ;;
            "yum")
                yum install -y bully reaver wifite fern-wifi-cracker \
                            kismet bettercap wifiphisher pixiewps \
                            mdk4 wifite2
                ;;
        esac
        
        # Install wifite2 from GitHub if not available
        if ! command -v wifite2 &> /dev/null; then
            echo -e "${YELLOW}[*] Installing wifite2 from GitHub...${NC}"
            git clone https://github.com/derv82/wifite2.git /tmp/wifite2
            cd /tmp/wifite2
            python3 setup.py install
            cd -
            rm -rf /tmp/wifite2
        fi
    fi
}

fix_permissions() {
    echo -e "${CYAN}[*] Fixing permissions...${NC}"
    
    # Set proper permissions
    chmod 755 /opt/wifi-demon
    chmod 755 /opt/wifi-demon/wifi_demon.py
    chmod 644 /etc/systemd/system/wifi-demon.service
    
    # Allow non-root users to run (with sudo)
    echo -e "${YELLOW}[*] Adding users to sudoers for WiFi tools...${NC}"
    
    # Check if user wants to add current user to sudoers
    CURRENT_USER=$(logname 2>/dev/null || echo $SUDO_USER)
    if [ ! -z "$CURRENT_USER" ]; then
        read -p "$(echo -e ${YELLOW}"[?] Add $CURRENT_USER to sudoers for WiFi tools? (y/n): "${NC})" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$CURRENT_USER ALL=(ALL) NOPASSWD: /usr/local/bin/wifi-demon" >> /etc/sudoers.d/wifi-demon
            echo "$CURRENT_USER ALL=(ALL) NOPASSWD: /usr/bin/airmon-ng" >> /etc/sudoers.d/wifi-demon
            echo "$CURRENT_USER ALL=(ALL) NOPASSWD: /usr/bin/airodump-ng" >> /etc/sudoers.d/wifi-demon
            echo "$CURRENT_USER ALL=(ALL) NOPASSWD: /usr/bin/aireplay-ng" >> /etc/sudoers.d/wifi-demon
            chmod 440 /etc/sudoers.d/wifi-demon
        fi
    fi
}

post_install() {
    echo -e "${GREEN}[+] Installation complete!${NC}"
    echo -e "${CYAN}[*] Usage instructions:${NC}"
    echo -e "${YELLOW}    sudo wifi-demon${NC}"
    echo -e "${YELLOW}    or${NC}"
    echo -e "${YELLOW}    wifidemon (if you added the alias)${NC}"
    echo ""
    echo -e "${CYAN}[*] Features:${NC}"
    echo -e "${YELLOW}    1. Scan WiFi networks${NC}"
    echo -e "${YELLOW}    2. Capture WPA handshakes${NC}"
    echo -e "${YELLOW}    3. Crack handshakes with wordlists${NC}"
    echo -e "${YELLOW}    4. Deauthentication attacks${NC}"
    echo -e "${YELLOW}    5. Interface monitoring${NC}"
    echo ""
    echo -e "${RED}[!] Legal Disclaimer:${NC}"
    echo -e "${YELLOW}    This tool is for educational and authorized testing only.${NC}"
    echo -e "${YELLOW}    Unauthorized access to computer networks is illegal.${NC}"
    echo ""
    echo -e "${GREEN}[+] Check the GitHub repo for updates:${NC}"
    echo -e "${CYAN}    https://github.com/n0merc/wifi-demon${NC}"
}

main() {
    print_banner
    check_root
    check_distro
    
    echo -e "${YELLOW}[!] This will install WiFi-Demon and required dependencies${NC}"
    read -p "$(echo -e ${YELLOW}"[?] Continue? (y/n): "${NC})" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}[!] Installation cancelled${NC}"
        exit 1
    fi
    
    install_dependencies
    install_wifi_demon
    create_desktop_entry
    setup_aliases
    install_optional_tools
    fix_permissions
    post_install
}

# Run main function
main
