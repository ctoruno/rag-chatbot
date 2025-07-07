from langchain_core.messages import trim_messages
from langchain.chat_models import ChatOpenAI

def create_message_trimmer(model: ChatOpenAI):
    """Create a message trimmer configured for the given model."""
    return trim_messages(
        max_tokens = 500000,
        strategy = "last",
        token_counter = model,
        include_system = True,
        allow_partial = False,
        start_on = "human",
    )