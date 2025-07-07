from langgraph.graph import MessagesState
from langchain.chat_models import ChatOpenAI
from ..prompts.templates import SYSTEM_PROMPT
from ..utils.message_trimmer import create_message_trimmer

def create_generate_query_or_respond_node(model: ChatOpenAI, retriever):
    """Factory function to create the generate_query_or_respond node."""

    def generate_query_or_respond(state: MessagesState):
        """Call the model to generate a response based on the current state."""
        trimmer = create_message_trimmer(model)
        trimmed_messages = trimmer.invoke(state["messages"])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *trimmed_messages
        ]
        response = model.bind_tools([retriever]).invoke(messages)
        return {"messages": [response]}
    
    return generate_query_or_respond