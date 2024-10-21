import os
import json
import base64
import asyncio
import websockets
from database_management import Database

from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, Request
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream, Start

load_dotenv()

# Set up Twilio client
twilio_account_sid = "ACfd6bd02d2d4665c10826f3cecbb33513"
twilio_auth_token = "bd804505ef52d54bf585d10118724fda"

twilio_client = Client(twilio_account_sid, twilio_auth_token)
database = Database(
    host="localhost",
    user="root",
    password="jhyfn2001",
    database="VoiceAssistant"
)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') # requires OpenAI Realtime API Access
PORT = int(os.getenv('PORT', 5050))
LOG_EVENT_TYPES = [
    'response.content.done', 'rate_limits.updated', 'response.done',
    'input_audio_buffer.committed', 'input_audio_buffer.speech_stopped',
    'input_audio_buffer.speech_started', 'session.created'
]

app = FastAPI()

if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

@app.post("/login")
def login():
    return "fakeToken"

@app.get("/", response_class=HTMLResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}


class HandleCall(BaseModel):
    websocket_url: str
    campaign_id: int
    to_number: str

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: HandleCall):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    host = request.websocket_url
    campaign_id = request.campaign_id
    start = Start()
    stream = Stream(url=host)

    stream.parameter(name="campaign_id", value=campaign_id)

    start.append(stream)
    response.append(start)
    # fixme возможно в male_outgoing_call должно быть это вместо response в качестве twiml
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.post("/make_outgoing_call")
async def make_outgoing_call(request: HandleCall):
    # testme
    to_number = request.to_number
    host = request.websocket_url
    campaign_id = request.campaign_id

    response = VoiceResponse()
    stream = Stream(url=host)
    start = Start()

    stream.parameter(name="campaign_id", value=campaign_id)

    start.append(stream)
    response.append(start)

    call = twilio_client.calls.create(
        to=to_number,
        from_="+16562210739",
        twiml=response
    )

    return call.sid

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
        stream_sid = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        # testme
                        campaign_id = data['start']['customParameters']["campaign_id"]
                        assistant_id = database.get_campaign(campaign_id)["assistant_id"]
                        assistant_data = database.get_assistant(assistant_id)
                        await send_session_update(openai_ws, assistant_data)
                        stream_sid = data['start']['streamSid']
                        print(f"Incoming stream has started {stream_sid}")
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"Received event: {response['type']}", response)
                    if response['type'] == 'session.updated':
                        print("Session updated successfully:", response)
                    if response['type'] == 'response.audio.delta' and response.get('delta'):
                        # Audio from OpenAI
                        try:
                            audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio_payload
                                }
                            }
                            await websocket.send_json(audio_delta)
                        except Exception as e:
                            print(f"Error processing audio data: {e}")
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def send_session_update(openai_ws, assistant_data):
    """Send session update to OpenAI WebSocket."""
    # testme 
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": assistant_data["voice"],
            "instructions": assistant_data["prompt"],
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))



class UserId(BaseModel):
    user_id: int

class AssistantData(BaseModel):
    user_id: int
    prompt: str
    voice: str

@app.post("/assistants")
def create_assistant(assistant_data: AssistantData):
    user_id = assistant_data.user_id
    prompt = assistant_data.prompt
    voice = assistant_data.voice
    
    database.create_assistant(user_id, prompt, voice)

    return {"Statis-Code": 200}

@app.get("/assistants")
def get_assistant(user_id: int):
    return database.get_user_assistants(user_id)



class CampaignData(BaseModel):
    user_id: int
    assistant_id: int
    phone_number_id: int
    campaign_type: str
    start_time: str
    end_time: str
    max_recalls: int
    recall_interval: int
    campaign_status: str

@app.post("/campaigns")
def create_campaign(campaign_data: CampaignData):
    user_id = campaign_data.user_id
    assistant_id = campaign_data.assistant_id
    phone_number_id = campaign_data.phone_number_id
    campaign_type = campaign_data.campaign_type
    start_time = campaign_data.start_time
    end_time = campaign_data.end_time
    max_recalls = campaign_data.max_recalls
    recall_interval = campaign_data.recall_interval
    campaign_status = campaign_data.campaign_status

    database.create_campaign(user_id, assistant_id, phone_number_id, campaign_type, start_time, end_time, max_recalls, recall_interval, campaign_status)

@app.get("/campaigns")
def get_campaings(user_id: int):
    return database.get_user_campaigns(user_id)




class PhoneNumber(BaseModel):
    phone_number: str
    user_id: int
    account_sid: str
    auth_token: str

@app.post("/phone-numbers")
def create_phone_number(phone_number_data: PhoneNumber):
    phone_number = phone_number_data.phone_number
    user_id = phone_number_data.user_id
    account_sid = phone_number_data.account_sid
    auth_token = phone_number_data.auth_token

    database.create_phone_number(phone_number, user_id, account_sid, auth_token)

@app.get("/phone-numbers")
def get_phone_numbers(user_id: int):
    return database.get_user_phone_numbers(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)