from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
import hypercorn
from sqlalchemy import and_, not_, or_
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from . import models,schemas
from .database import engine, SessionLocal

app = FastAPI(title="ZiemniaczaneRozmowy", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict() = dict()

    async def connect(self, websocket: WebSocket, client_id):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await manager.broadcast(f"status")

    async def disconnect(self, client_id):
        self.active_connections.pop(client_id)
        await manager.broadcast(f"Jedna bestie mniej")

    async def send_personal_message(self, message: str, client_id):
        await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await self.active_connections[connection].send_text(message)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


manager = ConnectionManager()
isHealthy = True

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    print(manager.active_connections)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(client_id)


@app.get('/user/',  response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()


@app.post('/user/', response_model=schemas.User)
async def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.login == new_user.login).first()
    if user:
        raise HTTPException(status_code=400, detail="Login already registered")
    await manager.broadcast(f"status")
    print(manager.active_connections)
    password =new_user.password
    db_user = models.User(login=new_user.login, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/user/login/", response_model=schemas.User)
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger = db.query(models.User).filter(models.User.login == user.login).filter(models.User.password == user.password).first()
    if not logger:
        raise HTTPException(status_code=404, detail="User not found")
    logger.is_active = True
    db.commit()
    db.refresh(logger)
    return logger


@app.post('/user/logout/', response_model=schemas.User)
def logout_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    logger = db.query(models.User).filter(models.User.login == user.login).first()
    if not logger:
        raise HTTPException(status_code=404, detail="User not found")
    logger.is_active = False
    db.commit()
    db.refresh(logger)
    return logger


@app.put('/users/status', response_model=schemas.User)
async def update_user_status(user: schemas.User, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    if db_user:
        db_user.is_active = user.is_active
        db.commit()
        db.refresh(db_user)
    print (db_user.is_active)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get('/user/messages/{reciver}/{author}/', response_model= List[schemas.Message])
def get_messages_to_user(reciver: int,author: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = db.query(models.Message)\
        .filter(and_(models.Message.reciver_id == reciver, models.Message.author_id== author)) \
        .order_by(models.Message.id).offset(skip).limit(limit).all()
    if len(messages) == 0:
        raise HTTPException(status_code=404, detail='Messages not found')
    return messages


@app.get("/message/{receiver_id}/{sender_id}/", response_model=List[schemas.Message])
def read_messages_to_user_from(receiver_id: int, sender_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Message) \
        .filter(or_(and_(models.Message.reciver_id == receiver_id, models.Message.author_id == sender_id),
                    and_(models.Message.reciver_id == sender_id, models.Message.author_id == receiver_id))) \
        .order_by(models.Message.date).offset(skip).limit(limit).all()


@app.get("/general/", response_model=List[schemas.Message])
def read_messages_general(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Message).filter(models.Message.reciver_id==13).order_by(models.Message.date).offset(skip).limit(limit).all()


@app.get("/singleton//{receiver_id}/{sender_id}/", response_model= schemas.Message)
def get_singleton(receiver_id: int, sender_id: int, db: Session = Depends(get_db)):
    return db.query(models.Message) \
        .filter(or_(and_(models.Message.reciver_id == receiver_id, models.Message.author_id == sender_id),
                    and_(models.Message.reciver_id == sender_id, models.Message.author_id == receiver_id))).order_by(models.Message.date.desc()).first()


@app.post('/user/messages/', response_model= schemas.Message)
async def create_message(message: schemas.MessageCreate, reciver: schemas.UserBase, db: Session = Depends(get_db)):
    db_reciver = db.query(models.User).filter(models.User.login == reciver.login).first()
    if not db_reciver:
        raise HTTPException(status_code=404, detail="User not found")
    if db_reciver.id in manager.active_connections:
        await manager.send_personal_message(f"new_message: {message.author_id}", db_reciver.id)
    if message.author_id in manager.active_connections:
        await manager.send_personal_message("new_message", message.author_id)
    if db_reciver.id == 13:
        await manager.broadcast("general")
    db_message = models.Message(**message.dict(), date=datetime.now(), reciver_id=db_reciver.id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.put("/message/{reciver}/read")
async def update_message_status(reciver: int, messages_ids: list, db: Session = Depends(get_db)):
    for m in messages_ids:
        if isinstance(m, int):
            message = db.query(models.Message).filter(models.Message.id == m).first()
            if message and message.reciver_id == reciver:
                message.is_recived = True
    db.commit()
    if reciver in manager.active_connections:
        await manager.send_personal_message("read", reciver)
    await manager.broadcast(f"read {reciver}")
    return status.HTTP_200_OK


@app.post("/message/{reciver}/{author}/unread")
def unread_messages_to_user_from(reciver: int, author: int, db: Session = Depends(get_db)):
    return db.query(models.Message) \
        .filter(and_(and_(models.Message.reciver_id == reciver, models.Message.author_id == author), not_(models.Message.is_recived))).count()

@app.get("/healthcheck")
def healthcheck():
    if isHealthy:
        return status.HTTP_200_OK
    else:
        raise HTTPException(status_code=500, detail="Unheathly")

@app.get("/unhealthy")
def setunhealthy():
    isHealthy = False
    return status.HTTP_200_OK

@app.get("/")
def read_root():
    return {"Hello": "World"}
