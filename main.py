import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(
    page_title="ClearLease Contract Analyzer",
    page_icon="📄",
    layout="centered"
)

st.title("📄 ClearLease Contract Analyzer")
st.markdown("""
Upload a photo or scan of a rental agreement. Our AI will analyze the dense legal text 
and extract the most critical clauses and hidden traps for you.
""")
st.divider()

uploaded_file = st.file_uploader(
    "Upload Lease Agreement (JPG, PNG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Document Preview", use_container_width=True)

if st.button("Analyze Contract", type="primary"):
    if uploaded_file is None:
        st.error("Please upload a document first.")
    else:
        with st.spinner("Analyzing legal clauses with Gemini 1.5 Pro..."):
            try:
                files = {"document": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                flask_url = "http://127.0.0.1:5000/analyze"
                
                response = requests.post(flask_url, files=files)
                
                if response.status_code == 200:
                    result_data = response.json()
                    
                    st.success("Analysis Complete & Saved to Database!")
                    
                    st.subheader("Extracted Contract Summary")
                    st.json(result_data.get("summary", {}))
                    
                    st.info(f"Database Record ID: {result_data.get('db_id', 'Unknown')}")
                    
                else:
                    st.error(f"Error from backend: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is your Flask server running?")