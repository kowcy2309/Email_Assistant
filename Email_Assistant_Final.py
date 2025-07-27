import os
import streamlit as st
import openai
import json
from dotenv import load_dotenv
import pyperclip

# Load environment variables
load_dotenv()
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = "https://genai-trigent-openai.openai.azure.com/"
openai.api_version = "2024-02-15-preview"


logo_path = "https://trigent.com/wp-content/uploads/Trigent_Axlr8_Labs.png"
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{logo_path}" alt="Trigent Logo" style="max-width:100%;">
    </div>
    """,
    unsafe_allow_html=True
)


# Path to the JSON file where signatures will be stored
SIGNATURES_FILE = 'signatures.json'

# Load signatures from the JSON file
def load_signatures():
    if os.path.exists(SIGNATURES_FILE):
        with open(SIGNATURES_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save signatures to the JSON file
def save_signatures(signatures):
    with open(SIGNATURES_FILE, 'w') as f:
        json.dump(signatures, f)

# Initialize session state variables
if 'signatures' not in st.session_state:
    st.session_state.signatures = load_signatures()

if 'email_text' not in st.session_state:
    st.session_state.email_text = ""
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'response_done' not in st.session_state:
    st.session_state.response_done = False
if 'customized_response' not in st.session_state:
    st.session_state.customized_response = ""
if 'sentiment' not in st.session_state:
    st.session_state.sentiment = None
if 'context_analysis' not in st.session_state:
    st.session_state.context_analysis = ""
if 'save_success_message' not in st.session_state:
    st.session_state.save_success_message = ""
if 'delete_success_message' not in st.session_state:
    st.session_state.delete_success_message = ""
if 'alert_message' not in st.session_state:
    st.session_state.alert_message = ""
if 'manage_signatures' not in st.session_state:
    st.session_state.manage_signatures = False
if 'show_finalized_email_button' not in st.session_state:
    st.session_state.show_finalized_email_button = False
if 'selected_signature' not in st.session_state:
    st.session_state.selected_signature = ""

# Function to analyze email content
def analyze_email_content(email_text):
    context_prompt = [
        {"role": "system", "content": "You are an assistant that helps analyze emails."},
        {"role": "user", "content": f"Analyze the following email and extract the main request, topic, urgency, and (in the format 'Sentiment: POSITIVE/NEGATIVE/NEUTRAL'). Provide a detailed analysis and print all heading other than detailed analysis. {email_text}"}
    ]
    
    try:
        context_response = openai.ChatCompletion.create(
            model="gpt-4",
            deployment_id="gpt-4o",
            messages=context_prompt,
            max_tokens=400 
        )
        
        context_analysis = context_response['choices'][0]['message']['content'].strip()
        
        sentiment = None
        sentiment_lines = [line for line in context_analysis.splitlines() if line.startswith("Sentiment:")]

        if sentiment_lines:
            sentiment_line = sentiment_lines[0]
            sentiment_parts = sentiment_line.split(':', 1)
            if len(sentiment_parts) > 1:
                sentiment_data = sentiment_parts[1].strip()
                if sentiment_data:
                    sentiment_label = sentiment_data.split('(', 1)[0].strip()
                    sentiment = {"label": sentiment_label}
                    context_analysis = context_analysis.replace(sentiment_line, '').strip()
                else:
                    context_analysis = context_analysis.replace(sentiment_line, '').strip()
        
        return sentiment, context_analysis

    except Exception as e:
        st.error(f"An error occurred while analyzing email content: {e}")
        return None, "Error analyzing content"

def generate_response(context_analysis, tone):
    response_prompt = [
        {"role": "system", "content": "You are an assistant that helps generate email responses."},
        {"role": "user", "content": f"Write a reply to the following email based on this context. Tone: {tone} Context: {context_analysis}"}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            deployment_id="gpt-4o",
            messages=response_prompt,
            max_tokens=400 
        )
        
        email_response = response['choices'][0]['message']['content'].strip()
        return email_response
    
    except Exception as e:
        st.error(f"An error occurred while generating the email response: {e}")
        return "Error generating response"

def analyze():
    if st.session_state.email_text.strip():  
        if not st.session_state.analysis_done: 
            st.session_state.sentiment, st.session_state.context_analysis = analyze_email_content(st.session_state.email_text)
            st.session_state.analysis_done = True
    else:
        st.warning("Please enter the content of the email before analyzing.")

def delete_signature(name):
    if name in st.session_state.signatures:
        del st.session_state.signatures[name]
        save_signatures(st.session_state.signatures)
        st.session_state.signatures = load_signatures()  
        st.session_state.delete_success_message = f"Signature '{name}' has been successfully deleted."
        st.session_state.save_success_message = "" 
        st.session_state.manage_signatures = False  
        st.rerun()  
    else:
        st.warning(f"Signature '{name}' not found.")

# Function to add or update a signature
def add_signature(name, content):
    if name and content:
        formatted_content = content.strip()
        st.session_state.signatures[name] = formatted_content
        save_signatures(st.session_state.signatures)
        st.session_state.signatures = load_signatures()  
        st.session_state.save_success_message = f"Signature '{name}' added/updated successfully."
        st.session_state.delete_success_message = ""  
        st.session_state.manage_signatures = False  
        st.session_state.manage_signature_name = ""  
        st.session_state.manage_signature_content = ""  
        st.session_state.signature = "" 
        st.rerun()  
    else:
        st.warning("Please provide both a name and content for the signature.")


st.title("Email Assistant")
st.caption("This application is designed to help users quickly generate personalized email responses by utilizing natural language understanding (NLU) to interpret the context and content of emails. By analyzing the nuances and details of each email, it ensures that the generated responses are relevant, coherent, and tailored to the specific situation. This tool significantly enhances communication efficiency, making it especially valuable for business professionals and customer support teams who need to manage high volumes of email correspondence. By reducing the time spent on crafting individual replies, users can focus more on strategic tasks and improve overall productivity.")



st.subheader("Email Content")
st.session_state.email_text = st.text_area("Paste the content of the received email here:", value=st.session_state.email_text, height=150)


analyze_button = st.button("Analyze")
if analyze_button:
    with st.spinner("Analyzing email content..."):
        analyze()

if st.session_state.analysis_done and st.session_state.context_analysis:
    st.subheader("Email Analysis")
    if st.session_state.sentiment:
        st.write(f"Sentiment: {st.session_state.sentiment['label']}")
    st.write(st.session_state.context_analysis)

    
    st.subheader("Preferred Tone")
    st.session_state.tone = st.radio(
        "Choose the preferred tone for responses",
        ["Formal", "Casual", "Professional","spartan"],
        key="tone_radio"  
    )

    # st.subheader("Additional Instructions")
    # additional_instructions = st.text_input("Provide any additional instructions for the email response (e.g., 'Generate a 100-word response')", key="additional_instructions")


    generate_response_button = st.button("Generate Response", key="generate_response_button")

    if generate_response_button:
        with st.spinner("Generating response..."):
            st.session_state.generated_response = generate_response(st.session_state.context_analysis, st.session_state.tone)
            st.session_state.response_done = True

# Display the generated email response
if st.session_state.response_done:
    st.subheader("Generated Email Response")
    st.markdown(st.session_state.generated_response)

    # Button to customize the email
    if st.button("Customize Email", key="customize_email_button"):
        st.session_state.customized_response = st.session_state.generated_response
        st.session_state.show_customization = True
        st.session_state.show_finalized_email_button = True  # Show the Finalized Email button


if 'show_customization' in st.session_state and st.session_state.show_customization:
    st.subheader("Customize Your Response")
    st.session_state.customized_response = st.text_area(
        "Make any final adjustments to the response below:",
        value=st.session_state.customized_response,
        height=150,
        key="customized_response_area"  
    )


    st.subheader("Select Signature")
    signature_names = list(st.session_state.signatures.keys())
    signature_selection = st.selectbox("Choose a signature", signature_names, key="signature_selectbox")
    st.session_state.selected_signature = st.session_state.signatures.get(signature_selection, "")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Delete Selected Signature", key="delete_signature_button"):
            if signature_selection:
                delete_signature(signature_selection)
    with col2:
        if st.button("Manage Signatures", key="manage_signatures_button"):
            st.session_state.manage_signatures = not st.session_state.manage_signatures

    if st.session_state.manage_signatures:
        st.subheader("Manage Signatures")

        signature_name = st.text_input("Signature Name", value=st.session_state.get('manage_signature_name', ""), key="signature_name_input")
        signature_content = st.text_area("Signature Content", value=st.session_state.get('manage_signature_content', ""), height=100, key="signature_content_input")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Signature", key="save_signature_button"):
                add_signature(signature_name, signature_content)
        with col2:
            if st.button("Clear Signature Fields", key="clear_signature_fields_button"):
                st.session_state.manage_signature_name = ""
                st.session_state.manage_signature_content = ""
                st.session_state.signature = ""

if st.session_state.save_success_message:
    st.success(st.session_state.save_success_message)
    st.session_state.save_success_message = ""  

if st.session_state.delete_success_message:
    st.success(st.session_state.delete_success_message)
    st.session_state.delete_success_message = ""  
if st.session_state.alert_message:
    st.warning(st.session_state.alert_message)

# Show Finalized Email button if it should be visible
if st.session_state.show_finalized_email_button:
    if st.button("Finalized Email", key="finalized_email_button"):
        # Combine the customized response with the selected signature
        if st.session_state.selected_signature:
            # Remove any existing signature from the customized response before appending
            signature_lines = st.session_state.selected_signature.strip().splitlines()
            if st.session_state.customized_response.endswith(st.session_state.selected_signature):
                st.session_state.customized_response = st.session_state.customized_response.rstrip(st.session_state.selected_signature).rstrip('\n\n')
            
            # Append the signature to the customized response
            finalized_email = st.session_state.customized_response + "\n\n" + st.session_state.selected_signature
        else:
            finalized_email = st.session_state.customized_response
        
        # Save the finalized email in session state
        st.session_state.finalized_email = finalized_email

        # Display the Copy to Clipboard button
        st.session_state.show_copy_button = True

# Re-display the finalized email and Copy to Clipboard button after success
if st.session_state.get('finalized_email', False):
    st.subheader("Finalized Email")
    st.write(st.session_state.finalized_email.replace("\n", "  \n"))

    if st.session_state.get('show_copy_button', False):
        if st.button("Copy to Clipboard", key="copy_to_clipboard_button_redisplay"):
            pyperclip.copy(st.session_state.finalized_email)           
            st.success("Finalized email copied to clipboard!")

footer_html = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<div style="text-align: center;">
    <p>
        Copyright © 2024 | <a href="https://trigent.com/ai/" target="_blank" aria-label="Trigent Website">Trigent Software Inc.</a> All rights reserved. |
        <a href="https://www.linkedin.com/company/trigent-software/" target="_blank" aria-label="Trigent LinkedIn"><i class="fab fa-linkedin"></i></a> |
        <a href="https://www.twitter.com/trigentsoftware/" target="_blank" aria-label="Trigent Twitter"><i class="fab fa-twitter"></i></a> |
        <a href="https://www.youtube.com/channel/UCNhAbLhnkeVvV6MBFUZ8hOw" target="_blank" aria-label="Trigent Youtube"><i class="fab fa-youtube"></i></a>
    </p>
</div>
"""

# Custom CSS to make the footer sticky
footer_css = """
<style>
.footer {
    position: fixed;
    z-index: 1000;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    color: black;
    text-align: center;
}
[data-testid="stSidebarNavItems"] {
    max-height: 100%!important;
}
[data-testid="collapsedControl"] {
            display: none;
}
</style>
"""

# Combining the HTML and CSS
footer = f"{footer_css}<div class='footer'>{footer_html}</div>"
st.markdown(footer, unsafe_allow_html=True)
