from langgraph.graph import MessagesState
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

from ..prompts.templates import GENERATE_PROMPT
from ..utils.message_trimmer import create_message_trimmer

def create_generate_answer_node(model: ChatOpenAI):
    """Factory function to create the generate_answer node."""
    
    def generate_answer(state: MessagesState):
        """Generate an answer using retrieved context."""
        trimmer = create_message_trimmer(model)
        trimmed_messages = trimmer.invoke(state["messages"])

        # Filter messages by type
        human_messages = [
            msg for msg in trimmed_messages 
            if hasattr(msg, "type") and msg.type == "human"
        ]
        tool_messages = [
            msg for msg in trimmed_messages 
            if hasattr(msg, "type") and msg.type == "tool"
        ]
        
        # Get the most recent of each type
        question = human_messages[-1].content if human_messages else None
        context = tool_messages[-1].content if tool_messages else None
        
        if not question or not context:
            return {"messages": [AIMessage(content="Missing question or context for answer generation.")]}
        
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = model.invoke([HumanMessage(content=prompt)])
        return {"messages": [response]}
    
    return generate_answer