import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from backend.utils import save_upload_file, render_latex

load_dotenv()

def generate_pdf(event_name, event_date, event_time, event_location, description, logo, images):
    os.makedirs("output", exist_ok=True)

    # === Save logo ===
    logo_path = ""
    if logo:
        logo_path = save_upload_file(logo, "logo.png")
    logo_filename = os.path.basename(logo_path) if logo_path else ""

    # === Save images ===
    image_paths = []
    if images:
        for i, img in enumerate(images):
            path = save_upload_file(img, f"photo_{i+1}.jpg")
            image_paths.append(path)
    image_path = image_paths[0] if image_paths else ""
    image_filename = os.path.basename(image_path) if image_path else ""

    # === Gemini API Setup ===
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file.")
    genai.configure(api_key=api_key)

    # === Generate content using Gemini ===
    model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
    prompt = f"""
    Write a formal and professional event report for the following details:

    Event Name: {event_name}
    Date: {event_date}
    Time: {event_time}
    Location: {event_location}
    Description: {description}

    The report should be structured in paragraphs and end with a positive conclusion.
    """
    response = model.generate_content(prompt)
    content = response.text.strip()

    # === Render LaTeX code ===
    latex_code = render_latex(
        event_name=event_name,
        event_date=event_date,
        event_time=event_time,
        event_location=event_location,
        event_description=content,
        logo_path=logo_filename,
        image_path=image_filename
    )

    # === Save .tex file ===
    tex_path = "output/event_report.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    # === Compile LaTeX via Flask API ===
    pdf_path = "output/event_report.pdf"
    try:
        with open(tex_path, "rb") as tex_file:
            response = requests.post("http://127.0.0.1:5000/compile", files={"tex_file": tex_file})

        if response.status_code == 200:
            with open(pdf_path, "wb") as f:
                f.write(response.content)
        else:
            raise RuntimeError(f"Failed to compile LaTeX via API. Status: {response.status_code}, Message: {response.text}")
    except Exception as e:
        raise RuntimeError(f"PDF generation failed: {e}")

    # === Clean auxiliary files ===
    for ext in [".aux", ".log", ".out"]:
        aux_file = tex_path.replace(".tex", ext)
        if os.path.exists(aux_file):
            os.remove(aux_file)

    return pdf_path, tex_path
