# server/main.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from server.modules.extract_email import extract_email_fields
from server.model_predict import predict_email

app = FastAPI()

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload-email", response_class=HTMLResponse)
async def upload_email(request: Request, email_file: UploadFile = File(...)):
    raw = (await email_file.read()).decode("utf-8", errors="ignore")
    fields = extract_email_fields(raw)

    full_text = f"{fields['subject']} {fields['from']} {fields['body']}"

    result = predict_email(full_text)

    return templates.TemplateResponse(
        "warning_template.html",
        {
            "request": request,
            "result": result,
            "subject": fields["subject"],
        },
    )
