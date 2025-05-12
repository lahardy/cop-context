from typing import Dict, Any, List, Optional

class Person:
    """A class to represent a person with various attributes"""
    
    def __init__(self, name: str = "", description: str = "", role: str = "", speaker_id: str = ""):
        self.name: str = name
        self.description: str = description
        self.role: str = role
        self.speaker_id: str = speaker_id
        self.quotes: List[str] = []
    
    def add_data(self, **kwargs) -> None:
        """Update person attributes with provided data"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_quote(self, quote: str) -> None:
        """Add a quote to the person's quotes"""
        self.quotes.append(quote)
    
    def merge(self, other: 'Person') -> 'Person':
        """Merge another person into this one, taking non-empty values"""
        if other.name and not self.name:
            self.name = other.name
        if other.description and not self.description:
            self.description = other.description
        if other.role and not self.role:
            self.role = other.role
        if other.speaker_id and not self.speaker_id:
            self.speaker_id = other.speaker_id
        # Add unique quotes
        for quote in other.quotes:
            if quote not in self.quotes:
                self.quotes.append(quote)
        return self
    
    def __str__(self) -> str:
        return f"Person(name='{self.name}', description='{self.description}', role='{self.role}', quotes={len(self.quotes)})"

class Context:
    """A simple context manager to store and retrieve state between tool calls"""
    
    def __init__(self, input_data: Dict[str, Any] = {}):
        self.data: Dict[str, Any] = {}
        self.input_data = input_data
        
    def set(self, key: str, value: Any) -> None:
        """Store a value in the context"""
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the context"""
        return self.data.get(key, default)
    
    def update(self, values: Dict[str, Any]) -> None:
        """Update context with multiple values"""
        self.data.update(values)
    
    def __str__(self) -> str:
        return str(self.data)