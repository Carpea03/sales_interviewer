import streamlit as st
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Streamlit app title and description
st.title("Chatbot Interviewer")
st.write("This chatbot will interview you and generate a compelling story based on your responses.")

# OpenAI API key (replace with your own)
openai.api_key = "YOUR_API_KEY"

# Function to generate chatbot response using OpenAI API
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    msg = MIMEMultipart()
    msg["From"] = "your_email@example.com"
    msg["To"] = recipient
    msg["Subject"] = "Chatbot Interview Transcript and Story"

    msg.attach(MIMEText(f"Interview Transcript:\n\n{transcript}\n\nGenerated Story:\n\n{story}"))

    server = smtplib.SMTP("smtp.example.com", 587)
    server.starttls()
    server.login("your_email@example.com", "your_email_password")
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
