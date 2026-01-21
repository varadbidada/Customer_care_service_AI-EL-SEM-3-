class BaseAgent:
    def __init__(self, name):
        self.name = name
    
    def process(self, message, context):
        raise NotImplementedError