"""Confirm we can call all three providers via one OpenRouter key."""
from jev_video.caller import call_model

tests = [
    ("chit_chat",      "Say hi in exactly 3 words."),
    ("coding",         "In Python, how do you reverse a list in one line?"),
    ("reasoning_math", "If 3x + 7 = 22, what is x? Just the number."),
]

for category, prompt in tests:
    result = call_model(category, prompt)
    print(f"\n[{category}]  via {result['model']}")
    print(f"  Prompt:  {prompt}")
    print(f"  Answer:  {result['text'].strip()}")
    print(f"  Tokens:  in={result['input_tokens']} out={result['output_tokens']}")
    print(f"  Cost:    ${result['cost_usd']:.6f}")
