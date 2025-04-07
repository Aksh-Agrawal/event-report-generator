from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from generator import generate_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_event_report(
    event_name: str = Form(...),
    event_date: str = Form(...),
    event_time: str = Form(...),
    event_location: str = Form(...),
    event_description: str = Form(...),
    logo: UploadFile = None,
    image: UploadFile = None,
):
    pdf_path = await generate_pdf(event_name, event_date, event_time, event_location, event_description, logo, image)
    return {"pdf_url": f"/files/{pdf_path}"}
