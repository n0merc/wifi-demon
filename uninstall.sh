#!/bin/bash
# WiFi-Demon Uninstaller

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}[!] Uninstalling WiFi-Demon...${NC}"

# Remove symlink
rm -f /usr/local/bin/wifi-demon
rm -f /usr/local/bin/wifidemon

# Remove installation directory
rm -rf /opt/wifi-demon

# Remove systemd service
systemctl stop wifi-demon.service 2>/dev/null
systemctl disable wifi-demon.service 2>/dev/null
rm -f /etc/systemd/system/wifi-demon.service
systemctl daemon-reload

# Remove desktop entry
rm -f /usr/share/applications/wifi-demon.desktop

# Remove configuration
rm -rf /etc/wifi-demon

# Remove sudoers entry
rm -f /etc/sudoers.d/wifi-demon

# Remove from shell configs
sed -i '/# WiFi-Demon aliases/,+3d' ~/.bashrc 2>/dev/null
sed -i '/# WiFi-Demon aliases/,+3d' ~/.zshrc 2>/dev/null

echo -e "${GREEN}[+] WiFi-Demon successfully uninstalled!${NC}"
