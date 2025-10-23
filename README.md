# SallyAI

**Winning Project – Medical AI Hackathon 2025, York University**  
**Authors:** Owen Ostler, Thomas Shvekher, and Alp Unsal  

---

## See It In Action  
[Watch the Live Demo](https://www.loom.com/share/2d2c0a3c8157435d90771a2a54d9b075?sid=2885d0ff-8164-49ab-8859-f83a9c6341b6)

---

## Overview  

SallyAI is an AI-driven medical assistant built in just **6 hours** during the 2025 York University Artificial Intelligence in Health Care Society Hackathon.  
It automates patient voice check-ins for thyroid-related conditions, generating structured summaries for physicians in real time.  

This project demonstrates how cutting-edge APIs and cloud infrastructure can be combined to create practical, medically assistive AI systems in limited time.

---

## Key Features  

- **Real-Time Voice Interaction** – Conducts natural, conversational patient check-ins via Twilio Media Streams.  
- **Adaptive Question Flow** – Adjusts follow-up questions based on patient responses, targeting thyroid-specific symptoms (weight, heart rate, neck pain, etc.).  
- **AI Summarization and Reporting** – Generates structured summaries using the OpenAI Realtime API and automatically emails them to physicians.  
- **Secure Configuration** – Sensitive data like API keys and credentials are stored in environment variables.  
- **Lightweight and Fast** – Built entirely within six hours using modern Python frameworks and APIs.

---

## Technical Architecture  

| Component | Purpose |
|------------|----------|
| **FastAPI** | Backend web framework for HTTP and WebSocket handling |
| **Twilio Media Streams** | Captures and streams live patient audio |
| **OpenAI GPT-4o Realtime API** | Processes and generates conversational responses |
| **SMTP (Gmail)** | Sends automated email summaries |
| **dotenv** | Manages configuration and credentials securely |
| **asyncio / websockets** | Handles concurrent real-time data transfer |

---

## Project Structure  

