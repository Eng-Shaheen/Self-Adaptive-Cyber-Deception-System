# Self-Adaptive Cyber Deception System

## Project Objective
This project demonstrates a **defensive cyber deception system** designed to detect attacker activity and respond with adaptive deception techniques in real time.  

The system integrates a **honeypot-based detection layer** with an **AI-driven decision engine** to select appropriate deception actions based on observed attacker behavior.  
This architecture mirrors **real-world SOC workflows**, providing early threat detection, attacker engagement, and automated defensive responses.

---

## System Architecture
**Pipeline:**  
Cowrie Honeypot → Event Webhook → Decision Engine → Deception Executor → Monitoring Dashboard

- **Honeypot (Cowrie):** Captures attacker interaction data (login attempts, commands).  
- **Event Webhook:** Normalizes and forwards events to the AI engine.  
- **Decision Engine:** Analyzes events and selects deception strategies.  
- **Deception Executor:** Deploys decoys and artifacts for attacker engagement.  
- **Monitoring Dashboard:** Provides real-time visibility of events, decisions, and actions.

---

## SOC / Security Operations Relevance
- Monitors suspicious activity continuously  
- Enriches alerts with deception-based intelligence  
- Automates defensive responses  
- Provides actionable visibility via dashboards and logs  

> Demonstrates real SOC/blue-team workflow concepts using AI and deception technologies.

---

## Screenshots & Observations

### 1. Monitoring Dashboard
![Dashboard](screenshots/Dashboard.png)  
**Observation:** Real-time events from the honeypot are visible. The dashboard shows incoming attacks, AI decisions, and deployed decoys. This simulates a SOC analyst monitoring live attacker activity.

### 2. Detailed AI Decision #1
![Detailed Decision](screenshots/Detailed_Decision.png)  
**Observation:** AI engine generates deception strategies based on attacker behavior. Each decision corresponds to a specific decoy deployment or response action.

### 3. Detailed AI Decision #2
![Detailed Decision 2](screenshots/Detailed_Decision_2.png)  
**Observation:** Additional decisions for complex attacker interactions. Demonstrates adaptive response logic and dynamic threat mitigation.

---

## Use Cases
- SOC alert triage and enrichment  
- Attacker behavior analysis  
- Deception-based threat intelligence  
- Security monitoring demonstrations  

---

## Technologies Used
- Python 3.9+  
- Docker & Docker Compose  
- Cowrie Honeypot  
- Flask  
- Linux environment  

---

## How to Run
See `RUN.md` for **step-by-step instructions** to deploy and test the system.  
The setup simulates a complete SOC-style workflow for learning and demonstration purposes.

---

## Notes
- AI decision engine adapts responses in real time  
- Decoys are stored in `assets/ai_generated/`  
- AI logs stored in `code/ai_module/logs/ai_decisions.jsonl`  
- All observations are **defensive only**; no offensive actions are included  

---

## Next Steps / Future Enhancements
- Expand deception coverage to multiple hosts and services  
- Integrate with external SIEM systems for automated alert enrichment  
- Enhance AI logic for more complex attack detection and response  
