from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sys
import os

# Add path to QRZ_Request module
sys.path.append("/mnt/data/app")
from QRZ_Request import check_qrz_request  # 假设函数是这样命名的

app = FastAPI()

# 挂载静态文件和模板目录
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "result": None})

@app.post("/", response_class=HTMLResponse)
async def post_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    qso_id: str = Form(...)
):
    try:
        result = query_qrz_by_qso_id(qso_id, username=username, password=password)
    except Exception as e:
        result = f"查询失败: {str(e)}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "qso_id": qso_id,
        "username": username,
        "password": password,
        "result": result
    })
# 启动命令（使用时运行）：
# uvicorn qrz_fastapi_app:app --reload --host 0.0.0.0 --port 8000