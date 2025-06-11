import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from websockets.protocol import State
import openai
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

PORT = int(os.getenv('PORT', 8080))
SYSTEM_MESSAGE = "You are an AI-powered virtual medical assistant conducting check-up calls for patients with thyroid conditions. Your role is to gather key health insights by asking structured questions about symptoms like weight changes, temperature tolerance, neck pain, skin and nail changes, diet, heart rate, and bowel movements. Adapt your questioning flow based on patient responses and ensure all relevant details are organized into a concise report for the doctor. If a response indicates a potential concern, flag it accordingly. Maintain a professional yet warm tone, ensuring patients feel heard while efficiently collecting essential medical information."
VOICE = 'alloy'
LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]
SHOW_TIMING_MATH = False

SUMMARY_INFO = ""

app = FastAPI()

if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

@app.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    # <Say> punctuation to improve text-to-speech flow
    response.pause(length=1)
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        additional_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
        await initialize_session(openai_ws)

        # Connection specific state
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None
        summary_requested = True
        summary_received = asyncio.Event()
        
        async def handle_summary_response(response):
            if response.get("type") == "response.content.done":
                summary_text = response.get("content", "No summary provided.")
                # Signal that the summary has been received
                summary_received.set()

        summary_requested = False

        

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, latest_media_timestamp
            try:
                async for message in websocket.iter_text():

                    data = json.loads(message) 
                    if data['event'] == 'media' and openai_ws.state == State.OPEN:
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        #print(f"Incoming stream has started {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                print("Client disconnected.")

                if openai_ws.state == State.OPEN:
                    await send_summary_prompt(openai_ws)

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)

                    global SUMMARY_INFO

                    if response['type'] == 'response.done':
                        if find_key(response, 'transcript') is not None:
                            SUMMARY_INFO += find_key(response, 'transcript')



                    if response['type'] in LOG_EVENT_TYPES:
                        #print(f"Received event: {response['type']}", response)
                        print()

                    if response.get('type') == 'response.audio.delta' and 'delta' in response:
                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                #print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")
                                print()

                        # Update last_assistant_item safely
                        if response.get('item_id'):
                            last_assistant_item = response['item_id']

                        await send_mark(websocket, stream_sid)

                    # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
                    if response.get('type') == 'input_audio_buffer.speech_started':
                        #print("Speech started detected.")
                        if last_assistant_item:
                            #print(f"Interrupting response with id: {last_assistant_item}")
                            await handle_speech_started_event()

                    if summary_requested and response.get('type') == 'response.content.done':
                        await handle_summary_response(response)
                        # Optionally, you can reset the flag after processing.
                        
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        async def shutdown_sequence():
            """After client disconnect, send summary prompt and wait for summary response."""
            if openai_ws.state == State.OPEN:
                #print("Sending summary prompt...")
                await send_summary_prompt(openai_ws)
                try:
                    # Increase timeout if needed.
                    await asyncio.wait_for(summary_received.wait(), timeout=20)
                except asyncio.TimeoutError:
                    #print("Timeout waiting for summary response.")
                    print()
                else:
                    #print("Summary response received successfully.")
                    print()

        async def handle_speech_started_event():
            """Handle interruption when the caller's speech starts."""
            nonlocal response_start_timestamp_twilio, last_assistant_item
            #print("Handling speech started event.")
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    #print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")
                    print()

                if last_assistant_item:
                    if SHOW_TIMING_MATH:
                        print(f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms")

                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time
                    }
                    await openai_ws.send(json.dumps(truncate_event))

                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })

                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None

        async def send_mark(connection, stream_sid):
            if stream_sid:
                mark_event = {
                    "event": "mark",
                    "streamSid": stream_sid,
                    "mark": {"name": "responsePart"}
                }
                await connection.send_json(mark_event)
                mark_queue.append('responsePart')

        receive_task = asyncio.create_task(receive_from_twilio())
        send_task = asyncio.create_task(send_to_twilio())

        # Wait for the receive task to complete (i.e. Twilio disconnects).
        await receive_task

        # Now run the shutdown sequence: send summary prompt and wait for the response.
        await shutdown_sequence()

        # If the send_to_twilio task is still running, cancel it now.
        if not send_task.done():
            send_task.cancel()
            try:
                await send_task
            except asyncio.CancelledError:
                print("send_to_twilio task cancelled.")

        # Finally, close the OpenAI connection.
        await openai_ws.close()
        print("OpenAI connection closed.")

async def send_initial_conversation_item(openai_ws):
    """Send initial conversation item if AI talks first."""
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Greet the user with 'Hello there! I am an AI voice assistant powered by Twilio and the OpenAI Realtime API. You can ask me for facts, jokes, or anything you can imagine. How can I help you?'"
                }
            ]
        }
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))

#Used for summary prompt
async def send_summary_prompt(openai_ws):
    summary_prompt = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": "Please summarize the call and provide a concise report of the conversation."
            }]
        }
    }
    #print('test1')
    await openai_ws.send(json.dumps(summary_prompt))
    await openai_ws.send(json.dumps({"type": "response.create"}))
    #print('test2')

#Used to find a key in a dictionary recursively
def find_key(d, target):
    if isinstance(d, dict):
        for key, value in d.items():
            if key == target:
                return value
            result = find_key(value, target)
            if result is not None:
                return result
    elif isinstance(d, list):
        for item in d:
            result = find_key(item, target)
            if result is not None:
                return result
    return None

async def handle_summary_response(openai_message):
    response = json.loads(openai_message)
    if response.get("type") == "response.content.done":
        # Assuming the summary text is part of the response content
        summary_text = response.get("content", "No summary provided.")
        print("Call Summary:", summary_text)


async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    await openai_ws.send(json.dumps(session_update))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
    await send_initial_conversation_item(openai_ws)


def generate_email_summary(transcript: str):
    prompt = (
        "You are an intelligent AI assistant tasked with summarizing patient check-in conversations related to thyroid disease into a structured and professional email for their doctor. Extract key details, including the patient's name, symptoms, medication adherence, and any concerns, and present them concisely and clearly. Ensure the email is well-organized with distinct sections for readability, using ALL CAPS for section headings instead of bold text. The tone should be clinical, precise, and appropriate for a medical professional. Conclude the email with a signature from the AI Patient Tracker Team. This is the final email to be sent, do not leave any variables in the email. If you do not know something, don't write it down."
    )

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=500,
    )
    summary_text = response.choices[0].message.content[8:-3]
    print(summary_text)

    try:
        summary_data = json.loads(summary_text)
        subject = 'Patient Update: Status URGENT'
        email_body = summary_data.get("email", "No email summary provided.")
    except Exception as e:
        print("Error parsing summary JSON:", e)
        subject = ""
        email_body = summary_text

    return subject, email_body


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject: str, body: str):
    # Email credentials
    sender_email = "aipatienttracker@gmail.com"
    receiver_email = "unsalalp10@gmail.com"
    password = "kxnc ambe ynkg hazv" # Replace with your App Password if 2FA is enabled

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Patient Update: Status URGENT'

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail SMTP Server and send the email
    try:
        print("📧 Connecting to SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()   # Secure the connection
        print("🔐 Logging in to email account...")
        server.login(sender_email, password)

        print("📤 Sending email...")
        server.sendmail(sender_email, receiver_email, msg.as_string())

        print("✅ Email sent successfully to", receiver_email)
        server.quit()

    except Exception as e:
        print(f"❌ Error sending email: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

    print(SUMMARY_INFO)

    subject, body = generate_email_summary(SUMMARY_INFO)

    send_email(subject=subject, body=body)
    print('Sent!')
