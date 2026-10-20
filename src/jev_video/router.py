"""Classify an incoming prompt and route it to the best model."""

import time

from typesafe_sdk import Choice, Score

from jev_video.jev import ask_jev
from jev_video.caller import call_model

# Single source of truth for category names. models.py keys off these strings.
CATEGORIES = {
    "chit_chat":         "Greetings, thanks, small talk, filler, or one-liners that don't ask for substantive help.",
    "coding":            "Writing, reviewing, debugging, or explaining code, SQL, shell commands, or config.",
    "reasoning_math":    "Problems that need step-by-step logic, calculations, proofs, or formal reasoning.",
    "writing_creative":  "Drafting emails, blog posts, marketing copy, essays, or any structured prose.",
    "general_knowledge": "Short factual questions a dictionary or encyclopedia would answer in one line.",
    "complex_analysis":  "Multi-step analysis, architecture, system design, synthesis, or long-horizon planning.",
}

CONFIDENCE_LEVELS = ["guessing", "unsure", "moderate", "confident", "certain"]
CONFIDENCE_THRESHOLD = 0.35


def classify(prompt: str) -> dict:
    """Ask JEV which category this prompt belongs to, plus how sure it is."""
    response = ask_jev(
        state=f"A user sent this prompt to an AI assistant:\n\n{prompt}",
        questions={
            "category": Choice(
                instructions="Which category does this prompt belong to? Pick exactly one.",
                criteria=CATEGORIES,
            ),
            "confidence": Score(
                instructions="How confident are you in that category choice?",
                criteria=CONFIDENCE_LEVELS,
            ),
        },
    )

    raw_category = response.answers["category"].choice
    raw_score = response.answers["confidence"].score
    confidence = raw_score / (len(CONFIDENCE_LEVELS) - 1)

    final_category, bumped = raw_category, False
    if confidence < CONFIDENCE_THRESHOLD and raw_category in ("chit_chat", "general_knowledge"):
        final_category = "general_knowledge"
        bumped = True

    return {
        "category": final_category,
        "raw_category": raw_category,
        "confidence": round(confidence, 2),
        "bumped": bumped,
    }


def route(prompt: str) -> dict:
    """End-to-end: classify the prompt, then call the right model."""
    t0 = time.perf_counter()
    decision = classify(prompt)
    t1 = time.perf_counter()
    answer = call_model(decision["category"], prompt)
    t2 = time.perf_counter()

    return {
        **decision,
        **answer,
        "classify_ms": round((t1 - t0) * 1000, 1),
        "answer_ms": round((t2 - t1) * 1000, 1),
    }
