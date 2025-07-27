# Email_Assistant
AI-powered Email Assistant built with Streamlit and Azure OpenAI. It analyzes emails for sentiment, urgency, and intent, then generates context-aware responses in selected tones. Includes signature management, customization, and clipboard copy features to streamline professional communication.

Use Case Description: AI-Powered Email Assistant with Signature Management
This Email Assistant is a Streamlit-based AI-powered web application designed to analyze and respond to incoming email content using Azure OpenAI (GPT-4) services. The application enhances productivity for business professionals and customer support teams by automating email understanding and reply generation.

✅ Key Features & Functionalities:
Email Context Analysis

Extracts the main topic, request, urgency, and determines the sentiment (Positive/Negative/Neutral) from the email content using GPT-4.

Presents a detailed analysis to help the user understand the tone and purpose of the email.

AI-Powered Response Generation

Based on the analyzed context and selected tone (Formal, Casual, Professional, Spartan), the assistant generates a relevant and well-structured email reply using GPT-4.

Interactive Customization

Users can review and customize the generated response through a rich text area before finalizing the email.

Signature Management System

Save, update, delete, and select from multiple email signatures.

Append selected signatures automatically to the final email.

Clipboard Integration

Finalized email can be copied directly to the clipboard for easy pasting into any email client.

Persistent Session State

Remembers user's text, responses, and signature settings across interactions using Streamlit's session_state.

User-Friendly UI

Includes branding (Trigent logo), structured layout, and a fixed footer with social media links.

Security & Environment Configuration

Uses python-dotenv to securely load API keys.

Connects to Azure OpenAI with specified deployment ID and version control.

💼 Business Value / Impact:
This tool reduces manual effort in email drafting, especially in high-volume scenarios like customer support, sales, or internal communication. By combining NLU with customizable templates and signatures, it ensures consistency, tone control, and time efficiency in professional communication.
