from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import math
import random
import time
from datetime import datetime, timedelta
import sqlite3
import os
import shutil

app = Flask(__name__)
CORS(app)

# ============================================================
# HELPERS
# ============================================================

def get_db_path():
    db_path = os.environ.get("DB_PATH")
    if db_path:
        return db_path
    if os.environ.get("VERCEL"):
        tmp_db = os.path.join("/tmp", "cyber_soc.db")
        if not os.path.exists(tmp_db):
            base_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_soc.db")
            if os.path.exists(base_db):
                shutil.copyfile(base_db, tmp_db)
            else:
                try:
                    from init_db import init_db
                    init_db(tmp_db)
                except Exception as e:
                    print("Failed to init db:", e)
        return tmp_db
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_soc.db")

def get_db_connection():
    return sqlite3.connect(get_db_path())

def clean_value(v):
    """Ensure value is JSON-serializable (handle NaN, inf, etc.)."""
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return 0
    return v


def clean_dict_list(lst):
    """Clean a list of dicts for JSON serialization."""
    cleaned = []
    for d in lst:
        cleaned.append({k: clean_value(v) for k, v in d.items()})
    return cleaned


# ============================================================
# SIMULATION DATA POOLS
# ============================================================

ATTACK_TYPES = [
    "DDoS Flood", "SQL Injection", "Brute Force", "Man-in-the-Middle",
    "Ransomware", "Phishing Payload", "Zero-Day Exploit", "DNS Tunneling",
    "ARP Spoofing", "Buffer Overflow", "XSS Attack", "Port Scanning",
    "Credential Stuffing", "Firmware Exploit", "Botnet C2 Communication",
    "Privilege Escalation", "Data Exfiltration", "Cryptojacking",
    "Session Hijacking", "API Abuse"
]

DEVICE_TYPES = [
    ("Smart Camera", "📷"), ("Thermostat", "🌡️"), ("Door Lock", "🔒"),
    ("Motion Sensor", "📡"), ("Smart Light", "💡"), ("Gateway", "🌐"),
    ("Smart Plug", "🔌"), ("Smoke Detector", "🔥"), ("Water Sensor", "💧"),
    ("Hub Controller", "🖥️"), ("IP Phone", "📞"), ("Smart Speaker", "🔊"),
    ("Air Quality Monitor", "🌬️"), ("Energy Meter", "⚡"), ("Security Panel", "🛡️"),
]

DEVICE_NAMES = [
    "Lobby-Cam-01", "Lobby-Cam-02", "Server-Room-Therm", "Main-Entry-Lock",
    "Warehouse-Motion-01", "Office-Light-A1", "Edge-Gateway-01", "Edge-Gateway-02",
    "Kitchen-Plug-01", "Floor3-Smoke-01", "Basement-Water-01", "Hub-Central",
    "Reception-Phone", "Conf-Speaker-01", "AQ-Monitor-Lab", "Energy-Meter-Main",
    "Parking-Cam-01", "Roof-Sensor-01", "Lab-Lock-02", "HVAC-Therm-02",
    "Dock-Cam-03", "Hallway-Motion-02", "Patio-Light-B1", "Gateway-DMZ",
    "Plug-ServerRack-01", "Floor1-Smoke-02", "Sprinkler-Ctrl", "Hub-Backup",
    "Exec-Phone-01", "Boardroom-Speaker", "AQ-Floor2", "Solar-Meter-01",
    "Garage-Cam-04", "Stairwell-Sensor", "Storage-Lock-03", "Outdoor-Light-C1",
    "Gateway-Branch-03", "Break-Room-Plug", "Attic-Smoke-03", "Pool-Water-02",
    "Sub-Hub-01", "Help-Desk-Phone", "Lounge-Speaker-02", "Lab-AQ-03",
    "UPS-Meter-01", "Panel-Zone-A", "Panel-Zone-B", "Panel-Zone-C",
    "Cam-Emergency-Exit", "IoT-Honeypot-01",
]

