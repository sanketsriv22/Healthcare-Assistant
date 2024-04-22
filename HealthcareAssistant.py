#!pip install dotenv
#!pip install openai
#!pip install streamlit

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import os

# load env variables from .env file
load_dotenv('/Users/sanket/Desktop/Projects/keys.env')

# access API key
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()


def main():

    # Create assistant and message thread objects
    assistant = create_assistant()
    thread = create_thread()

    # Streamlit set up
    st.title("Healthcare Assistant")
    st.subheader("Ask me anything about health!")

    # intialize chat history for streamlit
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message["content"])

    # Query for user input
    if query := st.chat_input("Type your health-related questions here:"):

        # run query through the API and return thread of message outputs
        messages = run_assistant(query, assistant, thread)

        # streamlit display query
        with st.chat_message("user"):
            st.markdown(query)

        # streamlit add query to total message list
        st.session_state.messages.append({"role": "user", "content": query})

        # parse most recent response from message thread
        response = f"Assistant: {messages.data[0].content[0].text.value}"

        # streamlit display response
        with st.chat_message("assistant"):
            st.markdown(response)

        # streamlit add response to total message list
        st.session_state.messages.append({"role": "assistant", "content": messages.data[0].content[0].text.value})


# should only create assistant object once per session
@st.cache_data
def create_assistant():
    assistant = client.beta.assistants.create(
        name="Healthcare Assistant",
        instructions="You are a healthcare professional assisting patients with their health-related queries. Offer guidance on nutrition, exercise, medication, and lifestyle changes to promote optimal health and well-being, tailored to the user's needs. Be empathetic and supportive in your responses, and ensure that all information provided is evidence-based and reliable. Always give a plan of action for the user.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-3.5-turbo",
    )
    return assistant


# should only create thread object once per session, to give context to conversation
@st.cache_data
def create_thread():
    thread = client.beta.threads.create()
    return thread


# does the heavy lifting by utilizing openAI's assistant API and generating a response
def run_assistant(query, assistant, thread):

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    while run.status != "completed":
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id = thread.id,
            run_id = run.id
        )
        if keep_retrieving_run.status == "completed":
            print("\n")
            break

    message_list = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    return message_list


if __name__ == "__main__":
    main()
    