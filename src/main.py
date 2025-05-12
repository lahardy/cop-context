"""
Main entry point for demonstrating the pipeline.

This script simulates a workflow where:
1. A structured transcript object is processed to build an initial shared data context.
2. The LLM pipeline is then used for further tasks, interacting with the tools
   which access and potentially update this shared context.
"""

# Load environment variables (e.g., API keys) if needed
# from dotenv import load_dotenv
# import os
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Ensure your OpenAI client is configured appropriately (e.g., with the API key)
# import openai
# openai.api_key = OPENAI_API_KEY

import re # Import regex for name extraction simulation
from typing import Dict, List, Any
from context import Context, Person # Import Context and Person
from pipeline import run_pipeline

# Import the example transcript data
# Make sure the path is correct based on your project structure and PYTHONPATH
# If 'src' is your source root, this should work.
from src.examples.police_example import conversation_transcript

# --- Transcript Processing Function ---------------------------------------

def build_context_from_transcript(transcript_data: Dict[str, Any]) -> Context:
    """
    Processes a transcript dictionary to extract speakers and quotes,
    populating an initial shared Context object that tools can later access.
    Simulates basic name identification from text.
    """
    print("--- Building Context from Transcript --- ")
    initial_context = Context()
    people: Dict[str, Person] = {}

    # Attempt to identify names mentioned in the text
    # This is a very basic simulation of Named Entity Recognition (NER)
    name_patterns = {
        "S1": re.compile(r"Officer Johnson", re.IGNORECASE),
        "S2": re.compile(r"Robert Chen", re.IGNORECASE),
        "S4": re.compile(r"Sergeant Martinez", re.IGNORECASE)
        # S3 is a witness, name not mentioned
    }

    if not transcript_data or "segments" not in transcript_data:
        print("  Warning: Transcript data is empty or missing 'segments'.")
        return initial_context

    for segment in transcript_data["segments"]:
        speaker_id = segment.get("speaker")
        text = segment.get("text", "")

        if not speaker_id:
            continue # Skip segments without a speaker ID

        # If speaker not seen, create Person. Use speaker ID as initial name.
        if speaker_id not in people:
            people[speaker_id] = Person(name=f"Speaker {speaker_id[1:]}", speaker_id=speaker_id)
            print(f"  Identified speaker: {people[speaker_id].name} ({speaker_id})")

        person = people[speaker_id]
        
        # Add the quote regardless
        person.add_quote(text)

        # Simple name extraction simulation
        if speaker_id in name_patterns:
            match = name_patterns[speaker_id].search(text)
            if match:
                extracted_name = match.group(0)
                if person.name != extracted_name:
                    print(f"    Updating name for {speaker_id} to: {extracted_name}")
                    person.name = extracted_name
                    # Add role based on name patterns if desired (e.g., Officer, Sergeant)
                    if "Officer" in extracted_name: person.role = "Police Officer"
                    elif "Sergeant" in extracted_name: person.role = "Police Sergeant"
                    elif "Chen" in extracted_name: person.role = "Civilian Driver" # Example role assignment
            elif speaker_id == "S2" and not person.role: # Assign role if not already set by name match
                 person.role = "Civilian Driver"
            elif speaker_id == "S3" and not person.role:
                 person.role = "Witness"

    initial_context.set("people", people)
    initial_context.set("transcript_processed", True)
    initial_context.set("original_transcript_metadata", transcript_data.get("metadata"))
    print("--- Context Building Complete ---")
    return initial_context

# --- Example Usage --------------------------------------------------------

if __name__ == "__main__":
    
    # 1. Build the initial shared data context by processing the transcript
    # This context is intended to be accessed and modified by tools called via the LLM pipeline.
    initial_context = build_context_from_transcript(conversation_transcript)
    
    # Display the initial context built from the transcript
    print("\n--- Initial Context State ---")
    extracted_people = initial_context.get("people", {})
    if extracted_people:
        for speaker_id, person in extracted_people.items():
            print(f"  {person.name} ({person.role if person.role else '?'}, {speaker_id}): {len(person.quotes)} quotes stored.")
    else:
        print("  No people extracted during processing.")
    print(f"Initial context data keys: {list(initial_context.data.keys())}")

    # 2. Run LLM pipeline tasks that interact with tools accessing the context
    print("\n--- Running LLM Pipeline Examples --- ")
    # IMPORTANT NOTE: For this demonstration, `run_pipeline` currently creates a *new*, 
    # separate Context instance internally for each call. Therefore, the tools executed 
    # within these examples won't see the `initial_context` built above.
    # 
    # TO MAKE TOOLS USE THE SHARED CONTEXT: Modify `run_pipeline` and `task_loop` 
    # in `pipeline.py` to accept an existing `Context` object as an argument 
    # and pass `initial_context` into them.
    
    # Example 1: Ask the LLM to use a tool to add a new person. 
    # This action *should* modify the shared context (if it were passed in).
    user_query = "Please create a record for Charlie. He is a project manager."
    print(f"\n--- Running pipeline with query: ---\n'{user_query}'\n")
    # In a real setup, you might call: final_response = run_pipeline(user_query, context=initial_context)
    final_response = run_pipeline(user_query)
    print(f"\n--- Pipeline Response: ---\n{final_response}\n")
    # After this call, if context were shared, initial_context would now contain Charlie.

    # Example 2: Ask the LLM to use a tool to look up a person 
    # This action *should* read from the shared context (if passed in).
    user_query_2 = "Tell me about Robert Chen."
    print(f"\n--- Running pipeline with query: ---\n'{user_query_2}'\n")
    # In a real setup: final_response_2 = run_pipeline(user_query_2, context=initial_context)
    # This would ideally find Robert Chen from the pre-processing step.
    final_response_2 = run_pipeline(user_query_2) # In this demo, it won't find him.
    print(f"\n--- Pipeline Response: ---\n{final_response_2}\n")