from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from server.modules.extract_email import extract_email_fields
from server.model_predict import predict_email
from server.quarantine import save_to_quarantine

app = FastAPI()

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload-email")
async def upload_email(email_file: UploadFile = File(...)):
    raw = (await email_file.read()).decode("utf-8", errors="ignore")

    fields = extract_email_fields(raw)

    subject = fields.get("subject", "")
    from_field = fields.get("from", "")
    body = fields.get("body", "")

    # ⬇⬇⬇ สำคัญมาก — ส่ง FULL TEXT เข้าโมเดล
    full_text = subject + "\n" + from_field + "\n" + body

    result = predict_email(full_text)

    if result == "phishing":
        save_to_quarantine(raw)
        return HTMLResponse(f"""
            <h2 style="color:red;">⚠ WARNING: Email appears to be PHISHING</h2>
            <p><b>Subject:</b> {subject}</p>

            <form action="/force-open" method="post">
                <input type="hidden" name="content" value="{raw.replace('"','\'')}">
                <button style="background-color:orange;padding:10px;">Read Anyway</button>
            </form>
        """)

    return HTMLResponse(f"""
        <h2 style="color:green;">✔ SAFE EMAIL</h2>
        <h3>{subject}</h3>
        <pre>{body}</pre>
    """)


@app.post("/force-open")
async def force_open(content: str = Form(...)):
    return HTMLResponse(f"""
        <h2 style="color:orange;">⚠ Viewing flagged email</h2>
        <pre>{content}</pre>
    """)


if __name__ == "__main__":
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)