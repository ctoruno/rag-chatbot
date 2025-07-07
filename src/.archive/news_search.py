
import json
from langchain.tools import BaseTool

class NewsSearchTool(BaseTool):
    """Tool for searching news events using vector similarity search"""
    
    name: str = "news_events_search"
    description: str = ""  # Will be set in __init__
    

    def __init__(self, vc, pc, dynamoDB, description: str):
        super().__init__()
        self.vc = vc                # Voyage Client
        self.pc = pc                # Pinecone Client
        self.dynamoDB = dynamoDB    # DynamoDB Client
        self.description = description
    

    def _prepare_doc(self, doc):
        """
        Formats a document's metadata and content chunk into a structured context string.
        Args:
            doc: An object containing document metadata and an identifier. 
                 Expected to have a 'metadata' dictionary with 'title' and 'country' keys, 
                 and an 'id' attribute for retrieving the document chunk.
        Returns:
            str: A formatted string including the document's title, country, and content chunk, 
                 delimited by context markers.
        """
        
        context_input = f"""
        [START OF CONTEXT EVENT]
        Title: {doc.metadata["title"]}
        Country: {doc.metadata["country"]}

        Retrieved information:
        {self.dynamoDB.get_chunk(doc.id)}
        [END OF CONTEXT EVENT]
        """

        return context_input

    def _run(self, query_data_json: str) -> str:
        try:
            query_data = json.loads(query_data_json)
            query = query_data.get("topic", "")
            
            # Build comprehensive metadata filter
            filter_dict = {}
            
            if query_data.get("country"):
                filter_dict["country"] = query_data["country"]
            
            if query_data.get("pillar_1") is not None:
                filter_dict["pillar_1"] = query_data["pillar_1"]
            
            if query_data.get("pillar_2") is not None:
                filter_dict["pillar_2"] = query_data["pillar_2"]

            if query_data.get("pillar_3") is not None:
                filter_dict["pillar_3"] = query_data["pillar_3"]
            
            if query_data.get("pillar_4") is not None:
                filter_dict["pillar_4"] = query_data["pillar_4"]
            
            if query_data.get("pillar_5") is not None:
                filter_dict["pillar_5"] = query_data["pillar_5"]
            
            if query_data.get("pillar_6") is not None:
                filter_dict["pillar_6"] = query_data["pillar_6"]

            if query_data.get("pillar_7") is not None:
                filter_dict["pillar_7"] = query_data["pillar_7"]
            
            if query_data.get("pillar_8") is not None:
                filter_dict["pillar_8"] = query_data["pillar_8"]

            if query_data.get("impact_score"):
                
                impact_filter = query_data["impact_score"]

                if isinstance(impact_filter, dict):  # Handle comparison operators like {"gte": 7.5}
                    filter_dict["impact_score"] = impact_filter
                else:
                    filter_dict["impact_score"] = impact_filter
            
            # Perform similarity search
            embedded_query = self.vc.embbed_text(query)
            docs = self.pc.query(
                embedded_query = embedded_query,
                filters = filter_dict
            )
            
            # Format results
            results = [self._prepare_doc(doc) for doc in docs]
            formatted_results = "\n\n".join(results)
            
            return formatted_results
                               
        except Exception as e:
            print(f"Error searching news events: {str(e)}")