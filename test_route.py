"""End-to-end test: prompt in, routed answer out."""
import json
from jev_video.router import route

prompts = [
    "hi",
    "what is the capital of Japan?",
    "write me a one-line Python regex for a UK postcode",
    "if a train leaves at 8am going 60mph and another at 9am going 80mph, when do they meet?",
]

for p in prompts:
    print(f"\n{'='*70}\nPrompt: {p}")
    result = route(p)
    print(f"Category: {result['category']}  (conf {result['confidence']}, bumped={result['bumped']})")
    print(f"Model:    {result['model']}")
    print(f"Timing:   classify {result['classify_ms']}ms  +  answer {result['answer_ms']}ms")
    print(f"Cost:     ${result['cost_usd']:.6f}")
    print(f"Answer:   {result['text'][:200]}")
