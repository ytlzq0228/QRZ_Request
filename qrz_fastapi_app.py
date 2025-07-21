from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sys
import os
import asyncio

# Add path to QRZ_Request module
sys.path.append("/mnt/data/app")
from QRZ_Request import check_qrz_request

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

clients = set()

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
    import builtins
    original_print = print

    async def async_print(*args, **kwargs):
        msg = ' '.join(str(a) for a in args)
        await broadcast(msg)
        original_print(*args, **kwargs)

    try:
        builtins.print = lambda *a, **k: asyncio.create_task(async_print(*a, **k))
        result = check_qrz_request(username=username, password=password, qso_id=qso_id)
    except Exception as e:
        result = f"查询失败: {str(e)}"
    finally:
        builtins.print = original_print

    return templates.TemplateResponse("form.html", {
        "request": request,
        "username": username,
        "password": password,
        "qso_id": qso_id,
        "result": result
    })

if __name__ == "__main__":
    uvicorn.run("qrz_fastapi_app:app", host="0.0.0.0", port=8000, reload=True)