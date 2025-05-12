# cop-context
Demonstrates an AI pipeline pre-processing structured data (e.g., transcripts) into a shared context, followed by LLM interaction using tools that access and modify this context

# AI Pipeline with Tools and Context Example

This project demonstrates a basic structure for building AI pipelines that leverage language models (like OpenAI's GPT) with external tools and manage shared state using a context object.

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── context.py       # Defines the Context and Person classes for shared state
│   ├── examples/        # Contains example data, like transcripts
│   │   └── police_example.py
│   ├── handlers.py      # Contains functions that execute tool logic
│   ├── imports.py       # (Optional/Assumed) Handles common imports like OpenAI client setup
│   ├── main.py          # Example entry point: pre-processes transcript then runs the pipeline
│   ├── pipeline.py      # Core logic orchestrating model calls, tool execution, and context management
│   ├── prompts.py       # Defines system prompts for the language model
│   └── tools.py         # Defines available tools (names, args schemas, OpenAI format)
├── requirements.txt   # Project dependencies
└── README.md          # This file
```

## Key Components

*   **`context.py`**: 
    *   `Context`: A simple class to store and retrieve data (`set`, `get`, `update`). It acts as a shared memory space accessible by different parts of the pipeline, primarily the tool handlers.
    *   `Person`: A data class used by the handlers to store information about individuals within the `Context`.
*   **`src/examples/police_example.py`**: Provides sample structured transcript data (`conversation_transcript`).
*   **`tools.py`**: Defines the tools the language model can request to use.
    *   `ToolName` (Enum): Provides standardized names for tools.
    *   `...Args` (Pydantic models): Define the expected arguments for each tool. Useful for validation.
    *   `tool_definitions`: A dictionary containing the tool schemas in the JSON format required by the OpenAI API. This tells the model what tools are available and what arguments they take.
*   **`prompts.py`**: Stores reusable system prompts.
    *   `PromptName` (Enum): Names for different prompts.
    *   `prompts`: Dictionary mapping `PromptName` to prompt strings. The `default_prompt` instructs the model on how to use the available tools.
*   **`handlers.py`**: Implements the actual logic for each tool.
    *   Each function (e.g., `create_person`, `lookup_person`) corresponds to a tool defined in `tools.py`.
    *   These functions receive parsed arguments from the model's request and the `Context` object.
    *   They interact with the `Context` (e.g., adding a `Person` to the `people` dictionary within the context) and return a result.
    *   `tool_handlers`: A dictionary mapping tool names (from `ToolName`) to their handler functions. Used by the pipeline to dispatch calls.
*   **`pipeline.py`**: Orchestrates the process when interacting with the language model.
    *   `get_completion`: Helper function to call the OpenAI API.
    *   `handle_tool_call`: Takes a tool call request from the model, finds the correct handler using `tool_handlers`, executes it with the shared `context`, and formats the result.
    *   `task_loop`: Manages a single turn of interaction with the LLM: calls the model, checks for tool calls, executes them via `handle_tool_call` (if needed), sends results back to the model, and gets the final response.
    *   `run_pipeline`: The main entry point for processing a query with the LLM. It can either initialize a new `Context` or (with modification) accept an existing one. It sets up the initial messages (system prompt + user query), calls `task_loop`, and returns the final response.
*   **`main.py`**: A script demonstrating the overall workflow:
    1.  Loads a sample transcript (from `src/examples/police_example.py`).
    2.  Calls `build_context_from_transcript` to pre-process this transcript, extracting entities (like speakers and their quotes) and populating an initial `Context` object.
    3.  Shows the state of this pre-populated `Context`.
    4.  Then, it demonstrates calling `run_pipeline` for subsequent LLM-based tasks. The comments highlight how the `initial_context` *could* be passed into and used by `run_pipeline` for a continuous state, though the current example resets it for each `run_pipeline` call.

## How it Works

1.  **Pre-processing (in `main.py`)**: 
    *   `main.py` loads the `conversation_transcript` from `src/examples/police_example.py`.
    *   It calls `build_context_from_transcript`, which parses the transcript, identifies speakers, extracts their quotes, and potentially other information (like names or roles through simple heuristics in this example).
    *   This information is used to create `Person` objects, which are stored in an `initial_context` object. This `initial_context` now holds a structured representation of the transcript's key entities.

2.  **LLM Pipeline Interaction (initiated from `main.py` calling `run_pipeline`)**:
    *   `run_pipeline` is called, for example, with a user query like "Summarize the interaction involving Officer Johnson."
    *   Ideally, this `run_pipeline` function would take the `initial_context` (or any ongoing context) as an argument.
    *   `run_pipeline` sets up the initial messages for the LLM (using a system prompt from `prompts.py` and the user query).
    *   It calls `task_loop`, which sends the messages and tool definitions (from `tools.py`) to the language model via `get_completion`.
    *   The model decides whether to respond directly or call a tool (e.g., `lookup_person` to find "Officer Johnson" in the context).
    *   If a tool is called:
        *   `task_loop` calls `handle_tool_call`.
        *   `handle_tool_call` finds the appropriate handler function in `handlers.py` (using `tool_handlers`).
        *   The handler (e.g., `lookup_person`) is executed. It accesses the `Context` (which should be the `initial_context` or an updated version of it) to find the requested information or make changes.
        *   `handle_tool_call` returns the result formatted as a tool message.
    *   `task_loop` appends the tool result message to the conversation history and calls `get_completion` again.
    *   The model receives the tool result and generates a final text response (e.g., "Officer Johnson was involved in a traffic stop...").
    *   This final response is returned up the chain to `main.py`.

## Setup and Running

1.  **Clone the repository (if applicable).**
2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure OpenAI API Key:**
    *   Make sure your OpenAI API key is set up. You can do this by setting the `OPENAI_API_KEY` environment variable.
    *   You might need to create a `.env` file in the root directory:
        ```
        OPENAI_API_KEY='your_api_key_here'
        ```
    *   Ensure your code (e.g., in `imports.py` or `main.py`) loads the environment variable and configures the OpenAI client.
    ```python
    # Example (ensure this matches your actual client setup)
    import os
    import openai
    from dotenv import load_dotenv

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # If using the new client:
    # client = openai.OpenAI()
    ```
5.  **Run the example:**
    ```bash
    python src/main.py
    ```

You should see output showing the transcript being pre-processed into an initial context, followed by the LLM pipeline processing sample queries. 