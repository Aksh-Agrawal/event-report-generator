from flask import Flask, request, send_file
import os
import subprocess

app = Flask(__name__)

@app.route("/compile", methods=["POST"])
def compile_pdf():
    if "tex_file" not in request.files:
        return {"error": "No LaTeX file provided."}, 400

    tex_file = request.files["tex_file"]
    os.makedirs("output", exist_ok=True)
    tex_path = os.path.join("output", "event_report.tex")
    pdf_path = os.path.join("output", "event_report.pdf")

    tex_file.save(tex_path)

    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory=output", tex_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20
        )

        if result.returncode != 0 or not os.path.exists(pdf_path):
            return {
                "error": "pdflatex failed.",
                "stdout": result.stdout.decode(),
                "stderr": result.stderr.decode()
            }, 500

        return send_file(pdf_path, as_attachment=True)

    except subprocess.TimeoutExpired:
        return {"error": "pdflatex compilation timed out."}, 500
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
