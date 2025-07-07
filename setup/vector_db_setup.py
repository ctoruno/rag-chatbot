
import os
import time
from datetime import datetime
from io import BytesIO

import boto3
import voyageai
from voyageai.error import InvalidRequestError
import tiktoken
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dynamoDB import DynamoDB


class VectorDBSetup:
    """Class to set up a vector database using data stored in S3, Voyage Embedding, and Pinecone."""
    def __init__(self, country, s3_bucket, batch_size, index_name, embbeding_model, ddb_table):
        self.country = country
        self.s3_bucket = s3_bucket
        self.batch_size = batch_size
        self.index_name = index_name
        self.embbeding_model = embbeding_model

        self.s3 = boto3.client("s3")
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        self.vc = voyageai.Client(os.getenv("VOYAGEAI_API_KEY"))
        self.pc = Pinecone(
            api_key = os.getenv("PINECONE_API_KEY"), 
            pool_threads = 30
        )
        self.ddb_resource = boto3.resource(
            "dynamodb", 
            region_name="us-east-1"
        )
        self.ddb_table = ddb_table
        self.ddb = DynamoDB(self.ddb_resource, self.ddb_table)


    def create_pinecone_index(self):
        if not self.pc.has_index(self.index_name):
            self.pc.create_index(
                self.index_name,
                dimension = 1024,
                spec = ServerlessSpec(
                    cloud = "aws",
                    region = "us-east-1"
                ),
                metric = "cosine"
            )
            print(f"Index {self.index_name} created successfully ✅")
        else:
            print(f"Index {self.index_name} already exists ✅")


    def _retrieve_data(self):
        """
        Retrieve data for the specified country from S3.
        This method reads a Parquet file from S3, drops duplicate entries based on the 'id' column,
        and converts the DataFrame to a list of dictionaries.
        Returns:
            list: A list of dictionaries containing the data for the specified country.
        """
        country_data_s3 = self.s3.get_object(
            Bucket = self.s3_bucket,
            Key = f"{self.country}_master.parquet.gzip"
        )
        country_data_df = pd.read_parquet(
            BytesIO(country_data_s3["Body"].read()),
            engine = "pyarrow"
        ).drop_duplicates(subset = "id")
        country_data = country_data_df.to_dict(orient="records")

        print(f"{len(country_data)} records found for {self.country}")

        return country_data
    

    def _prepare_document_for_embedding(self, doc):
        """
        Prepare the document for embedding by splitting it into chunks and creating a list of dictionaries
        containing the chunked text and metadata.
        Args:
            doc (dict): A dictionary containing the document data.
        Returns:
            list: A list of dictionaries, each containing a chunk of text and its associated metadata.
        """
        id = doc["id"]
        text = doc["content_trans"]
        text_length = len(self.encoding.encode(text))

        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name = "cl100k_base",
            model_name = "gpt-4o-mini",
            chunk_size = 1000,
            chunk_overlap = 100,
            separators=["\n\n", "\n", ". "]
        )
        
        if text_length <= 1150:
            chunks = [text]
        else:
            chunks = splitter.split_text(text)

        chunk_data_list = [
            {
                "text": chunk.strip(". "),
                "metadata": {
                    "article_id": id,
                    "chunk_id" : i,
                    "title" : doc["title_trans"],
                    "country" : self.country,
                    "pillar_1" : doc["pillar_1"],
                    "pillar_2" : doc["pillar_2"],
                    "pillar_3" : doc["pillar_3"],
                    "pillar_4" : doc["pillar_4"],
                    "pillar_5" : doc["pillar_5"],
                    "pillar_6" : doc["pillar_6"],
                    "pillar_7" : doc["pillar_7"],
                    "pillar_8" : doc["pillar_8"],
                    "impact_score" : doc["impact_score"],
                    "published_date" : doc["published_date"]
                }
            }
            for i, chunk in enumerate(chunks)
        ]
        
        return chunk_data_list
    

    def retrieve_and_prepare_data(self):
        """Retrieve and prepare data for embedding."""

        print("Retrieving data from S3...")
        country_data = self._retrieve_data()
        print("Data retrieval complete! ✅")

        print("Flattening record data for embedding...")
        processed_chunks = [
            self._prepare_document_for_embedding(doc) 
            for doc in country_data
        ]
        flattened_processed_chunks_all = [
            item 
            for sublist in processed_chunks 
            for item in sublist
        ]
        flattened_processed_chunks = [
            item 
            for item in flattened_processed_chunks_all
            if len(self.encoding.encode(item["text"])) > 75 # Filter out chunks with <= 75 tokens
        ]
        print("Data flattening complete! ✅")
        print("Total amount of chunks to process:", len(flattened_processed_chunks))

        return flattened_processed_chunks
    

    def embbed_and_ingest(self, batch, batch_num):
        """
        Embed and ingest a batch of documents into the Pinecone index.
        Args:
            batch (list): A list of dictionaries, each containing a document's id, text, and metadata.
        Returns:
            async_result: The result of the asynchronous upsert operation to Pinecone.
        """
        ids = [
            f"{self.country.upper()[0:3]}_B{batch_num}C{n}" 
            for n,_ in enumerate(batch)
        ]
        texts = [item["text"] for item in batch]
        metadata = [item["metadata"] for item in batch]

        docs = [
            {"chunk_id": a, "text": b} 
            for a,b in zip(ids, texts)
        ]
        self.ddb.add_chunks(  ## Uploading full text chunk to DynamoDB
            docs
        )

        try:
            embeddings = self.vc.embed(
                texts,
                model = self.embbeding_model,
                input_type = "document"
            ).embeddings
        except voyageai.error.InvalidRequestError as e:
            print(f"Error embedding batch {batch_num}: {e}")

        vectors = [
            {"id": a, "values": b, "metadata": c} 
            for a,b,c in zip(ids, embeddings, metadata)
        ]

        with self.pc.Index(self.index_name, pool_threads=30) as index:
            async_result = index.upsert(
                vectors=vectors, 
                namespace="ns-1",
                async_req=True
            ) 

        return async_result.get()
        

