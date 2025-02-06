import os
import json
import asyncio
import websockets
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing the OpenAI API key. Please set it in the .env file.")

VOICE = "alloy"
SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant. You love chatting about any topic and "
    "sprinkle in a joke or two when appropriate."
)
API_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"


async def initialize_session(ws):
    """Send a session update to configure the connection."""
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
        },
    }
    await ws.send(json.dumps(session_update))
    print("Session update sent.")


async def send_test_conversation_item(ws):
    """Send a test conversation item to kick off the dialogue."""
    test_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Hello, this is a test message to the realtime voice API.",
                }
            ],
        },
    }
    # Send the test message
    await ws.send(json.dumps(test_item))
    # Trigger a response
    await ws.send(json.dumps({"type": "response.create"}))
    print("Test conversation item sent.")


async def main():
    async with websockets.connect(
        API_URL,
        additional_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1",
        },
    ) as ws:
        print("Connected to OpenAI Realtime Voice API.")
        await initialize_session(ws)
        await send_test_conversation_item(ws)

        # Listen for and print responses from the API
        try:
            async for message in ws:
                response = json.loads(message)
                print("Received response:", json.dumps(response, indent=2))
        except websockets.ConnectionClosed:
            print("Connection closed by the server.")


if __name__ == "__main__":
    asyncio.run(main())