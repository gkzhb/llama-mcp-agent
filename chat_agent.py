import os
import streamlit as st
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage
from llama_index.llms.siliconflow import SiliconFlow
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.vector_stores.lancedb import LanceDBVectorStore
import logging
import sys

# Enable logging
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

llm = SiliconFlow(
    api_key=st.secrets.llm_api_key,
    model="Qwen/Qwen2.5-7B-Instruct",
    temperature=0.5,
    max_tokens=4096,
)

ollama_embedding = OllamaEmbedding(
    model_name="bge-m3",
    base_url="http://localhost:11434",
)
# changing the global default
Settings.embed_model = ollama_embedding
Settings.llm = llm
# Initialize LanceDB vector store
vector_store = LanceDBVectorStore(uri="./lancedb", mode="overwrite", query_type="hybrid")
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# Initialize VectorStoreIndex
index = VectorStoreIndex([], storage_context=storage_context)
doc = Document(text='''Your documentation here''')

# Insert into vector db
index.insert(doc)

# Create query engine
chat_engine = index.as_chat_engine()

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "I'm a smart agent!"}
    ]
    
# Streamlit UI config
st.set_page_config(page_title="LLM Chat Assistant", layout="wide")
st.title("LLM Chat Assistant")

# init session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Generate response using both LLM and vector store
            prompts = [ChatMessage(role=msg['role'], content=msg['content']) for msg in st.session_state.messages]
            response = chat_engine.stream_chat(prompts[-1].content, prompts[:-1])
            def response_generator():
                full_response = ""
                for chunk in response.chat_stream:
                    full_response += chunk.delta
                    yield chunk.delta
                message = {"role": "assistant", "content": full_response}
                st.session_state.messages.append(message)
            st.write_stream(response_generator())

