import streamlit as st
import requests
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(
    page_title="ClearLease Contract Analyzer",
    page_icon="📄",
    layout="centered"
)

# 2. App Header & Description
st.title("📄 ClearLease Contract Analyzer")
st.markdown("""
Upload a photo or scan of a rental agreement. Our AI will analyze the dense legal text 
and extract the most critical clauses and hidden traps for you.
""")
st.divider()

# 3. File Uploader UI
uploaded_file = st.file_uploader(
    "Upload Lease Agreement (JPG, PNG)", 
    type=["jpg", "jpeg", "png"]
)

# Display the uploaded image as a preview
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Document Preview", use_container_width=True)

# 4. The Trigger Button
if st.button("Analyze Contract", type="primary"):
    if uploaded_file is None:
        st.error("Please upload a document first.")
    else:
        # Show a loading spinner while the backend and AI do the work
        with st.spinner("Analyzing legal clauses with Gemini 1.5 Pro..."):
            try:
                # Prepare the image file to be sent over HTTP POST to our Flask backend
                # Note: We assume Flask will be running on port 5000 locally
                files = {"document": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                flask_url = "http://127.0.0.1:5000/analyze"
                
                # Send the request to the backend
                response = requests.post(flask_url, files=files)
                
                # 5. Handle the Backend Response
                if response.status_code == 200:
                    result_data = response.json()
                    
                    st.success("Analysis Complete & Saved to Database!")
                    
                    # Display the extracted 5-point summary
                    st.subheader("Extracted Contract Summary")
                    st.json(result_data.get("summary", {}))
                    
                    # Display the database confirmation
                    st.info(f"Database Record ID: {result_data.get('db_id', 'Unknown')}")
                    
                else:
                    st.error(f"Error from backend: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is your Flask server running?")