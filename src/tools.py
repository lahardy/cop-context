"""
Defines the tools available to the language model.

This includes:
1.  An Enum (`ToolName`) for easy reference to tool names.
2.  Pydantic models (`...Args`) defining the expected arguments for each tool.
    These are useful for validation and potentially for parsing arguments
    before calling handler functions.
3.  A dictionary (`tool_definitions`) mapping tool names to their JSON schema
    definitions, which are provided to the language model.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# --- Tool names ---------------------------------------------------
class ToolName(Enum):
    """Enumeration of available tool names."""
    CREATE_PERSON = "create_person"
    UPDATE_PERSON = "update_person"
    LOOKUP_PERSON = "lookup_person"
    MERGE_PERSONS = "merge_persons"

# --- Pydantic models for tool arguments --------------------------
# These models define the expected structure for arguments extracted
# from the language model's tool call request.

class CreatePersonArgs(BaseModel):
    """Arguments for the create_person tool."""
    name: str = Field(..., description="The person's name")
    description: Optional[str] = Field(default="", description="A description of the person")
    role: Optional[str] = Field(default="", description="The person's role")
    speaker_id: Optional[str] = Field(default="", description="The person's speaker ID")
    # context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context data") # Context is handled by the pipeline/handler

class UpdatePersonArgs(BaseModel):
    """Arguments for the update_person tool."""
    person_name: str = Field(..., description="The name of the person to update")
    name: Optional[str] = Field(default=None, description="Updated name")
    description: Optional[str] = Field(default=None, description="Updated description")
    role: Optional[str] = Field(default=None, description="Updated role")
    speaker_id: Optional[str] = Field(default=None, description="Updated speaker ID")
    quote: Optional[str] = Field(default=None, description="A quote to add to the person")
    # context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context data") # Context is handled by the pipeline/handler

class LookupPersonArgs(BaseModel):
    """Arguments for the lookup_person tool."""
    keyword: str = Field(..., description="The name or keyword to search for")
    # context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context data") # Context is handled by the pipeline/handler

class MergePersonsArgs(BaseModel):
    """Arguments for the merge_persons tool."""
    source_name: str = Field(..., description="The name of the source person")
    target_name: str = Field(..., description="The name of the target person to merge into")
    # context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context data") # Context is handled by the pipeline/handler

# --- Tool definitions (OpenAI format) ----------------------------
# This dictionary provides the tool schemas in the format expected by the OpenAI API.

tool_definitions = {
    ToolName.CREATE_PERSON: {
        "type": "function", # Recommended to specify type for newer API versions
        "function": {
            "name": ToolName.CREATE_PERSON.value,
            "description": "Create a new Person object in the context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The person's name"},
                    "description": {"type": "string", "description": "A description of the person"},
                    "role": {"type": "string", "description": "The person's role"},
                    "speaker_id": {"type": "string", "description": "The person's speaker ID"}
                },
                "required": ["name"]
            }
        }
    },
    
    ToolName.UPDATE_PERSON: {
        "type": "function",
        "function": {
            "name": ToolName.UPDATE_PERSON.value,
            "description": "Update a Person's data or add a quote.",
            "parameters": {
                "type": "object",
                "properties": {
                    "person_name": {"type": "string", "description": "The name of the person to update"},
                    "name": {"type": "string", "description": "Updated name"},
                    "description": {"type": "string", "description": "Updated description"},
                    "role": {"type": "string", "description": "Updated role"},
                    "speaker_id": {"type": "string", "description": "Updated speaker ID"},
                    "quote": {"type": "string", "description": "A quote to add to the person"}
                },
                "required": ["person_name"]
            }
        }
    },
    
    ToolName.LOOKUP_PERSON: {
        "type": "function",
        "function": {
            "name": ToolName.LOOKUP_PERSON.value,
            "description": "Find a person by name or keyword in description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "The name or keyword to search for"}
                },
                "required": ["keyword"]
            }
        }
    },
    
    ToolName.MERGE_PERSONS: {
        "type": "function",
        "function": {
            "name": ToolName.MERGE_PERSONS.value,
            "description": "Merge two Person objects, combining their data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_name": {"type": "string", "description": "The name of the source person"},
                    "target_name": {"type": "string", "description": "The name of the target person to merge into"}
                },
                "required": ["source_name", "target_name"]
            }
        }
    }
}