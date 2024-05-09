import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic
import tornado.websocket

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    try:
        yag = yagmail.SMTP(email_user, email_password)
        subject = "Chatbot Interview Transcript and Story"
        content = f"Interview Transcript:\n\n{transcript}\n\nGenerated Story:\n\n{story}"
        yag.send(to=recipient, subject=subject, contents=content)
        return True
    except Exception as e:
        st.error(f"An error occurred while sending the email: {str(e)}")
        return False

st.title("Guild Reporter")
st.write(
    "This chatbot will interview you and generate a story based on your responses."
)

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
        {"role": "user", "content": "Hi"},
        {
            "role": "assistant",
            "content": "Hello! I'm an AI interviewer for the Guild of Entrepreneurs community. I'm excited to learn more about you and your entrepreneurial journey. Let's start with your personal background. Can you tell me a bit about yourself and what led you to become an entrepreneur?",
        },
    ]

# Display chat messages from history on app rerun
for message in st.session_state.conversation_history[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input(
    "What would you like to share?",
    disabled=st.session_state.conversation_history[-1]["role"] == "user",
)
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
            Your task is to engage in a conversation with a new member of the Guild of Entrepreneurs community
to learn more about their background, business, and aspirations. The goal is to gather information
that will help you craft a compelling article introducing the member to the community. We want to go
beyond a simple introduction and get to a compelling story or lesson. Make sure to determine their pronouns and name before writing the article.

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
related to each topic. Some example follow-up questions include:
- If you could go back in time and give advice to yourself before you started your entrepreneurship
journey, what would you tell yourself?
- What's one thing you've learned in your field of expertise that could help entrepreneurs in their
journey?
- Do you have any advice on growing a business, speaking specifically from your personal experience?
- Advice on facing roadblocks in the growth journey, speaking specifically from your personal
experience
- Advice on facing failure, if applicable, speaking specifically from your personal experience
- If there's one topic you want to talk about that you believe will help entrepreneurs, what would
that be? Why that topic? What is it about? What's the problem that entrepreneurs can solve by
learning this topic? What's your advice regarding this topic?
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
<Example Output 1>
<aside>
✨ **Meet Levina**

*A writer turned brand strategist and project manager, Levina thrives by working with creatives in the branding world.  She collaborates with fellow strategists and studios to build brands that not only make a mark, but make other people's lives better. We reached out to Lev and asked her to share about the biggest lessons she’s learned so far as an entrepreneur.*

</aside>

### The ONE thing

If there's one thing I want every entrepreneur to have in their journey that would be ***PURPOSE***. You can have all the capital in the world, or be a master of time management, but at the end of the day, we all have to ask ourselves a fundamental question: ***Why does this matter to me?***

Entrepreneurship is hard enough as it is. You know it, I know it. There’s so many ups and downs. We set goals and we give our best, but there will be times when things don’t go our way. And then when it does, the next challenge arrives: consistency, sustainability, and longevity. It’s a marathon, not a sprint. And I’ve found that over the last decade of journeying in my creative business, one thing that keeps me going is my purpose. 

### Go back to your ‘Why’

I set out wanting to help make people’s lives and the planet better. It’s more than just working for sales and profit, but it’s about impact. It’s about coming alongside other entrepreneurs to help them make the difference they want to make. So when things get rough, I go back to my ‘Why’. 

But after that, the day-to-day is also not as simple. As entrepreneurs, there seems to be one problem that never leaves us: too much to do, so little time. Which is why it’s all the more important that we keep our eyes on the prize, to fix our eyes on our ‘Why’—the long haul—and set our priorities right. 

### Use your ‘Why’ as a decision-making filter

With endless decisions to be made, we need an anchor to keep us grounded in the bigger picture. Purpose is so important because it helps us prioritize tasks and filter out distractions. We don’t have to say ‘Yes’ to everything because we know what projects, collaborations, and tasks align with our goals. 

When we remember what’s at stake, it’s easier to make the right calls. When we remember why we do what we do, we don’t fall into the trap of just following trends. Rather, we can focus on our strengths and the impact we want to bring. 

### So what’s your purpose?

What fuels your to keep going? What makes your entrepreneurship journey worth fighting for? Get clarity on your purpose and use that a ‘North Star’ to propel you forward in every ups and downs you face in your process.
</Example Output 1>

<Example Output 2>
**Have you ever met someone who just seems to get it?**  That's my friend Alex.  He's been this way since way back in high school, hustling and selling pencil cases (seriously, who even knew there was a market for that?).  Even then, he could see what people needed and figure out how to make it happen.

**Fast forward to today, and Alex is a serial entrepreneur extraordinaire!**  He's launched companies across all sorts of industries.  We were curious – what drives him? Turns out, it's all about understanding people. He's fascinated by what motivates them, what challenges they face, and how to build something amazing to solve those problems. And guess what?  He's got the background to prove it. Accounting?  Nailed it.  Educational psychology?  Yep, that too. Now he's even diving into software engineering—the guy just never stops learning!

**One thing Alex emphasized is the importance of learning from everything, the wins, the losses, and the experiences that leave you scratching your head.** He believes that taking the time to really reflect on what went well (and what went hilariously wrong) is the secret weapon for growth, both personally and professionally. By reflecting on his own journey, he's uncovered some seriously cool insights that have totally reshaped his approach to building businesses.

**One of the biggest things he's learned? Making money is awesome, but it's not everything.** Sure, a business needs to turn a profit to keep the lights on and keep helping people. But Alex says it's also crucial to remember why you started in the first place – to make a positive impact and create something valuable for people's lives.

**Sometimes entrepreneurs feel weird about making money, like they're somehow taking advantage of people.** Alex says that's totally not the case!  If you're solving a real problem and making people's lives easier, you deserve to be rewarded for that. The key is finding that sweet spot between making a profit and staying true to your mission. That's the recipe for building a business that rocks and makes a difference.

**Speaking of making a difference, Alex is all about getting to know his customers on a deeper level.**  He believes the best way to understand what people need is to jump right in with them, ask a ton of questions, and figure out what's really going on beneath the surface.  By getting that deep understanding, you can create solutions that tackle the root of the problem, not just the band-aid fixes.

**Alex uses a cool doctor analogy to explain this.**  A good doctor wouldn't just throw pain meds at your backache without asking questions, right?  They'd dig deeper to find the real cause.  Entrepreneurs need to do the same!  By working hand-in-hand with clients and asking the right questions, you can help them figure out what they really need and come up with solutions that work for the long haul.

**Alex is still out there exploring the world of software engineering and working directly with clients.**  His dedication to learning and using his knowledge to help people and create awesome things is never-ending.  His whole journey, with all its twists and turns, is a total inspiration to all of us in the Guild of Entrepreneurs.  So next time you're feeling stuck, remember Alex and his dedication to helping people and building something sustainable.
</Example Output 2>
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
    try:
        with st.chat_message("assistant"):
            st.markdown(response_text)
    except tornado.websocket.WebSocketClosedError:
        st.warning("The connection was closed unexpectedly. Please refresh the page and try again.")
        st.stop()

    # Extract the article from the response
    if "<article>" in response_text:
        article_start = response_text.index("<article>") + len("<article>")
        article_end = response_text.index("</article>")
        article = response_text[article_start:article_end].strip()

        # Generate the interview transcript
        transcript = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.conversation_history])

        # Send the email with the transcript and article
        email_sender = st.secrets["EMAIL_USER"]
        email_receiver = "alexcarpenter2000@gmail.com,kusumadjajalevina@gmail.com"  # Replace with the actual recipient email address
        subject = "Chatbot Interview Transcript and Story"
        body = f"Interview Transcript:\n\n{transcript}\n\nGenerated Story:\n\n{article}"
        password = st.secrets["EMAIL_PASSWORD"]

        try:
            msg = MIMEMultipart()
            msg['From'] = email_sender
            msg['To'] = email_receiver
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_sender, password)
            server.send_message(msg)
            server.quit()

            st.success('Thank you so much for taking the time to have a conversation with the Guild Reporter! Your story has been sent to our human editors and we will be in touch with the next steps soon! 🚀')
        except Exception as e:
            st.error(f"An error occurred while sending the email: {e}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

