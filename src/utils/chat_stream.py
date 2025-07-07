from langchain_core.messages import AIMessage

class ChatStreamer:
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.last_response = ""
    
    def stream_response(self, messages):
        """Stream response and store full message"""
        def response_generator():
            full_response = ""
            for chunk, _ in self.app.stream(
                {"messages": messages}, 
                self.config, 
                stream_mode="messages"
            ):
                if isinstance(chunk, AIMessage):
                    content = chunk.content
                    full_response += content
                    yield content
            
            self.last_response = full_response
        
        return response_generator()
    
    def get_last_response(self):
        return self.last_response