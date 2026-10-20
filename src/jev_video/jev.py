"""Shared JEV wrapper used by the router and the guardrail."""
#import dependencies
import os
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient

# Load OPENROUTER_API_KEY from .env into environment variables.
load_dotenv()

# Create one TypeSafe client, pointed at OpenRouter's base URL.
# base_url="https://openrouter.ai/api" → the ONE line that redirects the SDK from TypeSafe-direct to OpenRouter
_client = TypeSafeClient(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api",
)

#Typesafe maps it to the latest jev model 
JEV_MODEL = "jev-latest"


def ask_jev(state: str, questions: dict):
    """Send any mix of Choice/Noul/Score questions to JEV in one call.

    state: the thing being judged (a user prompt, a shell command, etc.)
    questions: dict of name → question object (Choice, Noul, or Score)
    """
    return _client.system_one(state, questions, model=JEV_MODEL)
