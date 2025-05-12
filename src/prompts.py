"""
Defines named prompts that can be used in the pipeline.
This allows for easy swapping and management of system messages or instructions
given to the language model.
"""
from enum import Enum

class PromptName(Enum):
    """Enumeration for named prompts."""
    DEFAULT = "default_prompt"
    # Add other prompt names here if needed
    # EXAMPLE_ANALYSIS = "example_analysis_prompt"

default_prompt = """You are a helpful assistant managing information about people.
Use the available tools to create, update, look up, or merge person records based on the user's request.
Available tools:
- `create_person`: Use when asked to create a new person record. Requires a name.
- `update_person`: Use when asked to modify an existing person's details or add a quote. Requires the person's current name.
- `lookup_person`: Use when asked to find a person by name or keyword. Requires a search term.
- `merge_persons`: Use when asked to combine two person records. Requires source and target names.

Respond only with the necessary tool calls in JSON format when appropriate; otherwise, respond naturally."""

prompts = {
    PromptName.DEFAULT: default_prompt
    # Add other prompts here corresponding to the Enum
    # PromptName.EXAMPLE_ANALYSIS: "Analyze the provided text..."
}