## Project Structure

```bash
rag-chatbot/
├── pyproject.toml                 # uv configuration and dependencies
├── README.md                      # Project documentation
├── .env                          # Environment variables
├── .gitignore                    # Git ignore file
├── config/
│   ├── __init__.py
│   └── settings.py               # Shared configuration
├── data/                         # Raw data files
│   ├── csv/                      # Original CSV files
│   └── documents/                # Original text documents
├── setup/                        # 🔧 SETUP & PREPARATION CODE
│   ├── __init__.py
│   ├── infrastructure/           # AWS infrastructure creation
│   │   ├── __init__.py
│   │   ├── create_s3.py
│   │   ├── create_redshift.py
│   │   ├── create_opensearch.py
│   │   └── setup_bedrock.py
│   ├── data_preparation/         # Data processing & ingestion
│   │   ├── __init__.py
│   │   ├── csv_to_redshift.py    # Process CSVs → Redshift
│   │   ├── documents_to_s3.py    # Upload docs → S3
│   │   └── generate_embeddings.py # Generate embeddings → OpenSearch
│   └── scripts/                  # One-time setup scripts
│       ├── 01_setup_infrastructure.py
│       ├── 02_ingest_csv_data.py
│       ├── 03_process_documents.py
│       └── 04_create_embeddings.py
├── src/                          # 🤖 CHATBOT RUNTIME CODE
│   ├── __init__.py
│   ├── agents/                   # Main chatbot logic
│   │   ├── __init__.py
│   │   ├── rag_agent.py          # Main RAG orchestrator
│   │   ├── sql_agent.py          # Text-to-SQL agent
│   │   └── vector_agent.py       # Vector search agent
│   ├── retrievers/               # Data retrieval components
│   │   ├── __init__.py
│   │   ├── redshift_retriever.py # SQL query execution
│   │   └── opensearch_retriever.py # Vector search
│   ├── utils/                    # Runtime utilities
│   │   ├── __init__.py
│   │   ├── aws_clients.py        # AWS client management
│   │   └── query_router.py       # Route queries to SQL vs Vector
│   └── main.py                   # Chatbot entry point
├── shared/                       # 🔗 SHARED UTILITIES
│   ├── __init__.py
│   ├── aws_utils.py              # Common AWS operations
│   ├── embedding_utils.py        # Embedding operations
│   └── data_utils.py             # Common data operations
└── tests/
    ├── test_setup/               # Tests for setup code
    └── test_chatbot/             # Tests for chatbot code
```