import os
import streamlit as st
import sys
import uuid
from dotenv import load_dotenv
from openai import AzureOpenAI

# Reuse services from the API
current_file_directory = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_file_directory, "../../src")
sys.path.append(relative_path)
from api.services.presidio.python_presidio_service import PythonPresidioService
from api.services.state.inmemory_state_service import InMemoryStateService
from api.services.toolkit_service import ToolkitService

# Configure the example with an .env file
load_dotenv()

endpoint = os.getenv("ENDPOINT_URL", "")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-35-turbo")
apikey = os.getenv("API_KEY", "")
api_version = os.getenv("API_VERSION", "2024-05-01-preview")

# Show existing configuration in the sidebar and allow to change it
api_key = st.sidebar.text_input("API Key", apikey, type="password")
api_url = st.sidebar.text_input("API URL", endpoint)
api_version = st.sidebar.text_input("API Version", api_version)
deployment = st.sidebar.text_input("Deployment", deployment)

# Stop the execution if the configuration is not provided
if not api_key:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()
if not api_url:
    st.info("Please add your azure_endpoint to continue.")
    st.stop()
if not deployment:
    st.info("Please add your deployment name to continue.")
    st.stop()
if not api_version:
    st.info("Please add your API version to continue.")
    st.stop()

# Initialize the OpenAI client
client = AzureOpenAI(
    azure_endpoint=api_url,
    api_key=api_key,
    api_version=api_version,
)
    
# Initialize the service that will be used to anonymize and deanonymize the text
if "session_id" not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4().hex

if "state_service" not in st.session_state:
    st.session_state["state_service"] = InMemoryStateService()

presidio_service = PythonPresidioService()
toolkit_service = ToolkitService(presidio_service, st.session_state.state_service)

# Show the title of the chatbot
st.title("💬 Anonamize Chatbot")

# Initialize the chatbot message history
if "anonymized_messages" not in st.session_state:
    st.session_state["anonymized_messages"] = [
        {"role": "assistant", "content": "How can I help you?"}]

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}]

# Show the chatbot message history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Get prompt from the user
if prompt := st.chat_input():

    # Show the prompt in the chat
    st.chat_message("user").write(prompt)

    # Anonymize the prompt
    toolkit_results = toolkit_service.anonymize(
        text=prompt, session_id=st.session_state.session_id
    )
    anonymized_text = toolkit_results["text"]

    # Add the prompt and the anonymized prompt to the message history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.anonymized_messages.append(
        {"role": "user", "content": anonymized_text}
    )
    
    # Send the anonymized message history to the LLM and get the response
    response = client.chat.completions.create(
        model=deployment,
        messages=st.session_state.anonymized_messages,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )    
    message = response.choices[0].message.content

    # Deanonymize the response from the LLM
    deanonymized_answer = toolkit_service.deanonymize(
        text=message, session_id=st.session_state.session_id
    )
    
    # Add the response and the deanonymized response to the message history
    st.session_state.messages.append(
        {"role": "assistant", "content": deanonymized_answer["text"]}
    )
    st.session_state.anonymized_messages.append(
        {"role": "assistant", "content": message}
    )

    # Show the deanonymized response in the chat
    st.chat_message("assistant").write(deanonymized_answer["text"])

    # Show the anonymized message history in the sidebar
    anonymized_messages = [t["content"] for t in st.session_state.anonymized_messages]
    st.sidebar.write("**Anonymized messages:**")
    st.sidebar.write(anonymized_messages)
