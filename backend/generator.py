import os
import google.generativeai as genai
from dotenv import load_dotenv
from backend.utils import save_upload_file, render_latex, run_pdflatex

load_dotenv()

def generate_pdf(event_name, event_date, event_time, event_location, description, logo, images):
    os.makedirs("output", exist_ok=True)

    # === Save logo ===
    logo_path = ""
    if logo:
        print("Saving logo...")
        logo_path = save_upload_file(logo, "logo.png")
        print(f"Logo saved at: {logo_path}")
    logo_filename = os.path.basename(logo_path) if logo_path else ""

    # === Save images ===
    image_paths = []
    if images:
        print("Saving uploaded images...")
        for i, img in enumerate(images):
            print(f"Saving image {i + 1}")
            path = save_upload_file(img, f"photo_{i+1}.jpg")
            print(f"Saved image to: {path}")
            image_paths.append(path)
    image_path = image_paths[0] if image_paths else ""
    image_filename = os.path.basename(image_path) if image_path else ""
    print(f"Using image in LaTeX: {image_filename}")

    # === Gemini API Setup ===
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file or environment variable.")
    genai.configure(api_key=api_key)

    # === Generate content ===
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

    # === Render LaTeX ===
    latex_code = render_latex(
     event_name=event_name,
     event_date=event_date,
     event_time=event_time,
     event_location=event_location,
     event_description=content,  # ✅ Use correct argument name
     logo_path=logo_filename,
     image_path=image_filename
)


    # === Save .tex file ===
    tex_path = "output/event_report.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)
    print(f"LaTeX code saved to {tex_path}")


    print("\n====== GENERATED LaTeX CODE ======")
    print(latex_code)
    print("==================================\n")


    # === Compile PDF ===
    try:
        run_pdflatex(tex_path)
        print("PDF successfully generated.")
    except Exception as e:
        print("PDF generation failed:", e)
        raise

    output_path = "output/event_report.pdf"
    if not os.path.exists(output_path):
        raise FileNotFoundError("PDF was not generated. Check LaTeX syntax or pdflatex logs.")

    # === Clean auxiliary files ===
    for ext in [".aux", ".log", ".out"]:
        aux_file = tex_path.replace(".tex", ext)
        if os.path.exists(aux_file):
            os.remove(aux_file)

    return output_path, tex_path
