from langgraph.graph import MessagesState
from langchain.chat_models import ChatOpenAI
from ..prompts.templates import REWRITE_PROMPT
from ..utils.message_trimmer import create_message_trimmer

def create_rewrite_question_node(model: ChatOpenAI):
    """Factory function to create the rewrite_question node."""

    trimmer = create_message_trimmer(model)
    
    def rewrite_question(state: MessagesState):
        """Rewrite the original user question."""
        trimmed_messages = trimmer.invoke(state["messages"])
        question = trimmed_messages[0].content
        prompt = REWRITE_PROMPT.format(question=question)
        response = model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [{"role": "user", "content": response.content}]}
    
    return rewrite_question