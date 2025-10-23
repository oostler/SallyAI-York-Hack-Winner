# MedAIHack

This project won us the York University 2025 Artificial Intelligence in Health Care Society's annual hackathon
Authors: Owen Ostler, Thomas Shvekher, and Alp Unsal


MedAIHack is an AI-powered voice assistant designed for medical check-ins with a focus on thyroid assessments. This project was built during Hackathon York U to demonstrate how modern APIs and cloud services can be combined to streamline healthcare interactions. In this README, you'll not only find instructions on how to set up and run the project but also learn the rationale behind many of our key technical decisions.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technical Decisions and Rationale](#technical-decisions-and-rationale)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [API Access and Usage](#api-access-and-usage)
- [Email Configuration](#email-configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

MedAIHack is a backend service built using Python that integrates several powerful APIs:
- **FastAPI** provides high-performance HTTP and WebSocket support.
- **Twilio** handles real-time audio streams, connecting patients with our AI.
- **OpenAI Realtime API** processes and generates natural language responses on the fly.
- **SMTP (via Gmail)** sends summary emails to healthcare professionals after each call.

## Key Features

- **Real-time Audio Streaming:** Connects Twilio's Media Streams to our backend, allowing for seamless audio interaction.
- **Dynamic AI Interaction:** Uses the OpenAI Realtime API to generate contextually relevant responses during medical check-ins.
- **Automated Summary Generation:** Summarizes call conversations and dispatches emails with the session's key insights.
- **Modular and Configurable:** Environment variables are used to manage sensitive credentials and configuration settings.

## Technical Decisions and Rationale

### FastAPI
- **Why FastAPI?**  
  We chose FastAPI because of its modern design, high performance, and native support for asynchronous operations. This made it the ideal framework for handling both HTTP requests and WebSocket connections, which are essential for real-time audio streaming.

### Twilio Media Streams
- **Why Twilio?**  
  Twilio was selected for its robust and easy-to-integrate telephony API, especially its Media Streams feature, which allows us to stream audio in real time. This was crucial for building a responsive voice assistant capable of interacting with patients on the fly.

### OpenAI Realtime API
- **Why OpenAI?**  
  The decision to use OpenAI's Realtime API stemmed from our need for a powerful language model capable of understanding and generating human-like responses. Its ability to process natural language in real time makes it a perfect fit for interactive medical consultations.

### Email via SMTP (Gmail)
- **Why SMTP with Gmail?**  
  For sending call summaries, we needed a reliable and widely supported email service. Gmail SMTP was chosen due to its ease of use, security features, and familiarity among users. We emphasize the importance of using environment variables to store sensitive information like credentials.

### Environment Variables
- **Security and Flexibility:**  
  Using environment variables (managed via a `.env` file) ensures that sensitive data such as API keys and email credentials are kept out of the codebase. This practice enhances security and makes the configuration easily adaptable to different environments.

## Prerequisites

Before you begin, ensure you have the following:
- **Python 3.8+** – The project is built with Python and requires version 3.8 or higher.
- A **Twilio account** with Media Streams enabled.
- An **OpenAI API key** with access to the realtime API.
- A **Gmail account** (or equivalent SMTP service) for sending emails.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/MedAIHack.git
   cd MedAIHack
