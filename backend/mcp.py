from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
import secrets
import time

app = FastAPI()
_sessions: Dict[str, Dict] = {}

class HandshakeRequest(BaseModel):
    client_id: str

class CommandRequest(BaseModel):
    command: str
    params: Optional[dict] = None

def get_current_session(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    session = _sessions.get(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return session

@app.get("/")
async def root():
    return {"service": "fastmcp", "version": "0.1.0", "uptime": int(time.time())}

@app.post("/handshake")
async def handshake(req: HandshakeRequest):
    token = secrets.token_urlsafe(24)
    _sessions[token] = {"client_id": req.client_id, "created_at": int(time.time())}
    return {"token": token, "client_id": req.client_id}

@app.post("/command")
async def command(req: CommandRequest, session: dict = Depends(get_current_session)):
    return {"client_id": session["client_id"], "echo": req.command, "params": req.params or {}, "received_at": int(time.time())}

@app.get("/sessions")
async def list_sessions(session: dict = Depends(get_current_session)):
    return {"your_client": session["client_id"], "active_sessions": len(_sessions)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    token = None
    try:
        await websocket.send_json({"msg": "send_token"})
        data = await websocket.receive_json()
        token = data.get("token")
        if not token or token not in _sessions:
            await websocket.send_json({"error": "unauthorized"})
            await websocket.close(code=1008)
            return
        await websocket.send_json({"msg": f"welcome { _sessions[token]['client_id'] }"})
        while True:
            payload = await websocket.receive_text()
            await websocket.send_text(f"mcp:{payload}")
    except WebSocketDisconnect:
        return

if __name__ == "__main__":
    uvicorn.run("mcp:app", host="127.0.0.1", port=8765, log_level="info")