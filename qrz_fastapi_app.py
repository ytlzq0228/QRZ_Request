from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sys
import os
import asyncio
import builtins

# Add path to QRZ_Request module
sys.path.append("/mnt/data/app")
from QRZ_Request import check_qrz_request

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

clients = set()
log_queue = asyncio.Queue()

# 替换全局 print 为写入 log_queue
original_print = print

def hooked_print(*args, **kwargs):
    msg = ' '.join(str(a) for a in args)
    try:
        asyncio.create_task(log_queue.put(msg))
    except RuntimeError:
        pass  # 在事件循环外不处理
    original_print(*args, **kwargs)

builtins.print = hooked_print

@app.on_event("startup")
async def start_log_dispatcher():
    async def dispatch_logs():
        while True:
            msg = await log_queue.get()
            await broadcast(msg)
    asyncio.create_task(dispatch_logs())

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "result": None})

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(websocket)

async def broadcast(message: str):
    disconnected = set()
    for client in clients:
        try:
            await client.send_text(message)
        except Exception:
            disconnected.add(client)
    clients.difference_update(disconnected)

@app.post("/", response_class=HTMLResponse)
async def post_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    qso_id: str = Form(...)
):
    try:
        result = check_qrz_request(username=username, password=password, qso_id=qso_id)
    except Exception as e:
        result = f"查询失败: {str(e)}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "username": username,
        "password": password,
        "qso_id": qso_id,
        "result": result
    })

if __name__ == "__main__":
    uvicorn.run("qrz_fastapi_app:app", host="0.0.0.0", port=8000, reload=True)