THREAT_COUNTRIES = [
    ("Russia", 55.75, 37.62), ("China", 39.91, 116.40), ("North Korea", 39.03, 125.75),
    ("Iran", 35.69, 51.39), ("Brazil", -15.79, -47.88), ("India", 28.61, 77.21),
    ("Nigeria", 9.08, 7.49), ("Vietnam", 21.03, 105.85), ("Romania", 44.43, 26.10),
    ("Turkey", 39.93, 32.86), ("Indonesia", -6.21, 106.85), ("Pakistan", 33.69, 73.04),
    ("Ukraine", 50.45, 30.52), ("Argentina", -34.60, -58.38), ("Philippines", 14.60, 120.98),
]

SEVERITIES = ["critical", "high", "medium", "low"]
SEVERITY_WEIGHTS = [0.1, 0.25, 0.35, 0.3]

MITRE_CATEGORIES = [
    "Initial Access", "Execution", "Persistence", "Privilege Escalation",
    "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
    "Collection", "Command and Control", "Exfiltration", "Impact"
]


def _random_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def _random_mac():
    return ":".join(f"{random.randint(0,255):02x}" for _ in range(6))


def _time_ago(minutes):
    return (datetime.utcnow() - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


# ============================================================
# EXISTING ENDPOINT — CSV UPLOAD & ANALYSIS
# ============================================================

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files['file']
        df = pd.read_csv(file)

        # Fill NaN values
        df['encryption_used'] = df['encryption_used'].fillna('None')

        # ---- Basic Info ----
        total_rows = len(df)
        columns = list(df.columns)

        # ---- Attack Stats ----
        attack_count = int(df['attack_detected'].sum())
        normal_count = total_rows - attack_count
        attack_rate = round(attack_count / total_rows * 100, 1)

        # ---- Unusual Time Access ----
        unusual_time_count = int(df['unusual_time_access'].sum())

        # ---- Protocol Distribution ----
        protocol_dist = df['protocol_type'].value_counts().to_dict()
        protocol_chart = [{"name": str(k), "value": int(v)} for k, v in protocol_dist.items()]

        # ---- Browser Distribution ----
        browser_dist = df['browser_type'].value_counts().to_dict()
        browser_chart = [{"name": str(k), "value": int(v)} for k, v in browser_dist.items()]

        # ---- Encryption Distribution ----
        encryption_dist = df['encryption_used'].value_counts().to_dict()
        encryption_chart = [{"name": str(k), "value": int(v)} for k, v in encryption_dist.items()]

        # ---- Attack by Protocol ----
        attack_by_protocol = df.groupby('protocol_type')['attack_detected'].mean().round(3).to_dict()
        attack_by_protocol_chart = [
            {"name": str(k), "rate": round(float(v) * 100, 1)} for k, v in attack_by_protocol.items()
        ]

        # ---- Attack by Browser ----
        attack_by_browser = df.groupby('browser_type')['attack_detected'].mean().round(3).to_dict()
        attack_by_browser_chart = [
            {"name": str(k), "rate": round(float(v) * 100, 1)} for k, v in attack_by_browser.items()
        ]

        # ---- Failed Logins Distribution ----
        failed_login_dist = df['failed_logins'].value_counts().sort_index().to_dict()
        failed_login_chart = [{"logins": str(int(k)), "count": int(v)} for k, v in failed_login_dist.items()]

        # ---- Packet Size Histogram (binned) ----
        bins = [0, 200, 400, 600, 800, 1000, 1500]
        labels = ['0-200', '201-400', '401-600', '601-800', '801-1000', '1001+']
        df['packet_bin'] = pd.cut(df['network_packet_size'], bins=bins, labels=labels, right=True)
        packet_hist = df['packet_bin'].value_counts().sort_index().to_dict()
        packet_chart = [{"range": str(k), "count": int(v)} for k, v in packet_hist.items()]

        # ---- IP Reputation Score Stats ----
        ip_stats = {
            "mean": round(float(df['ip_reputation_score'].mean()), 2),
            "min": round(float(df['ip_reputation_score'].min()), 2),
            "max": round(float(df['ip_reputation_score'].max()), 2),
            "std": round(float(df['ip_reputation_score'].std()), 2),
        }

        # ---- Session Duration Stats ----
        session_stats = {
            "mean": round(float(df['session_duration'].mean()), 1),
            "min": round(float(df['session_duration'].min()), 1),
            "max": round(float(df['session_duration'].max()), 1),
        }

        # ---- Risk Score Breakdown ----
        def risk_level(row):
            score = 0
            if row['attack_detected'] == 1:
                score += 3
            if row['failed_logins'] >= 3:
                score += 2
            if row['unusual_time_access'] == 1:
                score += 1
            if row['ip_reputation_score'] < 30:
                score += 1
            if score >= 5:
                return 'Critical'
            elif score >= 3:
                return 'High'
            elif score >= 1:
                return 'Medium'
            else:
                return 'Low'

        df['risk_level'] = df.apply(risk_level, axis=1)
        risk_dist = df['risk_level'].value_counts().to_dict()
        risk_chart = [{"name": str(k), "value": int(v)} for k, v in risk_dist.items()]

        # ---- Batch trend (simulated sequential batches) ----
        batch_size = max(1, total_rows // 20)
        trend_data = []
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i + batch_size]
            trend_data.append({
                "batch": "B{}".format(len(trend_data) + 1),
                "attacks": int(batch['attack_detected'].sum()),
                "normal": int((batch['attack_detected'] == 0).sum()),
                "avgPacketSize": round(float(batch['network_packet_size'].mean()), 0),
            })

        # ---- Top risky sessions ----
        risky = df[df['attack_detected'] == 1].nlargest(10, 'failed_logins')
        top_risky = []
        for _, row in risky.iterrows():
            top_risky.append({
                "session_id": str(row['session_id']),
                "protocol_type": str(row['protocol_type']),
                "failed_logins": int(row['failed_logins']),
                "login_attempts": int(row['login_attempts']),
                "ip_reputation_score": round(float(row['ip_reputation_score']), 2),
                "browser_type": str(row['browser_type']),
                "unusual_time_access": int(row['unusual_time_access']),
            })

        result = {
            "rows": total_rows,
            "columns": columns,
            "attackCount": attack_count,
            "normalCount": normal_count,
            "attackRate": attack_rate,
            "unusualTimeCount": unusual_time_count,
            "protocolChart": protocol_chart,
            "browserChart": browser_chart,
            "encryptionChart": encryption_chart,
            "attackByProtocol": attack_by_protocol_chart,
            "attackByBrowser": attack_by_browser_chart,
            "failedLoginChart": failed_login_chart,
            "packetChart": packet_chart,
            "ipStats": ip_stats,
            "sessionStats": session_stats,
            "riskChart": risk_chart,
            "trendData": trend_data,
            "topRisky": top_risky,
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# NEW ENDPOINT — LIVE DASHBOARD METRICS
# ============================================================

@app.route("/api/dashboard/live", methods=["GET"])
def dashboard_live():
    seed = int(time.time() // 10)
    rng = random.Random(seed)

    active_threats = rng.randint(3, 28)
    devices_online = rng.randint(38, 50)
    anomalies = rng.randint(1, 15)
    bandwidth = round(rng.uniform(120, 890), 1)
    cpu_usage = round(rng.uniform(18, 72), 1)
    blocked_ips = rng.randint(45, 320)
    uptime = round(rng.uniform(99.2, 99.99), 2)
    threat_level = "critical" if active_threats > 20 else "high" if active_threats > 12 else "medium" if active_threats > 5 else "low"

    # 24-hour trend (24 data points)
    trend = []
    base_threats = 8
    for h in range(24):
        r = random.Random(seed + h)
        t = max(0, base_threats + r.randint(-5, 12))
        n = max(0, r.randint(200, 500))
        trend.append({
            "hour": f"{h:02d}:00",
            "threats": t,
            "normal": n,
            "blocked": max(0, t - r.randint(0, 3)),
        })

    # Top attacking IPs
    top_ips = []
    for i in range(8):
        r2 = random.Random(seed + i + 100)
        top_ips.append({
            "ip": f"{r2.randint(1,223)}.{r2.randint(0,255)}.{r2.randint(0,255)}.{r2.randint(1,254)}",
            "attacks": r2.randint(5, 85),
            "country": rng.choice(THREAT_COUNTRIES)[0],
            "severity": rng.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0],
        })
    top_ips.sort(key=lambda x: x["attacks"], reverse=True)

    return jsonify({
        "activeThreats": active_threats,
        "devicesOnline": devices_online,
        "totalDevices": 50,
        "anomalies": anomalies,
        "bandwidth": bandwidth,
        "cpuUsage": cpu_usage,
        "blockedIPs": blocked_ips,
        "uptime": uptime,
        "threatLevel": threat_level,
        "trend": trend,
        "topIPs": top_ips,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    })


# ============================================================
# NEW ENDPOINT — THREAT FEED
# ============================================================

@app.route("/api/threats/feed", methods=["GET"])
def threats_feed():
    seed = int(time.time() // 15)
    rng = random.Random(seed)
    count = rng.randint(10, 20)

    events = []
    for i in range(count):
        r = random.Random(seed + i)
        mins_ago = r.randint(0, 120)
        severity = r.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        events.append({
            "id": f"THR-{seed % 10000:04d}-{i:03d}",
            "timestamp": _time_ago(mins_ago),
            "attackType": r.choice(ATTACK_TYPES),
            "sourceIP": _random_ip(),
            "targetDevice": r.choice(DEVICE_NAMES),
            "severity": severity,
            "mitre": r.choice(MITRE_CATEGORIES),
            "status": r.choice(["blocked", "detected", "investigating", "mitigated"]),
            "confidence": round(r.uniform(0.6, 0.99), 2),
        })
    events.sort(key=lambda x: x["timestamp"], reverse=True)

    return jsonify({"events": events, "total": count})


# ============================================================
# NEW ENDPOINT — DEVICE INVENTORY
# ============================================================

@app.route("/api/devices", methods=["GET"])
def devices():
    seed = int(time.time() // 30)
    devices_list = []
    for i, name in enumerate(DEVICE_NAMES):
        r = random.Random(seed + i)
        dev_type, icon = DEVICE_TYPES[i % len(DEVICE_TYPES)]
        status = r.choices(["online", "offline", "warning"], weights=[0.7, 0.1, 0.2])[0]
        risk = round(r.uniform(5, 95), 1)
        devices_list.append({
            "id": f"DEV-{i+1:03d}",
            "name": name,
            "type": dev_type,
            "icon": icon,
            "ip": f"192.168.{r.randint(1,10)}.{r.randint(1,254)}",
            "mac": _random_mac(),
            "status": status,
            "riskScore": risk,
            "riskLevel": "critical" if risk > 80 else "high" if risk > 60 else "medium" if risk > 30 else "low",
            "lastSeen": _time_ago(r.randint(0, 60) if status == "online" else r.randint(60, 1440)),
            "firmware": f"v{r.randint(1,4)}.{r.randint(0,9)}.{r.randint(0,20)}",
            "traffic": round(r.uniform(0.1, 50), 1),
        })

    online = sum(1 for d in devices_list if d["status"] == "online")
    offline = sum(1 for d in devices_list if d["status"] == "offline")
    warning = sum(1 for d in devices_list if d["status"] == "warning")
    at_risk = sum(1 for d in devices_list if d["riskScore"] > 60)

    # Type distribution
    type_counts = {}
    for d in devices_list:
        type_counts[d["type"]] = type_counts.get(d["type"], 0) + 1
    type_chart = [{"name": k, "value": v} for k, v in type_counts.items()]

    return jsonify({
        "devices": devices_list,
        "summary": {"online": online, "offline": offline, "warning": warning, "atRisk": at_risk, "total": len(devices_list)},
        "typeChart": type_chart,
    })


# ============================================================
# NEW ENDPOINT — NETWORK TOPOLOGY
# ============================================================

@app.route("/api/network/topology", methods=["GET"])
def network_topology():
    seed = int(time.time() // 60)
    rng = random.Random(seed)
    nodes = [{"id": "hub", "name": "Central Hub", "type": "hub", "group": 0}]
    gateways = ["Edge-Gateway-01", "Edge-Gateway-02", "Gateway-DMZ", "Gateway-Branch-03"]
    for i, gw in enumerate(gateways):
        nodes.append({"id": f"gw{i}", "name": gw, "type": "gateway", "group": 1})
    for i in range(20):
        r = random.Random(seed + i)
        dt, icon = DEVICE_TYPES[i % len(DEVICE_TYPES)]
        nodes.append({"id": f"dev{i}", "name": DEVICE_NAMES[i], "type": dt, "icon": icon, "group": 2})

    edges = []
    for i in range(len(gateways)):
        edges.append({"source": "hub", "target": f"gw{i}"})
    for i in range(20):
        gw_idx = i % len(gateways)
        edges.append({"source": f"gw{gw_idx}", "target": f"dev{i}"})

    return jsonify({"nodes": nodes, "edges": edges})


# ============================================================
# NEW ENDPOINT — AI ANOMALY DETECTION
# ============================================================

@app.route("/api/ai/anomalies", methods=["GET"])
def ai_anomalies():
    seed = int(time.time() // 20)
    rng = random.Random(seed)
    anomalies = []
    count = rng.randint(5, 12)
    for i in range(count):
        r = random.Random(seed + i)
        score = round(r.uniform(0.55, 0.99), 3)
        anomalies.append({
            "id": f"ANM-{seed % 10000:04d}-{i:02d}",
            "device": r.choice(DEVICE_NAMES),
            "metric": r.choice(["packet_rate", "cpu_spike", "bandwidth_surge", "auth_failure_burst", "port_scan_detected", "unusual_protocol", "data_exfil_pattern"]),
            "score": score,
            "severity": "critical" if score > 0.9 else "high" if score > 0.8 else "medium" if score > 0.65 else "low",
            "description": r.choice([
                "Unusual outbound traffic volume detected",
                "Authentication failure rate exceeds baseline by 340%",
                "Port scanning activity from internal device",
                "Anomalous protocol usage detected on IoT segment",
                "Data transfer pattern matches exfiltration signature",
                "CPU utilization spike correlated with C2 beacon timing",
                "Firmware update request from unauthorized source",
                "DNS query pattern matches known DGA algorithm",
            ]),
            "timestamp": _time_ago(r.randint(0, 90)),
            "baseline": round(r.uniform(10, 50), 1),
            "observed": round(r.uniform(80, 500), 1),
        })
    anomalies.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"anomalies": anomalies, "modelVersion": "v2.4.1", "lastTrained": "2026-05-05T08:00:00Z"})


# ============================================================
# NEW ENDPOINT — GEO THREATS
# ============================================================

@app.route("/api/geo/threats", methods=["GET"])
def geo_threats():
    seed = int(time.time() // 20)
    rng = random.Random(seed)
    results = []
    for country, lat, lng in THREAT_COUNTRIES:
        r = random.Random(seed + hash(country))
        count = r.randint(2, 60)
        results.append({
            "country": country,
            "lat": lat + r.uniform(-1, 1),
            "lng": lng + r.uniform(-1, 1),
            "attacks": count,
            "severity": "critical" if count > 40 else "high" if count > 25 else "medium" if count > 10 else "low",
            "topAttack": r.choice(ATTACK_TYPES),
        })
    results.sort(key=lambda x: x["attacks"], reverse=True)
    return jsonify({"sources": results})


# ============================================================
# NEW ENDPOINT — ALERTS
# ============================================================

@app.route("/api/alerts", methods=["GET"])
def alerts():
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        alert_list = []
        for row in rows:
            alert_list.append(dict(row))
            
        summary = {s: sum(1 for a in alert_list if a["severity"] == s) for s in SEVERITIES}
        
        conn.close()
        return jsonify({"alerts": alert_list, "summary": summary, "total": len(alert_list)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alerts/<alert_id>/status", methods=["PUT"])
def update_alert_status(alert_id):
    try:
        data = request.json
        new_status = data.get("status")
        
        if new_status not in ["new", "investigating", "resolved", "dismissed"]:
            return jsonify({"error": "Invalid status"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET status = ? WHERE id = ?", (new_status, alert_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Alert not found"}), 404
            
        conn.close()
        return jsonify({"success": True, "message": f"Alert {alert_id} updated to {new_status}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)