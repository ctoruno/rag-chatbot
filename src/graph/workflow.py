from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import trim_messages

from ..clients import VoyageClient, PineconeClient, DynamoDBClient
from ..tools.news_search import NewsSearchTool
from ..nodes.generator import create_generate_query_or_respond_node
from ..nodes.rewriter import create_rewrite_question_node
from ..nodes.answerer import create_generate_answer_node
from ..prompts.templates import RETRIEVER_DESCRIPTION
from ..config.settings import settings

def create_workflow():
    """Create and return the complete workflow graph."""
    
    # Initialize clients
    vc = VoyageClient(
        api_key=settings.VOYAGE_API_KEY,
        model=settings.VOYAGE_MODEL
    )
    pc = PineconeClient(
        api_key=settings.PINECONE_API_KEY,
        index_name=settings.PINECONE_INDEX,
        namespace=settings.PINECONE_NAMESPACE,
        pool_threads=settings.POOL_THREADS
    )
    ddbc = DynamoDBClient(
        table_name=settings.DYNAMODB_TABLE,
        region_name=settings.DYNAMODB_REGION
    )
    
    # Initialize custom tools
    retriever = NewsSearchTool(
        vc=vc,
        pc=pc,
        ddbc=ddbc,
        description=RETRIEVER_DESCRIPTION
    )
    
    # Initialize LLM
    response_model = init_chat_model(
        settings.RESPONSE_MODEL,
        temperature=settings.TEMPERATURE
    )
    
    # Create nodes
    generate_query_or_respond = create_generate_query_or_respond_node(response_model, retriever)
    rewrite_question = create_rewrite_question_node(response_model)
    generate_answer = create_generate_answer_node(response_model)
    
    # Build workflow
    workflow = StateGraph(MessagesState)
    
    workflow.add_node("generate_query_or_respond", generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([retriever]))
    workflow.add_node("generate_answer", generate_answer)
    
    workflow.add_edge(START, "generate_query_or_respond")
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )
    workflow.add_edge("retrieve", "generate_answer")
    workflow.add_edge("generate_answer", END)

    # Memory Checkpointer
    memory = MemorySaver()
    
    return workflow.compile(
        checkpointer = memory
    )