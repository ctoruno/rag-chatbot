import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Voyage Configuration
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
    VOYAGE_MODEL = "voyage-3.5"
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX = "eurovoices-news-articles-vdb"
    PINECONE_NAMESPACE = "ns-1"

    # DynamoDB Configuration
    DYNAMODB_TABLE = "eurovoices-chunked-news"
    DYNAMODB_REGION = "us-east-1"

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    RESPONSE_MODEL = "openai:gpt-4.1"
    
    # Vector Database Search Configuration
    TOP_K = 250
    POOL_THREADS = 30
    TEMPERATURE = 0

settings = Settings()