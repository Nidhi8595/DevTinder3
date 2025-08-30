from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from jwt import PyJWTError
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
JWT_SECRET = "devtinder_secret_key_2025"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        # Update user online status
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"is_online": True, "last_seen": datetime.now(timezone.utc)}}
        )
        
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # Update user offline status (will be done in disconnect handler)
        
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message)

manager = ConnectionManager()

# Define Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    name: str
    bio: Optional[str] = ""
    skills: List[str] = []
    interests: List[str] = []
    profile_pic: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    bio: Optional[str] = ""
    skills: List[str] = []
    interests: List[str] = []
    profile_pic: Optional[str] = None
    connections: List[str] = []
    friend_requests_sent: List[str] = []
    friend_requests_received: List[str] = []
    is_online: bool = False
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    bio: Optional[str] = ""
    skills: List[str] = []
    interests: List[str] = []
    profile_pic: Optional[str] = None
    connections: List[str] = []
    friend_requests_sent: List[str] = []
    friend_requests_received: List[str] = []
    is_online: bool = False
    last_seen: datetime
    created_at: datetime

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageCreate(BaseModel):
    receiver_id: str
    text: str

class FriendRequestResponse(BaseModel):
    success: bool
    message: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return UserResponse(**user)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth endpoints
@api_router.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user_dict = user_data.dict()
    user_dict["password"] = hashed_password
    user = User(**user_dict)
    
    # Save to database
    user_doc = user.dict()
    await db.users.insert_one(user_doc)
    
    # Create token
    token = create_jwt_token(user.id)
    user_response = UserResponse(**user.dict())
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    # Find user by email
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    token = create_jwt_token(user["id"])
    user_response = UserResponse(**user)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

# Profile endpoints
@api_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@api_router.put("/profile", response_model=UserResponse)
async def update_profile(profile_data: UserProfile, current_user: UserResponse = Depends(get_current_user)):
    # Update user profile
    update_data = profile_data.dict()
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": update_data}
    )
    
    # Return updated user
    updated_user = await db.users.find_one({"id": current_user.id})
    return UserResponse(**updated_user)

# Feed endpoint - get users to swipe through
@api_router.get("/feed", response_model=List[UserResponse])
async def get_feed(current_user: UserResponse = Depends(get_current_user)):
    # Exclude self, connections, and pending friend requests
    exclude_ids = [current_user.id] + current_user.connections + current_user.friend_requests_sent + current_user.friend_requests_received
    
    users = await db.users.find({
        "id": {"$nin": exclude_ids}
    }).to_list(length=20)  # Limit to 20 users
    
    return [UserResponse(**user) for user in users]

# Friend request endpoints
@api_router.post("/users/{user_id}/friend-request", response_model=FriendRequestResponse)
async def send_friend_request(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    # Prevent self-request
    if user_id == current_user.id:
        return FriendRequestResponse(success=False, message="Cannot send friend request to yourself")
    
    # Check if user exists
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        return FriendRequestResponse(success=False, message="User not found")
    
    # Check if already connected
    if user_id in current_user.connections:
        return FriendRequestResponse(success=False, message="Already connected with this user")
    
    # Check if request already sent
    if user_id in current_user.friend_requests_sent:
        return FriendRequestResponse(success=False, message="Friend request already sent")
    
    # Check if request already received from this user
    if user_id in current_user.friend_requests_received:
        return FriendRequestResponse(success=False, message="This user has already sent you a request")
    
    # Send friend request
    await db.users.update_one(
        {"id": current_user.id},
        {"$push": {"friend_requests_sent": user_id}}
    )
    
    await db.users.update_one(
        {"id": user_id},
        {"$push": {"friend_requests_received": current_user.id}}
    )
    
    return FriendRequestResponse(success=True, message="Friend request sent successfully")

@api_router.post("/users/{user_id}/accept-request", response_model=FriendRequestResponse)
async def accept_friend_request(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    # Check if request exists
    if user_id not in current_user.friend_requests_received:
        return FriendRequestResponse(success=False, message="No friend request found from this user")
    
    # Accept request - add to connections and remove from requests
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$push": {"connections": user_id},
            "$pull": {"friend_requests_received": user_id}
        }
    )
    
    await db.users.update_one(
        {"id": user_id},
        {
            "$push": {"connections": current_user.id},
            "$pull": {"friend_requests_sent": current_user.id}
        }
    )
    
    return FriendRequestResponse(success=True, message="Friend request accepted successfully")

# Chat endpoints
@api_router.get("/chat/{connection_id}", response_model=List[Message])
async def get_chat_history(connection_id: str, current_user: UserResponse = Depends(get_current_user)):
    # Check if connected
    if connection_id not in current_user.connections:
        raise HTTPException(status_code=403, detail="Not connected with this user")
    
    # Get messages between users
    messages = await db.messages.find({
        "$or": [
            {"sender_id": current_user.id, "receiver_id": connection_id},
            {"sender_id": connection_id, "receiver_id": current_user.id}
        ]
    }).sort("timestamp", 1).to_list(length=None)
    
    return [Message(**message) for message in messages]

@api_router.post("/chat/send", response_model=Message)
async def send_message(message_data: MessageCreate, current_user: UserResponse = Depends(get_current_user)):
    # Check if connected
    if message_data.receiver_id not in current_user.connections:
        raise HTTPException(status_code=403, detail="Not connected with this user")
    
    # Create message
    message = Message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        text=message_data.text
    )
    
    # Save to database
    await db.messages.insert_one(message.dict())
    
    # Send real-time message to receiver if online
    message_json = json.dumps({
        "type": "new_message",
        "message": message.dict(),
        "sender_name": current_user.name
    }, default=str)
    await manager.send_personal_message(message_json, message_data.receiver_id)
    
    return message

# Get user connections
@api_router.get("/connections", response_model=List[UserResponse])
async def get_connections(current_user: UserResponse = Depends(get_current_user)):
    if not current_user.connections:
        return []
    
    connections = await db.users.find({
        "id": {"$in": current_user.connections}
    }).to_list(length=None)
    
    return [UserResponse(**user) for user in connections]

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        # Update user offline status
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"is_online": False, "last_seen": datetime.now(timezone.utc)}}
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()