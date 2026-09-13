import sqlite3
import random
import time
from datetime import datetime, timedelta
import os

DB_FILE = 'cyber_soc.db'

ATTACK_TYPES = [
    "DDoS Flood", "SQL Injection", "Brute Force", "Man-in-the-Middle",
    "Ransomware", "Phishing Payload", "Zero-Day Exploit", "DNS Tunneling",
    "ARP Spoofing", "Buffer Overflow", "XSS Attack", "Port Scanning",
    "Credential Stuffing", "Firmware Exploit", "Botnet C2 Communication",
    "Privilege Escalation", "Data Exfiltration", "Cryptojacking",
    "Session Hijacking", "API Abuse"
]

DEVICE_NAMES = [
    "Lobby-Cam-01", "Lobby-Cam-02", "Server-Room-Therm", "Main-Entry-Lock",
    "Warehouse-Motion-01", "Office-Light-A1", "Edge-Gateway-01", "Edge-Gateway-02",
    "Kitchen-Plug-01", "Floor3-Smoke-01", "Basement-Water-01", "Hub-Central",
    "Reception-Phone", "Conf-Speaker-01", "AQ-Monitor-Lab", "Energy-Meter-Main",
]

SEVERITIES = ["critical", "high", "medium", "low"]
SEVERITY_WEIGHTS = [0.1, 0.25, 0.35, 0.3]

def _random_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def _time_ago(minutes):
    return (datetime.utcnow() - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")

def init_db(db_file=DB_FILE):
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing {db_file} to start fresh.")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE alerts (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            severity TEXT,
            source_ip TEXT,
            device TEXT,
            attack_type TEXT,
            description TEXT,
            status TEXT
        )
    ''')

    seed = int(time.time() // 15)
    rng = random.Random(seed)
    count = rng.randint(45, 80)

    alerts_data = []
    for i in range(count):
        r = random.Random(seed + i)
        severity = r.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        
        alert_id = f"ALR-{seed % 10000:04d}-{i:03d}"
        timestamp = _time_ago(r.randint(0, 1440)) # Up to 24 hours ago
        source_ip = _random_ip()
        device = r.choice(DEVICE_NAMES)
        attack_type = r.choice(ATTACK_TYPES)
        description = r.choice([
            "Multiple failed authentication attempts detected",
            "Suspicious outbound connection to known C2 server",
            "Firmware integrity check failed",
            "Unusual data transfer volume detected",
            "Port scan detected from internal network",
            "Privilege escalation attempt blocked",
            "Malware signature match in network traffic",
            "Unauthorized API access attempt",
            "Certificate validation failure",
            "Anomalous DNS resolution pattern",
        ])
        status = r.choices(["new", "investigating", "resolved", "dismissed"], weights=[0.6, 0.2, 0.1, 0.1])[0]

        alerts_data.append((alert_id, timestamp, severity, source_ip, device, attack_type, description, status))

    cursor.executemany('''
        INSERT INTO alerts (id, timestamp, severity, source_ip, device, attack_type, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', alerts_data)

    conn.commit()
    conn.close()
    
    print(f"Successfully initialized {db_file} with {count} fake alerts.")

if __name__ == '__main__':
    init_db()
