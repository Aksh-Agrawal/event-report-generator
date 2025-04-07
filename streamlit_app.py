import streamlit as st
import base64
import requests

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

# External Flask API endpoint (change if hosted elsewhere)
API_URL = "http://localhost:5000/generate"

# Generate report
if st.button("Generate Report"):
    if not all([event_name, event_location, event_date, event_time, description, logo, photo]):
        st.warning("Please fill in all fields and upload both images.")
    else:
        with st.spinner("Generating PDF via API..."):
            files = {
                "logo": logo,
                "photo": photo,
            }
            data = {
                "event_name": event_name,
                "event_date": str(event_date),
                "event_time": event_time,
                "event_location": event_location,
                "description": description,
            }

            try:
                response = requests.post(API_URL, data=data, files=files)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to generate report: {e}")
                st.stop()

            result = response.json()
            pdf_bytes = base64.b64decode(result["pdf"])
            tex_bytes = base64.b64decode(result["tex"])

            st.success("✅ Report generated successfully!")

            # Download buttons
            st.download_button("📥 Download PDF", pdf_bytes, file_name="event_report.pdf", mime="application/pdf")
            st.download_button("📄 Download LaTeX (.tex)", tex_bytes, file_name="event_report.tex", mime="text/x-tex")

            # LaTeX code view
            with st.expander("🔍 View LaTeX Code"):
                st.code(tex_bytes.decode("utf-8"), language="latex")

            # PDF preview
            st.markdown("### 👀 Preview")
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600px"></iframe>',
                unsafe_allow_html=True
            )
