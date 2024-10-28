import os
import jwt
import json
import base64
import asyncio
import settings
import websockets
from database_management import Database

from typing import Dict

from twilio.rest import Client
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, EmailStr
from fastapi.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Stream, Start, Connect
from fastapi import FastAPI, WebSocket, Body, Depends, HTTPException, status, Request

# auth modules
from sqlalchemy.orm import Session
from user_account import User, get_db
from jwt.exceptions import InvalidTokenError


NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")
NGROK_EDGE = os.getenv("NGROK_EDGE", "edge:edghts_")

load_dotenv()

# Set up Twilio client
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')

twilio_client = Client(twilio_account_sid, twilio_auth_token)
database = Database(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB'),
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

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

#fixme place schemas in separate module
class UserBaseSchema(BaseModel):
    email: EmailStr

class CreateUserSchema(UserBaseSchema):
    password_hash: str = Field(alias="password")

class UserSchema(UserBaseSchema):
    user_id: int
    is_active: bool = Field(default=False)

    class Config:
        orm_mode = True

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(alias="username")
    password: str

def create_user(session: Session, user: CreateUserSchema):
    db_user = User(**user.dict())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user(session:Session, email:str):
    return session.query(User).filter(User.email == email).one()

class TokenData(BaseModel):
    email: EmailStr | None = None

def get_current_user(
        jwt_token: str,
        session: Session,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("email")
        if not email:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session=session, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.exception_handler(422)
def catch_unprocessed_entity(request: Request):
    print(request.json())
    return

@app.post('/signup', response_model=UserSchema)
def signup(
    payload: CreateUserSchema = Body(), 
    session: Session=Depends(get_db)
):
    """Processes request to register user account."""
    payload.password_hash = User.hash_password(payload.password_hash)
    return create_user(session, user=payload)

@app.post("/login", response_model=Dict)
def login(
    payload: UserLoginSchema = Body(),
    session: Session = Depends(get_db)
):
    print(payload)
    try:
        user: User = get_user(
            session=session, email=payload.email
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials"
        )

    is_validated:bool = user.validate_password(payload.password)
    if not is_validated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials"
        )

    return user.generate_token()

@app.get("/", response_class=HTMLResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}


class HandleCall(BaseModel):
    to_number: str
    host: str

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(
    jwt_token: str,
    campaign_id: int,
    request: Request,
    session: Session=Depends(get_db),
):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    # <Say> punctuation to improve text-to-speech flow
    response.say("Please wait while we connect you")
    response.pause(length=1)
    host = request.url.hostname
    connect = Connect()
    stream = connect.stream(url=f'wss://{host}/media-stream?campaign_id={campaign_id}')
    stream.parameter(name='campaign_id', value=campaign_id)
    response.append(connect)
    
    # fixme возможно в male_outgoing_call должно быть это вместо response в качестве twiml
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.post("/make_outgoing_call")
async def make_outgoing_call(
    jwt_token: str,
    campaign_id: int,
    request: HandleCall,
    session: Session=Depends(get_db),
):
    # testme
    # fixme campaign_id from jwt_token
    to_number = request.to_number
    host = request.host

    call = twilio_client.calls.create(
        to=to_number,
        from_="+12014256272",
        url=f"https://{host}/incoming-call?jwt_token={jwt_token}&campaign_id={campaign_id}"
    )

    return call.sid

@app.websocket("/media-stream")
async def handle_media_stream(
    campaign_id: int,
    websocket: WebSocket,
):
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
        assistant_id = database.get_campaign(campaign_id)["assistant_id"]
        assistant_data = database.get_assistant(assistant_id)
        await initialize_session(openai_ws, assistant_data)

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
                        #campaign_id = data['start']['customParameters']["campaign_id"]
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

        await asyncio.gather(send_to_twilio(), receive_from_twilio())

async def initialize_session(openai_ws, assistant_data):
    """Send session update to OpenAI WebSocket."""
    # testme 
    session_update = {
        "type": "session.created",
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
    print('Sending session create:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))



class AssistantData(BaseModel):
    prompt: str
    voice: str

@app.post("/assistants")
def create_assistant(
    jwt_token: str,
    assistant_data: AssistantData,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)

    user_id = user.user_id
    prompt = assistant_data.prompt
    voice = assistant_data.voice
    
    response = database.create_assistant(user_id, prompt, voice)

    return response

@app.get("/assistants")
def get_assistants(
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    return database.get_user_assistants(user_id)

@app.get("/assistant")
def get_assistant(
    assistant_id: int,
    jwt_token: str,
    session: Session=Depends(get_db),
):
    # for validation only
    get_current_user(jwt_token, session)
    return database.get_assistant(assistant_id) 

class CampaignData(BaseModel):
    assistant_id: int
    phone_number_id: int
    campaign_type: str
    start_time: str
    end_time: str
    max_recalls: int
    recall_interval: int
    campaign_status: str

@app.post("/campaigns")
def create_campaign(
    campaign_data: CampaignData,
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    assistant_id = campaign_data.assistant_id
    phone_number_id = campaign_data.phone_number_id
    campaign_type = campaign_data.campaign_type
    start_time = campaign_data.start_time
    end_time = campaign_data.end_time
    max_recalls = campaign_data.max_recalls
    recall_interval = campaign_data.recall_interval
    campaign_status = campaign_data.campaign_status

    return database.create_campaign(
        user_id,
        assistant_id,
        phone_number_id,
        campaign_type,
        start_time,
        end_time,
        max_recalls,
        recall_interval,
        campaign_status
    )

@app.get("/campaigns")
def get_campaings(
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    return database.get_user_campaigns(user_id)




class PhoneNumber(BaseModel):
    phone_number: str
    account_sid: str
    auth_token: str

@app.post("/phone-numbers")
def create_phone_number(
    phone_number_data: PhoneNumber,
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)

    user_id = user.user_id
    phone_number = phone_number_data.phone_number
    account_sid = phone_number_data.account_sid
    auth_token = phone_number_data.auth_token

    database.create_phone_number(phone_number, user_id, account_sid, auth_token)

@app.get("/phone-numbers")
def get_phone_numbers(
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    return database.get_user_phone_numbers(user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)