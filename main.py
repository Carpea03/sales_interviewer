import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import anthropic

# Streamlit app title and description
st.title("Chatbot Interviewer")
st.write("This chatbot will interview you and generate a compelling story based on your responses.")

# Anthropic API key (stored as a Streamlit secret)
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]

# Email credentials (stored as Streamlit secrets)
email_user = st.secrets["EMAIL_USER"]
email_password = st.secrets["EMAIL_PASSWORD"]
email_server = st.secrets["EMAIL_SERVER"]
email_port = st.secrets["EMAIL_PORT"]

# Initialize Anthropic client
anthropic = Anthropic(api_key=anthropic_api_key)

# Function to generate chatbot response using Anthropic API
def generate_response(prompt):
    response = anthropic.completions.create(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        max_tokens_to_sample=4000,
        model="claude-3-opus-20240229",
    )
    return response.completion.strip()

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = recipient
    msg["Subject"] = "Chatbot Interview Transcript and Story"

    msg.attach(MIMEText(f"Interview Transcript:\n\n{transcript}\n\nGenerated Story:\n\n{story}"))

    server = smtplib.SMTP(email_server, email_port)
    server.starttls()
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()

# Chatbot interview loop
def interview():
    st.write("Chatbot: Hello! I'm here to interview you. Let's start!")
    transcript = ""
    while True:
        user_input = st.text_input("You: ")
        if user_input.lower() in ["quit", "exit", "done"]:
            break
        transcript += f"You: {user_input}\n"
        prompt = f"{transcript}\nChatbot:"
        response = generate_response(prompt)
        transcript += f"Chatbot: {response}\n"
        st.write(f"Chatbot: {response}")

    story = generate_response(f"Based on the following interview transcript, write a compelling story about the interviewee:\n\n{transcript}")
    st.write(f"\nGenerated Story:\n{story}")

    recipient_email = st.text_input("Enter your email address to receive the transcript and story:")
    if st.button("Send Email"):
        send_email(transcript, story, recipient_email)
        st.write("Email sent successfully!")

# Run the chatbot interview
if __name__ == "__main__":
    interview()