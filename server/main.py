from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from server.modules.extract_email import extract_email_text
from server.model_predict import predict_email

app = FastAPI()
templates = Jinja2Templates(directory="server/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload-email", response_class=HTMLResponse)
async def upload_email(
    request: Request,
    email_file: UploadFile = File(...)
):
    raw = await email_file.read()
    text = extract_email_text(raw)

    label, risk, reasons, prob, highlights = predict_email(text)

    return templates.TemplateResponse(
        "warning_template.html",
        {
            "request": request,
            "label": label,
            "risk": round(risk * 100, 2),
            "reasons": reasons,
            "highlights": highlights,
            "content": text[:2000],
        },
    )
