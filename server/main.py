# server/main.py

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from server.model_predict import predict_email

app = FastAPI()

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )


@app.post("/scan", response_class=HTMLResponse)
async def scan_email(
    request: Request,
    email_file: UploadFile = File(...)
):
    try:
        result = predict_email(email_file)

        return templates.TemplateResponse(
            "warning_template.html",
            {
                "request": request,
                "label": result["label"],
                "risk": result["risk_percent"],
                "features": result["features"]
            }
        )

    except Exception as e:
        return HTMLResponse(
            content=f"<h3 style='color:red'>Error: {str(e)}</h3>",
            status_code=500
        )
