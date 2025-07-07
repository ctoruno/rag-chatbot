## Project Structure

```bash
.
├── app.py
├── notebooks
│   ├── react-agent.ipynb
│   ├── vector_db.ipynb
│   └── workflow-test.ipynb
├── pyproject.toml
├── README.md
├── setup
│   ├── __init__.py
│   ├── dynamoDB.py                 # Class to populate DynamoDB
│   └── vector_db_setup.py          # Class to populate Pinecone database
├── src
│   ├── __init__.py
│   ├── clients
│   │   ├── __init__.py
│   │   ├── dynamodb.py
│   │   ├── pinecone.py
│   │   └── voyage.py
│   ├── config
│   │   ├── __init__.py
│   │   └── settings.py             # Agent basic presettings
│   ├── graph
│   │   ├── __init__.py
│   │   └── workflow.py             # Graph workflow
│   ├── nodes
│   │   ├── __init__.py
│   │   ├── answerer.py             # Node: Answer using retrieve information
│   │   ├── generator.py            # Node: Answer directly or make a tool call
│   │   └── rewriter.py             
│   ├── prompts
│   │   ├── __init__.py
│   │   └── templates.py            # Prompt templates
│   ├── tools
│   │   ├── __init__.py
│   │   └── news_search.py          # News search tool
│   └── utils
│       ├── __init__.py
│       ├── chat_stream.py          # Module for streaming the chatbot responses
│       └── message_trimmer.py      # Module for trimming messages in long conversations
├── static      # Static font files for app
└── uv.lock
```