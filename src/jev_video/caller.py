"""Call any OpenRouter chat model via the OpenAI SDK."""

import os
from openai import OpenAI
from dotenv import load_dotenv
from jev_video.models import CATEGORY_TO_MODEL, PRICES

load_dotenv()

# Same OpenAI SDK — just pointed at OpenRouter.
_client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)


def call_model(category: str, prompt: str) -> dict:
    """Pick the model for this category, call it, return answer + usage + cost."""
    model = CATEGORY_TO_MODEL[category]

    response = _client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    usage = response.usage
    price = PRICES[model]
    cost = (
        usage.prompt_tokens * price["in"]
        + usage.completion_tokens * price["out"]
    ) / 1_000_000

    return {
        "model": model,
        "text": response.choices[0].message.content,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "cost_usd": round(cost, 6),
    }
