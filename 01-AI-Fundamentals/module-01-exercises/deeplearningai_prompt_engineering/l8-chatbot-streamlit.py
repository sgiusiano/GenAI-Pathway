import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(page_title="OrderBot - Pizza Restaurant", page_icon="🍕")

# Initialize OpenAI client
client = OpenAI()

# Function to get responses from the model
def get_completion_from_messages(messages, model="gpt-4.1", temperature=0):
    response = client.responses.create(
        model=model,
        input=messages,
        temperature=temperature,
    )
    return response.output_text

# Application title
st.title("🍕 OrderBot - Pizza Restaurant")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    # System message that defines the bot's behavior
    st.session_state.messages = [
        {'role':'system', 'content':'''
        You are OrderBot, an automated service to collect orders for a pizza restaurant. \
        You first greet the customer, then collects the order, \
        and then asks if it's a pickup or delivery. \
        You wait to collect the entire order, then summarize it and check for a final \
        time if the customer wants to add anything else. \
        If it's a delivery, you ask for an address. \
        Finally you collect the payment.\
        Make sure to clarify all options, extras and sizes to uniquely \
        identify the item from the menu.\
        You respond in a short, very conversational friendly style. \
        The menu includes \
        pepperoni pizza  12.95, 10.00, 7.00 \
        cheese pizza   10.95, 9.25, 6.50 \
        eggplant pizza   11.95, 9.75, 6.75 \
        fries 4.50, 3.50 \
        greek salad 7.25 \
        Toppings: \
        extra cheese 2.00, \
        mushrooms 1.50 \
        sausage 3.00 \
        canadian bacon 3.50 \
        AI sauce 1.50 \
        peppers 1.00 \
        Drinks: \
        coke 3.00, 2.00, 1.00 \
        sprite 3.00, 2.00, 1.00 \
        bottled water 5.00 \
        '''}
    ]

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])

# User input
if prompt := st.chat_input("What would you like to order?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Get assistant response
    response = get_completion_from_messages(st.session_state.messages)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

# Button to generate order summary
if st.button("Generate Order Summary"):
    if len(st.session_state.messages) > 1:  # Verify that there is a conversation
        # Copy messages and add instruction to generate summary
        summary_messages = st.session_state.messages.copy()
        summary_messages.append(
            {'role':'system', 'content':'create a json summary of the previous food order. Itemize the price for each item\
             The fields should be 1) pizza, include size 2) list of toppings 3) list of drinks, include size 4) list of sides include size 5)total price'}
        )
        
        # Get the summary
        summary = get_completion_from_messages(summary_messages, temperature=0)
        
        # Show the summary in an expander
        with st.expander("Order Summary", expanded=True):
            st.code(summary, language="json")
    else:
        st.warning("You need to place an order first to generate a summary.")

# Button to restart the conversation
if st.button("Restart Conversation"):
    # Keep only the system message
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()