def main():
    """Main function to set up the vector database for each EU member state."""

    start_time = datetime.now()
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    start_timer = time.time()

    load_dotenv()
    eu_member_states = [
        ## "Austria",
        ## "Belgium",
        ## "Bulgaria",
        ## "Croatia",
        ## "Cyprus",
        ## "Czechia",
        ## "Denmark",
        ## "Estonia",
        ## "Finland",
        ## "France",
        ## "Germany",
        ## "Greece",
        ## "Hungary",
        ## "Ireland",
        "Italy",
        ## "Latvia",
        ## "Lithuania",
        ## "Luxembourg",
        ## "Malta",
        ## "Netherlands",
        ## "Poland",
        ## "Portugal",
        "Romania",
        ## "Slovakia",
        ## "Slovenia",
        "Spain",
        ## "Sweden"
    ] # Adjusted for testing purposes

    for country in eu_member_states:
        print("============================================")
        print(f"PROCESSING DATA FOR {country.upper()} 🌎")
        print("============================================")

        print("Preparing setup instance...")
        setup_instance = VectorDBSetup(
            country=country,
            s3_bucket = "eurovoices-news-articles-data",
            batch_size = 100,
            index_name = "eurovoices-news-articles-vdb",
            embbeding_model = "voyage-3.5",
            ddb_table = "eurovoices-chunked-news"
        )
        print("Instance prepared successfully! ✅")
        print("----------------")

        print("Checking if pinecone index exists...")
        setup_instance.create_pinecone_index()
        print("----------------")

        print("Retrieving and preparing data for embedding...")
        flattened_processed_chunks = setup_instance.retrieve_and_prepare_data()
        print("----------------")

        print(f"Preparing to process data in batches. Batch size: {setup_instance.batch_size} chunks of text")
        n_batches = (len(flattened_processed_chunks) + setup_instance.batch_size - 1) // setup_instance.batch_size
        for batch_num, i in enumerate(range(0, len(flattened_processed_chunks), setup_instance.batch_size), start=1):
            print(f"Processing batch {batch_num} of {n_batches}")
            setup_instance.embbed_and_ingest(
                flattened_processed_chunks[i : i + setup_instance.batch_size],
                batch_num
            )
    
    print("=============================================================")
    print("Vector DB setup and data ingestion completed successfully! ✅")
    print("=============================================================")

    end_time = datetime.now()
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    duration_minutes = (time.time() - start_timer) / 60
    print(f"Total duration: {duration_minutes:.1f} minutes")
    

if __name__ == "__main__":
    main()
    