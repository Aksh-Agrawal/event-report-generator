import streamlit as st
import base64
from backend.generator import generate_pdf

st.set_page_config(page_title="Event Report Generator", layout="centered")
st.title("📄 Event Report Generator")

# Input fields
event_name = st.text_input("Event Name")
event_location = st.text_input("Location")
event_time = st.text_input("Time of Event")
event_date = st.date_input("Date of Event")
description = st.text_area("Event Description")

logo = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
photo = st.file_uploader("Upload Event Photo", type=["png", "jpg", "jpeg"])

# Generate report
if st.button("Generate Report"):
    if not all([event_name, event_location, event_date, event_time, description, logo, photo]):
        st.warning("Please fill in all fields and upload both images.")
    else:
        with st.spinner("Generating PDF..."):
            pdf_path, tex_path = generate_pdf(
                event_name, str(event_date), event_time, event_location,
                description, logo, [photo]  # ensure 'photo' is wrapped in a list
            )

            st.success("✅ Report generated successfully!")

         # PDF Download Button
            with open(pdf_path, "rb") as pdf_file:
                st.download_button("📥 Download PDF", pdf_file, file_name="event_report.pdf", mime="application/pdf")

          # Optional: Show .tex content
            with open(tex_path, "r", encoding="utf-8") as tex_file:
                tex_code = tex_file.read()
                st.download_button("📄 Download LaTeX (.tex)", tex_file, file_name="event_report.tex", mime="text/x-tex")
                with st.expander("🔍 View LaTeX Code"):
                    st.code(tex_code, language="latex")

        # PDF preview in app
        with open(pdf_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
            st.markdown("### 👀 Preview")
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600px"></iframe>',
                unsafe_allow_html=True
            )
