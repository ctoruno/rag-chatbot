import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DynamoDB:
    """
    Encapsulates an Amazon DynamoDB table of chunked news articles.
    """

    def __init__(self, dyn_resource, table_name):
        """
        Initializes the DynamoDB class with a DynamoDB resource.
        :param dyn_resource: A boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = dyn_resource.Table(table_name)


    def add_chunks(self, chunks):
        """
        Adds a chunk to the table.

        :param id: Chunk id [not equal to article id].
        :param text: Chunk text.
        """

        try:
            with self.table.batch_writer() as writer:
                for chunk in chunks:
                    writer.put_item(Item=chunk)
        except ClientError as err:
            logger.error(
                "Couldn't load data into table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        

if __name__ == "__main__":

    # Example usage
    dyn_resource = boto3.resource(
        "dynamodb", 
        region_name="us-east-1"
    )
    table_name = "eurovoices-chunked-news"

    try: 
        db = DynamoDB(dyn_resource, table_name)
        logger.info(f"Access to table {db.table.name} successful! ✅")
        db.add_chunks(
            [
                {
                    "chunk_id": "TEST1",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce pellentesque."
                },
                {
                    "chunk_id": "TEST2",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce pellentesque."
                },
                {
                    "chunk_id": "TEST3",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce pellentesque."
                }
            ]
        )
        logger.info("Testing chunks added successfully! ✅")

    except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise

