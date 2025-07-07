from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, PrivateAttr, Field

# class NewsSearchInput(BaseModel):
#     """Input schema for NewsSearchTool"""
#     query_data_json: str = Field(description="JSON string containing query and optional filters")

class NewsSearchInput(BaseModel):
    """Input schema for NewsSearchTool"""
    query: str = Field(description="Search query")
    country: Optional[str] = Field(default=None, description="Filter by country")
    pillar_1: Optional[int] = Field(default=None, description="Filter for Government Constraints")
    pillar_2: Optional[int] = Field(default=None, description="Filter for Corruption Control")
    pillar_3: Optional[int] = Field(default=None, description="Filter for Open Government")
    pillar_4: Optional[int] = Field(default=None, description="Filter for Fundamental Rights")
    pillar_5: Optional[int] = Field(default=None, description="Filter for Order and Security")
    pillar_6: Optional[int] = Field(default=None, description="Filter for Regulatory Enforcement")
    pillar_7: Optional[int] = Field(default=None, description="Filter for Civil Justice")
    pillar_8: Optional[int] = Field(default=None, description="Filter for Criminal Justice")
    impact_score: Optional[dict] = Field(default=None, description="Filter by impact score")


class NewsSearchTool(BaseTool):
    """Tool for searching news events using vector similarity search"""
    
    name: str = "news_events_search"
    description: str = ""  # Will be set in __init__
    args_schema: Type[BaseModel] = NewsSearchInput

    _vc: any = PrivateAttr()
    _pc: any = PrivateAttr()
    _ddbc: any = PrivateAttr()
    

    def __init__(self, vc, pc, ddbc, description: str):
        super().__init__(description=description)
        self._vc = vc         # Voyage Client
        self._pc = pc         # Pinecone Client
        self._ddbc = ddbc     # DynamoDB Client
    

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
        {self._ddbc.get_chunk(doc.id)}
        [END OF CONTEXT EVENT]
        """

        return context_input

    def _run(
        self, query: str, 
        country: Optional[str] = None, 
        pillar_1: Optional[int] = None, 
        pillar_2: Optional[int] = None, 
        pillar_3: Optional[int] = None, 
        pillar_4: Optional[int] = None, 
        pillar_5: Optional[int] = None,
        pillar_6: Optional[int] = None, 
        pillar_7: Optional[int] = None,
        pillar_8: Optional[int] = None, 
        impact_score: Optional[dict] = None,
        run_manager: Optional[any] = None
    ) -> str:

        try:
            
            # Build comprehensive metadata filter
            filter_dict = {}

            if country:
                filter_dict["country"] = country
            
            for i in range(1, 9):
                pillar_value = locals().get(f"pillar_{i}")
                if pillar_value is not None:
                    filter_dict[f"pillar_{i}"] = pillar_value
            
            if impact_score:
                filter_dict["impact_score"] = impact_score

            print("=========================================")
            print("PERFORMING SIMILARITY SEARCH IN DATABASE")
            print(f"Filters: {filter_dict}")
            print("=========================================")
            
            # Perform similarity search
            embedded_query = self._vc.embed_text(query)
            docs = self._pc.query(
                embedded_query = embedded_query,
                filters = filter_dict
            )
            
            # Format results
            results = [self._prepare_doc(doc) for doc in docs]
            formatted_results = "\n\n".join(results)
            
            return formatted_results
                               
        except Exception as e:
            error_msg = f"Error searching news events: {str(e)}"
            print(error_msg)
            return error_msg