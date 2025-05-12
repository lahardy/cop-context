"""
Defines handler functions for each tool.

Each handler function takes the arguments extracted from the model's tool call
and the shared `Context` object. It performs the actual action associated
with the tool (e.g., modifying data in the context) and returns a result.
The `tool_handlers` dictionary maps tool names to their corresponding handler functions.
"""
from context import Context, Person
from tools import ToolName
from typing import Dict, List, Any, Optional, Union

# --- Tool Handlers --------------------------------------------------------
# These functions implement the actual logic for each tool.
# They interact with the shared Context object to read/write data.

def create_person(name: str, description: str = "", role: str = "", speaker_id: str = "", context: Context = None) -> Dict[str, Any]:
    """Handler for the 'create_person' tool. Creates a Person in the context."""
    if context is None:
        # In a real application, consider a more robust error handling or logging mechanism.
        return {"error": "Context is required for create_person handler"}
    
    # Create a new person instance
    person = Person(name=name, description=description, role=role, speaker_id=speaker_id)
    
    # Retrieve the current 'people' dictionary from context, or initialize if not present.
    people = context.get("people", {})
    
    # Add the new person to the dictionary, using their name as the key.
    # Consider potential collisions or updating existing entries if needed.
    people[name] = person
    
    # Update the context with the modified 'people' dictionary.
    context.set("people", people)
    # Optionally, update context with info about the last operation for potential chaining or debugging.
    context.update({
        "last_operation": ToolName.CREATE_PERSON.value,
        "last_result_summary": f"Created person: {name}"
    })
    
    # Return a success status and information about the created person.
    # The result will be sent back to the language model.
    return {"status": "success", "person_name": name, "details": str(person)}

def update_person(person_name: str, name: Optional[str] = None, description: Optional[str] = None, 
                  role: Optional[str] = None, speaker_id: Optional[str] = None, 
                  quote: Optional[str] = None, context: Context = None) -> Dict[str, Any]:
    """Handler for the 'update_person' tool. Updates attributes or adds a quote."""
    if context is None:
        return {"error": "Context is required for update_person handler"}
    
    people = context.get("people", {})
    
    if person_name not in people:
        return {"error": f"Person '{person_name}' not found. Cannot update."}
    
    person = people[person_name]
    original_name = person_name # Store original name in case it changes
    updated = False

    # Prepare dictionary of updates, excluding None values
    updates = {}
    if name is not None and name != person.name: updates["name"] = name
    if description is not None: updates["description"] = description
    if role is not None: updates["role"] = role
    if speaker_id is not None: updates["speaker_id"] = speaker_id
    
    if updates:
        person.add_data(**updates)
        updated = True
        # If the name changed, update the key in the people dictionary
        if "name" in updates:
            new_name = updates["name"]
            if new_name != original_name:
                people.pop(original_name) # Remove old entry
                people[new_name] = person # Add new entry
    
    if quote is not None:
        person.add_quote(quote)
        updated = True
    
    if not updated:
        return {"status": "no_change", "message": f"No updates provided for {original_name}"}

    # Update the context with the potentially modified 'people' dictionary
    context.set("people", people)
    context.update({
        "last_operation": ToolName.UPDATE_PERSON.value,
        "last_result_summary": f"Updated person: {person.name}"
    })
    
    return {"status": "success", "person_name": person.name, "details": str(person)}

def lookup_person(keyword: str, context: Context = None) -> Dict[str, Any]:
    """Handler for the 'lookup_person' tool. Finds people by keyword."""
    if context is None:
        return {"error": "Context is required for lookup_person handler"}
    
    people = context.get("people", {})
    results = []
    keyword_lower = keyword.lower()
    
    # Simple search: check name, description, and role
    for name, person in people.items():
        if (keyword_lower in name.lower() or 
            keyword_lower in person.description.lower() or
            keyword_lower in person.role.lower()):
            # Return a summary or identifier, not the full object usually
            results.append({"name": person.name, "role": person.role, "description": person.description})
    
    context.update({
        "last_operation": ToolName.LOOKUP_PERSON.value,
        "last_result_summary": f"Found {len(results)} match(es) for '{keyword}'",
        "search_keyword": keyword
    })
    
    if not results:
        return {"status": "no_matches", "message": f"No people found matching '{keyword}'"}
    
    # Return the found results
    return {"status": "success", "results": results, "count": len(results)}

def merge_persons(source_name: str, target_name: str, context: Context = None) -> Dict[str, Any]:
    """Handler for the 'merge_persons' tool. Merges source into target."""
    if context is None:
        return {"error": "Context is required for merge_persons handler"}
    
    people = context.get("people", {})
    
    if source_name not in people:
        return {"error": f"Source person '{source_name}' not found. Cannot merge."}
    if target_name not in people:
        return {"error": f"Target person '{target_name}' not found. Cannot merge."}
    if source_name == target_name:
         return {"error": f"Cannot merge person '{source_name}' into themself."}
    
    source_person = people[source_name]
    target_person = people[target_name]
    
    # Perform the merge using the Person class's merge method
    target_person.merge(source_person)
    
    # Remove the source person after merging
    people.pop(source_name)
    
    # Update context
    context.set("people", people)
    context.update({
        "last_operation": ToolName.MERGE_PERSONS.value,
        "last_result_summary": f"Merged '{source_name}' into '{target_name}'",
        "merged_from": source_name,
        "merged_to": target_name
    })
    
    return {"status": "success", "merged_person_name": target_name, "details": str(target_person)}

# --- Handler Mapping ------------------------------------------------------
# Maps tool names (enum values) to their corresponding handler functions.
# This dictionary is used by the pipeline to dispatch tool calls.
tool_handlers = {
    ToolName.CREATE_PERSON.value: create_person,
    ToolName.UPDATE_PERSON.value: update_person,
    ToolName.LOOKUP_PERSON.value: lookup_person,
    ToolName.MERGE_PERSONS.value: merge_persons
}