import os
import jwt
import json
import base64
import asyncio
import settings
import websockets
from database_management import Database

from typing import Dict, Annotated, List

from twilio.rest import Client
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, EmailStr
from fastapi.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Stream, Start, Connect
from fastapi import FastAPI, WebSocket, Body, Depends, HTTPException, status, Request, File, Form, UploadFile

import pandas as pd
from io import BytesIO

# auth modules
from sqlalchemy.orm import Session
from user_account import User, get_db
from jwt.exceptions import InvalidTokenError

from actions import add_appointment_to_airtable

load_dotenv(override=True)

# Set up Twilio client
#twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
#twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')

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
    'input_audio_buffer.speech_started', 'session.created', 'error'
]
SHOW_TIMING_MATH = False
HOST = "api.voice.aismith.co"

app = FastAPI(openapi_url="/api/openapi.json", docs_url="/api/docs")

origins = [
    "*",
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

@app.post('/api/signup', response_model=UserSchema)
def signup(
    payload: CreateUserSchema = Body(), 
    session: Session=Depends(get_db)
):
    """Processes request to register user account."""
    payload.password_hash = User.hash_password(payload.password_hash)
    return create_user(session, user=payload)

@app.post("/api/login", response_model=Dict)
def login(
    payload: UserLoginSchema = Body(),
    session: Session = Depends(get_db),
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

@app.get("/api/", response_class=HTMLResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}


@app.post("/api/run-campaign")
async def run_campaign(campaign_id, jwt_token, session: Session = Depends(get_db)):
    get_current_user(jwt_token, session)
    campaign_data = database.get_campaign(campaign_id)
    phone_number_data = database.get_phone_number(campaign_data["phone_number_id"])
    clients_data = pd.read_csv(BytesIO(campaign_data["uploaded_file"]))
    clients_data["to_number"] = clients_data["to_number"].astype(str)

    for _, client in clients_data.iterrows():
        await make_outgoing_call(
                to_number=client.to_number,
                campaign_id=campaign_id,
                from_number=phone_number_data["phone_number"],
                account_sid=phone_number_data["account_sid"],
                auth_token=phone_number_data["auth_token"],
            )

class HandleCall(BaseModel):
    to_number: str
    host: str

@app.api_route("/api/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(campaign_id: int, request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    # <Say> punctuation to improve text-to-speech flow
    response.say("Please wait while we connect you")
    response.pause(length=1)
    host = request.url.hostname
    connect = Connect()
    stream = connect.stream(url=f'wss://{HOST}/stream/media-stream')

    stream.parameter(name='campaign_id', value=campaign_id)
    response.append(connect)

    return HTMLResponse(content=str(response), media_type="application/xml")

@app.post("/api/outgoing-call")
async def make_outgoing_call(
    to_number,
    campaign_id,
    from_number,
    account_sid,
    auth_token,
):
    with open("debug_logs.txt", "w") as f:
        f.write(f"outbound call invoked with campaign_id={campaign_id}\n")
        twilio_client = Client(account_sid, auth_token)
        f.write("twilio client created\n")
        print(twilio_client.incoming_phone_numbers.list())

        f.write("call created")
        call = twilio_client.calls.create(
            to=to_number,
            from_=from_number,
            url=f"https://{HOST}/api/incoming-call?campaign_id={campaign_id}"
        )
        f.write("oudbound call function returned\n")


        return {"response": "call created_successfully"}

@app.websocket("/stream/media-stream")
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
        # Connection specific state
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, latest_media_timestamp
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        #print("twilio send: ", audio_append)
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        campaign_id = data['start']['customParameters']['campaign_id']
                        assistant_id = database.get_campaign(campaign_id)['assistant_id']
                        print("initializing session")
                        await initialize_session(openai_ws, assistant_id)
                        print(f"Incoming stream has started {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
            print("sent_to_twilio INVOKED")
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"Received event: {response['type']}", response)
                        await websocket.send_json(response) # DELETE IF TWILIO NOT IGNORES

                    if response['type'] == "function_call":
                        arguments = json.loads(response["item"]["arguments"])
                        add_appointment_to_airtable(arguments["client_name"], arguments["appointment_details"], arguments["appointment_date"])

                    if response.get('type') == 'response.audio.delta' and 'delta' in response:
                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        print("Response from server received: ", json.dumps(audio_delta))
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

                        # Update last_assistant_item safely
                        if response.get('item_id'):
                            last_assistant_item = response['item_id']

                        await send_mark(websocket, stream_sid)

                    # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
                    if response.get('type') == 'input_audio_buffer.speech_started':
                        print("Speech started detected.")
                        if last_assistant_item:
                            print(f"Interrupting response with id: {last_assistant_item}")
                            await handle_speech_started_event()
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        async def handle_speech_started_event():
            """Handle interruption when the caller's speech starts."""
            nonlocal response_start_timestamp_twilio, last_assistant_item
            print("Handling speech started event.")
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")

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

        await asyncio.gather(receive_from_twilio(), send_to_twilio())

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


async def initialize_session(openai_ws, assistant_id):
    """Control initial session with OpenAI."""
    assistant_data = database.get_assistant(assistant_id)
    #print(assistant_data)
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": assistant_data['voice'],
            "instructions": assistant_data['prompt'],
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

    # Uncomment the next line to have the AI speak first
    # await send_initial_conversation_item(openai_ws)



class AssistantData(BaseModel):
    prompt: str
    voice: str
    assistant_name: str

@app.post("/api/assistants")
def create_assistant(
    jwt_token: str,
    assistant_data: AssistantData,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)

    user_id = user.user_id
    prompt = assistant_data.prompt
    voice = assistant_data.voice
    assistant_name = assistant_data.assistant_name
    
    response = database.create_assistant(user_id, prompt, voice, assistant_name)

    return response

@app.get("/api/assistants")
def get_assistants(
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    return database.get_user_assistants(user_id)

@app.get("/api/assistant")
def get_assistant(
    assistant_id: int,
    jwt_token: str,
    session: Session=Depends(get_db),
):
    # for validation only
    get_current_user(jwt_token, session)
    return database.get_assistant(assistant_id)

class Knowledge(BaseModel):
    knowledge_id: int
    file: bytes
    file_name: str

class UpdateAssistant(BaseModel):
    assistant_id: int
    prompt: str
    vocie: str
    assistant_name: str
    uploadet_files: List[Knowledge]

@app.patch("/api/assistant")
def update_assistant(
    assistant_data: UpdateAssistant,
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    assistant_id = assistant_data.assistant_id,
    assistant_name = assistant_data.assistant_name
    prompt = assistant_data.prompt
    voice = assistant_data.vocie
    uploaded_files = assistant_data.uploadet_files 
    return database.update_assistant(
        user_id=user_id,
        assistant_id=assistant_id,
        assistant_name=assistant_name,
        prompt=prompt,
        voice=voice,
        uploaded_files=uploaded_files,
    )

class CampaignData(BaseModel):
    assistant_id: int = Form(...)
    phone_number_id: int = Form(...)
    campaign_type: str = Form(...)
    start_time: str = Form(...)
    end_time: str = Form(...)
    max_recalls: int = Form(...)
    recall_interval: int = Form(...)
    campaign_status: str = Form(...)
    
@app.post("/api/campaign-days-of-week")
def create_campaign_days_of_week(
    campaign_id: int,
    day_of_week_id: int,
    jwt_token: str,
    session: Session=Depends(get_db), 
):
    get_current_user(jwt_token, session)
    return database.create_campaign_days_of_week(campaign_id, day_of_week_id)

@app.post("/api/campaigns")
def create_campaign(
    #campaign_data: CampaignData,
    jwt_token: str,
    uploaded_file: Annotated[bytes, File()],
    file_name: str = Form(...),
    assistant_id: int = Form(...),
    phone_number_id: int = Form(...),
    campaign_type: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    max_recalls: int = Form(...),
    recall_interval: int = Form(...),
    campaign_status: str = Form(...),
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    """assistant_id = campaign_data.assistant_id
    phone_number_id = campaign_data.phone_number_id
    campaign_type = campaign_data.campaign_type
    start_time = campaign_data.start_time
    end_time = campaign_data.end_time
    max_recalls = campaign_data.max_recalls
    recall_interval = campaign_data.recall_interval
    campaign_status = campaign_data.campaign_status
    uploaded_file = uploaded_file"""
    campaign_data = database.create_campaign(
        user_id,
        assistant_id,
        phone_number_id,
        campaign_type,
        start_time,
        end_time,
        max_recalls,
        recall_interval,
        campaign_status,
        uploaded_file,
        file_name,
    )

    campaign_id = campaign_data["id"]
    phone_number_data = database.get_phone_number(phone_number_id)
    account_sid = phone_number_data["account_sid"]
    auth_token = phone_number_data["auth_token"]
    phone_number = phone_number_data["phone_number"]

    if campaign_type == "inbound":
        client = Client(account_sid, auth_token)
        incoming_phone_number = client.incoming_phone_numbers('PN4242228effc5204a3e7303879548cb9b').update(voice_url=f"https://{HOST}/api/incoming-call?campaign_id={campaign_id}")

    return campaign_data

@app.post("/api/campaigns")
def create_campaign(
    jwt_token: str,
    uploaded_file: Annotated[bytes, File()],
    file_name: str = Form(...),
    assistant_id: int = Form(...),
    campaign_id: int = Form(...),
    phone_number_id: int = Form(...),
    campaign_type: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    max_recalls: int = Form(...),
    recall_interval: int = Form(...),
    campaign_status: str = Form(...),
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    campaign_data = database.update_campaign(
        campaign_id,
        user_id,
        assistant_id,
        phone_number_id,
        campaign_type,
        start_time,
        end_time,
        max_recalls,
        recall_interval,
        campaign_status,
        uploaded_file,
        file_name,
    )

    return campaign_data

@app.get("/api/campaigns")
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

@app.post("/api/phone-numbers")
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

    return database.create_phone_number(phone_number, user_id, account_sid, auth_token)

@app.get("/api/phone-numbers")
def get_phone_numbers(
    jwt_token: str,
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)
    user_id = user.user_id
    return database.get_user_phone_numbers(user_id)

@app.get("/api/days-of-week")
def get_days_of_week():
    return database.get_days_of_week()

@app.get("/api/campaign-days-of-week")
def get_campaign_days_of_week(
    campaign_id: int,
    jwt_token: str,
    session: Session=Depends(get_db),
):
    get_current_user(jwt_token, session)
    return database.get_campaign_days_of_week(campaign_id)

@app.post("/api/knowledge")
def create_knowledge(
    jwt_token: str,
    uploaded_file: Annotated[bytes, File()],
    file_name: str=Form(...),
    session: Session=Depends(get_db),
):
    user = get_current_user(jwt_token, session)

    user_id = user.user_id
    return database.create_knowledge(user_id, uploaded_file, file_name)

@app.post("/api/assistant-knowledge")
def create_assistants_knowledge(
    jwt_token: str,
    session: Session=Depends(get_db),
    assistant_id: int=Form(...),
    knowledge_id: int=Form(...),
):
    get_current_user(jwt_token, session)
    return database.create_assistant_knowledge(assistant_id, knowledge_id)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
