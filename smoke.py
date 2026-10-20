"""Smoke test: can we talk to JEV?"""
from typesafe_sdk import Noul
from jev_video.jev import ask_jev

# State is the actual query
# question is Noul Yes or No - Is it Trivial 

response = ask_jev(
    state="A user asked an AI assistant: what is 2+2?",
    questions={
        "is_trivial": Noul(instructions="Is this a trivial question for an AI to answer?"),
    },
)

answer = response.answers["is_trivial"]

print(f"Probability this is trivial: {answer.noul:.3f}")

#tells you which exact JEV build served the request (useful for debugging)
print(f"Model: {response.model}")
