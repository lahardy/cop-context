"""
Core pipeline logic for processing user input with a language model and tools.

This module orchestrates the interaction between the user, the language model,
and the defined tools. It follows a general pattern:
1.  Send user input (and system prompt) to the model.
2.  The model may respond directly or request a tool call.
3.  If a tool is called:
    a.  The corresponding handler function is executed with arguments from the model.
    b.  The handler interacts with the shared `Context`.
    c.  The result of the tool execution is sent back to the model.
4.  The model generates a final response based on the tool result (or its initial reasoning).
"""
import json
# import openai # Import normally handled by imports.py or at top-level of main
from context import Context
from tools import ToolName, tool_definitions
from handlers import tool_handlers
from prompts import PromptName, prompts
from typing import Dict, List, Any, Tuple

def get_completion(messages: List[Dict[str, str]], model: str, tools: List[Dict] = None, tool_choice: str = None) -> Any:
    """
    Get a completion from the OpenAI API.

    Args:
        messages: List of message dictionaries (system, user, assistant, tool).
        model: The OpenAI model ID (e.g., "gpt-4o-mini").
        tools: Optional list of tool definitions for the model to use.
        tool_choice: Optional specific tool to call or "auto"/"none".

    Returns:
        The OpenAI API response object.
    """
    # Ensure client is initialized (e.g., API key set)
    # This might be done globally or passed in.
    from imports import client # Assuming client is configured in imports.py
    
    completion_args = {
        "model": model,
        "messages": messages,
    }
    
    if tools:
        completion_args["tools"] = tools
        if tool_choice: # tool_choice can be "auto", "none", or {"type": "function", "function": {"name": "my_function"}}
            completion_args["tool_choice"] = tool_choice
    
    # Make the API call
    return client.chat.completions.create(**completion_args)

def handle_tool_call(tool_call: Any, context: Context) -> Tuple[Dict[str, str], Any]:
    """
    Execute a tool call based on its name and arguments, using the handlers.

    Args:
        tool_call: The tool_call object from the OpenAI response.
                   (Contains id, type, function.name, function.arguments)
        context: The shared Context object for this request.

    Returns:
        A tuple containing:
        - tool_result_msg: A dictionary formatted for the OpenAI API tool message.
        - result: The direct result from the tool handler.
    """
    tool_name = tool_call.function.name
    # Arguments are a JSON string, so parse them into a dictionary.
    try:
        args_dict = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        # Handle cases where arguments are not valid JSON
        error_msg = f"Error: Invalid JSON arguments for tool {tool_name}: {tool_call.function.arguments}"
        return {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": error_msg})}, None

    # Look up the handler function for this tool.
    if tool_name in tool_handlers:
        handler = tool_handlers[tool_name]
        
        # Call the handler with the parsed arguments and the context.
        # Note: This assumes handlers are designed to accept arguments unpacked 
        # from args_dict and a 'context' keyword argument.
        # More robust argument parsing could involve Pydantic models from tools.py.
        try:
            # Pass context explicitly to the handler
            result = handler(**args_dict, context=context) 
        except TypeError as e:
            # Handle errors if handler arguments don't match (e.g. missing context or wrong arg names)
            error_msg = f"Error calling handler for {tool_name}: {e}"
            return {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": error_msg})}, None
    else:
        # Handle cases where an unknown tool is called.
        error_msg = f"Error: Unknown tool '{tool_name}' requested."
        return {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": error_msg})}, None
    
    # Format the tool's result into a message for the OpenAI API.
    tool_result_msg = {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({ "result": result }) # The model expects the content to be a JSON string.
    }
    
    return tool_result_msg, result

def task_loop(messages: List[Dict[str, str]], model: str, context: Context) -> Tuple[List[Dict[str, str]], str]:
    """
    Execute a single interaction cycle: model -> [tool -> model] -> final response.
    
    This involves:
    1.  Calling the model with the current messages and available tools.
    2.  If the model requests a tool call:
        a.  Executing the tool via `handle_tool_call`.
        b.  Appending the tool's result to the messages.
        c.  Calling the model again with the updated messages to get a final response.
    3.  If no tool call is made, the model's first response is considered final.

    Args:
        messages: The current list of message objects (conversation history).
        model: The OpenAI model ID.
        context: The shared Context object.

    Returns:
        A tuple containing:
        - messages: The updated list of message objects (entire conversation).
        - final_content: The assistant's final textual response.
    """
    # Convert the tool definitions from the dictionary format to a list of schemas.
    tool_schemas_list = [value["function"] for value in tool_definitions.values()] 
    # For newer API: tool_schemas_list = list(tool_definitions.values()) if they include "type": "function"

    # --- Step 1: Initial call to the model ---    
    # Ask the model for a response, allowing it to choose a tool if appropriate ("auto").
    first_completion = get_completion(
        messages=messages,
        model=model,
        tools=tool_schemas_list, # Pass the schemas
        tool_choice="auto"      # Allow the model to decide if it needs a tool
    )
    assistant_msg_obj = first_completion.choices[0].message
    
    # Append the assistant's turn (which might be a message or a tool call request) to messages.
    # We need to reconstruct the tool_calls list if present for our message history.
    assistant_tool_calls = None
    if assistant_msg_obj.tool_calls:
        assistant_tool_calls = [
            {"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in assistant_msg_obj.tool_calls
        ]

    messages.append({
        "role": "assistant", 
        "content": assistant_msg_obj.content, # Can be None if only tool_calls are present
        "tool_calls": assistant_tool_calls
    })
    
    final_content = assistant_msg_obj.content # Default if no tool call

    # --- Step 2: Handle potential tool call(s) ---    
    if assistant_msg_obj.tool_calls:
        # Currently, this example handles the first tool call if multiple are returned.
        # A more robust implementation might loop through all tool_calls.
        tool_call = assistant_msg_obj.tool_calls[0]
        
        # Execute the tool and get its result.
        tool_result_msg, _ = handle_tool_call(tool_call, context)
        
        # Append the tool's result to the messages.
        messages.append(tool_result_msg)
        
        # --- Step 3: Call model again with tool result --- 
        # Send the tool's result back to the model to get a final, synthesized response.
        follow_up_completion = get_completion(
            messages=messages,
            model=model
            # No tools/tool_choice needed here usually, as we expect a textual response.
        )
        final_content = follow_up_completion.choices[0].message.content
        
        # Append the model's final response to messages.
        messages.append({"role": "assistant", "content": final_content})
    
    return messages, final_content

def run_pipeline(input_data: str, model: str = "gpt-4o-mini") -> str:
    """
    Main entry point for running the processing pipeline for a single user query.

    Initializes a Context, sets up initial system and user messages, and then
    runs the task_loop to get the final assistant response.

    Args:
        input_data: The user's query or input string.
        model: The OpenAI model ID to use.

    Returns:
        The assistant's final textual response.
    """
    # Create a new Context object for this specific run. 
    # This means context is fresh for each call to run_pipeline.
    # For persistent context across multiple turns, manage Context outside this function.
    context = Context()
    
    # Retrieve the system prompt. For this example, we use a default one.
    system_prompt = prompts.get(PromptName.DEFAULT, "You are a helpful assistant.")
    if isinstance(system_prompt, PromptName): # Ensure we get the string if an enum was returned by mistake
        system_prompt = prompts.get(system_prompt, "You are a helpful assistant.")

    # Initialize the conversation messages list.
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_data}
    ]
    
    # Execute the main interaction loop.
    # The returned `messages` list will contain the full conversation history for this run.
    _, final_content = task_loop(messages, model, context)
    
    # The pipeline returns the final textual content from the assistant.
    return final_content