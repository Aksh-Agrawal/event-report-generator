import os
import subprocess
import re

def escape_latex(text):
    """Escape special LaTeX characters so the PDF doesn't break."""
    if not text:
        return ""
    return re.sub(r'([&%$#_{}~^\\])', r'\\\1', text)


def save_upload_file(uploaded_file, filename):
    """Save uploaded file to output directory and return full path."""
    os.makedirs("output", exist_ok=True)  # Ensure output directory exists
    output_path = os.path.join("output", filename)
    with open(output_path, "wb") as f:
        f.write(uploaded_file.read())
    return output_path


def render_latex(event_name, event_date, event_time, event_location, event_description, logo_path, image_path):
    """Return LaTeX code string with filled-in event details."""
    return f"""
\\documentclass{{article}}
\\usepackage{{graphicx}}
\\usepackage{{geometry}}
\\usepackage{{titling}}
\\usepackage{{parskip}}
\\usepackage{{setspace}}

\\geometry{{margin=1in}}
\\setlength{{\\droptitle}}{{-4em}}
\\setstretch{{1.2}}

\\begin{{document}}

% Header with logo and event name
\\begin{{center}}
    \\includegraphics[width=0.3\\textwidth]{{{logo_path}}}\\\\[0.5cm]
    {{\\LARGE \\textbf{{{escape_latex(event_name)}}}}}\\\\[0.3cm]
    \\normalsize
    \\textbf{{Date:}} {escape_latex(event_date)} \\\\
    \\textbf{{Time:}} {escape_latex(event_time)} \\\\
    \\textbf{{Location:}} {escape_latex(event_location)}
\\end{{center}}

\\vspace{{1cm}}

{escape_latex(event_description)}

\\vspace{{1cm}}

% Main Event Image
\\begin{{center}}
    \\includegraphics[width=0.5\\textwidth]{{{image_path}}}
\\end{{center}}

\\end{{document}}
"""


def run_pdflatex(tex_file_path):
    output_dir = os.path.dirname(tex_file_path)
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", output_dir, tex_file_path],
            check=True,
            capture_output=True,
            text=True  # for readable output
        )
    except subprocess.CalledProcessError as e:
        print("----- LaTeX Compilation Output -----")
        print(e.stdout)
        print("----- LaTeX Compilation Error -----")
        print(e.stderr)
        raise RuntimeError("PDF compilation failed.") from e

