import boto3
from botocore.exceptions import ClientError
from typing import Optional

class DynamoDBClient:
    """Client for DynamoDB operations on chunked news articles."""

    def __init__(self, table_name: str, region_name: str = "us-east-1"):
        self.dyn_resource = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dyn_resource.Table(table_name)
    
    def get_chunk(self, chunk_id: str) -> Optional[str]:
        """
        Gets a chunk from the table.

        Args:
            chunk_id (str): Chunk identifier.
            
        Returns:
            Optional[str]: Chunk text content or None if not found.
        """
        try:
            response = self.table.get_item(Key={"chunk_id": chunk_id})
            chunk = response["Item"]
            return chunk["text"]
        except ClientError as e:
            print(f"Chunk {chunk_id} not found ❌. Here's why: {e.response['Error']['Message']}")
            return None