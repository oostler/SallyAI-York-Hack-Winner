# SallyAI

**Winning Project – Medical AI Hackathon 2025, York University**

**Authors:** Owen Ostler, Thomas Shvekher, and Alp Unsal

🎥 [Watch the Live Demo](https://www.loom.com/share/2d2c0a3c8157435d90771a2a54d9b075?sid=2885d0ff-8164-49ab-8859-f83a9c6341b6) 

📖 [Read Our Hackathon Project Report (PDF)](https://github.com/oostler/SallyAI-York-Hack-Winner/blob/main/Medical%20AI%20Hackathon%20-%20Group%207.pdf)

---

## Overview  

SallyAI is an AI-driven medical assistant built in just **6 hours** during the 2025 York University Artificial Intelligence in Health Care Society Hackathon. It automates patient voice check-ins for thyroid-related conditions and generates structured summaries for physicians in real time.  

The system integrates Twilio, FastAPI, and OpenAI’s GPT-4o models to deliver real-time conversational intelligence and automated clinical reporting.  
By combining real-time audio streaming, natural language understanding, and email automation, SallyAI demonstrates how rapidly deployable, AI-powered tools can improve medical workflows.

---

## Key Features  

- **Real-Time Voice Interaction** – Conducts natural patient phone call interviews through Twilio Media Streams.  
- **Dynamic Question Flow** – Uses context-driven AI to tailor questions around thyroid-related symptoms such as fatigue, heart rate irregularities, and temperature sensitivity.  
- **Realtime Processing (GPT-4o Realtime API)** – Handles voice recognition and dialogue generation directly during the call with near-zero latency.  
- **Automated Summarization (GPT-4o Text Model)** – After each session, a secondary GPT-4o text completion model transforms the transcript into a structured medical summary.  
- **Email Delivery Pipeline** – The generated summary is formatted into a physician-ready report and sent automatically via Gmail’s SMTP service.  

---

## Technical Architecture  

| Component | Purpose |
|------------|----------|
| **FastAPI** | Serves as the backend web framework handling HTTP requests and WebSocket connections |
| **Twilio Media Streams** | Streams live audio from the patient during phone call check-ins |
| **OpenAI GPT-4o Realtime API** | Provides low-latency understanding and spoken response generation |
| **OpenAI GPT-4o Text Completion API** | Generates structured text summaries and formatted clinical emails |
| **SMTP (Gmail)** | Handles outbound delivery of physician summary reports |
| **asyncio / websockets** | Enables concurrent event-driven audio processing and data exchange |

---

## How It Works  

steps:
  - A patient receives a voice call initiated by the Twilio Media Stream.
  - SallyAI begins a medically guided conversation, recording and analyzing responses in real time.
  - The audio data is continuously streamed to the **OpenAI GPT-4o Realtime API**, which interprets and generates spoken replies.
  - Once the conversation ends, SallyAI triggers a **GPT-4o text completion request** to summarize the full interaction into a structured medical report.
  - The report is automatically formatted as a clinical email and dispatched via **SMTP (Gmail)** to the physician.
  - All operations run asynchronously under **FastAPI**, ensuring responsive real-time performance and minimal latency.

---

## Inspiration & Impact

Inspiration:
  - SallyAI was inspired by the inefficiencies in clinical follow-ups for chronic conditions like thyroid disorders.
  - Our goal was to create a system that could replicate the efficiency and warmth of a real medical assistant, but scale instantly through automation.
  - The hackathon’s 6-hour time limit motivated us to build a fully functional prototype that proved how AI and cloud-based APIs can meaningfully assist healthcare delivery in real-world contexts.

Impact:
  - SallyAI demonstrates how conversational AI can reduce administrative burden for healthcare professionals by automating patient check-ins and documentation.
  - The system highlights the potential of GPT-4o for both real-time, speech-based medical interactions and structured medical reporting.
  - Its architecture can be adapted for other use cases such as mental health monitoring, remote triage, and chronic disease management.
  - By bridging real-time communication and AI summarization, SallyAI offers a glimpse into the next generation of accessible, scalable, and intelligent healthcare technology.

