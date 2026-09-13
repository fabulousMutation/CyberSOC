# 🛡️ CyberSOC: AI-Powered IoT Security Command Center

An enterprise-grade, full-stack Security Operations Center (SOC) dashboard designed to monitor, simulate, and analyze cybersecurity threats across a massive fleet of IoT devices.

## 🧠 Concept

Traditional IoT networks suffer from a lack of centralized visibility. **CyberSOC** solves this by providing a "single pane of glass" for security analysts. The platform fuses real-time telemetry simulation with historical deep-packet forensics to create a complete security monitoring environment.

The system uses a **hybrid data architecture**:
- **Live Simulation Engine**: Uses mathematical algorithms seeded by time to generate realistic, continuously changing network traffic, anomaly detections, and geographic threat data without needing a physical sensor array.
- **Stateful Alert Database**: A local SQLite database tracks the lifecycle of generated security alerts, allowing analysts to interact with the system (e.g., investigating or resolving threats).
- **Forensic Analytics Engine**: A Pandas-driven backend that ingests and processes raw `.csv` network logs for deep, post-incident forensic analysis.

---

## ✨ Key Features

1. **SOC Overview Hub**: Animated, real-time metrics showing active threats, network bandwidth, connected devices, and a 24-hour threat vs. normal traffic trend chart.
2. **Global Threat Intel**: A 3D isometric map featuring a rotating radar sweep that plots geographic attack origins and severity in real-time.
3. **Device Management**: A comprehensive endpoint inventory tracker with health statuses, risk score progress bars, and live filtering (Online, Offline, At Risk).
4. **Interactive Alert Center**: A triage queue where analysts can view the latest network alerts and change their status (New -> Investigating -> Resolved), saving state to a local SQL database.
5. **CSV Analytics Engine**: Upload complex network log datasets to instantly generate deep forensic reports on protocol distributions, encryption usage, and IP reputation scores.

---

## 🛠️ Technology Stack

- **Frontend**: React.js, React Router v6, Recharts (Data Visualization), CountUp (Animated Metrics), Custom Cyberpunk CSS (Glassmorphism & CSS Animations).
- **Backend**: Python, Flask (RESTful API), Pandas & NumPy (Data Processing).
- **Database**: SQLite (Local persistent storage).

---

## 🚀 Execution & Setup Guide

### Prerequisites
- Node.js & npm (for the React frontend)
- Python 3.x (for the Flask backend)

### Installation & Running
This project includes an automated startup script for Windows that handles installation and execution.

1. **Launch the Application**
   Double-click the `start_all.bat` file in the project root.
   
2. **What the script does automatically:**
   - Initializes the fake threat database (`init_db.py`), creating a fresh `cyber_soc.db` with realistic security alerts.
   - Installs necessary Node dependencies (`react-router-dom`, `react-countup`) if they are missing.
   - Starts the Python Flask backend on `http://127.0.0.1:5000`.
   - Starts the React development server on `http://localhost:3000` and opens your default web browser.

### Manual Execution (Optional)
If you prefer to start the servers manually:

**1. Initialize Database & Start Backend**
```bash
# Generate the database
python init_db.py

# Start Flask
python app.py
```

**2. Start Frontend**
```bash
cd frontend
npm install
npm start
```

---

## 🎨 UI/UX Highlights
The dashboard features a bespoke "Dark Cyber" aesthetic engineered for a premium feel:
- **Matrix Feeds**: Live attack logs scroll over translucent, glowing green grids.
- **Holographic 3D Maps**: The global map utilizes CSS 3D perspective transforms to create an isometric war-room layout.
- **Glassmorphism**: Floating panels feature blurred backdrops (`backdrop-filter`) and layered inset shadows to create depth.
- **Micro-animations**: Floating particles, pulsing severity badges, and glitch text effects on Critical alerts.
