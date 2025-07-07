from typing import List, Dict, Any
from pinecone import Pinecone

class PineconeClient:
    """Client for Pinecone vector database operations."""
    
    def __init__(self, api_key: str, index_name: str, namespace: str, pool_threads: int = 30):
        self.index_name = index_name
        self.namespace = namespace
        self.index = (
            Pinecone(api_key=api_key, pool_threads=pool_threads)
            .Index(index_name)
        )
        
    def query(self, embedded_query: List[float], filters: Dict[Any, Any], top_k: int = 250) -> List[Any]:
        """
        Query the Pinecone index with the given embedded query and filters.

        Args:
            embedded_query (List[float]): The embedded query to search for.
            filters (Dict[Any, Any]): The filters to apply to the query.
            top_k (int): Number of results to return.

        Returns:
            List[Any]: The query response matches from Pinecone.
        """
        return self.index.query(
            vector=embedded_query,
            top_k=top_k,
            namespace=self.namespace,
            include_metadata=True,
            filter=filters
        ).matches