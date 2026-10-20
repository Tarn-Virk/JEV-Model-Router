"""Map each router category to its best-in-class model + per-million-token prices.

Model slugs come from https://openrouter.ai/models. Verify current prices there
before publishing — OpenRouter updates them weekly.
"""

CATEGORY_TO_MODEL = {
    "chit_chat":         "google/gemini-3.5-flash",     # cheap, fast, fine for "hi"
    "coding":            "anthropic/claude-sonnet-5.5", # Anthropic strongest at code
    "reasoning_math":    "openai/gpt-5.6-sol",          # OpenAI strong on reasoning
    "writing_creative":  "anthropic/claude-opus-5.5",   # Anthropic best writing
    "general_knowledge": "google/gemini-3.5-flash",     # fast factual
    "complex_analysis":  "anthropic/claude-opus-5.5",   # long-horizon synthesis
}

# $ per 1 MILLION tokens. in = input (your prompt), out = output (the reply).
# PLACEHOLDER PRICES — verify on openrouter.ai/models before publishing.
PRICES = {
    "google/gemini-3.5-flash":     {"in": 0.16, "out": 0.63},
    "anthropic/claude-sonnet-5.5": {"in": 2.00, "out": 10.00},
    "openai/gpt-5.6-sol":          {"in": 2.00, "out": 10.00},
    "anthropic/claude-opus-5.5":   {"in": 4.00, "out": 20.00},
}
