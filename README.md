# Self-Adaptive Cyber Deception System

## Overview
This project implements a defensive cyber deception system designed to detect attacker activity and respond with adaptive deception techniques in real time.

The system integrates a honeypot-based detection layer with an AI-driven decision module that selects appropriate deception actions based on observed attacker behavior. The objective is to enhance early threat detection, increase attacker engagement time, and reduce the effectiveness of malicious reconnaissance.

This project demonstrates practical concepts used in modern defensive security operations, including deception technology, automated response, and security monitoring.

---

## System Architecture
The system follows a modular pipeline:

Cowrie Honeypot → Event Webhook → Decision Engine → Deception Executor → Monitoring Dashboard

Each component operates independently and communicates through structured event data to ensure scalability and flexibility.

---

## Key Components

- **Honeypot (Cowrie)**  
  Captures attacker interaction data such as login attempts and command execution.

- **Event Webhook**  
  Receives and normalizes honeypot events for processing.

- **Decision Engine**  
  Analyzes incoming events and selects appropriate deception responses based on predefined logic and contextual analysis.

- **Deception Executor**  
  Deploys realistic decoy artifacts and system responses based on the selected deception strategy.

- **Monitoring Dashboard**  
  Provides real-time visibility into attacker events, system decisions, and deployed deception actions.

---

## Security Operations Relevance
This system aligns with real-world SOC and blue-team workflows by:

- Monitoring suspicious activity
- Enriching alerts with deception-based intelligence
- Automating defensive responses
- Providing visibility through dashboards and logs

While implemented as a research and learning project, the architecture mirrors how commercial deception and monitoring solutions are integrated into enterprise environments.

---
## Use Cases
- SOC alert triage and enrichment
- Attacker behavior analysis
- Deception-based threat intelligence
- Security monitoring demonstrations

---

## Technologies Used
- Python
- Docker & Docker Compose
- Cowrie Honeypot
- Flask
- Linux

---

## How to Run
See `RUN.md` for step-by-step instructions to deploy and test the system using Docker.

---

## Disclaimer
This project is intended for defensive security research and educational purposes only.
