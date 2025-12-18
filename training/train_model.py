# server/main.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from server.modules.extract_email import extract_email_text
from server.model_predict import predict_email

app = FastAPI()

templates = Jinja2Templates(directory="server/templates")
app.mount("/static", StaticFiles(directory="server/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload-email", response_class=HTMLResponse)
async def upload_email(request: Request, file: UploadFile = File(...)):
    raw = await file.read()
    text = extract_email_text(raw)

    label, risk, reasons, prob, highlights = predict_email(text)

    template = "warning_template.html" if label == "PHISHING" else "safe_template.html"

    return templates.TemplateResponse(
        template,
        {
            "request": request,
            "label": label,
            "risk": risk,
            "prob": prob,
            "reasons": reasons,
            "highlights": highlights,
            "text": text[:8000],
        },
    )
