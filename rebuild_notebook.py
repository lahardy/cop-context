import nbformat as nbf
import os

# --- Configuration --------------------------------------------------------
SRC_DIR = 'src' # Directory containing the source Python files
EXAMPLE_DIR = os.path.join(SRC_DIR, 'examples')
OUTPUT_NOTEBOOK = 'AI_Pipeline_Demo.ipynb'

# --- Notebook Creation ----------------------------------------------------
nbf_version = nbf.v4
nb = nbf_version.new_notebook()

# --- Introduction Cell ----------------------------------------------------
nb.cells.append(nbf_version.new_markdown_cell("""# AI Pipeline with Tools and Shared Context Demo

This notebook demonstrates an end-to-end workflow for an AI pipeline that:
1. Pre-processes structured data (a conversation transcript) to build an initial **shared data context**.
2. Uses an **LLM (OpenAI)** with **tool-calling capabilities**.
3. Defines **tools** (schemas and Pydantic models) for the LLM to use.
4. Provides **handler functions** that implement the tool logic and interact with the shared context.
5. Uses **prompts** to guide the LLM.
6. Orchestrates the interaction using a **pipeline** structure.

**Goal:** Illustrate how different components (data pre-processing, LLM, tools, handlers, context) work together in a modular way.

> ⚠️ **Setup:** 
> * Set the `OPENAI_API_KEY` environment variable before running (e.g., in a `.env` file).
> * Run the first code cell to install necessary packages.
"""))

# --- Setup Cells ----------------------------------------------------------

# Install requirements
nb.cells.append(nbf_version.new_markdown_cell("""## 1. Setup

Install required packages and configure the OpenAI client."""))
nb.cells.append(nbf_version.new_code_cell("!pip install -q openai python-dotenv pydantic"))

# Load API Key and initialize client (Example)
nb.cells.append(nbf_version.new_code_cell("""import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print("⚠️ OpenAI API Key not found. Please set the OPENAI_API_KEY environment variable.")
else:
    # Configure the OpenAI client (ensure this matches your usage in pipeline.py)
    # If using the global openai.api_key:
    openai.api_key = OPENAI_API_KEY 
    print("OpenAI API Key configured.")
    # Or, if using the client instance:
    # client = openai.OpenAI()
    # print("OpenAI client initialized.")
    
    # Define the client variable if pipeline.py expects it (e.g., from imports.py)
    # This is needed if pipeline.py uses `from imports import client`
    # Adjust based on your actual setup
    try:
        client = openai.OpenAI()
        print("OpenAI client instance created as 'client'.")
    except Exception as e:
        print(f"Could not create OpenAI client instance: {e}")
        # Fallback or handle as needed
        client = None 
"""))

# --- Code Cells from Files ------------------------------------------------

# Define the order and file paths for code cells relative to SRC_DIR
# Grouped logically for notebook flow
cell_sources = [
    # Core Data Structures
    (os.path.join(SRC_DIR, 'context.py'), '2. Context and Person Classes'),
    # Tool Definitions
    (os.path.join(SRC_DIR, 'tools.py'), '3. Tool Definitions (Enum, Models, Schemas)'),
    # Tool Implementation
    (os.path.join(SRC_DIR, 'handlers.py'), '4. Tool Handlers (Implementation Logic)'),
    # LLM Guidance
    (os.path.join(SRC_DIR, 'prompts.py'), '5. Prompts'),
    # Orchestration Logic
    (os.path.join(SRC_DIR, 'pipeline.py'), '6. Pipeline Orchestration'),
    # Example Data
    (os.path.join(EXAMPLE_DIR, 'police_example.py'), '7. Example Transcript Data'),
    # Main Execution / Demo
    (os.path.join(SRC_DIR, 'main.py'), '8. Demonstration')
]

# Function to read file content safely
def read_file_content(file_path):
    try:
        with open(file_path, 'r') as f:
            # Strip the `if __name__ == "__main__":` block from files being included
            # as library code, but keep it for the final main.py execution cell.
            lines = f.readlines()
            if not file_path.endswith('main.py'):
                try:
                    main_index = [i for i, line in enumerate(lines) if line.strip().startswith('if __name__ == "__main__":')][0]
                    lines = lines[:main_index]
                except IndexError:
                    pass # No main block found
            return "".join(lines)
    except FileNotFoundError:
        print(f"Warning: File not found at {file_path}")
        return f"# Error: File not found at {file_path}"
    except Exception as e:
        print(f"Warning: Could not read file {file_path}: {e}")
        return f"# Error reading file {file_path}: {e}"

# Add code cells to the notebook
for file_path, header in cell_sources:
    print(f"Adding cell for: {file_path}")
    # Add a markdown header cell
    nb.cells.append(nbf_version.new_markdown_cell(f"## {header}"))
    
    # Read the file content
    content = read_file_content(file_path)
    
    # Add the code cell
    nb.cells.append(nbf_version.new_code_cell(content))

# --- Finalization ---------------------------------------------------------

# Write the notebook to a file
with open(OUTPUT_NOTEBOOK, 'w') as f:
    nbf.write(nb, f)

print(f"Notebook '{OUTPUT_NOTEBOOK}' successfully rebuilt from source files in '{SRC_DIR}'.") 