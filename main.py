import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic

st.title("Chatbot Interviewer")
st.write("This chatbot will interview you and generate a compelling story based on your responses.")

# Anthropic API key and email credentials (stored as Streamlit secrets)
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]
email_user = st.secrets["EMAIL_USER"]
email_password = st.secrets["EMAIL_PASSWORD"]
email_server = st.secrets["EMAIL_SERVER"]
email_port = st.secrets["EMAIL_PORT"]

# Validate static values immediately after they're defined
assert isinstance(anthropic_api_key, str), "API key must be a string"
assert isinstance(email_user, str), "Email user must be a string"
# Assertions for email_password, email_server, and email_port could be added here as needed

# Initialize Anthropic client
client = Anthropic(api_key=anthropic_api_key)

# Initialize 'conversation_history' in session_state if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "user", "content": "Hi"
        },
        {"role": "assistant", "content": "Hello! I'm an AI interviewer for the Guild of Entrepreneurs community. I'm excited to learn more about you and your entrepreneurial journey. Let's start with your personal background. Can you tell me a bit about yourself and what led you to become an entrepreneur?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.conversation_history[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("What would you like to share?",disabled=st.session_state.conversation_history[-1]["role"] == "user")
if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to conversation history
    st.session_state.conversation_history.append({"role": "user", "content": prompt})

    # Generate assistant response only if the last message in the conversation history is from the user
if st.session_state.conversation_history[-1]["role"] == "user":
    response_text = ""
    try:
        with client.messages.stream(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            temperature=1,
            system="""
You are an AI interviewer for the Guild of Entrepreneurs community. Your task is to engage in a
conversation with a new member to learn more about their background, business, and aspirations. The
goal is to gather information that will help you craft a compelling article introducing the member
to the community.

Conduct the interview by following these steps:

1. Maintain a friendly, curious, and engaging tone throughout the conversation to create a
comfortable and open environment.

2. Ask one question at a time, covering the 10 key topics outlined below. Wait for the member's
response before moving on to the next question.
- Personal background
- Business overview
- Expertise and skills
- Learning goals
- Target customers
- Challenges and successes
- Community involvement
- Hobbies and interests
- Collaboration opportunities
- Future vision

3. Use follow-up questions as needed to gather more details, specific examples, and deeper insights
related to each topic.

4. After completing the interview, take a moment to reflect on the conversation and organize your
thoughts in a <scratchpad>. Consider:
- Key takeaways and unique aspects of the member's story
- How their background and experiences have shaped their entrepreneurial journey
- The value they bring to the Guild of Entrepreneurs community
- Potential connections or collaboration opportunities with other members

5. Using the information gathered and your reflections, craft a well-structured and engaging article
that introduces the member to the Guild of Entrepreneurs community. Include the article inside
<article> tags.
- Open with a compelling hook that captures the essence of the member's story
- Provide an overview of their background, business, and aspirations
- Highlight their unique skills, experiences, and perspective
- Discuss their goals and how they hope to contribute to and benefit from the community
- Conclude with a forward-looking statement about their potential impact and future plans

Remember, the final article should facilitate meaningful connections and showcase the diverse
talents within the Guild of Entrepreneurs community.
""",
            messages=st.session_state.conversation_history,
        ) as stream:
            for text in stream.text_stream:
                response_text += text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

    # Add assistant response to conversation history
    st.session_state.conversation_history.append({"role": "assistant", "content": response_text})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.rerun()

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    try:
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
    except Exception as e:
        st.error(f"An error occurred while sending the email: {str(e)}")

# Extract the article from the response
if "<article>" in response_text:
    article_start = response_text.index("<article>") + len("<article>")
    article_end = response_text.index("</article>")
    article = response_text[article_start:article_end].strip()

    # Generate the interview transcript
    transcript = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.conversation_history])

    # Send the email with the transcript and article
    recipient = "alexcarpenter2000@gmail.com"  # Replace with the actual recipient email address
    send_email(transcript, article, recipient)

    # Display a success message
    st.success("The interview is completed, and the article has been sent via email.")

st.rerun()