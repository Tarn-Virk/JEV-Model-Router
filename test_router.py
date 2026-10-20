"""Test the classifier with a variety of prompts."""
from jev_video.router import classify

prompts = [
    "hi there!",
    "write me a Python function to reverse a linked list",
    "if a train leaves at 8am going 60mph and another at 9am going 80mph, when do they meet?",
    "draft an email asking my boss for a raise",
    "capital of Japan?",
    "design a horizontally scalable rate limiter under network partition",
]

for p in prompts:
    result = classify(p)
    print(f"[{result['category']:<17}] conf={result['confidence']:.2f}  {p[:60]}")
