from typing import List, Dict, Any
import voyageai
from pinecone import Pinecone
import boto3
from botocore.exceptions import ClientError

class VoyageClient():
    """Initialize Voyage Client"""
    
    def __init__(self, api_key: str, model: str):
        self.engine = voyageai.Client(api_key)
        self.model = model
    
    def embbed_text(self, text: str) -> List[float]:
        """
        Embeds the given text using the VoyageAI engine.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedded text as a list of floats.
        """

        return self.engine.embed(
            text,
            model = self.model,
            input_type = "document"
        ).embeddings[0]
    

class PineconeClient():
    """Initialize Pinecone Client"""
    def __init__(self, api_key: str, index: str, namespace: str):
        self.index = index
        self.namespace = namespace
        self.index = (
            Pinecone(
                api_key=api_key, 
                pool_threads=30
            )
            .Index(self.index)
        )
        
    def query(self, embedded_query: List[float], filters: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Query the Pinecone index with the given embedded query and filters.

        Args:
            embedded_query (list): The embedded query to search for.
            filters (dict): The filters to apply to the query.

        Returns:
            dict: The query response from Pinecone.
        """
        
        return self.index.query(
            vector = embedded_query,
            top_k = 250,
            namespace = self.namespace,
            include_metadata = True,
            filter = filters
        ).matches
    

class DynamoDBClient():
    """Encapsulates an Amazon DynamoDB table of chunked news articles."""

    def __init__(self, dyn_resource, table_name: str):
        """
        Initializes the DynamoDB class with a DynamoDB resource.
        :param dyn_resource: A boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = dyn_resource.Table(table_name)
    
    
    def get_chunk(self, chunk_id: str) -> str:
        """
        Gets a chunk from the table.

        :param chunk_id: Chunk id.
        :return: Chunk data.
        """

        try:
            response = self.table.get_item(
                Key = {
                    "chunk_id": chunk_id
                }
            )
            chunk = response["Item"]
            print(f"Chunk {chunk_id} retrieved successfully! ✅")
            return chunk["text"]
        except ClientError as e:
            print(f"Chunk {chunk_id} not found ❌. Here's why: {e.response["Error"]["Message"]}")
            return None