from typing import List
import voyageai

class VoyageClient:
    """Client for VoyageAI embeddings."""
    
    def __init__(self, api_key: str, model: str):
        self.engine = voyageai.Client(api_key)
        self.model = model
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embeds the given text using the VoyageAI engine.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The embedded text as a list of floats.
        """
        return self.engine.embed(
            text,
            model=self.model,
            input_type="document"
        ).embeddings[0]