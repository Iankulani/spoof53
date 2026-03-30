#!/bin/bash
# SPOOF53 Installation Script for Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                               ║${NC}"
echo -e "${BLUE}║${GREEN}               SPOOF53 - Installation Script               ${BLUE}║${NC}"
echo -e "${BLUE}║${GREEN}            Complete Penetration Testing Platform          ${BLUE}║${NC}"
echo -e "${BLUE}║                                                               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Warning: Running as root. This is required for advanced features.${NC}"
else
    echo -e "${RED}❌ This script must be run as root for full functionality${NC}"
    echo -e "${YELLOW}Please run: sudo ./install.sh${NC}"
    exit 1
fi

# Detect OS
echo -e "${BLUE}🔍 Detecting operating system...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}❌ Cannot detect OS${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Detected: $OS $VER${NC}"

# Install system dependencies based on OS
echo -e "${BLUE}📦 Installing system dependencies...${NC}"

case $OS in
    ubuntu|debian)
        apt-get update
        apt-get install -y \
            python3 python3-pip python3-dev python3-venv \
            git curl wget \
            nmap netcat-openbsd \
            hping3 dsniff macchanger \
            traceroute dnsutils whois \
            tcpdump wireshark \
            arp-scan nbtscan \
            sqlite3 \
            build-essential libpcap-dev \
            libssl-dev libffi-dev \
            chromium chromium-driver \
            xvfb \
            net-tools iproute2 \
            iptables \
            openssh-client \
            && rm -rf /var/lib/apt/lists/*
        ;;
    
    rhel|centos|fedora)
        if [ "$OS" = "fedora" ]; then
            dnf install -y \
                python3 python3-pip python3-devel \
                git curl wget \
                nmap nc hping3 dsniff macchanger \
                traceroute bind-utils whois \
                tcpdump wireshark \
                arp-scan nbtscan \
                sqlite \
                gcc make libpcap-devel \
                openssl-devel libffi-devel \
                chromium chromium-headless \
                xorg-x11-server-Xvfb \
                net-tools iproute \
                iptables \
                openssh-clients \
                && dnf clean all
        else
            yum install -y epel-release
            yum install -y \
                python3 python3-pip python3-devel \
                git curl wget \
                nmap nc hping3 dsniff macchanger \
                traceroute bind-utils whois \
                tcpdump wireshark \
                arp-scan nbtscan \
                sqlite \
                gcc make libpcap-devel \
                openssl-devel libffi-devel \
                chromium chromium-headless \
                xorg-x11-server-Xvfb \
                net-tools iproute \
                iptables \
                openssh-clients \
                && yum clean all
        fi
        ;;
    
    arch)
        pacman -Syu --noconfirm
        pacman -S --noconfirm \
            python python-pip \
            git curl wget \
            nmap netcat hping3 dsniff macchanger \
            traceroute bind-tools whois \
            tcpdump wireshark-cli \
            arp-scan nbtscan \
            sqlite \
            base-devel libpcap \
            openssl \
            chromium \
            xorg-server-xvfb \
            net-tools iproute2 \
            iptables \
            openssh
        ;;
    
    *)
        echo -e "${RED}❌ Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

# Install signal-cli
echo -e "${BLUE}📡 Installing signal-cli...${NC}"
SIGNAL_CLI_VERSION="0.12.3"
wget -q https://github.com/AsamK/signal-cli/releases/download/v${SIGNAL_CLI_VERSION}/signal-cli-${SIGNAL_CLI_VERSION}.tar.gz
tar -xzf signal-cli-${SIGNAL_CLI_VERSION}.tar.gz -C /opt/
ln -sf /opt/signal-cli-${SIGNAL_CLI_VERSION}/bin/signal-cli /usr/local/bin/signal-cli
rm signal-cli-${SIGNAL_CLI_VERSION}.tar.gz
echo -e "${GREEN}✅ signal-cli installed${NC}"

# Create virtual environment
echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
python3 -m venv /opt/spoof53-venv
source /opt/spoof53-venv/bin/activate

# Install Python requirements
echo -e "${BLUE}📚 Installing Python packages...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install additional packages
pip install \
    selenium \
    webdriver-manager \
    slack-sdk \
    slack-socket-mode \
    telethon \
    discord.py \
    paramiko \
    scapy \
    pyshorteners \
    qrcode \
    python-whois \
    netifaces \
    dnspython \
    beautifulsoup4 \
    colorama \
    tqdm \
    prettytable \
    python-nmap

# Create application directory
echo -e "${BLUE}📁 Creating application directories...${NC}"
mkdir -p /opt/spoof53
cp spoof53.py /opt/spoof53/
cp -r templates /opt/spoof53/ 2>/dev/null || true

# Create configuration directory
mkdir -p /opt/spoof53/.spoof53
mkdir -p /opt/spoof53/reports
mkdir -p /opt/spoof53/logs

# Set permissions
chmod +x /opt/spoof53/spoof53.py
chown -R root:root /opt/spoof53

# Create systemd service
echo -e "${BLUE}🔧 Creating systemd service...${NC}"
cat > /etc/systemd/system/spoof53.service <<EOF
[Unit]
Description=SPOOF53 Penetration Testing Platform
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/spoof53
Environment="PATH=/opt/spoof53-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/spoof53-venv/bin/python3 /opt/spoof53/spoof53.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create uninstall script
echo -e "${BLUE}🗑️  Creating uninstall script...${NC}"
cat > /opt/spoof53/uninstall.sh <<'EOF'
#!/bin/bash
# SPOOF53 Uninstall Script

echo "⚠️  This will remove SPOOF53 and all its data"
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Stop and disable service
systemctl stop spoof53 2>/dev/null
systemctl disable spoof53 2>/dev/null
rm -f /etc/systemd/system/spoof53.service
systemctl daemon-reload

# Remove files
rm -rf /opt/spoof53
rm -rf /opt/spoof53-venv

echo "✅ SPOOF53 uninstalled successfully"
EOF

chmod +x /opt/spoof53/uninstall.sh

# Reload systemd
systemctl daemon-reload

# Enable and start service
echo -e "${BLUE}🚀 Starting SPOOF53 service...${NC}"
systemctl enable spoof53
systemctl start spoof53

# Check status
sleep 2
if systemctl is-active --quiet spoof53; then
    echo -e "${GREEN}✅ SPOOF53 service is running${NC}"
else
    echo -e "${YELLOW}⚠️  Service not running. Check logs with: journalctl -u spoof53${NC}"
fi

# Print completion message
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║${BLUE}              SPOOF53 Installation Complete!                 ${GREEN}║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 USAGE:${NC}"
echo -e "  ${GREEN}• Interactive Mode:${NC}    sudo /opt/spoof53-venv/bin/python3 /opt/spoof53/spoof53.py"
echo -e "  ${GREEN}• Service Status:${NC}      systemctl status spoof53"
echo -e "  ${GREEN}• View Logs:${NC}          journalctl -u spoof53 -f"
echo -e "  ${GREEN}• Uninstall:${NC}          sudo /opt/spoof53/uninstall.sh"
echo ""
echo -e "${BLUE}🌐 Bot Configuration:${NC}"
echo -e "  Edit config files in: /opt/spoof53/.spoof53/"
echo -e "  • Discord:   /opt/spoof53/.spoof53/discord.json"
echo -e "  • Telegram:  /opt/spoof53/.spoof53/telegram.json"
echo -e "  • WhatsApp:  /opt/spoof53/.spoof53/whatsapp.json"
echo -e "  • Slack:     /opt/spoof53/.spoof53/slack.json"
echo -e "  • Signal:    /opt/spoof53/.spoof53/signal.json"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "  • Run with root privileges for full functionality"
echo -e "  • For ARP/DNS spoofing, install: apt-get install dsniff (Debian/Ubuntu)"
echo -e "  • For WhatsApp bot, scan QR code when prompted"
echo -e "  • For Signal bot, register account first: signal-cli -u +1234567890 register"
echo ""
echo -e "${GREEN}Happy testing! 🕶️${NC}"