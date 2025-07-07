import streamlit as st
from src import create_workflow
from src.utils.chat_stream import ChatStreamer
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Chatbot")
st.title("EuroDetective")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    st.session_state.graph = create_workflow()

if "streamer" not in st.session_state:
    st.session_state.streamer = ChatStreamer(
        app = st.session_state.graph,
        config = {"configurable": {"thread_id": "single_session_memory"}}
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask me about anything..."):
    with st.chat_message("user"):
        st.markdown(question)
    
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Send only the current question to LangGraph - MemorySaver handles the rest
    with st.chat_message("assistant"):
        current_message = [HumanMessage(content=question)]
        generator = (
            st.session_state
            .streamer
            .stream_response(current_message)
        )
        st.write_stream(generator)
        response_content = st.session_state.streamer.get_last_response()
    
    # Add assistant response to session state ONLY for display purposes
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": response_content
        }
    )
