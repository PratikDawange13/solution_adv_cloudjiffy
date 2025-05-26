import streamlit as st
import requests
import PyPDF2
import docx
from io import BytesIO

# Title and Description
st.title("Solution Advisor")
st.write("Input your Behavior Prompt and Roadmap to start talking with the AI chatbot!")

# Layout: Two Columns
col1, col2 = st.columns(2)

with col1:
    st.header("Behavior Prompt")
    behavior_prompt = st.text_area("Enter your prompt here:", placeholder="E.g., Explain AI adoption challenges")

with col2:
    st.header("Roadmap")
    roadmap_text = st.text_area("Enter your roadmap here:", placeholder="E.g., Timeline, milestones, etc.")
    uploaded_file = st.file_uploader("Upload Roadmap File (Optional)", type=["txt", "pdf", "docx"])

# Email field (now required by the API)
st.header("Email Information")
emails_input = st.text_input("Enter email address(es):", placeholder="your-email@example.com")
st.write("*Note: For multiple emails, separate with commas*")

# Language Selection
st.header("Language Selection")
language_options = {
    "Ava ": "en-US-AvaMultilingualNeural",
    "Andrew ": "en-US-AndrewMultilingualNeural",
    "Aarav ": "en-IN-AaravNeural",
    "Aashi ": "en-IN-AashiNeural",
    "Ezinne ": "en-NG-EzinneNeural",
    "Abeo ": "en-NG-AbeoNeural"
}

selected_language = st.selectbox(
    "Choose a language and voice:",
    options=list(language_options.keys()),
    index=0  # Default to first option
)

# Function to extract text from uploaded files
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode('utf-8', errors='ignore')
    elif uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(BytesIO(uploaded_file.read()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    else:
        return "Unsupported file format."

# Submit Button
if st.button("Submit"):
    # Handle file upload if provided
    roadmap_content = ""
    if uploaded_file:
        try:
            roadmap_content = extract_text_from_file(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            roadmap_content = ""
    elif roadmap_text:
        roadmap_content = roadmap_text
    
    # Check if necessary fields are filled
    if not behavior_prompt:
        st.warning("Please enter a Behavior Prompt.")
    elif not roadmap_content:
        st.warning("Please enter or upload a Roadmap.")
    elif not emails_input:
        st.warning("Please enter an email address.")
    else:
        # Process emails - convert to list format
        emails_list = [email.strip() for email in emails_input.split(',') if email.strip()]
        
        # Get selected language code
        selected_lang_code = language_options[selected_language]
        
        # Get selected language code
        selected_lang_code = language_options[selected_language]
        
        # Payload - emails should be a list
        payload = {
            "behavior_prompt": behavior_prompt,
            "roadmap": roadmap_content,
            "emails": emails_list,  # Now sending as a list
            "voice_id": selected_lang_code  # Add language code
        }
        
        # API call
        endpoint = "https://sol-advisor.cloudjiffy.net/"
        try:
            response = requests.post(endpoint, json=payload)
            if response.status_code == 200:
                data = response.json()
                room_url = data.get("room_url")
                
                if room_url:
                    st.success("Connected! You can now join the room.")
                    st.markdown(f"[Join Now]({room_url})", unsafe_allow_html=True)
                else:
                    st.error("Room URL not found in the response.")
            else:
                st.error(f"Error: Unable to connect. Status Code: {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")