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

# Meeting Duration Selection
st.header("Meeting Duration")
duration_options = {
    "15 minutes": 15,
    "30 minutes": 30,
    "45 minutes": 45,
    "1 hour": 60,
    "1.5 hours": 90,
    "2 hours": 120,
    "2.5 hours": 150,
    "3 hours": 180,
    "Custom": "custom"
}

selected_duration = st.selectbox(
    "How long do you want the meeting to be?",
    options=list(duration_options.keys()),
    index=1  # Default to 30 minutes
)

# Custom duration input if selected
meeting_duration_minutes = None
if selected_duration == "Custom":
    custom_duration = st.number_input(
        "Enter custom duration (in minutes):",
        min_value=5,
        max_value=480,  # 8 hours max
        value=60,
        step=5,
        help="Enter the meeting duration in minutes (5-480 minutes)"
    )
    meeting_duration_minutes = custom_duration
else:
    meeting_duration_minutes = duration_options[selected_duration]

# Display selected duration
st.info(f"Selected meeting duration: {meeting_duration_minutes} minutes")

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
        
        # Payload - emails should be a list, now including session time
        payload = {
            "behavior_prompt": behavior_prompt,
            "roadmap": roadmap_content,
            "emails": emails_list,  # Now sending as a list
            "voice_id": selected_lang_code,  # Add language code
            "session_time": meeting_duration_minutes  # Add session time in minutes
        }
        
        # API call
        endpoint = "https://solution-advisor.cloudjiffy.net/"
        # endpoint = "http://127.0.0.1:8000/"
        try:
            response = requests.post(endpoint, json=payload)
            if response.status_code == 200:
                data = response.json()
                room_url = data.get("room_url")
                
                if room_url:
                    st.success("✅ Connected! You can now join the room.")
                    
                    # Large Join Button
                    join_button_html = f'''
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{room_url}" target="_blank" style="
                            display: inline-block;
                            background: linear-gradient(45deg, #28a745, #20c997);
                            color: white;
                            padding: 15px 40px;
                            border-radius: 50px;
                            text-decoration: none;
                            font-weight: bold;
                            font-size: 18px;
                            box-shadow: 0 8px 25px rgba(40,167,69,0.3);
                            transition: all 0.3s ease;
                        ">
                            🚀 JOIN MEETING NOW
                        </a>
                    </div>
                    '''
                    st.markdown(join_button_html, unsafe_allow_html=True)
                    
                    # Clean and Simple Copy Section
                    st.subheader("📋 Meeting Link")
                    
                    # Display link in text input for easy copying
                    st.text_input("Copy this link:", value=room_url, key="meeting_url", help="Click in the box and press Ctrl+A then Ctrl+C to copy")
                    
                    # Simple Copy Button using Streamlit components
                    copy_html = f'''
                    <div style="margin: 10px 0;">
                        <button onclick="copyToClipboard()" style="
                            background-color: #ff4b4b;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 6px;
                            cursor: pointer;
                            font-weight: bold;
                            font-size: 14px;
                        ">
                            📋 Copy Meeting Link
                        </button>
                        <span id="copyMessage" style="margin-left: 10px; color: green; display: none;">✅ Copied!</span>
                    </div>
                    
                    <script>
                    function copyToClipboard() {{
                        var copyText = "{room_url}";
                        navigator.clipboard.writeText(copyText).then(function() {{
                            document.getElementById('copyMessage').style.display = 'inline';
                            setTimeout(function() {{
                                document.getElementById('copyMessage').style.display = 'none';
                            }}, 2000);
                        }}).catch(function() {{
                            alert('Please copy the link manually from the text box above');
                        }});
                    }}
                    </script>
                    '''
                    st.markdown(copy_html, unsafe_allow_html=True)
                    
                    # Alternative: Use columns for better layout
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.info(f"🕒 Meeting Duration: {meeting_duration_minutes} minutes")
                    with col2:
                        st.info(f"🗣️ Voice: {selected_language.strip()}")
                    
                    # Instructions
                    st.markdown("### 💡 Instructions:")
                    st.markdown("1. **Click the green button** to join the meeting directly")
                    st.markdown("2. **Copy the link** using the copy button or manually from the text box")
                    st.markdown("3. **Share the link** with other participants")
                    
                else:
                    st.error("❌ Room URL not found in the response.")
            else:
                st.error(f"❌ Error: Unable to connect. Status Code: {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
