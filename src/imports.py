from dotenv import load_dotenv
import json
import os
import openai
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
assert OPENAI_API_KEY, "OPENAI_API_KEY is not set"

client = openai.OpenAI(api_key=OPENAI_API_KEY)