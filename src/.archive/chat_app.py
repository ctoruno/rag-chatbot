from langchain_core.messages import trim_messages, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict, List
from typing import Sequence


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_question: str
    retrieved_context: List[Document]
    answer: str


class ChatApp:
    def __init__(
            self, 
            model_name, 
            model_provider, 
            thread_id
    ):
        self.model_name = model_name
        self.model_provider = model_provider
        self.thread_id = thread_id
        self.app = None
        self.config = None
        self.memory = None
        self._setup_app()
    
    def _setup_app(self):
        """Initialize the LangGraph application"""

        model = init_chat_model(
            self.model_name, 
            model_provider = self.model_provider
        )
        
        prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You are a brilliant assistant designed to identify and summarize events related to the rule of law in the 
                European Union, based on retrieved context from news articles. Your goal is to help users understand how 
                recent events affect key dimensions of the rule of law, such as judicial independence, civil and criminal 
                justice, civil liberties and freedoms, government accountability, law enforcement, order and security, and 
                abscense of corruption.

                Only use the content retrieved from the vector database. Do not invent or speculate beyond what is present. 
                If no relevant rule of law–related information is found in the retrieved content, say so clearly.

                - Be concise, factual, and neutral.
                - Highlight specific events, actors, and implications where applicable.
                - Use plain, accessible language.
                - If multiple events are mentioned, summarize each one in a clear, structured way.

                If the user asks about a topic unrelated to the rule of law, a country outside the 27 active members 
                of the EU represented in the retrieved context, or if the retrieved context does not have enough information
                about the topic and country in question, respond with:
                “The available information does not mention relevant rule of law–related events for that country or 
                topic. Please rephrase your question”

                Also, you talk like a pirate. Anwer to the best of your abilities, but always in pirate speak.
                """
            ),
            (
                "human",
                """
                You are given context from multiple news articles. Identify and summarize only the parts that describe 
                events relevant to the user question. Ignore unrelated text. Structure your answer clearly and concisely.

                [CONTEXT START]
                {retrieved_context}
                [CONTEXT END]

                ## USER QUESTION:
                {user_question}
                """
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        trimmer = trim_messages(
            max_tokens=100000,
            strategy="last",
            token_counter=model,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )
        
        workflow = StateGraph(state_schema=State)
        
        def call_model(state: State) -> dict:
            """Invoke the model with the trimmed messages and context"""
            trimmed_messages = trimmer.invoke(state["messages"])
            prompt = prompt_template.invoke(
                {
                    "messages": trimmed_messages,
                    "retrieved_context": state["retrieved_context"],
                    "user_question": state["user_question"],
                }
            )
            response = model.invoke(prompt)
            return {"messages": response}
        
        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)
        
        self.memory = MemorySaver()
        self.app = workflow.compile(checkpointer=self.memory)
        self.config = {
            "configurable": {"thread_id": self.thread_id}
        }
    
    def get_app(self):
        """Get the compiled LangGraph application"""
        return self.app
    
    def get_config(self):
        """Get the configuration"""
        return self.config
    
    def get_memory(self):
        """Get the memory saver"""
        return self.memory