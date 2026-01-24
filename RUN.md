## Self-Adaptive Cyber Deception System

This document explains how to run, test, and observe the complete deception system end-to-end.  
The setup is designed for demonstration, evaluation, and reproducibility.

---

## 1. Environment Requirements

- OS: Kali Linux (tested) or any Linux host
- Docker & Docker Compose installed
- Python 3.9+
- Internet connection (for package installation only)

---

## 2. Start the System

### Step 1: Clone the Repository

git clone https://github.com/Eng-Shaheen/Self-Adaptive-Cyber-Deception-System.git

cd Self-Adaptive-Cyber-Deception-System

### Step 2: Build and Start Containers

docker-compose up --build

This starts:
- Cowrie honeypot
- Webhook service
- AI decision engine
- Executor
- Dashboard

Leave this terminal running.

---

## 3. Verify Services

Open a browser and visit:

http://localhost:5000/dashboard

You should see:
- Incoming honeypot events
- AI decisions
- Deception actions
- System metrics
  
This dashboard simulates what a SOC analyst would monitor during active attacker engagement.

---

## 4. Simulate Attacker Activity

Open a new terminal and run:

cd sim  
bash simulate_events.sh

To generate multiple events:

bash produce_many_events.sh

These scripts simulate attacker behavior normally captured by Cowrie.

---

## 5. Observe AI-Driven Deception

As events arrive:
1. Cowrie logs attacker behavior
2. Webhook receives and parses events
3. AI module generates deception decisions
4. Executor creates realistic decoy artifacts
5. Dashboard updates in real time

Generated decoys are saved in:

assets/ai_generated/

AI decision logs are stored in:

code/ai_module/logs/ai_decisions.jsonl

---

## 6. Stop the System

To stop all services:

docker-compose down

---

## 7. Safety Note

This project is defensive-only and intended for:
- Research
- Education
- Security testing in controlled environments

No offensive or malicious automation is implemented.

---
